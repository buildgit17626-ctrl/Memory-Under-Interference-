# Focused execution and extension registration · 2026-11-16

## Approved scope and order

MAIN Focused has an initial planning budget of 4,808 calls; APPENDIX is deferred.
The budget includes upper allocations for unknown failed-task populations and
must be reconciled with frozen rosters before execution. No unused allocation
is reassigned without approval.

task-orders.json fixes an outcome-independent permutation of all 164 IDs for
each sweep. Each seed is the first eight bytes, big-endian, of SHA-256 of
"1729/EXPERIMENT". Each permutation shuffles numeric ID order with Python's
random.Random. The committed explicit IDs are authoritative.

For M3/R1/R2, filter this order by the frozen, independent per-model calibration
eligibility mask. Focused takes the first 20 eligible IDs and the extension adds
IDs 21–40. Both sets use the identical eligibility mask and condition grid.
Fewer than 20/40 eligible tasks produces a reported shortfall, never a
replacement based on scored outcomes. Fix the masks before scored sweeps.
Cross-model comparisons must distinguish shared-task and per-model populations.

This owner amendment extends task count only. The earlier Balanced timing
scenario also expanded factors. Its 9,048-call estimate does not describe this
extension. Each task-only extension adds the same number of sweep calls as
the initial 20 tasks: M3 +240, R1 +120, R2 +120, assuming the Focused grids
previously budgeted (six/three/three cells per task per model). Exact stimuli,
cells, eligibility and primary contrasts still need freezing before each sweep.

## Extension decision after Focused M3, R1 and R2

Evaluate all three sweeps together after their initial batches and scoring
finish. Extension is to 40 tasks for each eligible model using the fixed prefix.
There is one extension decision, with no later repeated precision checks.

Timing route: use the measured arithmetic mean wall seconds plus observed
inter-request gap and sensor-processing overhead, by sweep and model. Multiply
by that stratum's added requests and include starting/ending baselines, expected
block overhead and measured scoring requirements. Compare total additional
machine time with the owner's remaining time after reserving already planned
unfinished Focused work. The freeze is 2026-11-22 23:59 IST (18:29 UTC). Require the
projected time for ALL pending work plus the extension to be at most 70% of
the wall-clock hours remaining to the freeze. Include measured overhead and
pending independent calibration and evaluation. Missing overhead estimates
leave this route pending. Request no effect estimates or p-values for the timing decision.

Precision route (width threshold approved by owner on 2026-11-17): extend when either
model's primary 95% paired task-bootstrap interval has full width >0.20.
Use 2000 task resamples, seed 1732 and percentile limits. Proposed primary
contrasts are near-duplicate versus irrelevant filler in M3, averaged within
task over the frozen shared grid; strongest verbatim replay versus no replay
in R1; and near-duplicate versus unrelated distractors at matched count in R2.
These proposed contrasts and their exact cell mapping require owner review before the
affected sweep. Failure to define a primary contrast leaves the precision
route unavailable.

The 70% time rule is a hard gate for every extension, including precision-driven
extensions. Within that gate, use timing or precision as the reason to extend; report all widths, timing inputs, task counts,
deadline and decision in CHANGELOG.md. Never use effect direction, p-value,
significance, desired narrative or promising task outcomes. A precision-based
sample-size decision can affect nominal interval coverage: label it as
precision-adaptive, retain the Focused results, and disclose the stopping rule.
Final expanded intervals are descriptive percentile intervals; they do not
acquire a sequential-coverage guarantee from this rule.

## Energy registration

The pilot had 9/22 low-resolution post-load windows (40.9%, rounded 41%).
Primary energy comparisons aggregate gross and start-baseline-adjusted
post-load CPU-package Wh within each condition and model. Include failed
attempts. Report eligible count, finite-energy count, valid covered duration,
and net and gross totals. A partially covered total is labelled partial and
is unavailable as a complete condition-cost estimate. Do not impute gaps.

For energy per correct, use the identical retained-attempt population in both
numerator and success denominator and disclose excluded attempts. Undefined
ratios remain undefined when no attempts pass. Report task count and success
rate beside costs. Compare equal task populations for paired arm comparisons.
For the low-resolution sensitivity, remove post_load:low_resolution rows,
recompute totals and denominators, and show differing retained task sets.
This filter preferentially removes short calls and can alter arm composition.
Aggregation does not eliminate coarse sampling, baseline bias or sensor gaps.

Individual short-call energy is secondary. E4 is designated primary evidence
for controlled energy investigation and is deferred with APPENDIX. While E4
is deferred, report condition totals as supporting estimates and defer the
study's primary E4 energy claim. API prefill/decode durations can be reported;
no phase-specific electrical energy is attributed.

## First 100 M3 calls

At 100 completed logical M3 calls, stop launching further requests, finish the
end baseline and write a checkpoint containing observed mean wall seconds and
remaining-time forecast by model. Count invalid calls as completed for this
workload checkpoint, while listing their flags. Report to owner before resume.
Require an explicit review receipt tied to the schedule hash. This checkpoint
uses elapsed measurements and scheduled remaining calls, never correctness.
