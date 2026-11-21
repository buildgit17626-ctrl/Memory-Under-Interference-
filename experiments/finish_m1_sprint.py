"""Unattended approved M1 completion, scoring and verification; no new study."""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import psutil

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from prompt_energy.utilisation_journal import append_json, read_jsonl
from prompt_energy.utilisation_plan import ROOT


def phase_order(run, count) -> dict:
    """A failed or incomplete generation phase cannot silently enter scoring."""
    for phase in ("generation", "evaluation"):
        code = run(phase)
        if code != 0:
            return {"reason": "phase_stopped", "phase": phase, "exit_code": code}
        if phase == "generation" and count("calls.jsonl") != 1040:
            return {"reason": "generation_incomplete", "scoring": "deferred"}
    return {"reason": "verification_ready"}


def verification(root: Path) -> dict:
    calls, scores = read_jsonl(root / "calls.jsonl"), read_jsonl(root / "scores.jsonl")
    callkeys, scorekeys = {r["key"] for r in calls}, {r["key"] for r in scores}
    blocks = read_jsonl(root / "blocks.jsonl")
    starts = {r["block"] for r in blocks if r["event"] == "start"}
    ends = {r["block"] for r in blocks if r["event"] == "end"}
    return {
        "calls": len(calls),
        "unique_calls": len(callkeys),
        "scores": len(scores),
        "unique_scores": len(scorekeys),
        "missing_score_keys": sorted(callkeys - scorekeys),
        "foreign_score_keys": sorted(scorekeys - callkeys),
        "input_invalid": sum(not r["input_valid"] for r in calls),
        "output_caps": sum("output_cap" in r["flags"] for r in calls),
        "energy_available": sum(bool(r["energy_valid"]) for r in calls),
        "blocks_without_end": sorted(starts - ends),
        "all_expected_records_present": len(calls)
        == len(callkeys)
        == len(scores)
        == len(scorekeys)
        == 1040
        and callkeys == scorekeys
        and not starts - ends,
        "interpretation": "Verification only; retained flags require analysis",
    }


def stop_owned_tree(child) -> None:
    """Never terminate processes outside the subtree launched by this driver."""
    try:
        parent = psutil.Process(child.pid)
        descendants = parent.children(recursive=True)
    except psutil.NoSuchProcess:
        return
    for process in reversed(descendants):
        try:
            process.kill()
        except psutil.NoSuchProcess:
            pass
    try:
        parent.kill()
    except psutil.NoSuchProcess:
        pass
    child.wait()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hwinfo-log", type=Path, required=True)
    args = parser.parse_args()
    root = ROOT / "results/utilisation/m1-full"
    root.mkdir(parents=True, exist_ok=True)
    wall_end, mono_end = time.time() + 7.75 * 3600, time.monotonic() + 7.75 * 3600
    commands = {
        "generation": [
            sys.executable,
            "-u",
            "-m",
            "experiments.run_full_m1",
            "recover",
            "--hwinfo-log",
            str(args.hwinfo_log),
        ],
        "evaluation": [
            sys.executable,
            "-u",
            "-m",
            "experiments.utilisation",
            "score",
            "--session",
            str(root),
            "--dataset",
            str(ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz"),
        ],
    }

    def run(phase):
        remaining = min(wall_end - time.time(), mono_end - time.monotonic())
        if remaining <= 60:
            return 124
        append_json(
            root / "sprint-events.jsonl",
            {"event": "start", "phase": phase, "time": time.time(), "wall_end": wall_end},
        )
        with (root / "sprint-phases.log").open("a", encoding="utf-8") as stream:
            child = subprocess.Popen(
                commands[phase], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT
            )
            while child.poll() is None:
                if min(wall_end - time.time(), mono_end - time.monotonic()) <= 60:
                    stop_owned_tree(child)
                    return 124
                time.sleep(2)
        append_json(
            root / "sprint-events.jsonl",
            {"event": "end", "phase": phase, "time": time.time(), "exit_code": child.returncode},
        )
        return child.returncode

    result = phase_order(run, lambda name: len(read_jsonl(root / name)))
    if result["reason"] == "verification_ready":
        audit = verification(root)
        result = {
            "reason": "finished"
            if audit["all_expected_records_present"]
            else "verification_failed",
            **audit,
        }
    (root / "SPRINT_STATUS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    append_json(root / "sprint-events.jsonl", {"event": "stop", **result})
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
