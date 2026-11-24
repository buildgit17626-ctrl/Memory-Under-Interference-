"""Portable saved-evidence reanalysis. No model, embedding or network requests."""

# Bootstrap the supplied source tree before importing it; no installed package is assumed.
# ruff: noqa: E402

import argparse
import json
import math
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "code"))
sys.path.insert(0, str(BASE / "code/src"))

import pandas as pd

from analysis.memory_audit.effects import summaries
from analysis.memory_audit.mechanisms import cross_audit
from analysis.memory_audit.records import indexed, save_json, scored_value
from analysis.memory_audit.statistics import paired_ratio


def check_recorded_outcomes(frame):
    checked = 0
    for folder, group in frame.groupby("source_folder"):
        suffix = str(folder).replace("\\", "/").split("/results/utilisation/", 1)[-1]
        root = BASE / "data/raw/results/utilisation" / suffix
        calls, scores = indexed(root / "calls.jsonl"), indexed(root / "scores.jsonl")
        for r in group.to_dict("records"):
            call = calls[r["key"]]
            score = scores.get(r["key"])
            value = scored_value(
                score, call, call["task_id"] if r["stage"].startswith("M1") else None
            )
            if not ((math.isnan(value) and pd.isna(r["passed"])) or value == r["passed"]):
                raise ValueError("Published correctness does not match raw score: " + r["key"])
            for field in ("prompt_tokens", "output_tokens"):
                a, b = call.get(field), r[field]
                if not ((a is None and pd.isna(b)) or a == b):
                    raise ValueError("Published token value does not match raw call")
            checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=BASE / "reproduced")
    parser.add_argument("--energy", action="store_true")
    parser.add_argument("--figures", action="store_true")
    parser.add_argument(
        "--full", action="store_true", help="Rebuild all prior paired audit effects"
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if output == BASE or output in (BASE / "data", BASE / "tables", BASE / "figures"):
        raise ValueError("Choose a new reproduction output directory")
    output.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(BASE / "data/audit/calls-with-adherence.csv")
    checked = check_recorded_outcomes(frame)
    n = int(frame.phase.eq("main").sum())
    if n != 5528:
        raise ValueError("Main-study logical-call count does not reproduce")
    save_json(output / "conditions.json", summaries(frame))
    shutil.copyfile(BASE / "data/audit/secondary-scores.jsonl", output / "secondary-scores.jsonl")
    cross_audit(frame, output)
    original = json.loads((BASE / "data/audit/cross-pass-effects.json").read_text())
    observed = json.loads((output / "cross-pass-effects.json").read_text())
    for a, b in zip(original, observed, strict=True):
        for field in ("estimate", "ci95", "n_units", "holm_family4_p"):
            if a[field] != b[field]:
                raise ValueError("Cross-pass result does not reproduce: " + field)
    ratios = []
    for model, g in frame[frame.stage.eq("R1")].groupby("model"):
        a = g[g.condition.eq("oracle_selective")].set_index("task").sort_index()
        b = g[g.condition.eq("full_history")].set_index("task").sort_index()
        result = paired_ratio(
            a.net_wh.to_numpy(), a.passed.to_numpy(), b.net_wh.to_numpy(), b.passed.to_numpy()
        )
        ratios.append({"model": model, **result})
    save_json(output / "r1-paired-ratios.json", ratios)
    if args.full:
        from analysis.memory_audit import effects
        from analysis.memory_audit.mechanisms import bundle_audit
        from analysis.memory_audit.robustness import (
            energy_sensitivities,
            ratio_effects,
            scoring_sensitivities,
        )
        from analysis.memory_release.analytics import cross_bounds

        effects.ROOT = BASE / "data/raw"
        effects.run_effects(frame, output)
        functions = pd.read_csv(BASE / "data/audit/functions.csv")
        bundle_audit(frame, functions, output)
        energy_sensitivities(frame, output)
        scoring_sensitivities(frame, functions, output)
        ratio_effects(frame, output)
        save_json(
            output / "cross-specification-sensitivities.json",
            cross_bounds(pd.read_csv(output / "cross-pass-per-response.csv")),
        )
        a = json.loads((BASE / "data/audit/paired-effects.json").read_text())
        b = json.loads((output / "paired-effects.json").read_text())
        if len(a) != len(b):
            raise ValueError("Full paired-effect row count mismatch")
        for left, right in zip(a, b, strict=True):
            for field in ("estimate", "ci95", "p_value", "holm_p", "n_units"):
                if left[field] != right[field]:
                    raise ValueError("Full paired-effect result mismatch: " + field)
    if args.energy:
        from analysis.memory_audit.sensors import integrate_many

        groups = json.loads((BASE / "data/energy/groups.json").read_text())
        windows = json.loads((BASE / "data/energy/windows.json").read_text())
        checked_windows, unavailable = 0, 0
        for group in groups:
            power = pd.read_csv(BASE / group["file"], float_precision="round_trip")
            rows = [r for r in windows if r["sensor_group"] == group["id"]]
            for r in integrate_many(
                power.timestamp_utc_epoch_s.to_numpy(), power.cpu_package_w.to_numpy(), rows
            ):
                if r.get("raw_wh") is None:
                    unavailable += 1
                elif not r.get("agrees_within_1e_8_wh"):
                    raise ValueError("Numerical energy integration mismatch")
                else:
                    checked_windows += 1
        save_json(
            output / "energy-check.json",
            {"available_windows_verified": checked_windows, "unavailable_windows": unavailable},
        )
    if args.figures:
        from analysis.memory_release import common, figures

        common.ROOT = BASE / "data/raw"
        common.RELEASE = output
        figures.AUDIT = BASE / "data/audit"
        figures.RELEASE = output
        (output / "tables").mkdir(exist_ok=True)
        shutil.copyfile(
            BASE / "tables/cross-specification-sensitivities.json",
            output / "tables/cross-specification-sensitivities.json",
        )
        figures.main()
    status = {
        "logical_calls_checked_against_raw": checked,
        "main_logical_requests": n,
        "cross_pass_effects_reproduced": len(observed),
        "new_model_inference": 0,
    }
    save_json(output / "REPRODUCED.json", status)
    print(json.dumps(status), flush=True)


if __name__ == "__main__":
    main()
