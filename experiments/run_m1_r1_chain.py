"""One approved availability window: finish M1, pilot/gate R1, optionally full R1."""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.finish_m1_sprint import stop_owned_tree
from experiments.prepare_r1_v2 import BASE, configuration
from experiments.supervise_v2 import verify_v2_artifacts
from prompt_energy.ollama import Client, decode_response, utc_now
from prompt_energy.records import directory_lock
from prompt_energy.timed_queue import timed_queue
from prompt_energy.utilisation_eval import load_dataset
from prompt_energy.utilisation_freeze import verify_registration
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import ROOT, digest, schedule
from prompt_energy.utilisation_run import by_key
from prompt_energy.utilisation_supervisor import FREEZE


def pilot_gate(calls: list, expected: int, seconds: float, remaining: float) -> dict:
    covered = sum(bool(r.get("energy_valid")) for r in calls)
    bad = sum(
        not r.get("input_valid")
        or r.get("call_failed", False)
        or "output_cap" in r.get("flags", [])
        for r in calls
    )
    projected = (seconds / expected) * 400 if len(calls) == expected else None
    passed = (
        len(calls) == expected
        and bad == 0
        and covered == expected
        and projected is not None
        and projected + 1500 < remaining
    )
    return {
        "pass": passed,
        "calls": len(calls),
        "expected": expected,
        "invalid_or_capped": bad,
        "energy_available": covered,
        "observed_pilot_seconds": seconds,
        "projected_full_seconds": projected,
        "remaining_seconds": remaining,
        "reserve_seconds": 1500,
        "uses_correctness": False,
    }


def verify():
    verify_v2_artifacts()
    name = "studies/utilisation/r1-v2/execution.sha256"
    committed = subprocess.check_output(["git", "show", "HEAD:" + name], cwd=ROOT)
    if (ROOT / name).read_bytes().replace(b"\r\n", b"\n") != committed:
        raise ValueError("Chain manifest changed")
    for line in committed.decode().splitlines():
        sha, path = line.split("  ", 1)
        if hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest() != sha:
            raise ValueError("Chain input changed: " + path)
    ref = json.loads((ROOT / "results/utilisation/r1-v2-validation/report.json").read_text())
    if ref["checks"] != 40 or ref["passed"] != 40:
        raise ValueError("R1 references not valid")
    result = {}
    for phase in ["pilot", "full"]:
        cfg, sha = configuration(phase)
        path = BASE / phase / "stimuli.json"
        items = json.loads(path.read_text())
        jobs = schedule(items, cfg, sha)
        verify_registration(jobs, path, cfg)
        if digest(items) != ref[phase + "_stimuli"]:
            raise ValueError("R1 validation material mismatch")
        result[phase] = (cfg, jobs)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "recover"])
    parser.add_argument("--hwinfo-log", type=Path)
    args = parser.parse_args()
    materials = verify()
    if args.action == "check":
        print(
            "Verified chain: M1 finish/evaluate/verify -> R1 pilot50 -> automa"
            "tic gate -> R1 full400 if time fits. No requests."
        )
        return
    if args.hwinfo_log is None:
        parser.error("--hwinfo-log required")
    root = ROOT / "results/utilisation/m1-r1-chain"
    root.mkdir(parents=True, exist_ok=True)
    wall_end = min(time.time() + 7.75 * 3600, datetime.fromisoformat(FREEZE).timestamp())
    mono_end = time.monotonic() + max(0, wall_end - time.time())

    def remaining():
        return min(wall_end - time.time(), mono_end - time.monotonic())

    def child(command, label):
        with (root / (label + ".log")).open("a", encoding="utf-8") as stream:
            process = subprocess.Popen(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
            while process.poll() is None:
                if remaining() < 60:
                    stop_owned_tree(process)
                    raise RuntimeError("Overall sprint deadline")
                time.sleep(2)
        if process.returncode:
            raise RuntimeError(label + " stopped with exit " + str(process.returncode))

    try:
        append_json(
            root / "events.jsonl",
            {
                "event": "start",
                "time": time.time(),
                "wall_end": wall_end,
                "hwinfo": str(args.hwinfo_log),
            },
        )
        child(
            [
                sys.executable,
                "-u",
                "-m",
                "experiments.finish_m1_sprint",
                "--hwinfo-log",
                str(args.hwinfo_log),
            ],
            "M1",
        )
        m1 = json.loads((ROOT / "results/utilisation/m1-full/SPRINT_STATUS.json").read_text())
        if not m1.get("all_expected_records_present"):
            raise RuntimeError("M1 verification incomplete; R1 not started")
        cfg, _ = materials["pilot"]
        load_dataset(
            ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz",
            cfg["benchmark"]["dataset_sha256"],
        )
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            client = Client()
            version = decode_response(client.exchange("/api/version"))["version"]
            tags = decode_response(client.exchange("/api/tags"))["models"]
            for model in cfg["models"]:
                if not any(
                    t["name"] == model["tag"] and t["digest"] == model["expected_digest"]
                    for t in tags
                ):
                    raise ValueError("Model digest mismatch")
            for phase in ["pilot", "full"]:
                cfg, jobs = materials[phase]
                folder = ROOT / "results/utilisation/r1-v2" / phase
                folder.mkdir(parents=True, exist_ok=True)
                if remaining() <= 1560:
                    raise RuntimeError("Not enough reserved time for R1 requests")
                append_json(
                    folder / "sessions.jsonl",
                    {
                        "started_at": utc_now(),
                        "ollama_version": version,
                        "schedule_hash": digest(jobs),
                        "wall_end": wall_end,
                        "phase": phase,
                    },
                )
                status = timed_queue(
                    folder, jobs, client, args.hwinfo_log, hours=min(7.5, (remaining() - 60) / 3600)
                )
                if status["remaining"]:
                    raise RuntimeError("R1 " + phase + " incomplete; resumable checkpoint saved")
                # Separate child evaluator bounds scoring time and obtains its own lock.
                if phase == "pilot":
                    break
        pilot_root = ROOT / "results/utilisation/r1-v2/pilot"
        child(
            [
                sys.executable,
                "-u",
                "-m",
                "experiments.utilisation",
                "score",
                "--session",
                str(pilot_root),
                "--dataset",
                str(ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz"),
            ],
            "R1-pilot-evaluation",
        )
        from prompt_energy.utilisation_journal import read_jsonl

        sessions = read_jsonl(pilot_root / "sessions.jsonl")
        first = datetime.fromisoformat(sessions[0]["started_at"]).timestamp()
        duration = (pilot_root / "scores.jsonl").stat().st_mtime - first
        pilot_scores = by_key(pilot_root / "scores.jsonl")
        if len(pilot_scores) != 50:
            raise RuntimeError("R1 pilot scoring incomplete")
        if any(
            part["status"] == "infrastructure_error"
            for score in pilot_scores.values()
            for task in score.get("functions", {}).values()
            for part in task.values()
        ):
            raise RuntimeError("R1 pilot evaluator infrastructure failure")
        gate = pilot_gate(
            list(by_key(pilot_root / "calls.jsonl").values()), 50, duration, remaining()
        )
        (root / "R1_GATE.json").write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
        if not gate["pass"]:
            raise RuntimeError(
                "R1 automatic validity/time gate did not pass; full stage not started"
            )
        cfg, jobs = materials["full"]
        folder = ROOT / "results/utilisation/r1-v2/full"
        folder.mkdir(parents=True, exist_ok=True)
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            append_json(
                folder / "sessions.jsonl",
                {
                    "started_at": utc_now(),
                    "ollama_version": version,
                    "schedule_hash": digest(jobs),
                    "wall_end": wall_end,
                    "phase": "full",
                },
            )
            status = timed_queue(
                folder, jobs, client, args.hwinfo_log, hours=min(7.5, (remaining() - 60) / 3600)
            )
        if status["remaining"]:
            raise RuntimeError("R1 full timed checkpoint; remaining calls saved for resume")
        child(
            [
                sys.executable,
                "-u",
                "-m",
                "experiments.utilisation",
                "score",
                "--session",
                str(folder),
                "--dataset",
                str(ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz"),
            ],
            "R1-full-evaluation",
        )
        if len(by_key(folder / "scores.jsonl")) != 400:
            raise RuntimeError("R1 full scoring incomplete")
        result = {
            "reason": "finished",
            "M1_calls": 1040,
            "R1_pilot_calls": 50,
            "R1_full_calls": 400,
            "R1_full_scores": len(by_key(folder / "scores.jsonl")),
        }
    except (RuntimeError, ValueError, OSError) as exc:
        result = {"reason": "stopped", "detail": str(exc), "resumable": True}
    (root / "STATUS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    append_json(root / "events.jsonl", {"event": "stop", **result})
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
