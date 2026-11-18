# Drift quality-flag amendment — 2026-11-18

Owner approval: “Approve drift as a flag”, recorded 2026-11-18T07:08:41+05:30
(recording time, not a claimed timestamp of the approval message).

## Files and design
Change utilisation_supervisor.py, tests, SPEC, the supervisor guide and the
review record; refresh the committed execution hash manifest. After a completed
block, baseline drift is logged as a quality flag instead of a reason to halt.
The next block still needs fresh accepted idle baselines. No generation during
this implementation; recovery remains the owner's manual action.

## Registered amendment
This supersedes only the baseline-drift hard stop in the terminal supervisor
and the 2026-11-17 measurement-reliability amendment. The threshold remains
abs(end-start) > max(1 W, 0.10 * start). Blocks remain at most 25 calls; before
each block require two adjacent stable 60-second idle windows, with at most six
windows. Failure to settle still halts. A drift-only close returns normally so
the existing outer loop prepares the next block with a new sensor/baseline.

Append quality-events.jsonl with block ID, start/end baseline windows, signed
drift, threshold and affected call keys; print that flag in terminal output.
Existing block end events already carry baseline_drift and remain the source
for joining flags to measurements. Do not rewrite any call, response or energy.
An independent hard stop during the block still halts, even when drift occurs.
Input-count mismatch, insufficient rolling energy coverage, exhausted logical
failure rate, disk-space limit, experiment freeze and outcome embargo remain.
The final 40-isolated/100-loaded checkpoint still stops the pipeline.

## Energy disposition and analysis
Retain the original gross and start-baseline net estimates as primary. Flag all
drifted blocks, including the three already observed; do not repair or repeat
requests. Extend the explicitly post hoc secondary end-baseline, midpoint and
exclude-drifted-block sensitivity reporting to these flagged blocks. Exclude
all flagged blocks together, with per-block diagnostics and matched denominators;
report coverage and low-resolution sensitivity separately. Alternative constant
baselines do not recover the unobserved idle trajectory. These changes respond
to observed measurement diagnostics and are not a prospective energy validation.

## Risk, interpretation and assumptions
Continuing trades uninterrupted collection for weaker energy comparability.
Flags do not make drifted energy unbiased; energy findings require the registered
limitations and sensitivities. Calls are sequential and the next fresh stable
pair is required regardless of whether the previous block drifted. No new
outcomes were inspected to choose this rule. No model, task, prompt, scoring,
seed, token budget, threshold or original study config changes.

## Checks and open questions
Mock tests must show continuation after drift, preservation of other hard stops,
unchanged stored estimates, no duplicate requests on resume and fresh baselines
for successive blocks. Verify original study and updated execution hashes.
There are no outstanding design questions for this approved amendment.
