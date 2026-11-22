"""Registered E5 then semantic M3/R2, until finished, user pause or validity stop."""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.prepare_continuation import BASE, configuration
from prompt_energy.continuation_evaluation import evaluate_stage, validity_gate
from prompt_energy.continuation_queue import continuation_queue
from prompt_energy.ollama import Client, decode_response, utc_now
from prompt_energy.records import directory_lock
from prompt_energy.utilisation_eval import load_dataset
from prompt_energy.utilisation_freeze import verify_registration
from prompt_energy.utilisation_journal import append_json, read_jsonl
from prompt_energy.utilisation_plan import ROOT, digest, schedule
from prompt_energy.utilisation_run import by_key
from prompt_energy.utilisation_supervisor import Halt, write_checkpoint

OUTPUT = ROOT / "results/utilisation/continuation-v3"
PAUSE = OUTPUT / "PAUSE"


def verify() -> dict:
    manifest = BASE / "execution.sha256"
    blob = subprocess.check_output(
        ["git", "show", "HEAD:" + manifest.relative_to(ROOT).as_posix()], cwd=ROOT
    )
    if manifest.read_bytes().replace(b"\r\n", b"\n") != blob:
        raise ValueError("Continuation manifest changed")
    for line in blob.decode().splitlines():
        expected, name = line.split("  ", 1)
        if (
            hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            != expected
        ):
            raise ValueError("Frozen continuation artifact changed: " + name)
    authority = json.loads((BASE / "authority.json").read_text())
    if authority["elapsed_time_cutoff"] is not None or not authority["owner_authorized"]:
        raise ValueError("Missing explicit continuation authority")
    validation = json.loads((BASE / "validation-report.json").read_text())
    if (
        validation["target_references_passed"] != 40
        or validation["alternatives_passed"] != validation["included_tasks"]
    ):
        raise ValueError("Reference/material audit incomplete")
    result = {}
    for stage in ("E5", "R2"):
        for phase in ("pilot", "full"):
            cfg, checksum = configuration(stage, phase)
            stimuli = BASE / stage / phase / "stimuli.json"
            jobs = schedule(json.loads(stimuli.read_text()), cfg, checksum)
            registration = verify_registration(jobs, stimuli, cfg)
            result[(stage, phase)] = cfg, jobs, registration
    return result


def audit(folder: Path, jobs: list[dict]) -> dict:
    calls = by_key(folder / "calls.jsonl")
    scores = by_key(folder / "scores.jsonl")
    expected = {j["key"] for j in jobs}
    cross = by_key(folder / "cross-pass.jsonl")
    adherence = by_key(folder / "adherence.jsonl")
    cross_expected = {j["key"] for j in jobs if j["identity"].get("similarity") == "near_duplicate"}
    adherence_expected = {j["key"] for j in jobs if j["experiment"] == "E5"}
    endings = [b for b in read_jsonl(folder / "blocks.jsonl") if b["event"] == "end"]
    result = {
        "expected": len(expected),
        "calls": len(calls),
        "scores": len(scores),
        "all_expected_records_present": (
            set(calls) == set(scores) == expected
            and set(cross) == cross_expected
            and set(adherence) == adherence_expected
        ),
        "cross_pass_records": len(cross),
        "adherence_records": len(adherence),
        "input_invalid": sum(not r["input_valid"] for r in calls.values()),
        "api_failures": sum(r.get("call_failed", False) for r in calls.values()),
        "output_caps": sum("output_cap" in r["flags"] for r in calls.values()),
        "energy_available": sum(r["energy_valid"] for r in calls.values()),
        "drifted_blocks": sum("baseline_drift" in r.get("flags", []) for r in endings),
        "infrastructure_errors": sum(
            p["status"] == "infrastructure_error"
            for r in scores.values()
            for t in r["functions"].values()
            for p in t.values()
        )
        + sum(
            p["status"] == "infrastructure_error"
            for r in cross.values()
            for p in r["partitions"].values()
        ),
    }
    (folder / "AUDIT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "recover", "pause", "monitor"])
    parser.add_argument("--hwinfo-log", type=Path)
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.action == "pause":
        PAUSE.write_text(utc_now() + "\n", encoding="utf-8")
        print(
            "Pause requested: finish active request/test and close baseline; no automatic resume."
        )
        return
    if args.action == "monitor":
        for stage in ("E5", "R2"):
            for phase in ("pilot", "full"):
                folder = OUTPUT / stage / phase
                cfg, checksum = configuration(stage, phase)
                jobs = schedule(
                    json.loads((BASE / stage / phase / "stimuli.json").read_text()), cfg, checksum
                )
                calls = list(by_key(folder / "calls.jsonl").values())
                print(
                    json.dumps(
                        {
                            "stage": stage,
                            "phase": phase,
                            "expected": len(jobs),
                            "calls": len(calls),
                            "scores": len(by_key(folder / "scores.jsonl")),
                            "mean_wall_seconds": sum(r["wall_seconds"] for r in calls) / len(calls)
                            if calls
                            else None,
                        }
                    )
                )
        if (OUTPUT / "STATUS.json").exists():
            print((OUTPUT / "STATUS.json").read_text())
        return
    prepared = verify()
    if args.action == "check":
        print(
            json.dumps(
                {
                    "verified": True,
                    "calls": {f"{s}/{p}": len(v[1]) for (s, p), v in prepared.items()},
                    "elapsed_time_cutoff": None,
                }
            )
        )
        return
    if args.hwinfo_log is None:
        parser.error("--hwinfo-log required")
    cfg = prepared[("E5", "pilot")][0]
    status = {
        "reason": "running",
        "started_at": utc_now(),
        "sensor": str(args.hwinfo_log),
        "elapsed_time_cutoff": None,
    }

    def record():
        (OUTPUT / "STATUS.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    record()
    try:
        if PAUSE.exists():
            raise Halt("User pause remains active; explicit owner resume required")
        tasks = load_dataset(
            ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz",
            cfg["benchmark"]["dataset_sha256"],
        )
        alternatives = json.loads((BASE / "R2/alternatives.json").read_text())
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            client = Client()
            version = decode_response(client.exchange("/api/version"))["version"]
            actual = decode_response(client.exchange("/api/tags"))["models"]
            for model in cfg["models"]:
                if not any(
                    m["name"] == model["tag"] and m["digest"] == model["expected_digest"]
                    for m in actual
                ):
                    raise Halt("Model digest mismatch")
            for stage in ("E5", "R2"):
                for phase in ("pilot", "full"):
                    if PAUSE.exists():
                        raise Halt("User pause")
                    cfg, jobs, registration = prepared[(stage, phase)]
                    folder = OUTPUT / stage / phase
                    folder.mkdir(parents=True, exist_ok=True)
                    status.update(stage=stage, phase=phase, operation="generation")
                    record()
                    append_json(
                        folder / "sessions.jsonl",
                        {
                            "started_at": utc_now(),
                            "ollama_version": version,
                            "registration": registration,
                            "schedule_hash": digest(jobs),
                            "sensor": str(args.hwinfo_log),
                            "execution_authority": "owner_continuation_2026_11_23",
                            "elapsed_time_cutoff": None,
                        },
                    )
                    result = continuation_queue(folder, jobs, client, args.hwinfo_log, PAUSE)
                    if result["remaining"]:
                        raise Halt("User pause", result)
                    status["operation"] = "offline_evaluation"
                    record()
                    if not evaluate_stage(folder, tasks, cfg, PAUSE, alternatives):
                        raise Halt("User pause during offline scoring")
                    report = audit(folder, jobs)
                    if (
                        not report["all_expected_records_present"]
                        or report["infrastructure_errors"]
                    ):
                        raise Halt("Incomplete or infrastructure-failed evaluation", report)
                    if phase == "pilot":
                        gate = validity_gate(
                            list(by_key(folder / "calls.jsonl").values()),
                            list(by_key(folder / "scores.jsonl").values()),
                            len(jobs),
                        )
                        durations = [
                            r["wall_seconds"] for r in by_key(folder / "calls.jsonl").values()
                        ]
                        full_count = len(prepared[(stage, "full")][1])
                        gate["projected_full_request_seconds"] = (
                            sum(durations) / len(durations) * full_count
                        )
                        gate["projection_excludes"] = (
                            "idle baselines, sensor wait, gaps, scoring and retries"
                        )
                        (folder / "GATE.json").write_text(
                            json.dumps(gate, indent=2) + "\n", encoding="utf-8"
                        )
                        print(json.dumps({"stage": stage, "pilot_gate": gate}), flush=True)
                        if not gate["pass"]:
                            raise Halt("Pilot validity gate failed: " + stage, gate)
                    print(json.dumps({"stage": stage, "phase": phase, "audit": report}), flush=True)
        status.update(reason="finished", finished_at=utc_now(), operation="complete")
    except (Halt, ValueError, OSError, RuntimeError, KeyboardInterrupt) as exc:
        status.update(reason="stopped", error=str(exc) or "KeyboardInterrupt", stopped_at=utc_now())
        write_checkpoint(OUTPUT, status["error"], status)
        record()
        print(json.dumps(status), flush=True)
        raise SystemExit(2) from exc
    record()
    append_json(OUTPUT / "events.jsonl", {"event": "finished", "time": time.time(), **status})
    print(json.dumps(status), flush=True)


if __name__ == "__main__":
    main()
