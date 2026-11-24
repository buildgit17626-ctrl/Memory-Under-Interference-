"""Condition summaries and versioned primary/exploratory paired contrasts."""

import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.memory_audit.design import ENERGY_MODE, ROOT
from analysis.memory_audit.records import save_json
from analysis.memory_audit.statistics import holm, interval, paired, ratio

METRICS = (
    "prompt_tokens",
    "output_tokens",
    "prefill_s",
    "decode_s",
    "wall_s",
    "gross_wh",
    "net_wh",
    "end_net_wh",
    "midpoint_net_wh",
    "total_gross_wh",
    "total_net_wh",
)


def summaries(frame: pd.DataFrame) -> list[dict]:
    output = []
    for (stage, model, condition), g in frame.groupby(["stage", "model", "condition"], sort=True):
        g = g.copy()
        g["unit"] = g["repeat"].astype(str) if stage.startswith("E4") else g["task"]
        usable = g[g.passed.notna()]
        pass_units = usable.groupby("unit").passed.mean()
        unscored = bool((g.score_status == "not_scored").all())
        row = {
            "stage": stage,
            "model": model,
            "condition": condition,
            "attempts": len(g),
            "units": g.unit.nunique(),
            "usable_correctness": len(usable),
            "successes": int(usable.passed.sum()) if not unscored else None,
            "pass_rate_attempt_weighted": float(usable.passed.mean()) if len(usable) else None,
            "task_weighted_pass": interval(pass_units.to_numpy()),
            "operational_successes": int((g.passed == 1).sum()),
            "operational_yield": float((g.passed == 1).mean()) if not unscored else None,
            "api_failed": int(g.api_failed.sum()),
            "invalid": int((~g.input_valid).sum()),
            "caps": int(g.capped.sum()),
            "energy_available": int(g.gross_wh.notna().sum()),
            "energy_condition_complete": bool(g.gross_wh.notna().all()),
            "low_resolution": int(g.low_resolution.sum()),
            "drifted_calls": int(g.drifted.sum()),
            "whole_bundle_successes": int((g.whole_passed == 1).sum()),
            "energy_tool_mode": ENERGY_MODE,
            "unit_interpretation": "repeat (synthetic probe)"
            if stage.startswith("E4")
            else "anchor task conditional on fixed companions"
            if stage.startswith("M1")
            else "task",
        }
        for field in METRICS:
            valid = g[g[field].notna()]
            row[field] = {
                "observations": len(valid),
                "sum_available": float(valid[field].sum()) if len(valid) else None,
                **interval(valid.groupby("unit")[field].mean().to_numpy()),
                "total_ci95": interval(valid.groupby("unit")[field].sum().to_numpy(), total=True)[
                    "ci95"
                ],
            }
        if stage == "E5":
            row["adherence_ci"] = interval(g.groupby("unit").adherence.mean().to_numpy())
            joint = g.assign(joint=(g.passed == 1) & (g.adherence == 1))
            row["joint_correct_and_adherent"] = interval(
                joint.groupby("unit").joint.mean().to_numpy()
            )
        for field in ("gross_wh", "net_wh", "end_net_wh", "midpoint_net_wh"):
            covered = g[g[field].notna() & g.passed.notna()]
            grouped = covered.groupby("unit")[[field, "passed"]].sum()
            row[field + "_per_correct_covered"] = {
                "attempts": len(covered),
                "complete_condition": len(covered) == len(g),
                **ratio(grouped[field].to_numpy(), grouped.passed.to_numpy()),
            }
        output.append(row)
    return output


def contrast_specs() -> list[dict]:
    specs = []

    def add(stage, a, b, family, label, name=None, outcome="passed", n=1):
        specs.append(
            {
                "stage": stage,
                "treatment": a if isinstance(a, list) else [a],
                "control": b if isinstance(b, list) else [b],
                "family": family,
                "analysis_label": label,
                "name": name or f"{a} minus {b}",
                "outcome": outcome,
                "samples": n,
            }
        )

    add("E0", "P3_1", "P1", "E0_primary_2", "registered contrast reproduction", n=3)
    add(
        "M3_initial",
        ["near_duplicate/1000", "near_duplicate/4000"],
        ["irrelevant/1000", "irrelevant/4000"],
        "M3_initial_primary_2",
        "registered contrast reproduction",
        "near-minus-irrelevant averaged length",
    )
    for kind in ("irrelevant", "other_tasks", "near_duplicate"):
        for length in (1000, 4000):
            add(
                "M3_initial",
                f"{kind}/{length}",
                "isolated_no_filler",
                "M3_initial_secondary_12",
                "registered secondary comparison",
            )
    for k in (2, 3, 4, 6):
        add(
            "M1",
            f"passive/K{k}",
            "isolated",
            "M1_registered_exploratory_16",
            "registered exploratory; fixed-companion conditional",
        )
        add(
            "M1",
            f"active/K{k}",
            f"passive/K{k}",
            "M1_registered_exploratory_16",
            "registered exploratory; target correctness, fixed companions",
        )
        add(
            "M1",
            f"passive/K{k}",
            f"filler/K{k}",
            "M1_matched_filler_posthoc_8",
            "posthoc; target correctness, fixed companions",
        )
    primary = {
        ("verbatim_replay", "full_history"),
        ("oracle_selective", "full_history"),
        ("lossless_compaction", "full_history"),
    }
    for a, b in sorted(primary):
        add("R1", a, b, "R1_primary_6", "registered contrast reproduction")
    policies = [
        "full_history",
        "no_history",
        "verbatim_replay",
        "lossless_compaction",
        "oracle_selective",
    ]
    for a, b in combinations(policies, 2):
        if (a, b) not in primary and (b, a) not in primary:
            add("R1", b, a, "R1_remaining_posthoc_14", "posthoc policy comparison")
    levels = [f"{n}_{p}" for n in (1000, 2000) for p in ("beginning", "end")]
    add(
        "M3R2",
        ["near_duplicate_" + x for x in levels],
        ["irrelevant_" + x for x in levels],
        "M3R2_primary_2",
        "registered contrast reproduction",
        "near-minus-irrelevant averaged cells",
    )
    for x in levels:
        for kind in ("near_duplicate", "related", "irrelevant"):
            add(
                "M3R2",
                kind + "_" + x,
                "isolated",
                "M3R2_isolation_posthoc_24",
                "posthoc cell-isolation",
            )
        add(
            "M3R2",
            "near_duplicate_" + x,
            "irrelevant_" + x,
            "M3R2_cells_posthoc_8",
            "posthoc individual-cell comparison",
        )
    for condition in ("similar", "other_one", "other_three"):
        add("M2", condition, "neutral", "M2_primary_6", "registered contrast reproduction")
        add("M2", condition, "isolated", "M2_isolation_posthoc_6", "posthoc isolation comparison")
    for a, b in (("buried", "immediate"), ("replayed", "buried")):
        add(
            "E5",
            a,
            b,
            "E5_adherence_primary_4",
            "registered contrast reproduction",
            outcome="adherence",
        )
        add("E5", a, b, "E5_correctness_secondary_4", "secondary correctness")
    for condition in ("immediate", "buried", "replayed", "corrected"):
        add("E5", condition, "no_preference", "E5_control_posthoc_8", "posthoc correctness")
    return specs


def complete_units(g: pd.DataFrame, conditions: list[str], field: str, samples: int) -> dict:
    selected = g[g.condition.isin(conditions)]
    if selected.empty:
        return {}
    counts = selected.groupby(["task", "condition"]).size().unstack(fill_value=0)
    counts = counts.reindex(columns=conditions, fill_value=0)
    stats = selected.groupby("task")[field].agg(["mean", "count"])
    keep = counts.eq(samples).all(axis=1) & stats["count"].eq(samples * len(conditions))
    return stats.loc[keep, "mean"].to_dict()


def compare(
    g: pd.DataFrame,
    spec: dict,
    model: str,
    variant: str,
    outcome_data: pd.DataFrame | None = None,
    include_metrics: bool = True,
) -> dict:
    field = spec["outcome"]
    outcome_data = g if outcome_data is None else outcome_data
    a = complete_units(outcome_data, spec["treatment"], field, spec["samples"])
    b = complete_units(outcome_data, spec["control"], field, spec["samples"])
    ids = sorted(set(a) & set(b))
    av, bv = np.array([a[t] for t in ids]), np.array([b[t] for t in ids])
    binary = len(spec["treatment"]) == len(spec["control"]) == spec["samples"] == 1
    result = {
        **spec,
        "model": model,
        "variant": variant,
        **paired(av, bv, binary_test=binary),
        "paired_task_ids": ids,
        "task_rate_increase_ids": [t for t in ids if a[t] > b[t]],
        "task_rate_decrease_ids": [t for t in ids if a[t] < b[t]],
        "pass_to_fail_ids": [t for t in ids if a[t] == 0 and b[t] == 1] if binary else None,
        "fail_to_pass_ids": [t for t in ids if a[t] == 1 and b[t] == 0] if binary else None,
        "metrics": {},
        "exchangeability_assumption": "paired unit labels swappable under null",
    }
    if spec["stage"] == "M1":
        result["dependency_warning"] = (
            "Anchor-task CI/test conditional on fixed companions; overlapping bundles "
            "do not supply independent component-level replication."
        )
    for metric in METRICS if include_metrics else ():
        ma = complete_units(g, spec["treatment"], metric, spec["samples"])
        mb = complete_units(g, spec["control"], metric, spec["samples"])
        matched = sorted(set(ma) & set(mb))
        result["metrics"][metric] = {
            **interval(np.array([ma[t] - mb[t] for t in matched])),
            "paired_task_ids": matched,
        }
    # Cell transitions retain repeated observations but never count them as independent tasks.
    transitions = []
    lookup = {(r.task, r.condition, r["sample"]): r for _, r in g.iterrows()}
    for task in ids if variant == "primary" else []:
        for i, ac in enumerate(spec["treatment"]):
            bc = spec["control"][min(i, len(spec["control"]) - 1)]
            for sample in range(spec["samples"]):
                ar = lookup.get((task, ac, sample))
                br = lookup.get((task, bc, sample))
                if ar is not None and br is not None:
                    aa, bb = float(ar[field]), float(br[field])
                    transitions.append(
                        {
                            "task": task,
                            "cell": ac,
                            "control": bc,
                            "sample": sample,
                            "before": bb,
                            "after": aa,
                            "before_key": br["key"],
                            "after_key": ar["key"],
                        }
                    )
    result["cell_transitions"] = transitions
    return result


def run_effects(frame: pd.DataFrame, destination: Path) -> list[dict]:
    data = frame.copy()
    data.loc[data.stage == "M3_isolated", "stage"] = "M3_initial"
    labels = json.loads(
        (ROOT / "results/utilisation/supervised/analysis/heldout-labels.json").read_text()
    )
    variants = (
        "primary",
        "exclude_caps",
        "optimistic_cap_bound",
        "exclude_HumanEval32",
        "heldout_eligible",
        "exclude_drift",
        "exclude_low_resolution",
        "exclude_drift_and_short",
    )
    results = []
    for spec_index, spec in enumerate(contrast_specs()):
        print(
            json.dumps({"effect_spec": spec_index, "stage": spec["stage"], "name": spec["name"]}),
            flush=True,
        )
        for model, base in data[data.stage == spec["stage"]].groupby("model"):
            for variant in variants:
                g = base.copy()
                current_spec = dict(spec)
                if variant == "exclude_caps":
                    g = g[~g.capped]
                elif variant == "optimistic_cap_bound":
                    g.loc[g.capped, "passed"] = 1.0
                elif variant == "exclude_HumanEval32":
                    g = g[g.task != "HumanEval/32"]
                elif variant == "heldout_eligible":
                    eligible = {t for t, record in labels[model].items() if record["solvable"]}
                    g = g[g.task.isin(eligible)]
                    if spec["stage"] == "E0":
                        g = g[g["sample"].isin([1, 2])]
                        current_spec["samples"] = 2
                        current_spec["heldout_outcome_samples"] = [1, 2]
                elif variant.startswith("exclude_"):
                    keep = np.ones(len(g), dtype=bool)
                    if "drift" in variant:
                        keep &= ~g.drifted.to_numpy()
                    if "low_resolution" in variant or "short" in variant:
                        keep &= ~g.low_resolution.to_numpy()
                    g = g[keep]
                if spec["outcome"] not in g:
                    continue
                energy_selection = variant in {
                    "exclude_drift",
                    "exclude_low_resolution",
                    "exclude_drift_and_short",
                }
                record = compare(
                    g, current_spec, model, variant, base if energy_selection else None
                )
                if energy_selection:
                    record["variant_scope"] = (
                        "Energy-population sensitivity; original correctness denominator retained."
                    )
                results.append(record)
    for family in {r["family"] for r in results}:
        for variant in variants:
            group = [r for r in results if r["family"] == family and r["variant"] == variant]
            for row, adjusted in zip(group, holm([r["p_value"] for r in group]), strict=True):
                row["holm_p"] = adjusted
                row["family_tests"] = len(group)
    save_json(destination / "paired-effects.json", results)
    flat = [
        {k: v for k, v in r.items() if k not in {"metrics", "cell_transitions"}} for r in results
    ]
    pd.DataFrame(flat).to_csv(destination / "paired-effects.csv", index=False)
    return results
