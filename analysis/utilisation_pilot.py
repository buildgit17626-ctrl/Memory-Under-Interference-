"""Report measured pilot rows and explicit, unapproved workload scenarios."""

import csv
import json
import statistics

from prompt_energy.utilisation_journal import read_jsonl
from prompt_energy.utilisation_plan import ROOT
from prompt_energy.utilisation_run import by_key

PILOT = ROOT / "results/utilisation/pilot"
OUT = ROOT / "artifacts/utilisation/pilot"


def scenarios():
    # Each count is across both models. Changes are options for owner choice.
    main = {
        "focused": {
            "E0": 164 * 2 * 3 * 2,
            "M3": 20 * 2 * 3 * 1 * 2,
            "R1": 20 * 3 * 2,
            "R2": 20 * 3 * 2,
            "U1": 164 * 4 * 2,
            "U2": 164 * 2,
            "E3": 10 * 2 * 2 * 3 * 3 * 2,
        },
        "balanced": {
            "E0": 164 * 2 * 3 * 2,
            "M3": 40 * 3 * 3 * 2 * 2,
            "R1": 40 * 7 * 2,
            "R2": 40 * 7 * 2,
            "U1": 164 * 4 * 2,
            "U2": 164 * 2,
            "E3": 10 * 4 * 4 * 3 * 3 * 2,
        },
        "catalogue": {
            "E0": 164 * 2 * 3 * 2,
            "M3": 60 * 4 * 3 * 3 * 2,
            "R1": 60 * 13 * 2,
            "R2": 60 * 10 * 2,
            "U1": 164 * 4 * 2,
            "U2": 164 * 2,
            "E3": 20 * 4 * 4 * 3 * 3 * 2,
        },
    }
    appendix = {
        "focused": {
            "M1_bundle": 15 * 2 * 1 * 2,
            "M1_separate": 15 * (2 + 4) * 1 * 2,
            "M2": 20 * (4 + 4) * 2,
            "E5": 40 * 6 * 3 * 2,
            "E4": 3 * 2 * 5 * 2,
            "U5": 20 * 3 * 2,
        },
        "balanced": {
            "M1_bundle": 30 * 3 * 2 * 2,
            "M1_separate": 30 * (2 + 3 + 4) * 2 * 2,
            "M2": 40 * (4 + 4) * 2,
            "E5": 80 * 6 * 3 * 2,
            "E4": 5 * 2 * 10 * 2,
            "U5": 40 * 3 * 2,
        },
        "catalogue": {
            "M1_bundle": 60 * 4 * 2 * 2,
            "M1_separate": 60 * (2 + 3 + 4 + 6) * 2 * 2,
            "M2": 60 * (4 + 4) * 2,
            "E5": 164 * 6 * 3 * 2,
            "E4": 5 * 2 * 20 * 2,
            "U5": 60 * 3 * 2,
        },
    }
    return {"MAIN": main, "APPENDIX": appendix}


def main():
    rows = list(by_key(PILOT / "calls.jsonl").values())
    if len(rows) != 22:
        raise ValueError(f"Pilot incomplete: {len(rows)}/22")
    OUT.mkdir(parents=True, exist_ok=True)
    metrics = []
    for r in rows:
        post = r["energy"]["windows"].get("post_load", {})
        metrics.append(
            {
                "key": r["key"],
                "model": r["model"],
                "experiment": r["experiment"],
                "task": r["task_id"],
                "arm": r["condition"],
                "wall_s": r["wall_seconds"],
                "input_tokens": r["prompt_tokens"],
                "output_tokens": r["output_tokens"],
                "prefill_s": r["prefill_ns"] / 1e9,
                "decode_s": r["decode_ns"] / 1e9,
                "decode_tokens_s": (r["output_tokens"] / (r["decode_ns"] / 1e9))
                if r["output_tokens"] >= 10
                else None,
                "input_valid": r["input_valid"],
                "output_cap": "output_cap" in r["flags"],
                "gross_post_load_wh": post.get("raw_wh"),
                "net_post_load_wh": post.get("adjusted_wh"),
                "flags": "|".join(r["flags"] + r["energy"]["flags"]),
            }
        )
    with (OUT / "calls.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics[0]))
        writer.writeheader()
        writer.writerows(metrics)
    summary = []
    for model in sorted({r["model"] for r in metrics}):
        for exp in ("E0", "context_probe"):
            g = [r for r in metrics if r["model"] == model and r["experiment"] == exp]
            summary.append(
                {
                    "model": model,
                    "experiment": exp,
                    "n": len(g),
                    **{
                        k: (
                            statistics.mean(r[k] for r in g if r[k] is not None)
                            if any(r[k] is not None for r in g)
                            else None
                        )
                        for k in (
                            "wall_s",
                            "input_tokens",
                            "output_tokens",
                            "prefill_s",
                            "decode_s",
                            "decode_tokens_s",
                        )
                    },
                    "valid_inputs": sum(r["input_valid"] for r in g),
                    "cap_hits": sum(r["output_cap"] for r in g),
                    "energy_coverage": sum(r["net_post_load_wh"] is not None for r in g),
                    "low_resolution": sum("post_load:low_resolution" in r["flags"] for r in g),
                }
            )
    models = sorted({r["model"] for r in metrics})
    # Lower/upper planning rates use observed mean short/long-call service time.
    # These are extrapolations, not statistical confidence intervals or bounds.
    rates = []
    for model in models:
        s = [r for r in summary if r["model"] == model]
        short = next(r for r in s if r["experiment"] == "E0")
        long = next(r for r in s if r["experiment"] == "context_probe")
        rates.append((short["wall_s"] + 5, long["wall_s"] + short["decode_s"] + 5))
    low = statistics.mean(r[0] for r in rates)
    high = statistics.mean(r[1] for r in rates)
    forecasts = []
    for family, versions in scenarios().items():
        for name, counts in versions.items():
            calls = sum(counts.values())
            forecasts.append(
                {
                    "family": family,
                    "version": name,
                    "calls": calls,
                    "components": counts,
                    "service_hours_short_mean": calls * low / 3600,
                    "service_hours_long_mean": calls * high / 3600,
                }
            )
    report = {
        "blocks": read_jsonl(PILOT / "blocks.jsonl"),
        "summary": summary,
        "scenarios": forecasts,
        "assumptions": [
            "Scenarios are proposals; no full schedule was approved.",
            "U1 budgets all 164 tasks per model as an upper count; actual failure "
            "sets are unknown.",
            "E3 reduced scale uses 10/10/20 tasks per model and 2x2/4x4/4x4 feedback-memory cells.",
            "M3 focused/balanced/catalogue use 20/40/60 tasks; 2/3/4 lengths; 1/2/3 positions.",
            "R1 uses 3/7/13 distinct cells; zero replay is counted once. Catalogue is 1+4*3.",
            "R2 uses 3/7/10 cells; zero distractors is counted once. Catalogue is 1+3*3.",
            "M1 uses 15/30/60 bundles PER K and 1/2/2 orders; K sets 2,4 / 2,3,4 / 2,3,4,6.",
            "M2 budgets four target conditions plus four interruption calls per task, "
            "pending protocol.",
            "E4 count excludes priming/unload/preload, which require additional setup time.",
            "U3 and U4 require scoring time, not model calls.",
            "Short rates use E0 wall+5s; long rates use probe wall+E0 decode+5s. "
            "Models receive equal weights.",
            "Timing range is not a confidence interval or a guarantee; long "
            "repair/bundle outputs can exceed it.",
            "Excluded time includes independent calibration, reference scoring, "
            "baselines, priming, retries and downtime.",
            "All figures are pilot diagnostics; no correctness or hypothesis claims are inferred.",
        ],
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    lines = [
        "# Diagnostic timing pilot",
        "",
        "This report describes 22 pilot requests. No full run was started.",
        "",
        "## Measured results",
        "",
        (
            "| Model | Subset | n | Wall s | Output tok/s | Prefill s | Decode s | "
            "Energy | Low resolution |"
        ),
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in summary:
        lines.append(
            f"| {r['model']} | {r['experiment']} | {r['n']} | "
            f"{r['wall_s']:.3f} | {r['decode_tokens_s']} | "
            f"{r['prefill_s']:.3f} | {r['decode_s']:.3f} | "
            f"{r['energy_coverage']}/{r['n']} | {r['low_resolution']} |"
        )
    lines += [
        "",
        "Means are across requests. Tokens/s uses output tokens divided by API "
        "decode duration for each request, then averages those rates.",
        "",
        "## Scope scenarios awaiting owner choice",
        "",
        "| Family | Scope | Calls | Short-rate hours | Long-rate hours |",
        "|---|---|---:|---:|---:|",
    ]
    for r in forecasts:
        lines.append(
            f"| {r['family']} | {r['version']} | {r['calls']} | "
            f"{r['service_hours_short_mean']:.1f} | "
            f"{r['service_hours_long_mean']:.1f} |"
        )
    lines += [
        "",
        "## Counts and timing formulas",
        "",
        "Every count includes both models. report.json contains component counts. "
        "The scenarios() function in analysis/utilisation_pilot.py contains "
        "each multiplication and the exact scope definition.",
        "",
        "The short scenario uses mean E0 wall time. The long scenario adds E0 mean decode "
        "time to probe wall time because the probes returned no code. "
        "Add the 5s gap and average models. "
        "Multiply each service rate by the proposed call count and divide by 3600.",
        "",
    ]
    lines += ["- " + a for a in report["assumptions"]]
    lines += [
        "",
        "The 4000-token probes returned empty text (0.5B) and 0 (1.5B). "
        "Their counts matched, but they supply no coding-workload decode evidence. "
        "Probe tokens/s is suppressed for fewer than ten output tokens. "
        "Long repair or bundled outputs can take substantially longer than these forecasts.",
        "",
        "## Sensor baseline records",
        "",
    ]
    for b in report["blocks"]:
        lines.append(
            f"- {b['event']} baseline {b['baseline']['watts']:.3f} W; flags {b.get('flags', [])}."
        )
    (OUT / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"summary": summary, "scenarios": forecasts}, indent=2))


if __name__ == "__main__":
    main()
