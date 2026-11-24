"""Recompute release-critical counts and explicitly posthoc cross-pass bounds."""

import json

import numpy as np
import pandas as pd

from analysis.memory_audit.design import STAGES, stage_path
from analysis.memory_audit.records import indexed, save_json
from analysis.memory_audit.statistics import holm, paired
from analysis.memory_release.common import AUDIT, MODELS, RELEASE, directories


def energy_reduction_percent(full: float, retained: float) -> float:
    """Describe a ratio of observed estimated costs, without an accuracy/causal claim."""
    if full <= 0:
        raise ValueError("Positive full-history energy per correct solution required")
    return 100 * (1 - retained / full)


def cross_bounds(cross: pd.DataFrame) -> list[dict]:
    output = []
    for variant in ("complete_case", "unknown_lower_bound", "unknown_upper_bound"):
        for model in MODELS:
            g = cross[cross.model == model].copy()
            for control in ("irrelevant", "isolation"):
                a = g[g.condition.str.startswith("near_duplicate_")].copy()
                b = g[
                    g.condition.str.startswith("irrelevant_")
                    if control == "irrelevant"
                    else g.condition.eq("isolated")
                ].copy()
                if variant != "complete_case":
                    a["distractor_only"] = a.distractor_only.fillna(
                        0 if variant == "unknown_lower_bound" else 1
                    )
                    b["distractor_only"] = b.distractor_only.fillna(
                        1 if variant == "unknown_lower_bound" else 0
                    )
                aa = a.groupby("task").distractor_only.agg(["mean", "count"])
                bb = b.groupby("task").distractor_only.agg(["mean", "count"])
                ids = sorted(
                    set(aa[aa["count"] == 4].index)
                    & set(bb[bb["count"] == (4 if control == "irrelevant" else 1)].index)
                )
                output.append(
                    {
                        "variant": variant,
                        "model": model,
                        "comparison": "near-minus-" + control,
                        "analysis_label": "posthoc observed-data sensitivity",
                        "task_ids": ids,
                        "unknown_near_rows": int(a.cell.eq("invalid_or_censored").sum()),
                        "unknown_control_rows": int(b.cell.eq("invalid_or_censored").sum()),
                        **paired(aa.loc[ids, "mean"].to_numpy(), bb.loc[ids, "mean"].to_numpy()),
                    }
                )
        family = [r for r in output if r["variant"] == variant]
        for row, p in zip(family, holm([r["p_value"] for r in family]), strict=True):
            row["holm_family4_p"] = p
    return output


def main() -> None:
    directories()
    inventory = []
    for stage in STAGES:
        calls = indexed(stage_path(stage) / "calls.jsonl")
        inventory.append(
            {
                "stage": stage.name,
                "population": stage.phase,
                "logical_requests": len(calls),
                "expected": stage.expected,
                "api_failures": sum(bool(r.get("call_failed")) for r in calls.values()),
                "output_caps": sum("output_cap" in r.get("flags", []) for r in calls.values()),
            }
        )
    completed = [r for r in inventory if r["population"] == "main"]
    total = sum(r["logical_requests"] for r in completed)
    if total != 5528:
        raise ValueError(f"Expected 5528 completed main logical calls, found {total}")
    save_json(
        RELEASE / "tables/source-counts.json",
        {"completed_main_logical_requests": total, "stages": inventory},
    )
    pd.DataFrame(inventory).to_csv(RELEASE / "tables/source-counts.csv", index=False)
    cross = pd.read_csv(AUDIT / "cross-pass-per-response.csv")
    bounds = cross_bounds(cross)
    save_json(RELEASE / "tables/cross-specification-sensitivities.json", bounds)
    pd.json_normalize(bounds).to_csv(
        RELEASE / "tables/cross-specification-sensitivities.csv", index=False
    )
    for original in json.loads((AUDIT / "cross-pass-effects.json").read_text()):
        current = next(
            r
            for r in bounds
            if r["variant"] == "complete_case"
            and r["model"] == original["model"]
            and r["comparison"] == original["comparison"]
        )
        for field in ("estimate", "ci95", "n_units", "holm_family4_p"):
            if not np.array_equal(current[field], original[field]):
                raise ValueError("Cross-pass audit reproduction mismatch: " + field)
    print(
        json.dumps(
            {
                "main_logical_requests": total,
                "cross_sensitivity_rows": len(bounds),
                "new_inference": 0,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
