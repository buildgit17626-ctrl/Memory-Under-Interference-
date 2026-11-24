# Skeptical scientific review — 24 November 2026

Provisional interpretation for owner review; no manuscript claims are approved. This is a posthoc audit of existing data. Reproducing a registered contrast does not make additional analyses preregistered. No new model inference occurred.

## What would change these interpretations?

A scoring/reference discrepancy, a different defensible adherence definition, paired cap exclusions, selected-population changes, dependence-aware replication, or energy rankings that reverse under baseline/coverage sensitivities would change the interpretations. Evidence from other models/hardware/tasks could change their generality. Null tests here do not establish equivalence. The intervals are pointwise percentile task bootstrap intervals, not simultaneous family intervals.

## Five candidate observations for discussion

1. **Semantic alternatives are associated with a different failure mix.** The following new posthoc contrasts concern distractor-only success, not overall target accuracy. Complete-cell matching excludes censored/missing pairs; no internal mechanism or intentional choice is inferred.

|Model|Near minus control|Tasks|Difference pp|95% CI pp|Holm family4 p|
|---|---|---:|---:|---|---:|
|qwen2.5-coder:0.5b|near-minus-isolation|40|1.25|[-5, 8.75]|1|
|qwen2.5-coder:0.5b|near-minus-irrelevant|40|3.125|[-3.125, 11.25]|1|
|qwen2.5-coder:1.5b|near-minus-isolation|39|9.615|[3.205, 17.95]|0.03125|
|qwen2.5-coder:1.5b|near-minus-irrelevant|39|8.974|[3.205, 16.67]|0.03125|

By comparison, registered revised M3/R2 target-correctness contrasts:

- qwen2.5-coder:0.5b: n=40; -11.25 pp, CI [-20.62, -2.5], Holm p=0.0564.
- qwen2.5-coder:1.5b: n=40; -2.5 pp, CI [-10, 4.391], Holm p=0.6353.

A pointwise interval can exclude zero while a multiplicity-adjusted test does not reject. Report both. Do not select whichever yields a stronger claim.

2. **R1 supplies an efficiency comparison, without an established accuracy advantage.** The reduced oracle policy is privileged, omits distractors and changes length/position; it is not an automated retriever. The following energy-per-correct differences are posthoc ratio contrasts, oracle minus full history, over identical covered task sets.

|Model|Tasks|Net Wh/correct difference|95% CI|
|---|---:|---:|---|
|qwen2.5-coder:0.5b|40|-0.249|[-0.5296, -0.1275]|
|qwen2.5-coder:1.5b|40|-0.104|[-0.1523, -0.07758]|

R1 registered correctness effects (pp):

- qwen2.5-coder:0.5b, lossless_compaction minus full_history: 5, CI [-7.5, 17.5], Holm p=1.
- qwen2.5-coder:1.5b, lossless_compaction minus full_history: 0, CI [-15, 15], Holm p=1.
- qwen2.5-coder:0.5b, oracle_selective minus full_history: 7.5, CI [-5, 22.5], Holm p=1.
- qwen2.5-coder:1.5b, oracle_selective minus full_history: 2.5, CI [-10, 15], Holm p=1.
- qwen2.5-coder:0.5b, verbatim_replay minus full_history: 2.5, CI [-7.5, 12.5], Holm p=1.
- qwen2.5-coder:1.5b, verbatim_replay minus full_history: 2.5, CI [-5, 10], Holm p=1.

Exact rendered target+preference+query equivalence: 80/400 R1 calls, all in policies ['oracle_selective']. Priority A's proposed control therefore already exists for both models. The no_history policy omits the explicit code-only preference; it is not that matched control. Formatting compaction preserves the target wording and drops other history; it is not semantic summarization.

3. **Task load and additional output work must be separated.** Passive versus token-matched filler measures target correctness under extra task descriptions. Active generation additionally requests K functions. Every M1 bundle graph has one connected membership component; the following anchor-task intervals/tests are conditional and cannot supply dependence-robust population inference.

|Model|Passive minus filler|Tasks|Difference pp|Conditional CI pp|Holm8 p|
|---|---|---:|---:|---|---:|
|qwen2.5-coder:0.5b|passive/K2 minus filler/K2|40|-12.5|[-27.5, 2.5]|0.4531|
|qwen2.5-coder:1.5b|passive/K2 minus filler/K2|40|-10|[-25, 2.5]|0.4531|
|qwen2.5-coder:0.5b|passive/K3 minus filler/K3|40|-22.5|[-37.5, -7.5]|0.08203|
|qwen2.5-coder:1.5b|passive/K3 minus filler/K3|40|-20|[-35, -5]|0.1289|
|qwen2.5-coder:0.5b|passive/K4 minus filler/K4|40|-22.5|[-40.06, -2.5]|0.1962|
|qwen2.5-coder:1.5b|passive/K4 minus filler/K4|40|-20|[-35, -7.5]|0.1289|
|qwen2.5-coder:0.5b|passive/K6 minus filler/K6|40|-25|[-37.5, -12.5]|0.01562|
|qwen2.5-coder:1.5b|passive/K6 minus filler/K6|40|-15|[-27.5, -2.5]|0.2109|

Active per-function and whole-bundle differences against the same component isolation references:

|Model|Bundle|Function-fraction pp|Conditional CI pp|Whole-bundle pp|Components|
|---|---|---:|---|---:|---:|
|qwen2.5-coder:0.5b|active/K2|-17.5|[-26.25, -8.75]|-5|1|
|qwen2.5-coder:0.5b|active/K3|-28.33|[-35.83, -20.83]|0|1|
|qwen2.5-coder:0.5b|active/K4|-33.12|[-40, -26.23]|0|1|
|qwen2.5-coder:0.5b|active/K6|-34.58|[-40, -29.17]|0|1|
|qwen2.5-coder:1.5b|active/K2|-18.75|[-30, -8.75]|-22.5|1|
|qwen2.5-coder:1.5b|active/K3|-25.83|[-35.85, -15.83]|-25|1|
|qwen2.5-coder:1.5b|active/K4|-33.12|[-42.5, -23.75]|-20|1|
|qwen2.5-coder:1.5b|active/K6|-37.08|[-45.42, -28.74]|-7.5|1|

The apparent K trend also changes bundle composition; do not treat K as a clean dose-response. Component isolation costs are reused lookup sums, not physical repeated baseline runs. See m1-work-and-function-cost.json.

4. **E5's registered strict metric is at its floor.**

Original adherence: 0/400 responses. This rule requires unfenced parseable Python, although the wording asked for code only rather than explicitly forbidding fences. It cannot by itself distinguish retention conditions in this sample.

|Model|Condition|Attempts|Strict|Fence-tolerant|Correct and strict|Correct and fence-tolerant|Comments present|Docstrings present|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|qwen2.5-coder:0.5b|buried|40|0|37|0|14|16|39|
|qwen2.5-coder:0.5b|corrected|40|0|36|0|14|15|38|
|qwen2.5-coder:0.5b|immediate|40|0|36|0|11|7|37|
|qwen2.5-coder:0.5b|no_preference|40|0|15|0|5|24|37|
|qwen2.5-coder:0.5b|replayed|40|0|39|0|13|11|40|
|qwen2.5-coder:1.5b|buried|40|0|40|0|21|1|0|
|qwen2.5-coder:1.5b|corrected|40|0|40|0|22|4|5|
|qwen2.5-coder:1.5b|immediate|40|0|40|0|23|1|2|
|qwen2.5-coder:1.5b|no_preference|40|0|21|0|15|13|23|
|qwen2.5-coder:1.5b|replayed|40|0|40|0|23|1|1|

Fence-tolerant and comment/docstring-free scores are posthoc mechanical proxies. Comments/docstrings may be code or explanations; human semantic annotation is not supplied by a syntax test. A degenerate all-zero/all-one bootstrap interval is an empirical-resample property, not certainty of the population rate. Secondary buried/replay contrasts also do not establish an adherence benefit (scoring-sensitivity-effects.json).

5. **Effects do not repeat uniformly across models and designs.** E0 and M2 primary contrasts do not establish an ordering after their family corrections; intervals permit meaningful differences. Initial M3 uses different selected populations and a weaker near-duplicate construction, so it cannot be pooled with revised semantic M3/R2.

- E0/qwen2.5-coder:0.5b, P3_1 minus P1: n=163, -2.249 pp, CI [-7.771, 2.863], Holm p=0.447.
- E0/qwen2.5-coder:1.5b, P3_1 minus P1: n=164, 2.642 pp, CI [-1.22, 6.301], Holm p=0.4416.
- M3_initial/qwen2.5-coder:0.5b, near-minus-irrelevant averaged length: n=20, -27.5 pp, CI [-45, -10], Holm p=0.03369.
- M3_initial/qwen2.5-coder:1.5b, near-minus-irrelevant averaged length: n=20, -2.5 pp, CI [-17.5, 12.5], Holm p=1.
- M2/qwen2.5-coder:0.5b, similar minus neutral: n=40, -12.5 pp, CI [-25.06, 0.0625], Holm p=0.8984.
- M2/qwen2.5-coder:1.5b, similar minus neutral: n=40, -2.5 pp, CI [-12.5, 7.5], Holm p=1.
- M2/qwen2.5-coder:0.5b, other_one minus neutral: n=40, -7.5 pp, CI [-17.5, 0], Holm p=1.
- M2/qwen2.5-coder:1.5b, other_one minus neutral: n=40, 2.5 pp, CI [-10, 15], Holm p=1.
- M2/qwen2.5-coder:0.5b, other_three minus neutral: n=40, -5 pp, CI [-17.5, 7.5], Holm p=1.
- M2/qwen2.5-coder:1.5b, other_three minus neutral: n=40, -15 pp, CI [-27.5, -2.5], Holm p=0.4219.

M2 uses fixed description-only conversational transcripts. Complete input counts match across loaded conditions, but these are not tasks actually executed earlier by the model. Similarity and interruption count are not a fully crossed factorial design.

## Energy coverage and sensitivity

Tool/mode: HWiNFO CPU Package Power; trapezoidal; approximate post-load; block-start net. CPU-package estimates exclude wall-plug/system-wide energy. E4 was designated the primary energy evidence and is incomplete; R1 cost comparisons here remain descriptive/posthoc, not a completed confirmatory energy study. Primary totals include failures; coverage and correct-count denominators are attached. End/midpoint baselines and exclusions are posthoc. Short-window exclusion preferentially removes cheap conditions and changes the population.

|Stage|Calls|Energy readings|Low-resolution|Drift-flagged calls|
|---|---:|---:|---:|---:|
|E0|1968|1966|611|249|
|E4_partial|76|76|35|1|
|E5|400|400|0|0|
|M1|1040|1040|55|75|
|M2|400|400|26|25|
|M3R2|1040|1038|22|239|
|M3_initial|240|240|0|25|
|M3_isolated|40|40|17|0|
|R1|400|400|78|50|

R1 sensitivity example (available-covered population, not a pooled or population-matched replacement for primary):

|Model|Policy|Variant|Retained/40|Net Wh/correct|95% CI|
|---|---|---|---:|---:|---|
|qwen2.5-coder:0.5b|full_history|start|40/40|0.3254|[0.1969, 0.6125]|
|qwen2.5-coder:0.5b|full_history|end|40/40|0.3188|[0.1924, 0.6009]|
|qwen2.5-coder:0.5b|full_history|midpoint|40/40|0.3221|[0.1951, 0.6067]|
|qwen2.5-coder:0.5b|full_history|exclude_drift|32/40|0.4429|[0.2357, 1.053]|
|qwen2.5-coder:0.5b|full_history|exclude_short|40/40|0.3254|[0.1969, 0.6125]|
|qwen2.5-coder:0.5b|full_history|exclude_both|32/40|0.4429|[0.2357, 1.053]|
|qwen2.5-coder:0.5b|oracle_selective|start|40/40|0.07639|[0.05284, 0.1217]|
|qwen2.5-coder:0.5b|oracle_selective|end|40/40|0.07464|[0.05162, 0.1198]|
|qwen2.5-coder:0.5b|oracle_selective|midpoint|40/40|0.07551|[0.05224, 0.1206]|
|qwen2.5-coder:0.5b|oracle_selective|exclude_drift|35/40|0.08437|[0.05579, 0.1508]|
|qwen2.5-coder:0.5b|oracle_selective|exclude_short|25/40|0.09632|[0.06373, 0.1762]|
|qwen2.5-coder:0.5b|oracle_selective|exclude_both|22/40|0.1111|[0.06856, 0.2359]|
|qwen2.5-coder:1.5b|full_history|start|40/40|0.1542|[0.1217, 0.2138]|
|qwen2.5-coder:1.5b|full_history|end|40/40|0.1505|[0.1189, 0.2084]|
|qwen2.5-coder:1.5b|full_history|midpoint|40/40|0.1523|[0.1204, 0.2112]|
|qwen2.5-coder:1.5b|full_history|exclude_drift|34/40|0.1481|[0.1125, 0.2094]|
|qwen2.5-coder:1.5b|full_history|exclude_short|40/40|0.1542|[0.1217, 0.2138]|
|qwen2.5-coder:1.5b|full_history|exclude_both|34/40|0.1481|[0.1125, 0.2094]|
|qwen2.5-coder:1.5b|oracle_selective|start|40/40|0.0502|[0.03819, 0.07164]|
|qwen2.5-coder:1.5b|oracle_selective|end|40/40|0.04911|[0.03733, 0.06997]|
|qwen2.5-coder:1.5b|oracle_selective|midpoint|40/40|0.04966|[0.03777, 0.07079]|
|qwen2.5-coder:1.5b|oracle_selective|exclude_drift|34/40|0.05406|[0.04075, 0.07633]|
|qwen2.5-coder:1.5b|oracle_selective|exclude_short|18/40|0.06391|[0.04701, 0.09615]|
|qwen2.5-coder:1.5b|oracle_selective|exclude_both|17/40|0.05999|[0.04396, 0.09087]|

Paired R1 oracle-minus-full ratio sensitivities, each on the same retained tasks in both arms. Exclusions can select a different task population. An unavailable interval means at least one bootstrap draw has zero correct solutions in an arm; it is not replaced by a conditional finite interval.

|Model|Energy definition|Variant|Paired tasks|Wh/correct difference|95% CI|
|---|---|---|---:|---:|---|
|qwen2.5-coder:0.5b|gross_wh|primary|40|-0.3305|[-0.7058, -0.1683]|
|qwen2.5-coder:0.5b|net_wh|primary|40|-0.249|[-0.5296, -0.1275]|
|qwen2.5-coder:0.5b|end_net_wh|primary|40|-0.2441|[-0.5196, -0.1241]|
|qwen2.5-coder:0.5b|midpoint_net_wh|primary|40|-0.2466|[-0.5252, -0.126]|
|qwen2.5-coder:0.5b|net_wh|exclude_caps|35|-0.1127|[-0.2067, -0.06468]|
|qwen2.5-coder:0.5b|net_wh|exclude_drift|28|-0.3171|[-0.902, -0.116]|
|qwen2.5-coder:0.5b|net_wh|exclude_short|25|-0.5038|unavailable|
|qwen2.5-coder:0.5b|net_wh|exclude_both|18|-0.5511|unavailable|
|qwen2.5-coder:1.5b|gross_wh|primary|40|-0.1368|[-0.1996, -0.1029]|
|qwen2.5-coder:1.5b|net_wh|primary|40|-0.104|[-0.1523, -0.07758]|
|qwen2.5-coder:1.5b|end_net_wh|primary|40|-0.1014|[-0.1484, -0.0755]|
|qwen2.5-coder:1.5b|midpoint_net_wh|primary|40|-0.1027|[-0.1503, -0.07654]|
|qwen2.5-coder:1.5b|net_wh|exclude_caps|40|-0.104|[-0.1523, -0.07758]|
|qwen2.5-coder:1.5b|net_wh|exclude_drift|29|-0.102|[-0.1656, -0.07093]|
|qwen2.5-coder:1.5b|net_wh|exclude_short|18|-0.1114|[-0.2084, -0.07478]|
|qwen2.5-coder:1.5b|net_wh|exclude_both|13|-0.1149|[-0.2899, -0.06826]|

Recorded prefix hashes checked: 6763; mismatches 0. Integrated windows recorded: 12006; independently recomputable 12004; disagreements at 1e-8 Wh tolerance 0. Unavailable windows remain missing. Numerical agreement does not calibrate HWiNFO, isolate unrelated CPU work, or validate approximate post-load boundaries.

Recorded host/process checks: environment-block-audit.json preserves AC, power mode, CPU/RAM/library metadata, baseline drift and endpoint CPU-counter deltas. All saved block-start checks observed AC/Best performance. Endpoint snapshots do not establish uninterrupted host state or isolate per-call background CPU energy. Counter resets/PID reuse are flagged. Cache state was not a crossed experimental factor outside E4; native cached-token readings remain in calls.csv and are a limit on interpreting prefill/energy mechanisms.

## Scoring and oracle sensitivities

- alternative_suite: 1029 separate sandbox scores; 0 infrastructure-unavailable.
- cap_salvage_original_extraction: 60 separate sandbox scores; 0 infrastructure-unavailable.
- merged_complete_fences: 1 separate sandbox scores; 0 infrastructure-unavailable.
- Audited extraction/capped target candidates with changed focal correctness: 0/43. This is not a proof that every extraction is optimal or every failing solution is wrong logic.
- HumanEval/32 remains under the original oracle. Its exclusion, caps as missing, optimistic cap bounds and held-out eligibility are tabulated in PHASES_1_4_REPORT.md/paired-effects.json. E0 eligibility sensitivity excludes sample0 from comparison outcomes; the primary retains all registered samples.
- Cap exclusion can reverse small R1 correctness point estimates on 0.5B; the registered effects remain uncertain. The independently selected eligibility subset can increase revised M3/R2's 0.5B effect magnitude. These are changes of target population, not grounds to replace the full-roster primary estimate. Exact effect sizes, retained IDs, intervals and corrected tests are in the sensitivity table, including null/opposite outcomes.
- Representative distractor-only code implements <= rather than < on HumanEval/0 (0.5B), and reversed group order on HumanEval/1 (1.5B). Separate distinguishing witness checks agree with those labels. The six-example deterministic review is not a prevalence estimate. Both-pass has no sampled examples because no such outcomes occurred in near-condition records; it must remain an explicit zero category. See REPRESENTATIVE_CODE_AUDIT.md.

## Partial E4 and excluded claims

- qwen2.5-coder:0.5b, prefix 0: warm 4, cold 4, matched repeats 2.
- qwen2.5-coder:0.5b, prefix 500: warm 2, cold 5, matched repeats 0.
- qwen2.5-coder:0.5b, prefix 1000: warm 5, cold 4, matched repeats 1.
- qwen2.5-coder:0.5b, prefix 2000: warm 4, cold 6, matched repeats 1.
- qwen2.5-coder:0.5b, prefix 4000: warm 6, cold 2, matched repeats 1.
- qwen2.5-coder:1.5b, prefix 0: warm 1, cold 2, matched repeats 0.
- qwen2.5-coder:1.5b, prefix 500: warm 4, cold 2, matched repeats 1.
- qwen2.5-coder:1.5b, prefix 1000: warm 4, cold 3, matched repeats 0.
- qwen2.5-coder:1.5b, prefix 2000: warm 4, cold 2, matched repeats 0.
- qwen2.5-coder:1.5b, prefix 4000: warm 7, cold 5, matched repeats 0.

E4 has too few matched repeats for the planned cache-energy result; several cells have none and singleton intervals are unavailable. Cache preparation/priming is outside measured requests. One extra setup-only interrupted intent is not a completed measured generation. E3 and U1-U5 were not conducted. There is no end-to-end MemoryGraph intervention evidence, no semantic summarization arm, and no recognition/know-do test.

## Reviewer disposition

The useful report is a controlled, narrow behavioral measurement study with an explicit cost trade-off and alternative-consistent error analysis. It does not establish internal memory capacity, human-like forgetting, intentional giving up, a universal optimal memory policy, or MemoryGraph effectiveness. No model training, feature selection or learned predictor was needed for these comparisons.

Before manuscript drafting: owner review of candidate observations; verify literature/novelty; semantic annotation of ambiguous preferences if claimed; report all design revisions and stopping history; resolve author/affiliation/contribution statements. No new run is necessary to satisfy R1 Priority A's already-existing control. MemoryGraph details are needed only for a future frozen intervention study.

## Evidence checks and what remains unavailable

schedule-audit.json compares every saved job's frozen fields, not only row counts; input-manifest.json seals original journals/configurations/registrations and sensor mirrors. Logical-call attempts in condition tables exclude retry multiplicity; inventory.json separately lists started attempts and saved HTTP responses. All raw retry evidence is retained. An immutable local Git manifest supports provenance but is not an independently timestamped public registration.

This audit has not supplied calibrated sensor error, independent bundle replication, human preference annotations, external benchmark validation, or a peer-reviewed novelty judgment. Raw results/sensor files are locally git-ignored; a reproducible public release still needs an accessible data archive and licence/privacy review. Citation verification and manuscript/figures are later phases, pending owner interpretation review.
