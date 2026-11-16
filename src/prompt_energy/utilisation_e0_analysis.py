"""Task-paired E0 analysis with explicit denominators and held-out labels."""

import json
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

from prompt_energy.utilisation_run import by_key


def exact_swap_p(differences: list[int]) -> float:
    distribution = Counter({0: 1})
    for difference in differences:
        distribution = Counter({k: v for k, v in distribution.items()})
        following = Counter()
        for total, ways in distribution.items():
            following[total + difference] += ways
            following[total - difference] += ways
        distribution = following
    threshold = abs(sum(differences))
    return sum(v for k, v in distribution.items() if abs(k) >= threshold) / 2 ** len(differences)


def reference_sensitivity(paired: list[dict]) -> dict:
    """Describe the approved exclusion without altering primary outcomes."""
    retained = [p for p in paired if p["task_id"] != "HumanEval/32"]
    result = {
        "excluded_task_id": "HumanEval/32",
        "retained_paired_tasks": len(retained),
        "excluded_from_paired": len(paired) - len(retained),
        "mean_pass_difference": None,
        "ci95": None,
    }
    if retained:
        values = np.array([p["pass_count_difference"] / 3 for p in retained])
        rng = np.random.default_rng(1732)
        draws = values[rng.integers(0, len(values), size=(2000, len(values)))].mean(axis=1)
        result.update(
            mean_pass_difference=float(values.mean()),
            ci95=np.quantile(draws, [0.025, 0.975]).tolist(),
        )
    return result


def analyse(root: Path, output: Path, *, heldout_policy: dict) -> dict:
    calls = by_key(root / "calls.jsonl")
    scores = by_key(root / "scores.jsonl")
    model_results = {}
    labels = {}
    for model in sorted({r["model"] for r in calls.values()}):
        rows = [r for r in calls.values() if r["model"] == model]
        cells = {}
        for row in rows:
            identity = (row["task_id"], row["condition"], row["sample_idx"])
            if identity in cells:
                raise ValueError("Duplicate E0 task-arm-sample")
            score = scores.get(row["key"])
            if score and score["status"] not in {"invalid_input", "infrastructure_error"}:
                parts = [
                    p for result in score.get("functions", {}).values() for p in result.values()
                ]
                if any(p["status"] == "infrastructure_error" for p in parts):
                    continue
                cells[identity] = (score["status"] == "passed", row)
        paired = []
        groups = {label: [] for label in ["both_pass", "P1_only", "P3_1_only", "both_fail"]}
        task_ids = [f"HumanEval/{i}" for i in range(164)]
        for tid in task_ids:
            if not all((tid, arm, s) in cells for arm in ("P1", "P3_1") for s in range(3)):
                continue
            flags = {arm: [cells[tid, arm, s][0] for s in range(3)] for arm in ("P1", "P3_1")}
            a, b = any(flags["P1"]), any(flags["P3_1"])
            name = "both_pass" if a and b else "P1_only" if a else "P3_1_only" if b else "both_fail"
            groups[name].append(tid)

            def delta(field, cells=cells, tid=tid):
                vals = {
                    arm: [cells[tid, arm, s][1].get(field) for s in range(3)]
                    for arm in ("P1", "P3_1")
                }
                return (
                    np.mean(vals["P3_1"]) - np.mean(vals["P1"])
                    if all(v is not None for vs in vals.values() for v in vs)
                    else None
                )

            energies = {}
            for arm in ("P1", "P3_1"):
                energies[arm] = [
                    cells[tid, arm, s][1]["energy"]["windows"]
                    .get("post_load", {})
                    .get("adjusted_wh")
                    for s in range(3)
                ]
            energy_delta = (
                float(np.mean(energies["P3_1"]) - np.mean(energies["P1"]))
                if all(v is not None for vs in energies.values() for v in vs)
                else None
            )
            paired.append(
                {
                    "task_id": tid,
                    "passes": flags,
                    "pass_count_difference": sum(flags["P3_1"]) - sum(flags["P1"]),
                    "output_tokens_difference": float(delta("output_tokens"))
                    if delta("output_tokens") is not None
                    else None,
                    "net_energy_difference_wh": energy_delta,
                }
            )
        if not paired:
            raise ValueError(f"No complete paired E0 tasks for {model}")
        d = np.array([p["pass_count_difference"] / 3 for p in paired])
        rng = np.random.default_rng(1732)
        boots = np.mean(d[rng.integers(0, len(d), size=(2000, len(d)))], axis=1)
        discordant = len(groups["P1_only"]) + len(groups["P3_1_only"])
        model_results[model] = {
            "scheduled": 984,
            "finished_calls": len(rows),
            "scored_cells": len(cells),
            "complete_paired_tasks": len(paired),
            "missing_tasks": [t for t in task_ids if t not in {p["task_id"] for p in paired}],
            "table": {k: {"count": len(v), "task_ids": v} for k, v in groups.items()},
            "mean_pass_difference": float(np.mean(d)),
            "ci95": np.quantile(boots, [0.025, 0.975]).tolist(),
            "exact_triplet_swap_p": exact_swap_p([p["pass_count_difference"] for p in paired]),
            "any_of_three_exact_mcnemar_p": float(
                binomtest(len(groups["P3_1_only"]), discordant).pvalue
            )
            if discordant
            else 1.0,
            "energy_complete_task_pairs": sum(
                p["net_energy_difference_wh"] is not None for p in paired
            ),
            "task_differences": paired,
        }
        for field in ("output_tokens_difference", "net_energy_difference_wh"):
            valid = np.array([p[field] for p in paired if p[field] is not None], dtype=float)
            if len(valid):
                rng = np.random.default_rng(1732)
                draws = valid[rng.integers(0, len(valid), size=(2000, len(valid)))].mean(axis=1)
                model_results[model][field] = {
                    "n_tasks": len(valid),
                    "mean": float(valid.mean()),
                    "ci95": np.quantile(draws, [0.025, 0.975]).tolist(),
                }
            else:
                model_results[model][field] = {"n_tasks": 0, "mean": None, "ci95": None}
        model_results[model]["reference_sensitivity"] = reference_sensitivity(paired)
        labels[model] = {}
        if heldout_policy.get("name") == "approved_E0_P1_sample0_holdout":
            for tid in task_ids:
                calibration = cells.get((tid, "P1", 0))
                outcomes = [cells.get((tid, "P1", s)) for s in (1, 2)]
                if calibration and all(outcomes):
                    labels[model][tid] = {
                        "solvable": bool(calibration[0]),
                        "difficulty_estimate_pass_fraction": float(calibration[0]),
                        "difficulty_sample_ids": [0],
                        "outcome_sample_ids": [1, 2],
                        "outcome_pass_fraction": sum(x[0] for x in outcomes) / 2,
                    }
        else:
            raise ValueError("Independent held-out policy not approved/implemented")
    ordered = sorted(model_results, key=lambda m: model_results[m]["exact_triplet_swap_p"])
    running = 0.0
    for rank, model in enumerate(ordered):
        running = max(running, (len(ordered) - rank) * model_results[model]["exact_triplet_swap_p"])
        model_results[model]["holm_p"] = min(1.0, running)
    result = {"models": model_results, "heldout_policy": heldout_policy}
    output.mkdir(parents=True, exist_ok=True)
    (output / "e0-analysis.json").write_text(json.dumps(result, indent=2))
    (output / "heldout-labels.json").write_text(json.dumps(labels, indent=2))
    print(
        json.dumps(
            {
                m: {k: v for k, v in r.items() if k != "task_differences"}
                for m, r in model_results.items()
            },
            indent=2,
        )
    )
    return result
