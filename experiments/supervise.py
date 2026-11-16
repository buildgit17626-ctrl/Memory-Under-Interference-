"""Terminal-only supervisor. Run prepare first; all input blockers are explicit."""

import argparse
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from prompt_energy.hwinfo import LogFormat
from prompt_energy.ollama import Client, decode_response
from prompt_energy.records import directory_lock
from prompt_energy.utilisation_e0_analysis import analyse
from prompt_energy.utilisation_eval import evaluate, load_dataset
from prompt_energy.utilisation_freeze import verify_registration
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import ROOT, digest, load_config, schedule
from prompt_energy.utilisation_run import Sensor, by_key
from prompt_energy.utilisation_supervisor import (
    Halt,
    generate_batch,
    validate_pipeline,
    write_checkpoint,
)


def load_jobs(path: str, cfg: dict, config_hash: str) -> list:
    stimulus = ROOT / path
    jobs = schedule(json.loads(stimulus.read_text()), cfg, config_hash)
    verify_registration(jobs, stimulus, cfg)
    return jobs


def timing_checkpoint(root: Path, e0: list, m3: list, pipeline: dict) -> dict:
    groups = defaultdict(list)
    for row in by_key(root / "M3" / "calls.jsonl").values():
        groups[row["identity"]["context_length"]].append(row)
    rates = {}
    for length, rows in groups.items():
        rates[length] = {
            "calls": len(rows),
            "mean_seconds": sum(r["wall_seconds"] for r in rows) / len(rows),
            "invalid": sum(not r["input_valid"] for r in rows),
            "output_caps": sum("output_cap" in r["flags"] for r in rows),
        }
    budget = pipeline.get("remaining_main_by_length")
    estimates = None
    remaining_calls = max(
        0,
        4808 - len(by_key(root / "E0" / "calls.jsonl")) - len(by_key(root / "M3" / "calls.jsonl")),
    )
    service = [r["mean_seconds"] + 5 for r in rates.values()]
    timing_scenarios = (
        [remaining_calls * min(service), remaining_calls * max(service)] if service else None
    )
    if budget and all(str(length) in {str(k) for k in rates} for length in budget):
        estimates = sum(
            count * (rates[next(k for k in rates if str(k) == str(length))]["mean_seconds"] + 5)
            for length, count in budget.items()
        )
    return {
        "e0_planned": len(e0),
        "m3_planned": len(m3),
        "m3_finished": sum(r["calls"] for r in rates.values()),
        "by_context_length": rates,
        "remaining_main_service_seconds": estimates,
        "remaining_MAIN_call_budget": remaining_calls,
        "remaining_MAIN_service_scenarios_seconds": timing_scenarios,
        "scenario_warning": "Rate extrapolations; future output lengths and overhead are unknown",
        "runtime_note": "Requires frozen pending counts; excludes unmeasured overhead",
        "pending_main_by_length": budget,
    }


def execute(root: Path, pipeline: dict, log: Path, cfg: dict, sha: str) -> None:
    validate_pipeline(root, cfg, pipeline)
    e0 = load_jobs(pipeline["e0_stimuli"], cfg, sha)
    if len(e0) != 1968 or any(j["experiment"] != "E0" for j in e0):
        raise Halt("E0 roster must have 1968 registered calls")
    tasks = load_dataset(ROOT / pipeline["dataset"], cfg["benchmark"]["dataset_sha256"])
    client = Client()
    tags = decode_response(client.exchange("/api/tags"))["models"]
    version = decode_response(client.exchange("/api/version"))
    append_json(
        root / "supervisor.jsonl",
        {"event": "runtime_preflight", "ollama": version, "models": tags, "time": time.time()},
    )
    for model in cfg["models"]:
        if not any(
            m["name"] == model["tag"] and m["digest"] == model["expected_digest"] for m in tags
        ):
            raise Halt("Model digest mismatch")
    for phase, jobs in [("E0", e0)]:
        folder = root / phase
        folder.mkdir(parents=True, exist_ok=True)
        evaluate(folder, tasks, cfg)
        while len(by_key(folder / "calls.jsonl")) < len(jobs):
            sensor = Sensor(log, folder, LogFormat(encoding="cp1252"))
            generate_batch(folder, jobs, client, sensor, 5)
            evaluate(folder, tasks, cfg)
    analyse(root / "E0", root / "analysis", heldout_policy=pipeline["heldout_policy"])
    labels = json.loads((root / "analysis" / "heldout-labels.json").read_text())
    m3 = load_jobs(pipeline["m3_stimuli"], cfg, sha)
    orders = json.loads((ROOT / cfg["scope"]["task_orders"]).read_text())["sweeps"]["M3"][
        "task_order"
    ]
    eligible_jobs = []
    for model in cfg["models"]:
        selected = [tid for tid in orders if labels[model["tag"]].get(tid, {}).get("solvable")][:20]
        subset = [j for j in m3 if j["model"] == model["tag"] and j["task_id"] in selected]
        eligible_jobs.extend(subset)
        actual = {j["task_id"] for j in subset}
        if actual != set(selected) or len(selected) != 20:
            raise Halt("M3 roster must equal first 20 independently eligible frozen IDs")
    keep = {j["key"] for j in eligible_jobs}
    m3 = [j for j in m3 if j["key"] in keep]
    if len(m3) != 240:
        raise Halt("Focused M3 must have 240 calls")
    if any(j["experiment"] != "M3" or "context_length" not in j["identity"] for j in m3):
        raise Halt("M3 stimulus requires experiment and context_length identity")
    folder = root / "M3"
    folder.mkdir(parents=True, exist_ok=True)
    completed = len(by_key(folder / "calls.jsonl"))
    if completed < 100:
        sensor = Sensor(log, folder, LogFormat(encoding="cp1252"))
        generate_batch(folder, m3, client, sensor, 5, limit=100 - completed)
    evaluate(folder, tasks, cfg)
    write_checkpoint(
        root,
        "STOP: first 100 M3 calls complete; owner review required",
        timing_checkpoint(root, e0, m3, pipeline),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run", "recover", "monitor"])
    parser.add_argument("--pipeline", type=Path, default=ROOT / "studies/utilisation/pipeline.json")
    parser.add_argument("--root", type=Path, default=ROOT / "results/utilisation/supervised")
    parser.add_argument(
        "--hwinfo-log",
        type=Path,
        default=Path("C:/Users/Dhruv Brahmbhatt/Downloads/New folder/ver1_hwf.CSV"),
    )
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    root = args.root
    root.mkdir(parents=True, exist_ok=True)
    if args.action == "monitor":
        for phase in ["E0", "M3"]:
            rows = list(by_key(root / phase / "calls.jsonl").values())
            print(
                json.dumps(
                    {
                        "phase": phase,
                        "completed": len(rows),
                        "invalid": sum(not r["input_valid"] for r in rows),
                        "output_caps": sum("output_cap" in r["flags"] for r in rows),
                    }
                )
            )
        if (root / "CHECKPOINT.md").exists():
            print((root / "CHECKPOINT.md").read_text())
        return
    if args.action in {"run", "recover"} and not args.child:
        # Parent stays in the user's terminal and restarts unexpected worker exits.
        command = [
            sys.executable,
            "-u",
            "-m",
            "experiments.supervise",
            args.action,
            "--pipeline",
            str(args.pipeline),
            "--root",
            str(root),
            "--hwinfo-log",
            str(args.hwinfo_log),
            "--child",
        ]
        for restart in range(6):
            with (root / "terminal.log").open("a", encoding="utf-8") as log:
                process = subprocess.Popen(
                    command,
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                for line in process.stdout:
                    print(line, end="", flush=True)
                    log.write(line)
                    log.flush()
                code = process.wait()
            if code in {0, 2}:
                raise SystemExit(code)
            append_json(
                root / "supervisor.jsonl",
                {"event": "worker_restart", "restart": restart, "exit": code},
            )
            if restart < 5:
                time.sleep(min(60, 5 * (restart + 1)))
                # Pass recover to the new child; hard stops already exit with 2.
                command[4] = "recover"
        write_checkpoint(root, "Worker restart budget exhausted", {"restarts": 5})
        raise SystemExit(2)
    cfg, sha = load_config()
    try:
        pipeline = json.loads(args.pipeline.read_text())
        validate_pipeline(root, cfg, pipeline)
        if args.action == "prepare":
            print(
                json.dumps(
                    {
                        "e0": len(load_jobs(pipeline["e0_stimuli"], cfg, sha)),
                        "config_hash": sha,
                        "pipeline_hash": digest(pipeline),
                    }
                )
            )
            return
        if (root / "CHECKPOINT.md").exists() and args.action != "recover":
            raise Halt("Existing checkpoint requires explicit recover after review")
        # Sharing the study lock keeps all scoring and generation mutually exclusive.
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            append_json(
                root / "supervisor.jsonl",
                {"event": args.action, "pid": os.getpid(), "time": time.time()},
            )
            execute(root, pipeline, args.hwinfo_log, cfg, sha)
    except Halt as exc:
        write_checkpoint(root, str(exc), {"action": args.action})
        print(str(exc))
        raise SystemExit(2) from exc
    except Exception as exc:
        write_checkpoint(
            root,
            "Unexpected failure; recover command resumes saved state",
            {"type": type(exc).__name__, "detail": str(exc)},
        )
        raise


if __name__ == "__main__":
    main()
