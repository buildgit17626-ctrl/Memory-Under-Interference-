# Terminal supervisor

The terminal process owns a watchdog and appends stdout/stderr to terminal.log.
It attempts an unexpected worker restart five times. Each logical generation
has an independent six-attempt budget (initial attempt plus five retries).
A process crash after a start event consumes that attempt. A durable successful
response is recovered without a new generation; if sensor coverage cannot be
recovered, energy stays missing. Recover never repairs or selects model answers.

Run from the repository root in PowerShell:

    .\.venv313\Scripts\python -u -m experiments.supervise run

Monitor from another terminal:

    .\.venv313\Scripts\python -m experiments.supervise monitor

After inspecting and fixing a checkpoint, resume with:

    .\.venv313\Scripts\python -u -m experiments.supervise recover

The default sensor file is the owner's ver1_hwf.CSV. Override --hwinfo-log
with the actual active file. Run prepare to see any missing input decisions
before attempting live work. All generation commands are gated by pipeline.json
and committed config/stimuli/preregistration identities. Missing prerequisites
halt explicitly. Pending choices in pipeline.json are deliberate.

Only the E0 and first-100-M3 pipeline is supported. Per-condition M3 stimuli
must be frozen for all potentially eligible tasks, then filtered to the fixed
eligible prefix. The complete catalogue is committed before E0 generation. The implementation
filters it after independent eligibility scoring and verifies 240 selected calls.

Held-out difficulty needs a fixed policy disjoint from the generation
outcomes against which it is compared. The analysis supports a specifically
approved P1 sample-0 holdout with E0 outcome samples 1/2. E0's primary contrast
still uses all three samples. A separate calibration, if chosen, requires
its own schedule and additional call accounting. No such policy is selected
silently in pipeline.json.

Energy coverage means a finite integrated post-load window; low-resolution
finite windows count as covered but retain their flags. The rolling 20-call
check halts at three missing windows. Failed-call rate concerns exhausted API
or transport attempts, not wrong code, test failures or output caps. The
candidate evaluator is isolated from measured generation by 100-call batches.
Recheck power and sensor freshness at each batch. The end baseline can detect
drift retrospectively. A sleep or logging outage can leave a window missing.

CHECKPOINT.md includes the stop reason. The intended 100-M3 checkpoint also
contains context-length timing strata and remaining MAIN estimates when the
pending MAIN counts are frozen. Unknown overhead is identified, never silently
treated as zero. Freeze at 2026-11-22 23:59 IST is a hard stop. The E0 report
prints denominators, exact task-triplet swap p-values, Holm-adjusted values,
any-of-three task tables, exact McNemar p-values, paired bootstrap intervals,
per-task output-token differences and covered net-energy differences.

The owner approved the reference anomaly decision and M3 grid, then delegated
remaining choices. P1 sample 0 now defines the held-out label and the complete
M3 catalogue is frozen. The supervisor filters that catalogue to the eligible
prefix after E0 scoring. No model generation occurred while
building or testing the supervisor.
