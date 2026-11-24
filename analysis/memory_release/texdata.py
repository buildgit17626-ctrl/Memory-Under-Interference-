"""Machine-generated manuscript numbers and tables, tied to audited source rows."""

import json
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

from analysis.memory_audit.records import save_json
from analysis.memory_release.analytics import energy_reduction_percent
from analysis.memory_release.common import AUDIT, MODELS, RELEASE, directories


def main():
    directories()
    conditions = json.loads((AUDIT / "conditions.json").read_text())
    effects = json.loads((AUDIT / "paired-effects.json").read_text())
    bounds = json.loads((RELEASE / "tables/cross-specification-sensitivities.json").read_text())
    ratios = json.loads((AUDIT / "energy-per-correct-differences.json").read_text())
    mg = json.loads((RELEASE / "tables/memorygraph-audit.json").read_text())
    claims, macros = {}, []

    def add(name, text, source, field):
        macros.append("\\newcommand{\\" + name + "}{" + text + "}")
        claims[name] = {"rendered": text, "source": source, "field": field}

    counts = json.loads((RELEASE / "tables/source-counts.json").read_text())
    add(
        "MainRequests",
        f"{counts['completed_main_logical_requests']:,}",
        "tables/source-counts.json",
        "completed_main_logical_requests",
    )
    for label, model in zip(("Small", "Large"), MODELS, strict=True):
        r = next(
            r
            for r in bounds
            if r["model"] == model
            and r["variant"] == "complete_case"
            and r["comparison"] == "near-minus-irrelevant"
        )
        add(
            label + "Cross",
            f"{r['estimate'] * 100:.2f}",
            "tables/cross-specification-sensitivities.json",
            f"{model}/complete_case/near-minus-irrelevant/estimate",
        )
        add(
            label + "CrossCI",
            f"[{r['ci95'][0] * 100:.2f}, {r['ci95'][1] * 100:.2f}]",
            "tables/cross-specification-sensitivities.json",
            f"{model}/complete_case/ci95",
        )
        add(
            label + "CrossN",
            str(r["n_units"]),
            "tables/cross-specification-sensitivities.json",
            f"{model}/complete_case/n_units",
        )
        add(
            label + "CrossP",
            f"{r['holm_family4_p']:.5g}",
            "tables/cross-specification-sensitivities.json",
            f"{model}/complete_case/holm_family4_p",
        )
        for policy, short in (("full_history", "Full"), ("oracle_selective", "Oracle")):
            c = next(
                r
                for r in conditions
                if r["stage"] == "R1" and r["model"] == model and r["condition"] == policy
            )
            q = c["net_wh_per_correct_covered"]
            add(
                label + short + "Energy",
                f"{q['estimate'] * 1000:.2f}",
                "data/audit/conditions.json",
                f"R1/{model}/{policy}/net_wh_per_correct_covered/estimate",
            )
        costs = {
            row["condition"]: row["net_wh_per_correct_covered"]["estimate"]
            for row in conditions
            if row["stage"] == "R1" and row["model"] == model
        }
        add(
            label + "EnergyReduction",
            f"{energy_reduction_percent(costs['full_history'], costs['oracle_selective']):.1f}",
            "data/audit/conditions.json",
            f"R1/{model}/100*(1-oracle_selective/full_history) net_wh_per_correct_covered",
        )
        r = next(
            r
            for r in ratios
            if r["stage"] == "R1"
            and r["model"] == model
            and r["comparison"] == "oracle_selective minus full_history"
            and r["field"] == "net_wh"
            and r["variant"] == "primary"
        )
        add(
            label + "EnergyDiff",
            f"{r['difference'] * 1000:.2f}",
            "data/audit/energy-per-correct-differences.json",
            f"R1/{model}/net_wh/primary/difference",
        )
        add(
            label + "EnergyCI",
            f"[{r['ci95'][0] * 1000:.2f}, {r['ci95'][1] * 1000:.2f}]",
            "data/audit/energy-per-correct-differences.json",
            f"R1/{model}/net_wh/primary/ci95",
        )
        for stage, family, name in (
            ("E0", "E0_primary_2", "Prompt"),
            ("M3_initial", "M3_initial_primary_2", "Initial"),
            ("M3R2", "M3R2_primary_2", "Target"),
        ):
            r = next(
                r
                for r in effects
                if r["stage"] == stage
                and r["model"] == model
                and r["family"] == family
                and r["variant"] == "primary"
            )
            add(
                label + name + "Diff",
                f"{r['estimate'] * 100:.2f}",
                "data/audit/paired-effects.json",
                f"{stage}/{model}/{family}/estimate",
            )
            add(
                label + name + "CI",
                f"[{r['ci95'][0] * 100:.2f}, {r['ci95'][1] * 100:.2f}]",
                "data/audit/paired-effects.json",
                f"{stage}/{model}/{family}/ci95",
            )
            add(
                label + name + "P",
                f"{r['holm_p']:.5g}",
                "data/audit/paired-effects.json",
                f"{stage}/{model}/{family}/holm_p",
            )
    for method, label in (("semantic", "EmbeddingMRR"), ("tfidf", "LexicalMRR")):
        add(
            label,
            str(
                Decimal(str(mg["methods"][method]["mrr"])).quantize(
                    Decimal(".0001"), rounding=ROUND_HALF_UP
                )
            ),
            "tables/memorygraph-audit.json",
            f"methods/{method}/mrr",
        )
    (RELEASE / "manuscript/numbers.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")
    save_json(RELEASE / "tables/manuscript-claim-map.json", claims)
    policies = [
        "full_history",
        "no_history",
        "verbatim_replay",
        "lossless_compaction",
        "oracle_selective",
    ]
    names = [
        "Full history",
        "Target/query",
        "Verbatim replay",
        "Lossless compaction",
        "Oracle retention",
    ]
    lines = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Model & Policy & Correct/40 & Input & Output & Net mWh/correct \\",
        r"\midrule",
    ]
    for model in MODELS:
        for policy, name in zip(policies, names, strict=True):
            r = next(
                r
                for r in conditions
                if r["stage"] == "R1" and r["model"] == model and r["condition"] == policy
            )
            lines.append(
                f"{model.split(':')[-1].upper()} & {name} & {r['successes']}/40 & "
                f"{r['prompt_tokens']['estimate']:.1f} & {r['output_tokens']['estimate']:.1f} & "
                f"{r['net_wh_per_correct_covered']['estimate'] * 1000:.2f} " + r"\\"
            )
        lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (RELEASE / "manuscript/r1_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Primary outcome contrasts, including null and opposite effects.
    lines = [
        r"\begin{longtable}{p{.075\linewidth}p{.065\linewidth}p{.26\linewidth}rrp{.18\linewidth}r}",
        r"\toprule Study & Model & Contrast & $n$ & Diff. pp & 95\% CI pp & Holm $p$ \\",
        r"\midrule",
    ]
    for r in effects:
        if r["variant"] != "primary" or r["family"] not in {
            "E0_primary_2",
            "M3_initial_primary_2",
            "M3R2_primary_2",
            "M2_primary_6",
            "R1_primary_6",
            "E5_adherence_primary_4",
        }:
            continue
        name = r["name"].replace("_", r"\_")
        if r["stage"] == "E5":
            name += " (strict adherence)"
        stage = "Initial M3" if r["stage"] == "M3_initial" else r["stage"].replace("_", r"\_")
        lines.append(
            f"{stage} & {r['model'].split(':')[-1].upper()} & {name} & {r['n_units']} & "
            f"{r['estimate'] * 100:.2f} & $[{r['ci95'][0] * 100:.2f}, {r['ci95'][1] * 100:.2f}]$ & "
            f"{r['holm_p']:.5g} " + r"\\"
        )
    lines += [r"\bottomrule", r"\end{longtable}"]
    (RELEASE / "manuscript/primary_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    frame = pd.read_csv(AUDIT / "calls-with-adherence.csv")
    frame = frame[frame.phase.eq("main")].copy()
    frame.loc[frame.stage.eq("M3_isolated"), "stage"] = "M3_initial"
    rows = []
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule Study & Calls & API failures & Caps & Energy readings \\",
        r"\midrule",
    ]
    for stage, group in frame.groupby("stage"):
        row = {
            "stage": stage,
            "calls": len(group),
            "api_failures": int(group.api_failed.sum()),
            "caps": int(group.capped.sum()),
            "energy": int(group.gross_wh.notna().sum()),
        }
        rows.append(row)
        name = stage.replace("_", r"\_")
        lines.append(
            f"{name} & {row['calls']} & {row['api_failures']} & {row['caps']} & "
            f"{row['energy']} " + r"\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    (RELEASE / "manuscript/inventory_table.tex").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    save_json(RELEASE / "tables/manuscript-inventory.json", rows)
    print(json.dumps({"machine_bound_manuscript_macros": len(claims)}), flush=True)


if __name__ == "__main__":
    main()
