"""Explicitly posthoc control completeness and joint preference outcomes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import pandas as pd

from analysis.memory_audit.design import DESTINATION
from analysis.memory_audit.effects import compare
from analysis.memory_audit.records import save_json
from analysis.memory_audit.statistics import holm, interval


def supplemental_controls(destination=DESTINATION):
    frame = pd.read_csv(destination / "calls-with-adherence.csv")
    specs = []

    def add(stage, a, b, outcome, family):
        specs.append(
            {
                "stage": stage,
                "treatment": [a],
                "control": [b],
                "outcome": outcome,
                "family": family,
                "name": f"{a} minus {b}",
                "samples": 1,
                "analysis_label": "posthoc audit control-completeness comparison",
            }
        )

    for k in (2, 3, 4, 6):
        add("M1", f"filler/K{k}", "isolated", "passed", "M1_filler_isolation_posthoc8")
    add("M2", "neutral", "isolated", "passed", "M2_neutral_isolation_posthoc2")
    for field in ("adherence", "adherence_fence_tolerant", "adherence_strict_proxy"):
        frame["joint_" + field] = ((frame.passed == 1) & (frame[field] == 1)).astype(float)
        for condition in ("immediate", "buried", "replayed", "corrected"):
            for outcome in (field, "joint_" + field):
                add("E5", condition, "no_preference", outcome, "E5_control_" + outcome + "_8")
    rows = []
    for spec in specs:
        for model, group in frame[frame.stage == spec["stage"]].groupby("model"):
            rows.append(compare(group, spec, model, "posthoc_controls"))
    for family in {r["family"] for r in rows}:
        group = [r for r in rows if r["family"] == family]
        for r, adjusted in zip(group, holm([r["p_value"] for r in group]), strict=True):
            r["holm_p"] = adjusted
    save_json(destination / "supplemental-control-effects.json", rows)
    joint = []
    for (model, condition), g in frame[frame.stage == "E5"].groupby(["model", "condition"]):
        for field in ("adherence", "adherence_fence_tolerant", "adherence_strict_proxy"):
            for endpoint in (field, "joint_" + field):
                joint.append(
                    {
                        "model": model,
                        "condition": condition,
                        "endpoint": endpoint,
                        "attempts": len(g),
                        "successes": int(g[endpoint].sum()),
                        "analysis_label": "original strict metric"
                        if field == "adherence"
                        else "posthoc mechanical definition",
                        **interval(g.groupby("task")[endpoint].mean().to_numpy()),
                    }
                )
    save_json(destination / "e5-joint-intervals.json", joint)


if __name__ == "__main__":
    supplemental_controls()
