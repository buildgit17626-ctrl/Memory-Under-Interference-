# E5 -> revised M3/R2 continuation - 2026-11-23

Owner requests both stages in one unattended run, E5 then revised M3/R2.
Calls remain sequential and measured generation never overlaps evaluation.
The E5 scope presented immediately before this instruction is 50 diagnostic
pilot calls then 400 fresh full calls: 40 tasks, two models, five histories,
one code-only preference, temperature zero. Other preference families are not
silently included. The registered old E5 situation framing is not reused.

E5 literal histories use eight fixed other task specifications from the frozen
R1 materials. The target specification and final query remain identical.
Conditions: no preference; code-only immediately before query; preference
before distractors; preference before distractors plus replay before query;
earlier explanation preference followed by explicit code-only correction.
The no-preference arm keeps the same history, so it is a history-matched
control rather than the old R1 no-history arm. Plain-code adherence is a
mechanical proxy: unfenced raw text parses as Python and contains the named
top-level function. Report fenced-code presence and extracted correctness
separately; this does not verify absence of every natural-language comment.

Revised M3/R2 grid: 40 tasks, two models, 1000/2000 filler tokens, target
beginning/end, irrelevant/related/near-duplicate, 960 full calls. Concrete
output-contract distractor construction has been sent for owner approval;
do not implement or launch that condition until answered. Its signatures,
reference behavior and cross-pass distinguishing cases must be validated.
Preserve all 40 tasks; do not drop difficult-to-author tasks after outcomes.

Files: separate prepare/validate entry, frozen per-phase config/stimuli/prereg,
preference builder/adherence classifier, new continuation worker and queue,
E5/M3R2 chain, unit tests, learning notes, SPEC and CHANGELOG. Leave every
completed experiment's frozen source file and manifest untouched. A new worker
fork preserves existing retries, hard stops and energy logic; only the expired
execution freeze is replaced by the owner's explicit continuation authority.
New source hashes identify this execution change; old code stays auditable.

Queue has no elapsed-time cutoff. It skips saved unique keys, checks a PAUSE
file before each attempt, finishes the active request and closes its baseline,
then records a checkpoint. User pause never auto-resumes. Original request
timeouts, retry budgets, 25-call measurement blocks, stable baseline pairs,
sensor/disk checks and drift flags remain. Record duration-based forecasts;
do not promise morning completion. The finite registered schedule still ends.

Each stage pilot has the same validity-only gate: reference checks pass, exact
input counts, no API failure/output cap, complete finite primary energy,
all scores present, no scoring infrastructure failure. Correctness never gates
full continuation. Pilot and full jobs have distinct identities/directories.
After each full generation phase score separately, audit keys and flags, then
advance to the next prepared, committed and owner-authorized stage. If materials
or gates fail, write the concrete checkpoint rather than generate invalid data.

Tests: histories/query isolation, budget and token fit, adherence edge cases,
pilot exclusion, mock-model retries, pause before/retry/between-stage behavior,
no eight-hour cutoff and unchanged legacy freeze. Full pytest/Ruff before run.
Assumptions: same models/roster/oracle; new live log ver9 is only a candidate
until freshness/cadence/schema/host checks pass; scientific details are not
implied by a working sensor; no outcome-based design revision or task removal.

## Owner refinement, before any new generation

Owner rejected output-contract-only interference. Main revised M3/R2 uses a
computationally meaningful alternative for each target (boundary/comparison,
edge-case, tie-breaking, recurrence, operator or algorithm requirement).
Validate modified references against manually specified distinguishing cases
and the benchmark argument suites in restricted subprocesses. Exclude only
unreliable constructions, record their reasons before any model request and
report the actual reduced roster/count if needed. Never show modified reference
code or distinguishing tests to the model. Only description/signature enters
background; target instructions explicitly name the original function.

Three examples have been shown: strict versus inclusive distance threshold
(HumanEval/0), XOR versus XNOR (/11), empty-prefix exclusion versus inclusion
(/14), with expected outputs and an explicit validation-pending label.
Optional output-contract condition stays deferred and separately labelled.

M3/R2 also needs up to 80 exact-setting isolation controls. Pilot is the first
five tasks in the seeded pre-existing R2 order filtered to the approved roster:
120 loaded calls plus up to ten isolation controls; fresh full stage up to
960 loaded plus 80 controls. Pilot data never promote into full results.
This expands the computational budget beyond the 960 loaded-call grid; actual
counts and measured time are shown before full continuation. No morning promise.
