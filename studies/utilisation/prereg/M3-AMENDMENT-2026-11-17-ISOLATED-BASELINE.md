# M3 amendment draft Â· isolated temperature-zero baseline

Dated 2026-11-17T21:21:35+05:30

Status: draft for owner review. This document adds no calls to the current
supervisor. Existing frozen configuration, stimuli, registrations, source,
logs and hash manifest are untouched. Activation requires a separately
versioned registration and execution plan after the owner reviews this draft.

## Reason and existing comparator

The 2026-11-17 M3 registration specifies E0 P1 samples 1 and 2 as the
isolated generation comparator for analyses using eligibility/difficulty
labels. Sample index 0 defines those labels and must never supply the
isolated outcome in the loaded-versus-isolated difference.

That comparator has temperature 0.2, whereas the M3 grid has temperature zero.
Consequently it cannot give a decoding-matched isolated baseline. The running
pipeline produces held-out E0 label/comparator records but does not implement
a final M3 loaded-versus-isolated analysis. No such comparison has been
computed. The proposed extra calls below supply the matched comparator.

## Exact implemented eligible-task rule

For each model separately, use the E0 P1 sample_idx=0 request (seed 1729).
A task's solvable label is true exactly when that response has valid input,
a usable evaluation outcome and passes both the base and plus partitions under
the registered evaluator. The original oracle and tolerance apply, including
HumanEval/32 in the primary population.

In the current label-export implementation, P1 samples 1 and 2 must also have
usable scored outcomes for a label record to be emitted. Their correctness
does not affect the solvable label. Report absent records and why they are
absent; this completeness gate must be acknowledged in the population count.

Read the committed M3 permutation in task-orders.json, filter it by true
per-model solvable labels, then take the first 20 task IDs. The running
supervisor halts if fewer than 20 are available. Freeze those selected IDs
before any additional baseline outcome is inspected. A new baseline failure
does not remove a task or change its eligibility. No replacement uses M3 or
new baseline correctness.

## Proposed additional condition

For each of those 20 selected tasks on each model, generate exactly one fresh
no-filler response. This adds 20 Ã— 2 = 40 logical calls. Use a new condition
ID, isolated_no_filler, and new request keys in a separately frozen manifest.
Do not copy an E0 response or its score into this condition.

Use the same M3 target wrapper and final instruction. Construct the user
prompt by omitting the left and right filler strings entirely:

    [TARGET TASK: complete only {entry_point}]
    {benchmark_task_prompt}
    [END TARGET]

    Return only the Python code defining {entry_point}.

Preserve the actual wrapper newlines from the frozen M3 builder. Use the same
system text and Ollama chat template. The isolated prompt is shorter by
design: no padding is added to make its token count equal 1000 or 4000.
Independently count its complete rendered input and record the actual count.

Use the same model digests, Q4_K_M quantisation, num_ctx=8192,
temperature=0, seed=1729, num_predict=2048, eight threads, num_gpu=0,
keep_alive=0, 900-second HTTP deadline, five-second gaps, extraction rule
and sandbox/scoring settings as the loaded M3 grid.

Randomise the 40 baseline calls across models/tasks with random.Random(1730)
over a canonical model/task ordering, then freeze the explicit order.
Record per-call latency, tokens, API durations and HWiNFO windows with all
existing sensor and power guards. No setting change follows the outcomes.

## Timing and outcome-access restriction

Run these calls only AFTER the existing 100-call M3 timing checkpoint and
BEFORE anyone or any analysis reads M3 correctness outcomes. Timing, counts,
input validity, censoring and energy-coverage checks may be inspected at the
checkpoint. Keep M3 correctness evaluation deferred until the added baseline
calls finish. Do not claim outcomes were unseen if they were accessed.

The current supervisor automatically scores the first 100 M3 calls before
writing its checkpoint. That sequence does not enforce this new restriction.
A later approved execution amendment must defer that scoring step. This draft
does not edit the running supervisor. At drafting time there are 100 E0 calls,
zero E0 scores, zero M3 calls and zero M3 scores; the existing supervisor has
halted on baseline drift. No M3 outcome was inspected for this amendment.

The first 100 loaded calls therefore precede the new baseline in time.
Record batch IDs, baseline drift and execution timestamps. This chronology
can confound loaded-versus-isolated energy or latency differences and remains
a limitation even though outcome access is withheld.

## Estimand and analysis

For each model and each of the six loaded M3 cells, estimate

    drop = mean(isolated_no_filler pass - loaded_cell pass)

on paired eligible task IDs. Positive values indicate lower measured loaded
success. Each isolated response is reused as the comparator across its six
loaded conditions; those six comparisons are correlated. Resample tasks with
all their matched loaded and isolated outcomes retained, using seed 1732,
2000 resamples and 95% percentile limits. Print per-cell paired counts,
discordant IDs, successes, missing/censored counts and intervals.

This is the operationalisation of the owner's existing loaded-versus-isolated
question, not an additional hypothesis. The existing primary near-duplicate
versus irrelevant contrast remains the primary M3 contrast. Treat this added
isolated comparison as secondary and label the amendment date and timing.
Do not select contrasts based on their direction or significance.

Use a complete-case paired denominator for each cell. Invalid/missing
baseline observations are reported as missing and do not trigger task
replacement. Valid-input output-cap events and test failures are non-passes
under the registered constrained-generation endpoint and are labelled
separately. Retry only infrastructure failures within the existing attempt
policy; preserve all attempts.

Report the original E0 P1 sample-1/2 comparator, if shown, as a secondary
temperature-0.2 comparison. Never use P1 sample 0 as its outcome. The new
temperature-zero condition is the decoding-matched comparator. Keep the
HumanEval/32 sensitivity distinct from the primary retained-task result.

Aggregate energy by condition/model over documented matched populations,
report gross/net and partial coverage, and retain the registered
low-resolution sensitivity. The extra baseline does not resolve the
coarse-sampling issue or turn E4's deferred primary-energy evidence into a
completed result.

## Budget, extension and limits

The Focused planning budget increases from 4808 to 4848 if all 40 calls are
run. Exactly one isolated response per eligible task/model is required, not
one per loaded cell. If extending M3 to 40 tasks per model, add one baseline
for each newly eligible task as well: 40 more baseline calls.

Include all new baseline, scoring, gap and block costs in the owner's 70%
remaining-time test before 2026-11-22 23:59 IST. No extension or later scored
batch is authorised merely by committing this draft.

Inference is restricted to the selected, single-sample-solvable task
population, two model variants, one benchmark and this machine. A fresh
baseline can fail even when eligibility passed. One response per cell has
generation variability; repeated task pairing does not remove that uncertainty.
