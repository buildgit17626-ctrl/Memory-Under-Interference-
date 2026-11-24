# Memory Under Interference: authorized audit, Phases1-4

Owner requested a final empirical/statistical audit on2026-11-24. Generation
remains paused; E3/unrun U studies and MemoryGraph are outside this execution.
No manuscript/submission or new inference is authorized by this audit. The
owner explicitly requests assistance with analysis, superseding the default
working agreement that the owner writes analysis himself for this scope.

## Evidence and output isolation

Code: analysis/memory_audit/{design,records,statistics,effects,mechanisms,
sensors,robustness,examples,provenance,environment,supplement,report,review,seal,run}.py
and tests/test_memory_audit.py. All outputs go into
artifacts/memory-audit/2026-11-24-v1; raw journals, existing scores, registered
protocols and frozen harness modules stay byte-for-byte unchanged. Inventory
all listed main/pilot stages, raw responses/attempts/blocks/sensor mirrors,
validation and analysis inputs. Hash input files and recorded sensor prefixes;
verify committed manifests. Persist audit execution metadata and commands.

Normalize one row per logical call; per-function M1 rows are separate. Recompute
extraction/native fields and score-to-source links without main-process code
execution. Fail closed on duplicate/foreign keys and flag mismatches, missing
records and unfinished attempts rather than guessing. Existing scalar status
is not sufficient when partition infrastructure errors exist. Preserve caps
as bounded-endpoint nonpasses; API/input/infrastructure failures are missing
for valid-input correctness and separately included in operational yield.

## Statistical scope fixed before this audit's condition effects

Use registered2000 task bootstrap draws/seed1732/95% percentile limits. Keep
all repeated seed outcomes within a task and both contrast arms together.
Report attempt, usable/censored/invalid/infrastructure counts, successes,
pass fractions, operational yield, native tokens/timings, covered energy and
ratio denominators. Missing values are never zeros. Energy per correct uses
the same covered attempts in numerator/denominator; zero successes undefined.
Report zero-correct bootstrap draws and unbounded interval endpoints rather
than dropping them. Bootstrap intervals describe task/repeat variation, not
calibrated sensor accuracy. No causal or internal-cognition claims.

Registered contrast reproduction families:
- E0 P3_1-P1, triplet mean per task, exact triplet swaps, Holm2.
- Initial M3 near_duplicate-irrelevant averaged lengths, Holm2; six
  loaded-isolation cell comparisons/model are secondary family12.
- M1 passive-isolation and active-passive at K2/3/4/6/model: exploratory
  as registered, family16. Passive-token-matched-filler is additional posthoc
  family8. Function and whole-bundle versus matched component-isolation
  references are new separate posthoc families; never compare target-only
  passive success with whole-bundle active success as if identical outcomes.
- R1 replay/oracle/compaction-full per model, Holm6; remaining pairwise policy
  comparisons separate posthoc family14. No-history preference confounding
  and absence of natural exact token matches must be reported.
- Revised M3/R2 near-irrelevant averaged length/position, Holm2; individual
  cells, related effects and isolation comparisons secondary/posthoc.
- M2 similar/other_one/other_three-neutral per model, Holm6; other pairs
  posthoc. Complete input counts must match for loaded comparisons.
- E5 buried-immediate and replayed-buried primary adherence, Holm4;
  correctness and correction/control comparisons secondary, separate families.
- E4 partial: cold/warm paired by model,prefix,repeat; repeat-bootstrap only,
  no task-CI label or completed-study significance claim. Report unmatched
  cells and incomplete target400; old and revised pilot/full never pool.

For singleton binary task outcomes use exact discordant-pair binomial McNemar.
For task means of repeated cells use exact paired sign swaps of rational
pass-count differences. Every test states its exchangeability assumption.
Transitions retain IDs: binary pass/fail and, separately, seed/cell transitions
for repeated outcomes; aggregate rate changes are not binary transitions.
Metric CIs preserve paired matched units and report metric-specific denominators.

M1 dependency audit builds bundle-membership components. Task-anchor bootstrap
is conditional on the fixed companion design; it does not estimate uncertainty
from choosing other companions. If bundles form one connected component, a
dependence-robust component-bootstrap CI/test is unavailable, not manufactured.
Report this beside all conditional M1 intervals/tests. Additional active
comparisons use per-function fraction and all-functions success against the
same functions' existing isolation outcomes; source reuse is explicit.

## Mechanisms and scoring sensitivities

Cross-score saved revised M3/R2 outputs on corresponding modified suites,
including isolation, irrelevant and related controls. Use the unchanged
restricted evaluator, timeout and pinned references; save keyed resumable
new audit scores. Count target-only/distractor-only/both/neither, keeping
invalid/capped observations distinct. Compare distractor-only indicators
against isolation and length/position-matched irrelevant controls; paired
task intervals, explicitly posthoc families. Review deterministic representative
code/witness examples; avoid selecting only attractive successes.

M1 outputs: per-function versus whole-bundle endpoints, component-isolation
references, input/output work and overlapping bundles. R1 audit all literal
inputs/instructions; exact equivalence check for proposed target+preference+
query against existing oracle_selective, no new calls. E5 preserve original
adherence; secondary mechanical audits count fences, outside-fence text,
comments/docstrings and joint correctness. Fence-tolerant syntax and stricter
comment/docstring-free proxies are posthoc, not semantic human judgments.

Extraction sensitivity: compare stored extraction to frozen extractor; audit
all parseable complete Python fence blocks and versioned merged-block candidate.
Only differing candidates are re-scored in the restricted evaluator, including
cases originally passing. Original extraction/scoring never replaced. For
caps, report exclude-cap complete-pair sensitivity and optimistic all-cap-pass
bound (a bound, not observed successes); optionally score the original retained
capped extraction in a separate audit journal. Infrastructure errors remain
missing rather than model failures.

## Energy/sampling robustness

Verify raw sensor-prefix SHA256 and recompute trapezoidal integrations from
read-only mirrors where available. Keep original signed gross/start-net.
Join start/end baseline and drift by block; derive end/midpoint subtraction,
exclude-drift blocks, low-resolution exclusion and their intersection as posthoc
sensitivities. Report differing retained populations; a partial sum is not a
complete condition estimate. Report sensor sampling/coverage and integration
agreement, observed baseline uncertainty and negative estimates; no invented
calibration/error bars. Also examine total versus approximate post-load windows.

Correctness sensitivities: exclude HumanEval/32 without changing its oracle;
use independently held-out E0 P1 sample0 eligibility subsets for revised40-task
studies, retaining all-task primary; report original M3 selected population
separately. These labels are noisy and partly decoding-mismatched. Never use
the eligibility sample itself as the isolated outcome. Code-policy failures
remain distinct from wrong logic. All secondary labels are explicit.

## Deliverables, verification and interpretation gate

Inventory/input hashes, integrity issues, condition tables, paired effects/
transition IDs, primary/secondary family corrections, cross-pass tables/new
scores, prompt/adherence/extraction audits, bundle dependency report, energy
sensitivities and an evidence-linked Phases1-4 report. Findings are provisional
until owner interpretation review. Report all null/opposite results. Every
table includes generating script/source IDs and energy tool/mode where relevant.
Tests exercise clustering, transitions, ratio edge cases, Holm, integration,
missingness/caps, no-pooling and evaluator isolation. Full pytest and Ruff clean.

Posthoc audit supplements, explicitly labeled after initial effect inspection:
paired energy-ratio drift/short/cap exclusions; missing filler-isolation and
neutral-isolation controls; E5 no-preference and joint proxy comparisons;
recorded host/process CPU-counter diagnostics. These are not new hypotheses
or model calls. Endpoint process counters do not identify per-call energy use.

Assumptions: requested posthoc audit authorizes these diagnostic estimands and
separate sandbox evaluations, not new inference or changes to registered
primary scoring. Unknown/inestimable uncertainty is reported. No hypotheses,
data, citations, affiliations or author contributions are invented.
