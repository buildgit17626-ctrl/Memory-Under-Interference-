# Version 1 findings

Release candidate: author interpretation/publication approval pending. This document freezes evidence-supported wording, not approval of an internal mechanism or a peer-reviewed claim.

Main-study logical requests verified directly from calls.jsonl: **5,528**. Pilots remain separate; E4 full is partial (76/400), E3/U-family/MG1 unrun.

## A. Alternative-consistent failures (posthoc)

|Model|Variant|Tasks|Competing minus irrelevant pp|95% task CI pp|Holm4 p|
|---|---|---:|---:|---|---:|
|qwen2.5-coder:0.5b|complete_case|40|3.125|[-3.125, 11.25]|1|
|qwen2.5-coder:1.5b|complete_case|39|8.974|[3.205, 16.67]|0.03125|
|qwen2.5-coder:0.5b|unknown_lower_bound|40|3.125|[-3.125, 11.25]|1|
|qwen2.5-coder:1.5b|unknown_lower_bound|40|6.875|[-0.01562, 15]|0.53125|
|qwen2.5-coder:0.5b|unknown_upper_bound|40|3.125|[-3.125, 11.25]|1|
|qwen2.5-coder:1.5b|unknown_upper_bound|40|10.62|[3.75, 18.75]|0.015625|

Complete-case evidence on 1.5B is suggestive and cap-sensitive. The adverse assignment loses corrected support; it is a missing-outcome scenario, not an observed repair. 0.5B is inconclusive. Isolation is also cross-scored to distinguish pre-existing alternative behavior. No cognition/intent claim. Sources: tables/cross-specification-sensitivities.json, data/audit/cross-pass-per-response.csv; generators: code/analysis/memory_release/analytics.py and code/analysis/memory_audit/mechanisms.py.

## B. Task-description content (exploratory)

|Model|Passive minus matched filler|Tasks|Difference pp|Conditional CI pp|Holm8 p|
|---|---|---:|---:|---|---:|
|qwen2.5-coder:0.5b|passive/K2 minus filler/K2|40|-12.5|[-27.5, 2.5]|0.45312|
|qwen2.5-coder:1.5b|passive/K2 minus filler/K2|40|-10|[-25, 2.5]|0.45312|
|qwen2.5-coder:0.5b|passive/K3 minus filler/K3|40|-22.5|[-37.5, -7.5]|0.082031|
|qwen2.5-coder:1.5b|passive/K3 minus filler/K3|40|-20|[-35, -5]|0.12891|
|qwen2.5-coder:0.5b|passive/K4 minus filler/K4|40|-22.5|[-40.06, -2.5]|0.19617|
|qwen2.5-coder:1.5b|passive/K4 minus filler/K4|40|-20|[-35, -7.5]|0.12891|
|qwen2.5-coder:0.5b|passive/K6 minus filler/K6|40|-25|[-37.5, -12.5]|0.015625|
|qwen2.5-coder:1.5b|passive/K6 minus filler/K6|40|-15|[-27.5, -2.5]|0.21094|

The contrasts are conditional on fixed companions. All bundle-membership graphs have one connected component; robust independent-component CIs are unavailable. Active mode requests more output and has different budgets. No universal multitasking penalty or causal internal mechanism is established. Sources: data/audit/paired-effects.json, m1-bundle-dependencies.json, m1-work-and-function-cost.json; generators: effects.py, mechanisms.py, robustness.py.

## C. Retention and cost (descriptive/posthoc energy)

|Model|Full-history net mWh/correct|Oracle net mWh/correct|Paired difference mWh|95% CI mWh|
|---|---:|---:|---:|---|
|qwen2.5-coder:0.5b|325.384|76.387|-248.997|[-529.6, -127.5]|
|qwen2.5-coder:1.5b|154.159|50.204|-103.955|[-152.3, -77.58]|

Energy: HWiNFO CPU Package Power, trapezoidal approximate post-load integration, block-start idle subtraction. All 40 R1 calls per policy/model have readings. Correctness gains/equivalence are not established. Input length, position, instructions, output length, caps and privileged relevance knowledge are confounded. No retrieval overhead is measured. End/midpoint/drift/cap/short sensitivities remain separate; E4 primary energy evidence is incomplete. Sources: data/audit/conditions.json, energy-per-correct-differences.json, energy-sensitivities.json; generators statistics.py, effects.py, robustness.py.

## D. Preference metric and null/contradictory results

Original strict E5 adherence is **0/400**. It requires unfenced parseable code; the instruction did not explicitly ban Markdown fences. Secondary fence/comment/docstring audits preserve the original scores. Code comments/docstrings are not automatically explanations. No retention claim follows from the floor. Registered R1 replay/correctness comparisons and M2 comparisons are inconclusive after their family corrections; absence of rejection is not equivalence. Sources: data/audit/e5-joint-outcomes.csv, e5-joint-intervals.json, paired-effects.json; generators: mechanisms.py, supplement.py, effects.py.

## E. Companion prototype, not an evaluated intervention

Pinned MemoryGraph c569143ec6be1c767a2c56c59c936f85bd1fc1cb: 600 labelled pairs, 24 fictional profiles, 120 queries. Saved-score MRR reproduces: embeddings 0.736389, TF-IDF 0.516250. No new embeddings or model requests. Synthetic templates, globally fitted lexical benchmark vocabulary, and the different per-query interface vocabulary limit generality. The recorded pytest preference demonstration emits unittest; both successful generations are capped. Correctness/energy were unscored. Source: companion/*.csv/json/jsonl and tables/memorygraph-audit.json; generator: companion.py.

## What would change interpretation?

Alternative/oracle/extraction mistakes; cap assumptions; independent bundle replication; human semantic adherence annotations; different task populations; validated energy calibration and end-to-end retrieval overhead. Current findings do not measure internal memory, recognition, giving up or learned representations.
