# Using the utilisation harness

Run PowerShell from the repository root using the Python 3.13 environment.
Prepare expands a manifest and prints counts, the schedule hash and the first
rendered request. The included example has synthetic token counts for dry
preparation. It is unsuitable for scoring.

    .\.venv313\Scripts\python -m experiments.utilisation prepare --session results/utilisation/example --stimuli studies/utilisation/example-stimuli.json
    .\.venv313\Scripts\python -m pytest -q tests/test_utilisation.py
    .\.venv313\Scripts\python -m experiments.utilisation monitor --session results/utilisation/SESSION

For a frozen study session, use these entry points with actual files:

    python -m experiments.utilisation run --session results/utilisation/SESSION --stimuli STIMULI.json --hwinfo-log SENSOR.csv
    python -m experiments.utilisation score --session results/utilisation/SESSION --dataset DATASET.jsonl.gz

## Stimulus and session contract

Each manifest row defines one condition/item. The scheduler expands configured
models, repetitions and per-sample seeds. E0 uses the existing exact P1/P3_1
builder. Other experiments supply a dictionary of lists of literal strings and
a layout listing the section name for each insertion. Include spaces, delimiters
and newlines in the strings. The compiler rejects unmatched or unused sections.
Allowed names are in utilisation_plan.SECTIONS. For example, M3 layout
["filler","task","filler"] places the target between two filler chunks.
U3 and U4 consume existing output and have no generation prompt.

Supply prompt_tokens keyed by model, computed independently on the exact
templated input including the system message. The core validates these counts;
it does not substitute an estimated count for a pinned tokenizer. Include
round, parent attempt, order and other varying factors in identity. Prepare E3
rounds as separate batches after scoring and freezing the feedback. Bundle
entries must be distinct and identity.task_ids must name their tasks. U2 uses
A/B/C/D and identity.correct_option for the offline answer key; the key is
outside the rendered prompt. Freeze the recognition instruction accordingly.
E4 warm and cold refer to model-resident requests; setup envelopes are logged
separately. The built-in cache check requires an explicit counter and exact
expected count. Validate counter semantics on the actual runtime before scoring.

Use one experiment per registered batch. Commit its stimuli and prereg/ID.json,
with date, hypotheses, competing_predictions, conditions, outcomes, analysis,
exclusions, config_hash, stimuli_hash and schedule_hash. Text artifact hashes
use Git LF bytes. The runner records the Git commit and registration hashes.
Use a separate session directory for a new registration. All CLI scoring and
generation share an OS-released study lock. Idle sleep is inhibited for an
active block. AC power, Best performance and HWiNFO configuration remain
host setup requirements. The growing sensor CSV is mirrored in session/sensors.
Process snapshots document competing programs; they cannot remove their energy.

starts.jsonl links each attempt to a logical key. responses.jsonl stores the
raw HTTP envelope before energy processing. calls.jsonl stores the final flags,
counts, times and extraction. scores.jsonl contains separate offline outcomes.
blocks.jsonl carries baselines, drift flags and process snapshots. Join by
block ID to include drift in analysis. Input-count mismatches are invalid;
output-cap hits are censored. Negative net energy and low-resolution windows
are flagged. Missing windows have no estimate. API errors are recorded before
stopping. A lost HTTP response may have executed on the server; a later retry
has a new attempt ID. Saved responses never cause regeneration. A missing
trailing newline is an incomplete journal record: recovery retains its bytes
and appends new records in a numbered segment. Malformed complete records or
duplicate logical results stop the reader. ETA uses completed wall time plus
the gap and excludes baseline, sensor wait and cache-priming overhead.

## Offline evaluator validation

The references command takes an explicit validation digest independently of
the scored-run config. Candidate code only runs in the resource-limited worker.
The implementation compares against the trusted reference on each actual
base_input and plus_input and applies the find_zero residual oracle. Its
per-candidate deadline differs from upstream per-input timing. Use a fresh
validation directory when changing evaluator code. Reproduce the audit:

    python -m experiments.utilisation references --session results/utilisation/validation/final --dataset results/utilisation/validation/HumanEvalPlus.jsonl.gz --validation-sha256 272720b90ac375502c8ed23cd791c2a93dfb22a911641a494da74a426c09f101

On this host the HumanEval/32 canonical Newton solver returns
17.3124550475086 for plus_input[119]. The absolute polynomial residual
is about 0.002315, above the release tolerance 0.0001. Retain this finding
for owner review before approving reference validation. No tolerance change
or task exclusion was applied.

### Reference audit result

HumanEval+ v0.1.10 on Python 3.13: 163 of 164 canonical solutions passed both
partitions. HumanEval/32 passed base and failed plus. The reference audit
counts task IDs once; the implementation is audit_references() in
src/prompt_energy/utilisation_eval.py. The data and machine-specific validation
journal are local results, excluded from Git.

## M3 review checkpoint

The runner stops before request 101 of M3 in its frozen session and writes
m3-checkpoint.json. Its forecasts stratify measured wall seconds by model and
include the configured gap. Ending baselines are collected on exit. After the
owner sees the report and approves continuing, record m3-review.json with the
checkpoint schedule_hash, checkpoint_calls=100 and owner_approved=true. The
runner checks this receipt on every resume. Keep all M3 requests in the same
frozen session to maintain the cumulative checkpoint count.
