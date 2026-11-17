# M3 supervisor-order amendment draft · 2026-11-17

Status: DRAFT, inactive pending owner approval and a drift-disposition decision.
The owner explicitly requested no recovery or generation during this change.
The registered drift threshold remains abs(end_W-start_W)>max(1 W,0.10*start_W).

## Revised sequence

1. Complete frozen E0 generation and sandboxed scoring. Preserve all 100
   existing responses; a recovery never regenerates completed logical calls.
2. Run E0 paired analysis and emit eligibility labels using P1 sample 0 only
   for the success label, with scored P1 samples 1/2 available. Their pass/fail
   values do not control eligibility. Primary E0 still uses all three samples.
3. Freeze each model's first 20 eligible IDs in the committed M3 permutation.
   Generate 40 fresh isolated temperature-zero responses, one per task/model.
4. Generate only the first 100 requests from the frozen filtered M3 grid.
   Do not score either isolated or loaded M3 outputs in this revision.
5. Collect end baseline, apply every registered hard stop and write the
   timing/coverage/censoring CHECKPOINT.md. Stop for owner review.

This supersedes the earlier draft that placed isolated baseline calls after
the 100 loaded calls. Baselines now precede all loaded M3 generation.
No M3 outcome evaluation or inspection is permitted before the checkpoint.
All current M3 call and score counts are zero, so the sequence can still be
adopted prospectively. A later scored analysis requires separate authorisation.

## Matched isolated baseline

Keep the same M3 target wrapper, trailing request, system template, model
digests, num_ctx=8192, temperature=0, seed=1729, output cap=2048, eight CPU
threads, GPU=0, keep_alive=0 and 900-second HTTP deadline. Remove filler only.
Keep actual input counts; do not pad the isolated call to the loaded length.
Apply the same extraction and Windows sandbox policies later, when scoring
is authorised. Preserve cap events and infrastructure failures separately.

Freeze a catalogue for every model/task pair before any new calls. Derive the
40 selected baseline requests using the fixed eligible IDs after E0 scoring.
Retain the predetermined seed-1730 shuffled order in the selected subset.
The no-filler result must not change task eligibility or replace E0 sample 0.
P1 samples 1/2 remain a secondary temperature-0.2 isolated comparator only.
The new temperature-zero condition is the matched comparator.

## Outcomes, inference and budget

Keep the registered primary M3 near-duplicate versus irrelevant contrast.
The secondary loaded drop is mean(isolated pass - loaded pass), paired by
task for each loaded condition. Bootstrap tasks together with their shared
baseline and six loaded outcomes, 2000 draws, seed 1732. Do not use the
eligibility response as the isolated outcome. No new hypothesis is added.

Focused planning allocation becomes 4848 including the 40 extra baselines.
After E0 (1968), isolated (40) and the first 100 loaded calls, 2740 allocated
calls remain. Actual failed-task populations can reduce later allocations.
The 70% remaining-time rule and 2026-11-22 23:59 IST freeze still apply.
Latency/energy comparison may be affected by sequential phase and block
conditions. Aggregate gross/net energy with coverage and drift disclosure,
and retain the registered low-resolution sensitivity. E4 remains deferred.

## Halt evidence and energy choices

CHECKPOINT.md states exactly "Baseline power drift beyond registered threshold".
Block 6e81165862424391b79b69d0bfbc2dca began with 11.26919846134594 W,
ended with 9.59877406792041 W, and drifted by -1.670424393425531 W.
Its registered threshold was max(1, 0.1*11.26919846134594)
= 1.1269198461345942 W. The strict threshold comparison was exceeded.

Starting baseline: 2026-11-17 00:24:16.993846–00:25:16.993846 IST.
Ending baseline: 2026-11-17 00:46:46.424836–00:47:46.424836 IST.
All 100 E0 calls were made in that block, spanning
00:25:18.756054–00:46:35.095100 IST. The exact keys, task IDs, arm,
model, sample and request/window timestamps are in affected-calls.csv.
All 100 post-load readings are finite. A block-level drift flag applies to
all 100; this does not establish the onset or magnitude of error in each call.

The registration requires signed drift to be flagged, starting baseline used
for net energy, missing/invalid sensor windows left missing, and low-resolution
sensitivity reported. It contains no automatic blanket exclusion for drift.
The supervisor's drift guard halts future calls; that guard does not itself
erase finite estimates or invalidate generated code/correctness observations.

Options for owner decision (none selected):
A. Retain the original start-baseline gross/net estimates, join baseline_drift
   to every affected call, and disclose the full block. This is the option
   directly supported by the registered all-available analysis.
B. Add a sensitivity excluding the entire drifted block's energy. This needs
   a dated analysis amendment; the exclusion is not a registered default.
   Keep code/token/latency observations and report incomplete energy coverage.
C. Recompute net energy using end or midpoint baselines in an explicitly
   post hoc sensitivity. It requires a dated amendment; it cannot replace
   the registered primary starting-baseline values or alter raw records.
D. Re-measure equivalent requests in a new batch and preserve both batches.
   This requires a repetition/allocation amendment, adds calls/time and cannot
   silently overwrite or replace the original 100 responses.

Discarding selected calls based on their observed costs, interpolating an
unknown drift onset, silently resetting the baseline, or changing the
threshold is outside the registered rule.

## Activation and hashes

Legacy experiments/supervise.py and all existing frozen config, task orders,
stimuli, preregistrations, manifests and raw journals remain unchanged.
A separate version-2 controller implements this draft for offline order tests.
Activation requires approval of this amendment and an explicit choice about
the halted block's energy. The review record is currently pending with no
energy choice. Thus the recovery command presently halts before requests.

New files receive separate SHA-256 entries. The Git commit and CHANGELOG.md
hash change. Original config, E0/M3 stimuli, schedule and pipeline hashes do
not change, nor does the old manifest. The added isolated catalogue, new
controller and new sequence acquire their own hashes. Future baseline
request keys and the complete phase sequence necessarily differ.
