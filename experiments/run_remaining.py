"""Sequential remaining-study driver: finish R2, gated M2/E4, diagnostic E3 only."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.prepare_continuation import source
from experiments.prepare_remaining import BASE, OUTPUT, configuration, jobs_for
from experiments.run_continuation import OUTPUT as OLD_OUTPUT
from experiments.run_continuation import PAUSE
from experiments.run_continuation import verify as verify_old
from experiments.utilisation_pilot import template
from prompt_energy.continuation_evaluation import evaluate_stage, validity_gate
from prompt_energy.continuation_queue import continuation_queue
from prompt_energy.full_run import check_host
from prompt_energy.hwinfo import LogFormat, preflight_log
from prompt_energy.metadata import host_metadata
from prompt_energy.ollama import Client, decode_response, utc_now
from prompt_energy.records import directory_lock
from prompt_energy.remaining_cache import CacheClient
from prompt_energy.remaining_cache import gate as cache_gate
from prompt_energy.remaining_cache_worker import cache_batch
from prompt_energy.remaining_repair import run_pilot
from prompt_energy.utilisation_freeze import verify_registration
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import ROOT
from prompt_energy.utilisation_run import by_key
from prompt_energy.utilisation_supervisor import Halt, write_checkpoint

STAGES = (("M2", "pilot"), ("M2", "full"), ("E4", "pilot"), ("E4", "full"), ("E3", "pilot"))


def verify() -> dict:
    verify_old()
    path = BASE / "execution.sha256"
    blob = subprocess.check_output(
        ["git", "show", "HEAD:" + path.relative_to(ROOT).as_posix()], cwd=ROOT
    )
    if path.read_bytes().replace(b"\r\n", b"\n") != blob:
        raise ValueError("Remaining queue manifest uncommitted or changed")
    for line in blob.decode().splitlines():
        expected, name = line.split("  ", 1)
        current = (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(current).hexdigest() != expected:
            raise ValueError("Frozen remaining artifact changed: " + name)
    validation = json.loads((BASE / "feedback-validation.json").read_text())
    if len(validation) != 10 or any(r["status"] != "passed" for r in validation):
        raise ValueError("Feedback validation incomplete")
    prepared = {}
    for stage, phase in STAGES:
        cfg, checksum = configuration(stage, phase)
        jobs = jobs_for(stage, phase, cfg, checksum)
        prepared[(stage, phase)] = (
            cfg,
            jobs,
            verify_registration(jobs, BASE / stage / phase / "stimuli.json", cfg),
        )
    return prepared


def sequential_steps(finish_r2, m2_pilot, m2_full, e4_pilot, e4_full, e3_pilot) -> None:
    """A failed gate or deliberate stop prevents every later step."""
    finish_r2()
    m2_pilot()
    m2_full()
    e4_pilot()
    e4_full()
    e3_pilot()


def snapshot() -> dict:
    records = {}
    for stage, phase in STAGES:
        folder = OUTPUT / stage / phase
        folders = (
            [folder]
            if stage != "E3"
            else [folder / "initial", *[folder / f"round-{i}" for i in (1, 2, 3)]]
        )
        calls = [r for f in folders for r in by_key(f / "calls.jsonl").values()]
        records[f"{stage}/{phase}"] = {
            "calls": len(calls),
            "scores": sum(len(by_key(f / "scores.jsonl")) for f in folders),
            "input_invalid": sum(not r["input_valid"] for r in calls),
            "api_failed": sum(r.get("call_failed", False) for r in calls),
            "energy_available": sum(r["energy_valid"] for r in calls),
            "output_caps": sum("output_cap" in r["flags"] for r in calls),
            "mean_measured_wall_seconds": sum(r["wall_seconds"] for r in calls) / len(calls)
            if calls
            else None,
            "setup_HTTP_requests": len(by_key(folder / "controls.jsonl")),
        }
    records["R2/full"] = {
        "calls": len(by_key(OLD_OUTPUT / "R2/full/calls.jsonl")),
        "planned": 1040,
        "scores": len(by_key(OLD_OUTPUT / "R2/full/scores.jsonl")),
    }
    return records


def recover(log: Path, prepared: dict) -> None:
    _, tasks, tokenizer = source()
    client = Client()
    state = {
        "reason": "running",
        "started_at": utc_now(),
        "sensor": str(log),
        "elapsed_time_cutoff": None,
    }

    def status(**update):
        state.update(update)
        (OUTPUT / "STATUS.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    def old():
        status(stage="R2", phase="full", operation="frozen_continuation")
        subprocess.run(
            [
                sys.executable,
                "-u",
                "-m",
                "experiments.run_continuation",
                "recover",
                "--hwinfo-log",
                str(log),
            ],
            cwd=ROOT,
            check=True,
        )
        old_status = json.loads((OLD_OUTPUT / "STATUS.json").read_text())
        if old_status.get("reason") != "finished":
            raise Halt("Existing R2 continuation stopped", old_status)

    def stage(stage_name: str, phase: str):
        if PAUSE.exists():
            raise Halt("User pause")
        cfg, jobs, registration = prepared[(stage_name, phase)]
        folder = OUTPUT / stage_name / phase
        folder.mkdir(parents=True, exist_ok=True)
        status(stage=stage_name, phase=phase, operation="generation")
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            append_json(
                folder / "sessions.jsonl",
                {
                    "time": utc_now(),
                    "registration": registration,
                    "sensor": str(log),
                    "version": decode_response(client.exchange("/api/version")),
                },
            )
            actual = decode_response(client.exchange("/api/tags"))["models"]
            for m in cfg["models"]:
                if not any(
                    x["name"] == m["tag"] and x["digest"] == m["expected_digest"] for x in actual
                ):
                    raise Halt("Model digest mismatch")
            if stage_name == "E3":
                run_pilot(
                    folder,
                    jobs,
                    cfg,
                    tasks,
                    json.loads((BASE / "E3/feedback-examples.json").read_text()),
                    json.loads((BASE / "E3/heldout-tasks.json").read_text()),
                    client,
                    log,
                    PAUSE,
                    tokenizer,
                    template,
                )
                return
            proxy = CacheClient(client, folder, [m["tag"] for m in cfg["models"]], PAUSE)
            result = continuation_queue(
                folder,
                jobs,
                proxy if stage_name == "E4" else client,
                log,
                PAUSE,
                **({"generator": cache_batch} if stage_name == "E4" else {}),
            )
            if result["remaining"]:
                raise Halt("User pause", result)
            if stage_name == "M2":
                status(operation="offline_scoring")
                if not evaluate_stage(folder, tasks, cfg, PAUSE, {}):
                    raise Halt("User pause")
                scores = list(by_key(folder / "scores.jsonl").values())
                infrastructure = [
                    p
                    for s in scores
                    for t in s["functions"].values()
                    for p in t.values()
                    if p["status"] == "infrastructure_error"
                ]
                if infrastructure:
                    raise Halt("M2 evaluator infrastructure failure")
            calls = list(by_key(folder / "calls.jsonl").values())
            if phase == "pilot":
                gate = (
                    cache_gate(calls, len(jobs))
                    if stage_name == "E4"
                    else validity_gate(calls, scores, len(jobs))
                )
                (folder / "GATE.json").write_text(
                    json.dumps(gate, indent=2) + "\n", encoding="utf-8"
                )
                if not gate["pass"]:
                    raise Halt(stage_name + " pilot validity gate failed", gate)
            print(
                json.dumps({"completed_stage": stage_name, "phase": phase, "calls": len(calls)}),
                flush=True,
            )

    status()
    try:
        sequential_steps(
            old,
            lambda: stage("M2", "pilot"),
            lambda: stage("M2", "full"),
            lambda: stage("E4", "pilot"),
            lambda: stage("E4", "full"),
            lambda: stage("E3", "pilot"),
        )
    except (Halt, ValueError, OSError, subprocess.CalledProcessError) as exc:
        status(reason="stopped", stop_reason=str(exc))
        write_checkpoint(
            OUTPUT,
            str(exc),
            {"state": state, "inventory": snapshot(), "details": getattr(exc, "details", {})},
        )
        print("STOP: " + str(exc), flush=True)
        return
    status(reason="finished", operation="owner_review_E3_pilot")
    write_checkpoint(OUTPUT, "Approved queue complete; full E3 remains unauthorized", snapshot())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "recover", "monitor", "pause"])
    parser.add_argument("--hwinfo-log", type=Path)
    parser.add_argument(
        "--resume", action="store_true", help="Owner explicitly clears the saved pause"
    )
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.action == "pause":
        PAUSE.write_text(utc_now() + "\n", encoding="utf-8")
        print("Pause requested; finish active request/test and closing baseline.")
        return
    if args.action == "monitor":
        print(json.dumps(snapshot(), indent=2))
        if (OUTPUT / "STATUS.json").exists():
            print((OUTPUT / "STATUS.json").read_text())
        print(json.dumps({"pause_active": PAUSE.exists()}))
        return
    prepared = verify()
    if args.action == "check":
        print(
            json.dumps(
                {
                    "verified": True,
                    "initial_schedules": {f"{s}/{p}": len(v[1]) for (s, p), v in prepared.items()},
                    "E3_maximum_total": 130,
                    "new_maximum_measured_calls": 1000,
                    "setup_and_priming_additional": True,
                }
            )
        )
        return
    if args.hwinfo_log is None:
        parser.error("--hwinfo-log is required")
    check_host(host_metadata())
    preflight_log(args.hwinfo_log, LogFormat(encoding="cp1252"))
    if PAUSE.exists():
        if not args.resume:
            raise Halt("Saved pause; owner must pass --resume to launch")
        PAUSE.unlink()
        append_json(
            OUTPUT / "owner-actions.jsonl", {"action": "explicit_resume", "time": utc_now()}
        )
    recover(args.hwinfo_log, prepared)


if __name__ == "__main__":
    main()
