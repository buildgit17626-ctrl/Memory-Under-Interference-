"""Reproduce completion/quality counts without interpreting treatment effects."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.run_m1_r1_chain import verify
from prompt_energy.utilisation_journal import read_jsonl
from prompt_energy.utilisation_plan import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix-bytes", type=int)
    parser.add_argument("--prefix-sha256")
    args = parser.parse_args()
    registration = verify()
    report = {}
    for phase in ("pilot", "full"):
        root = ROOT / "results/utilisation/r1-v2" / phase
        calls, scores = read_jsonl(root / "calls.jsonl"), read_jsonl(root / "scores.jsonl")
        expected = {j["key"] for j in registration[phase][1]}
        callkeys, scorekeys = {r["key"] for r in calls}, {r["key"] for r in scores}
        blocks = read_jsonl(root / "blocks.jsonl")
        starts = {r["block"] for r in blocks if r["event"] == "start"}
        ends = {r["block"] for r in blocks if r["event"] == "end"}
        drifted = {
            r["block"]
            for r in blocks
            if r["event"] == "end" and "baseline_drift" in r.get("flags", [])
        }
        groups = Counter((r["model"], r["condition"]) for r in calls)
        complete = (
            len(calls) == len(callkeys) == len(expected) == len(scores) == len(scorekeys)
            and callkeys == scorekeys == expected
            and not starts - ends
        )
        report[phase] = {
            "expected": len(expected),
            "calls": len(calls),
            "unique_calls": len(callkeys),
            "scores": len(scores),
            "unique_scores": len(scorekeys),
            "score_status_counts": dict(Counter(r["status"] for r in scores)),
            "partition_status_counts": dict(
                Counter(
                    partition["status"]
                    for r in scores
                    for task in r["functions"].values()
                    for partition in task.values()
                )
            ),
            "complete": complete,
            "missing_calls": sorted(expected - callkeys),
            "missing_scores": sorted(expected - scorekeys),
            "input_invalid": sum(not r["input_valid"] for r in calls),
            "api_failures": sum(bool(r.get("call_failed")) for r in calls),
            "output_caps": sum("output_cap" in r["flags"] for r in calls),
            "energy_available": sum(bool(r["energy_valid"]) for r in calls),
            "energy_flags": dict(Counter(f for r in calls for f in r["energy"].get("flags", []))),
            "drifted_blocks": len(drifted),
            "calls_in_drifted_blocks": sum(r["block"] in drifted for r in calls),
            "end_flags": dict(
                Counter(f for r in blocks if r["event"] == "end" for f in r.get("flags", []))
            ),
            "blocks_without_end": sorted(starts - ends),
            "group_counts": [
                {"model": m, "policy": p, "calls": n} for (m, p), n in sorted(groups.items())
            ],
            "call_sha256": hashlib.sha256((root / "calls.jsonl").read_bytes()).hexdigest(),
        }
    if args.prefix_bytes is not None:
        raw = (ROOT / "results/utilisation/r1-v2/full/calls.jsonl").read_bytes()
        report["pre_resume_prefix_preserved"] = (
            hashlib.sha256(raw[: args.prefix_bytes]).hexdigest() == args.prefix_sha256
        )
    destination = ROOT / "results/utilisation/r1-v2/completion-audit.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not all(report[p]["complete"] for p in ("pilot", "full")):
        raise SystemExit(2)
    if report.get("pre_resume_prefix_preserved") is False:
        raise SystemExit("Pre-resume raw prefix changed")


if __name__ == "__main__":
    main()
