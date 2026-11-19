"""Offline audit and draft matrices. This entry point cannot generate model calls."""

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.config import MODELS, TASK_IDS
from prompt_energy.memory_revision import condition_matrix
from prompt_energy.utilisation_journal import read_jsonl
from prompt_energy.utilisation_plan import ROOT


def audit(root: Path) -> dict:
    """Print complete denominators; never infer a match from temperature alone."""
    report = {}
    for phase in ("E0", "M3-isolated", "M3"):
        folder = root / phase
        calls = read_jsonl(folder / "calls.jsonl")
        scores = read_jsonl(folder / "scores.jsonl")
        report[phase] = {
            "calls": len(calls),
            "unique_keys": len({r["key"] for r in calls}),
            "scores": len(scores),
            "unique_score_keys": len({r["key"] for r in scores}),
            "missing_score_keys": sorted({r["key"] for r in calls} - {r["key"] for r in scores}),
            "input_invalid": sum(not r.get("input_valid", False) for r in calls),
            "output_caps": sum("output_cap" in r.get("flags", []) for r in calls),
            "energy_available": sum(bool(r.get("energy_valid")) for r in calls),
            "score_status_counts": dict(Counter(r["status"] for r in scores)),
            "settings": [
                json.loads(s)
                for s in sorted(
                    {json.dumps(r["request"]["options"], sort_keys=True) for r in calls}
                )
            ],
            "raw_calls_sha256": hashlib.sha256((folder / "calls.jsonl").read_bytes()).hexdigest(),
        }
    e0 = read_jsonl(root / "E0/calls.jsonl")
    expected = {
        (tid, model, arm, sample)
        for tid in (f"HumanEval/{i}" for i in range(164))
        for model in MODELS
        for arm in ("P1", "P3_1")
        for sample in range(3)
    }
    observed = [(r["task_id"], r["model"], r["condition"], r["sample_idx"]) for r in e0]
    report["E0_grid"] = {
        "expected_cells": len(expected),
        "observed_cells": len(observed),
        "unique_cells": len(set(observed)),
        "missing_cells": sorted(expected - set(observed)),
        "unexpected_cells": sorted(set(observed) - expected),
    }
    report["reuse_rule"] = (
        "Reuse only exact task/full request/model-digest matches; no automatic T0 equivalence."
    )
    report["skip_generation"] = ["E0", "legacy_M3_240"]
    return report


def draft(root: Path, pilot_n: int) -> dict:
    """Owner-approved roster; pilot factors remain explicitly proposed."""
    if not 1 <= pilot_n <= len(TASK_IDS):
        raise ValueError("Pilot size outside the approved 40-task roster")
    matrices = {
        exp: condition_matrix(exp, list(TASK_IDS), list(MODELS)) for exp in ("M1", "M3R2_v2", "R1")
    }
    # M1 was previously deferred, so it has no committed sweep permutation.
    # Apply the already documented per-experiment seed rule without outcomes.
    seed = int.from_bytes(hashlib.sha256(b"1729/M1").digest()[:8], "big")
    order = [f"HumanEval/{i}" for i in range(164)]
    random.Random(seed).shuffle(order)
    selected = [t for t in order if t in TASK_IDS][:pilot_n]
    matrices["M1_pilot_proposal"] = condition_matrix("M1", selected, list(MODELS), ks=(2, 4))
    root.mkdir(parents=True, exist_ok=True)
    for name, matrix in matrices.items():
        (root / f"{name}-matrix-DRAFT.json").write_text(
            json.dumps(matrix, indent=2) + "\n", encoding="utf-8"
        )
    return {
        "status": "DRAFT_NOT_AUTHORISED_FOR_GENERATION",
        "approved_roster": list(TASK_IDS),
        "matrix_calls": {k: len(v) for k, v in matrices.items()},
        "M1_pilot_proposed_task_ids": selected,
        "M1_pilot_K_proposal": [2, 4],
        "M1_task_order_seed": seed,
        "M1_task_order_proposal": order,
        "M1_pilot_missing_isolation_upper_bound": pilot_n * len(MODELS),
        "legacy_M3_skipped": True,
        "blockers": [
            "exact pilot factors pending review",
            "R1 histories/summaries/preferences need review",
            "new R2 distractors need cross-pass discrimination audit",
            "pilot generation not started",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["audit", "draft"])
    parser.add_argument("--output", type=Path, default=ROOT / "results/utilisation/revision-v2")
    parser.add_argument("--pilot-tasks", type=int, default=5)
    args = parser.parse_args()
    result = (
        audit(ROOT / "results/utilisation/supervised")
        if args.action == "audit"
        else draft(args.output, args.pilot_tasks)
    )
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / f"{args.action}-report.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
