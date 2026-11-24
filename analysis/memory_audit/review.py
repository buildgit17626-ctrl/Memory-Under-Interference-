"""Generate a readable skeptical review entirely from versioned audit outputs."""

import json
from pathlib import Path

import pandas as pd

from analysis.memory_audit.design import ENERGY_MODE


def fmt(value, scale=1):
    return "NA" if value is None or pd.isna(value) else f"{value * scale:.4g}"


def ci(value, scale=1):
    return "unavailable" if value is None else "[" + ", ".join(fmt(x, scale) for x in value) + "]"


def write_review(d: Path):
    def load(name):
        return json.loads((d / name).read_text())

    calls = pd.read_csv(d / "calls-with-adherence.csv")
    condition_rows = load("conditions.json")
    effects = load("paired-effects.json")
    cross = load("cross-pass-effects.json")
    energy = load("energy-sensitivities.json")
    ratios = load("energy-per-correct-differences.json")
    lines = [
        "# Skeptical scientific review — 24 November 2026",
        "",
        "Provisional interpretation for owner review; no manuscript claims are approved. "
        "This is a posthoc audit of existing data. Reproducing a registered contrast does "
        "not make additional analyses preregistered. No new model inference occurred.",
        "",
        "## What would change these interpretations?",
        "",
        "A scoring/reference discrepancy, a different defensible adherence definition, "
        "paired cap exclusions, selected-population changes, dependence-aware replication, "
        "or energy rankings that reverse under baseline/coverage sensitivities would change "
        "the interpretations. Evidence from other models/hardware/tasks could change their "
        "generality. Null tests here do not establish equivalence. The intervals are "
        "pointwise percentile task bootstrap intervals, not simultaneous family intervals.",
        "",
        "## Five candidate observations for discussion",
        "",
        "1. **Semantic alternatives are associated with a different failure mix.** "
        "The following new "
        "posthoc contrasts concern distractor-only success, not overall target accuracy. "
        "Complete-cell matching excludes censored/missing pairs; no internal mechanism "
        "or intentional choice is inferred.",
        "",
        "|Model|Near minus control|Tasks|Difference pp|95% CI pp|Holm family4 p|",
        "|---|---|---:|---:|---|---:|",
    ]
    for r in cross:
        lines.append(
            f"|{r['model']}|{r['comparison']}|{r['n_units']}|"
            f"{fmt(r['estimate'], 100)}|{ci(r['ci95'], 100)}|"
            f"{fmt(r['holm_family4_p'])}|"
        )
    lines += ["", "By comparison, registered revised M3/R2 target-correctness contrasts:", ""]
    for r in effects:
        if r["variant"] == "primary" and r["family"] == "M3R2_primary_2":
            lines.append(
                f"- {r['model']}: n={r['n_units']}; {fmt(r['estimate'], 100)} pp, "
                f"CI {ci(r['ci95'], 100)}, Holm p={fmt(r['holm_p'])}."
            )
    lines += [
        "",
        "A pointwise interval can exclude zero while a multiplicity-adjusted test "
        "does not reject. Report both. Do not select whichever yields a stronger claim.",
        "",
        "2. **R1 supplies an efficiency comparison, without an established accuracy "
        "advantage.** The reduced oracle policy is privileged, omits distractors and "
        "changes length/position; it is not an automated retriever. The following "
        "energy-per-correct differences are posthoc ratio contrasts, oracle minus "
        "full history, over identical covered task sets.",
        "",
        "|Model|Tasks|Net Wh/correct difference|95% CI|",
        "|---|---:|---:|---|",
    ]
    for r in ratios:
        if (
            r["stage"] == "R1"
            and r["comparison"] == "oracle_selective minus full_history"
            and r["field"] == "net_wh"
            and r.get("variant", "primary") == "primary"
        ):
            lines.append(f"|{r['model']}|{r['n_units']}|{fmt(r['difference'])}|{ci(r['ci95'])}|")
    lines += ["", "R1 registered correctness effects (pp):", ""]
    for r in effects:
        if r["variant"] == "primary" and r["family"] == "R1_primary_6":
            lines.append(
                f"- {r['model']}, {r['name']}: {fmt(r['estimate'], 100)}, "
                f"CI {ci(r['ci95'], 100)}, Holm p={fmt(r['holm_p'])}."
            )
    prompt = pd.read_csv(d / "r1-prompt-audit.csv")
    equivalent = prompt[prompt.target_preference_query_exact_equivalent]
    lines += [
        "",
        f"Exact rendered target+preference+query equivalence: {len(equivalent)}/"
        f"{len(prompt)} R1 calls, all in policies "
        f"{sorted(equivalent.policy.unique().tolist())}. Priority A's proposed "
        "control therefore already exists for both models. The no_history policy "
        "omits the explicit code-only preference; it is not that matched control. "
        "Formatting compaction preserves the target wording and drops other history; "
        "it is not semantic summarization.",
        "",
        "3. **Task load and additional output work must be separated.** Passive "
        "versus token-matched filler measures target correctness under extra task "
        "descriptions. Active generation additionally requests K functions. "
        "Every M1 bundle graph has one connected membership component; the "
        "following anchor-task intervals/tests are conditional and cannot supply "
        "dependence-robust population inference.",
        "",
        "|Model|Passive minus filler|Tasks|Difference pp|Conditional CI pp|Holm8 p|",
        "|---|---|---:|---:|---|---:|",
    ]
    for r in effects:
        if r["variant"] == "primary" and r["family"] == "M1_matched_filler_posthoc_8":
            lines.append(
                f"|{r['model']}|{r['name']}|{r['n_units']}|"
                f"{fmt(r['estimate'], 100)}|{ci(r['ci95'], 100)}|{fmt(r['holm_p'])}|"
            )
    lines += [
        "",
        "Active per-function and whole-bundle differences against the same "
        "component isolation references:",
        "",
        "|Model|Bundle|Function-fraction pp|Conditional CI pp|Whole-bundle pp|Components|",
        "|---|---|---:|---|---:|---:|",
    ]
    for r in load("m1-bundle-dependencies.json"):
        f, w = (
            r["function_fraction_difference_conditional"],
            r["whole_bundle_difference_conditional"],
        )
        lines.append(
            f"|{r['model']}|{r['condition']}|{fmt(f['estimate'], 100)}|"
            f"{ci(f['ci95'], 100)}|{fmt(w['estimate'], 100)}|{r['component_count']}|"
        )
    lines += [
        "",
        "The apparent K trend also changes bundle composition; do not treat K "
        "as a clean dose-response. Component isolation costs are reused lookup sums, "
        "not physical repeated baseline runs. See m1-work-and-function-cost.json.",
        "",
        "4. **E5's registered strict metric is at its floor.**",
        "",
    ]
    joint = pd.read_csv(d / "e5-joint-outcomes.csv")
    lines.append(
        f"Original adherence: {joint.adherence.sum()}/{joint.attempts.sum()} responses. "
        "This rule requires unfenced parseable Python, although the wording "
        "asked for code only rather than explicitly forbidding fences. It cannot "
        "by itself distinguish retention conditions in this sample."
    )
    lines += [
        "",
        "|Model|Condition|Attempts|Strict|Fence-tolerant|Correct and strict|"
        "Correct and fence-tolerant|Comments present|Docstrings present|",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in joint.to_dict("records"):
        lines.append(
            "|"
            + "|".join(
                str(r[k])
                for k in [
                    "model",
                    "condition",
                    "attempts",
                    "adherence",
                    "fence_tolerant",
                    "joint",
                    "joint_fence_tolerant",
                    "comments",
                    "docstrings",
                ]
            )
            + "|"
        )
    lines += [
        "",
        "Fence-tolerant and comment/docstring-free scores are posthoc mechanical "
        "proxies. Comments/docstrings may be code or explanations; human semantic "
        "annotation is not supplied by a syntax test. A degenerate all-zero/all-one "
        "bootstrap interval is an empirical-resample property, not certainty of "
        "the population rate. Secondary buried/replay contrasts also do not establish "
        "an adherence benefit (scoring-sensitivity-effects.json).",
        "",
        "5. **Effects do not repeat uniformly across models and designs.** E0 and "
        "M2 primary contrasts do not establish an ordering after their family "
        "corrections; intervals permit meaningful differences. Initial M3 uses "
        "different selected populations and a weaker near-duplicate construction, "
        "so it cannot be pooled with revised semantic M3/R2.",
        "",
    ]
    for r in effects:
        if r["variant"] == "primary" and r["family"] in {
            "E0_primary_2",
            "M2_primary_6",
            "M3_initial_primary_2",
        }:
            lines.append(
                f"- {r['stage']}/{r['model']}, {r['name']}: n={r['n_units']}, "
                f"{fmt(r['estimate'], 100)} pp, CI {ci(r['ci95'], 100)}, "
                f"Holm p={fmt(r['holm_p'])}."
            )
    lines += [
        "",
        "M2 uses fixed description-only conversational transcripts. Complete "
        "input counts match across loaded conditions, but these are not tasks "
        "actually executed earlier by the model. Similarity and interruption count "
        "are not a fully crossed factorial design.",
        "",
        "## Energy coverage and sensitivity",
        "",
        "Tool/mode: " + ENERGY_MODE + ". "
        "CPU-package estimates exclude wall-plug/system-wide energy. E4 was designated "
        "the primary energy evidence and is incomplete; R1 cost comparisons here remain "
        "descriptive/posthoc, not a completed confirmatory energy study. Primary "
        "totals include failures; coverage and correct-count denominators are "
        "attached. End/midpoint baselines and exclusions are posthoc. Short-window "
        "exclusion preferentially removes cheap conditions and changes the population.",
        "",
        "|Stage|Calls|Energy readings|Low-resolution|Drift-flagged calls|",
        "|---|---:|---:|---:|---:|",
    ]
    for stage, g in calls[calls.phase.isin(["main", "partial"])].groupby("stage"):
        lines.append(
            f"|{stage}|{len(g)}|{g.gross_wh.notna().sum()}|"
            f"{g.low_resolution.sum()}|{g.drifted.sum()}|"
        )
    lines += [
        "",
        "R1 sensitivity example (available-covered population, not a pooled "
        "or population-matched replacement for primary):",
        "",
        "|Model|Policy|Variant|Retained/40|Net Wh/correct|95% CI|",
        "|---|---|---|---:|---:|---|",
    ]
    for r in energy:
        if r["stage"] == "R1" and r["condition"] in {"full_history", "oracle_selective"}:
            q = r["energy_per_correct_covered"]
            lines.append(
                f"|{r['model']}|{r['condition']}|{r['variant']}|"
                f"{r['retained_attempts']}/{r['original_attempts']}|"
                f"{fmt(q['estimate'])}|{ci(q['ci95'])}|"
            )
    lines += [
        "",
        "Paired R1 oracle-minus-full ratio sensitivities, each on the same "
        "retained tasks in both arms. Exclusions can select a different task population. "
        "An unavailable interval means at least one bootstrap draw has zero correct "
        "solutions in an arm; it is not replaced by a conditional finite interval.",
        "",
        "|Model|Energy definition|Variant|Paired tasks|Wh/correct difference|95% CI|",
        "|---|---|---|---:|---:|---|",
    ]
    for r in ratios:
        if r["stage"] == "R1" and r["comparison"] == "oracle_selective minus full_history":
            lines.append(
                f"|{r['model']}|{r['field']}|{r.get('variant', 'primary')}|"
                f"{r['n_units']}|{fmt(r['difference'])}|{ci(r['ci95'])}|"
            )
    prefixes, windows = load("sensor-prefix-audit.json"), load("sensor-integration-audit.json")
    available = [r for r in windows if r.get("recomputed_wh") is not None]
    lines += [
        "",
        f"Recorded prefix hashes checked: {len(prefixes)}; mismatches "
        f"{sum(not r['match'] for r in prefixes)}. Integrated windows recorded: "
        f"{len(windows)}; independently recomputable {len(available)}; disagreements "
        f"at 1e-8 Wh tolerance {sum(not r['agrees_within_1e_8_wh'] for r in available)}. "
        "Unavailable windows remain missing. Numerical agreement does not calibrate "
        "HWiNFO, isolate unrelated CPU work, or validate approximate post-load boundaries.",
        "",
        "Recorded host/process checks: environment-block-audit.json preserves AC, "
        "power mode, CPU/RAM/library metadata, baseline drift and endpoint CPU-counter "
        "deltas. All saved block-start checks observed AC/Best performance. Endpoint "
        "snapshots do not establish uninterrupted host state or isolate per-call "
        "background CPU energy. Counter resets/PID reuse are flagged. Cache state was "
        "not a crossed experimental factor outside E4; native cached-token readings "
        "remain in calls.csv and are a limit on interpreting prefill/energy mechanisms.",
        "",
        "## Scoring and oracle sensitivities",
        "",
    ]
    scores = [json.loads(line) for line in (d / "secondary-scores.jsonl").read_text().splitlines()]
    for operation in sorted({r["operation"] for r in scores}):
        group = [r for r in scores if r["operation"] == operation]
        lines.append(
            f"- {operation}: {len(group)} separate sandbox scores; "
            f"{sum(r['passed'] is None for r in group)} infrastructure-unavailable."
        )
    changes = load("scoring-changes.json")
    lines.append(
        f"- Audited extraction/capped target candidates with changed focal correctness: "
        f"{sum(r['before'] != r['after'] for r in changes)}/{len(changes)}. This is "
        "not a proof that every extraction is optimal or every failing solution is wrong logic."
    )
    lines += [
        "- HumanEval/32 remains under the original oracle. Its exclusion, caps as "
        "missing, optimistic cap bounds and held-out eligibility are tabulated in "
        "PHASES_1_4_REPORT.md/paired-effects.json. E0 eligibility sensitivity excludes "
        "sample0 from comparison outcomes; the primary retains all registered samples.",
        "- Cap exclusion can reverse small R1 correctness point estimates on 0.5B; "
        "the registered effects remain uncertain. The independently selected eligibility "
        "subset can increase revised M3/R2's 0.5B effect magnitude. These are changes "
        "of target population, not grounds to replace the full-roster primary estimate. "
        "Exact effect sizes, retained IDs, intervals and corrected tests are in the "
        "sensitivity table, including null/opposite outcomes.",
        "- Representative distractor-only code implements <= rather than < on "
        "HumanEval/0 (0.5B), and reversed group order on HumanEval/1 (1.5B). "
        "Separate distinguishing witness checks agree with those labels. The "
        "six-example deterministic review is not a prevalence estimate. Both-pass "
        "has no sampled examples because no such outcomes occurred in near-condition "
        "records; it must remain an explicit zero category. See REPRESENTATIVE_CODE_AUDIT.md.",
        "",
        "## Partial E4 and excluded claims",
        "",
    ]
    for r in load("e4-partial-paired.json"):
        lines.append(
            f"- {r['model']}, prefix {r['prefix_tokens']}: warm {r['warm_calls']}, "
            f"cold {r['cold_calls']}, matched repeats {len(r['paired_repeats'])}."
        )
    lines += [
        "",
        "E4 has too few matched repeats for the planned cache-energy result; "
        "several cells have none and singleton intervals are unavailable. Cache "
        "preparation/priming is outside measured requests. One extra setup-only "
        "interrupted intent is not a completed measured generation. E3 and U1-U5 "
        "were not conducted. There is no end-to-end MemoryGraph intervention "
        "evidence, no semantic summarization arm, and no recognition/know-do test.",
        "",
        "## Reviewer disposition",
        "",
        "The useful report is a controlled, narrow behavioral measurement study "
        "with an explicit cost trade-off and alternative-consistent error analysis. "
        "It does not establish internal memory capacity, human-like forgetting, "
        "intentional giving up, a universal optimal memory policy, or MemoryGraph "
        "effectiveness. No model training, feature selection or learned predictor "
        "was needed for these comparisons.",
        "",
        "Before manuscript drafting: owner review of candidate observations; "
        "verify literature/novelty; semantic annotation of ambiguous preferences "
        "if claimed; report all design revisions and stopping history; resolve "
        "author/affiliation/contribution statements. No new run is necessary to "
        "satisfy R1 Priority A's already-existing control. MemoryGraph details "
        "are needed only for a future frozen intervention study.",
        "",
        "## Evidence checks and what remains unavailable",
        "",
        "schedule-audit.json compares every saved job's frozen fields, not only row "
        "counts; input-manifest.json seals original journals/configurations/registrations "
        "and sensor mirrors. Logical-call attempts in condition tables exclude retry "
        "multiplicity; inventory.json separately lists started attempts and saved HTTP "
        "responses. All raw retry evidence is retained. An immutable local Git manifest "
        "supports provenance but is not an independently timestamped public registration.",
        "",
        "This audit has not supplied calibrated sensor error, independent bundle "
        "replication, human preference annotations, external benchmark validation, "
        "or a peer-reviewed novelty judgment. Raw results/sensor files are locally "
        "git-ignored; a reproducible public release still needs an accessible data "
        "archive and licence/privacy review. Citation verification and manuscript/figures "
        "are later phases, pending owner interpretation review.",
        "",
    ]
    (d / "REVIEWER_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    tables = [
        "# Per-condition audit table",
        "",
        "Attempt-weighted rates use valid-input "
        "correctness denominators; API/infrastructure failures remain separate. "
        "Caps are bounded-endpoint nonpasses. Full CIs, all timing fields and "
        "numerators/denominators are in conditions.json/csv. M1 correctness here "
        "is the focal target; whole-bundle/per-function endpoints are separate.",
        "",
        "Energy tool/mode: " + ENERGY_MODE + ".",
        "",
        "|Stage/model|Condition|Attempts|Correct/usable|Pass %|95% task CI %|Caps|"
        "Energy n|Mean input/output tokens|Gross/net Wh total|Net Wh/correct|",
        "|---|---|---:|---|---:|---|---:|---:|---|---|---:|",
    ]
    for r in condition_rows:
        tables.append(
            f"|{r['stage']}/{r['model']}|{r['condition']}|{r['attempts']}|"
            f"{r['successes']}/{r['usable_correctness']}|"
            f"{fmt(r['pass_rate_attempt_weighted'], 100)}|"
            f"{ci(r['task_weighted_pass']['ci95'], 100)}|{r['caps']}|"
            f"{r['energy_available']}|{fmt(r['prompt_tokens']['estimate'])}/"
            f"{fmt(r['output_tokens']['estimate'])}|"
            f"{fmt(r['gross_wh']['sum_available'])}/{fmt(r['net_wh']['sum_available'])}|"
            f"{fmt(r['net_wh_per_correct_covered']['estimate'])}|"
        )
    (d / "CONDITION_TABLES.md").write_text("\n".join(tables) + "\n", encoding="utf-8")
