"""Secondary sensitivities retain original scoring and explicit available-only populations."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.memory_audit.design import ENERGY_MODE
from analysis.memory_audit.effects import compare, complete_units, contrast_specs
from analysis.memory_audit.records import indexed, save_json
from analysis.memory_audit.statistics import holm, interval, paired_ratio, ratio


def energy_sensitivities(frame: pd.DataFrame, destination: Path) -> None:
    output = []
    for (stage, model, condition), base in frame[frame.phase.isin(["main", "partial"])].groupby(
        ["stage", "model", "condition"]
    ):
        for variant in (
            "start",
            "end",
            "midpoint",
            "exclude_drift",
            "exclude_short",
            "exclude_both",
        ):
            g = base.copy()
            if variant in {"exclude_drift", "exclude_both"}:
                g = g[~g.drifted]
            if variant in {"exclude_short", "exclude_both"}:
                g = g[~g.low_resolution]
            field = (
                "end_net_wh"
                if variant == "end"
                else "midpoint_net_wh"
                if variant == "midpoint"
                else "net_wh"
            )
            g = g.copy()
            g["unit"] = g["repeat"].astype(str) if stage.startswith("E4") else g.task
            valid = g[g[field].notna()]
            covered = valid[valid.passed.notna()]
            totals = covered.groupby("unit")[[field, "passed"]].sum()
            output.append(
                {
                    "stage": stage,
                    "model": model,
                    "condition": condition,
                    "variant": variant,
                    "analysis_label": "registered starting baseline"
                    if variant == "start"
                    else "posthoc energy sensitivity",
                    "original_attempts": len(base),
                    "retained_attempts": len(g),
                    "energy_attempts": len(valid),
                    "retained_tasks_or_repeats": valid.unit.nunique(),
                    "gross_wh_available": float(valid.gross_wh.sum()) if len(valid) else None,
                    "net_wh_available": float(valid[field].sum()) if len(valid) else None,
                    "net_total_ci95": interval(
                        valid.groupby("unit")[field].sum().to_numpy(), total=True
                    )["ci95"],
                    "negative_net_calls": int((valid[field] < 0).sum()),
                    "complete_retained_population": len(valid) == len(g),
                    "correctness_and_energy_attempts": len(covered),
                    "correct_covered": int(covered.passed.sum()),
                    "energy_per_correct_covered": ratio(
                        totals[field].to_numpy(), totals.passed.to_numpy()
                    ),
                    "tool_mode": ENERGY_MODE,
                    "selection_warning": (
                        "Removing short/drifted calls changes the energy population; "
                        "correctness primary unchanged."
                    ),
                }
            )
    save_json(destination / "energy-sensitivities.json", output)
    pd.json_normalize(output, sep=".").to_csv(destination / "energy-sensitivities.csv", index=False)


def scoring_sensitivities(frame: pd.DataFrame, functions: pd.DataFrame, destination: Path) -> None:
    scores = list(indexed(destination / "secondary-scores.jsonl").values())
    results, changes = [], []
    for operation in ("merged_complete_fences", "cap_salvage_original_extraction"):
        g = frame.copy()
        selected = [s for s in scores if s["operation"] == operation]
        for s in selected:
            mask = (g["key"] == s["call_key"]) & (g.task == s["task"])
            if mask.any():
                before = g.loc[mask, "passed"].iloc[0]
                after = float(s["passed"]) if s["passed"] is not None else np.nan
                changes.append(
                    {
                        "operation": operation,
                        "key": s["call_key"],
                        "task": s["task"],
                        "before": before,
                        "after": after,
                        "audit_score_key": s["key"],
                    }
                )
                g.loc[mask, "passed"] = after
        joined = g.copy()
        joined.loc[joined.stage == "M3_isolated", "stage"] = "M3_initial"
        for spec in contrast_specs():
            for model, group in joined[joined.stage == spec["stage"]].groupby("model"):
                if spec["outcome"] in group:
                    results.append(compare(group, spec, model, operation, include_metrics=False))
    for proxy in ("adherence_fence_tolerant", "adherence_strict_proxy"):
        for original in [s for s in contrast_specs() if s["outcome"] == "adherence"]:
            spec = original | {
                "outcome": proxy,
                "analysis_label": "posthoc mechanical adherence audit",
            }
            for model, group in frame[frame.stage == "E5"].groupby("model"):
                results.append(compare(group, spec, model, proxy, include_metrics=False))
    for variant in {r["variant"] for r in results}:
        for family in {r["family"] for r in results}:
            group = [r for r in results if r["variant"] == variant and r["family"] == family]
            for row, p in zip(group, holm([r["p_value"] for r in group]), strict=True):
                row["holm_p"] = p
    save_json(destination / "scoring-sensitivity-effects.json", results)
    save_json(destination / "scoring-changes.json", changes)
    # Count verified function occurrences, explicitly retaining repeated membership.
    rows = []
    isolation = frame[(frame.stage == "M1") & (frame.condition == "isolated")].set_index(
        ["model", "task"]
    )
    for (model, condition), group in frame[
        (frame.stage == "M1") & frame.condition.str.startswith("active/")
    ].groupby(["model", "condition"]):
        keys = set(group["key"])
        ff = functions[(functions.stage == "M1") & functions["key"].isin(keys)]
        control_energy, control_tokens, control_correct = [], [], []
        for _, call in group.iterrows():
            refs = [isolation.loc[(model, task)] for task in json.loads(call.bundle_members)]
            control_energy.extend(r.net_wh for r in refs)
            control_tokens.extend(r.output_tokens for r in refs)
            control_correct.extend(r.passed for r in refs)
        rows.append(
            {
                "model": model,
                "condition": condition,
                "requests": len(group),
                "requested_function_occurrences": len(ff),
                "correct_function_occurrences": int(ff.passed.sum()),
                "per_function_correctness": float(ff.passed.mean()),
                "whole_bundle_successes": int((group.whole_passed == 1).sum()),
                "active_output_tokens": float(group.output_tokens.sum()),
                "component_isolation_output_tokens_reused": float(np.sum(control_tokens)),
                "active_net_wh": float(group.net_wh.sum()),
                "component_isolation_net_wh_reused": float(np.sum(control_energy)),
                "component_isolation_correct_occurrences": float(np.sum(control_correct)),
                "energy_per_verified_function_occurrence": float(
                    group.net_wh.sum() / ff.passed.sum()
                )
                if ff.passed.sum()
                else None,
                "warning": (
                    "Component references reused; totals are counterfactual lookup sums, "
                    "not new physical measurements."
                ),
            }
        )
    save_json(destination / "m1-work-and-function-cost.json", rows)


def ratio_effects(frame: pd.DataFrame, destination: Path) -> None:
    data = frame.copy()
    data.loc[data.stage == "M3_isolated", "stage"] = "M3_initial"
    output = []
    for spec in contrast_specs():
        if spec["outcome"] != "passed":
            continue
        for model, g in data[data.stage == spec["stage"]].groupby("model"):
            fields = [
                (f, "primary") for f in ("gross_wh", "net_wh", "end_net_wh", "midpoint_net_wh")
            ]
            fields += [
                ("net_wh", v)
                for v in ("exclude_caps", "exclude_drift", "exclude_short", "exclude_both")
            ]
            for field, variant in fields:
                population = g
                if variant == "exclude_caps":
                    population = population[~population.capped]
                if variant in {"exclude_drift", "exclude_both"}:
                    population = population[~population.drifted]
                if variant in {"exclude_short", "exclude_both"}:
                    population = population[~population.low_resolution]
                ids = set(g.task)
                for conditions in (spec["treatment"], spec["control"]):
                    ids &= set(complete_units(population, conditions, field, spec["samples"]))
                    ids &= set(complete_units(population, conditions, "passed", spec["samples"]))
                ids = sorted(ids)
                a = (
                    g[g.task.isin(ids) & g.condition.isin(spec["treatment"])]
                    .groupby("task")[[field, "passed"]]
                    .sum()
                    .reindex(ids)
                )
                b = (
                    g[g.task.isin(ids) & g.condition.isin(spec["control"])]
                    .groupby("task")[[field, "passed"]]
                    .sum()
                    .reindex(ids)
                )
                output.append(
                    {
                        "stage": spec["stage"],
                        "model": model,
                        "comparison": spec["name"],
                        "field": field,
                        "variant": variant,
                        "task_ids": ids,
                        "analysis_label": "posthoc paired cost-ratio audit",
                        **paired_ratio(
                            a[field].to_numpy(),
                            a.passed.to_numpy(),
                            b[field].to_numpy(),
                            b.passed.to_numpy(),
                        ),
                    }
                )
    save_json(destination / "energy-per-correct-differences.json", output)
