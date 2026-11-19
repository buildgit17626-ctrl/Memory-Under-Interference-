# 2026-11-16 · Initial design approval

The owner approved the shared configuration. The dataset, evaluator and tokenizer pins still require verification. The local Ollama manifests reference both approved historical digests as layers and declare the same template digest (1e65450c30670713aa47fe23e8b9662bdf4065e81cc8e3cbfaa98924fcc0d320). Inspect the runtime identity and check rendered token counts before generating.

The dated design record uses SHA-256 over Git blob contents, which permits verification across Windows checkout newline settings. For each scored experiment, commit its dated preregistration, stimuli, roster, resolved config and SHA-256 manifest before its first generation. Record the commit and manifest hash in the session journal and verify both on resume. Log and obtain approval for parameter changes before scoring.

2026-11-16: Added the core harness and offline reference validation. PyYAML
6.0.2 reads the approved YAML. No settings or model outputs were changed.
The reference audit used the v0.1.10 HumanEval+ release, without freezing a
new dataset or waiving a failing reference. See HARNESS.md.

2026-11-16 pilot: owner authorised 22 diagnostic requests. The pilot uses
tokenizers 0.21.4 and explicit Qwen chat-template rendering via raw=true to
verify input counts on the exact submitted text. The scored-study config
remains as approved. See prereg/pilot.json and docs/plans/UTILISATION_PILOT.md.

2026-11-16 pilot completed: all 22 authorised responses saved. All prompt
counts matched; both long inputs were exactly 4000 tokens. Long responses were
empty on 0.5B and "0" on 1.5B. No output caps were hit. Energy coverage was
22/22, including 9 post-load low-resolution windows. Resume produced zero
new requests. Timing extrapolations in analysis/utilisation_pilot.py are
unapproved scope scenarios, not confidence intervals or runtime guarantees.

2026-11-16 Focused selected by owner: MAIN initial planning budget 4808,
APPENDIX deferred. Added fixed sweep permutations with prefix task selection,
a task-only extension to 40, proposed interval width threshold 0.20 awaiting
approval and time trigger awaiting owner deadline. Decision uses timing or
precision, independent of direction and significance. Recorded aggregate
energy rules, deferred E4 energy evidence, M3 100-call review and E0 draft.
Final stimulus grids, eligible rosters and evaluator pins remain to freeze.

2026-11-17 owner approval: full primary 95% CI width threshold >0.20.
Experiments freeze 2026-11-22 23:59 IST. All pending work plus an extension
must fit in at most 70% of the hours left, using measured seconds per call.
The latest "extend only if" instruction is applied as a hard timing gate
even when precision triggers extension. Preserve the rest of November for
writing, applications, statements and recommenders.

2026-11-17 supervisor requested by owner: up to five retries per logical call,
separate offline scoring, E0 paired analysis, independent labels and stop after
100 M3 calls. Prepared terminal entry point and explicit hard-stop checks.
Call failure means exhausted API/infrastructure attempts, not wrong generated
code. The energy threshold is interpreted as fewer than 18 valid windows in
a rolling 20-call population. These operational interpretations are disclosed
for review. Execution remains gated by the pending calibration policy, exact
Focused M3 selection and HumanEval/32 reference decision.

Resolved existing input pins from local validation files: HumanEval+
v0.1.10 dataset SHA-256, Qwen tokenizer/template hashes and evaluator source
hash. Generated 328 exact E0 stimuli expanding to 1968 calls offline.
This is input preparation and has made no new model requests.

2026-11-17 owner approved the Focused M3 grid: complete rendered input sizes
1000 and 4000 tokens, middle target position, all three filler types,
20 eligible tasks per model, 240 scheduled calls. Owner also approved keeping
HumanEval/32 in all 164-task primary results under the original oracle and
adding an explicitly labelled sensitivity excluding HumanEval/32.
Independent held-out calibration policy remains pending.

2026-11-17 delegated launch: owner requested launch and delegated remaining
choices. Selected P1 sample 0 holdout with samples 1/2 for subsequent grouped
generation comparisons, preserving the 1968-call primary E0 and 4808 budget.
Defined M3 neutral, cyclic other-task and renamed-target duplicate fillers;
precompute every possible target variant before E0 and filter the frozen
catalogue by calibration-prefix selection. Duplicate fillers preserve target
semantics, so their results cannot demonstrate contradictory interference.
The target midpoint and filler boundary policy are recorded in each stimulus.

Launch preflight caught stimulus hashes taken over Windows checkout newlines
instead of committed LF bytes. Normalised both E0 and M3 registration hashes
to the documented Git-blob convention before any generation.

## Retrospective delegated-decision log recorded 2026-11-17T21:21:35+05:30

Original decision commit 442594e was committed at 2026-11-17T00:22:34+05:30.
The following entries distinguish that original commit timestamp from this
later documentation timestamp.

- Recorded 2026-11-17T21:21:35+05:30; original decision timestamp 2026-11-17T00:22:34+05:30. Chose E0 P1
  sample_idx=0 (seed 1729) for eligibility and binary difficulty; samples
  1/2 supply subsequent independent generation outcomes. Primary E0 retains
  all three samples. This saves the proposed additional 984 calibration calls
  but produces noisy single-sample labels. Its sample-0 outcome must never be
  reused as an isolated success comparator.
- Recorded 2026-11-17T21:21:35+05:30; original decision timestamp 2026-11-17T00:22:34+05:30. Chose renamed
  copies of the target specification as M3 near-duplicate filler. This is
  redundant competing naming, not contradictory semantic interference.
- Recorded 2026-11-17T21:21:35+05:30; original decision timestamp 2026-11-17T00:22:34+05:30. Froze all 164
  tasks' M3 texts before E0, then selected each model's first 20 eligible IDs
  in the already committed permutation. Selection depends on the sample-0
  solvable label, never loaded or fresh-baseline outcomes.

Amendment draft recorded 2026-11-17T21:21:35+05:30: propose 40 fresh temperature-zero no-filler
M3 calls after the 100-call timing checkpoint and before M3 outcome access.
The registered fallback comparator is E0 P1 samples 1/2 at temperature 0.2;
a matched-temperature baseline is not currently scheduled. The running
supervisor scores M3 before its checkpoint, so adopting the proposed sequence
requires a subsequent execution amendment. This change is documentation only.

Read-only status check: supervisor halted on baseline drift after 100 E0
calls; zero E0 scoring records and zero M3 calls/scoring records. No correctness
outcomes were inspected. Existing frozen artifact hashes verified unchanged.

## Drift evidence and proposed order revision recorded 2026-11-17T21:45:46+05:30

Owner prohibited recovery/generation and any change to the drift threshold.
Read CHECKPOINT.md, block events and request timing/energy metadata only.
Halt text is "Baseline power drift beyond registered threshold".
Start baseline 11.26919846134594 W over 00:24:16.993846–00:25:16.993846 IST;
end 9.59877406792041 W over 00:46:46.424836–00:47:46.424836 IST on 2026-11-17.
Signed drift -1.670424393425531 W exceeds unchanged max(1 W,10% of start)
= 1.1269198461345942 W. All 100 completed E0 calls belong to this block and
have finite post-load readings. Exact keys and timestamps were exported by
analysis/utilisation_drift_audit.py, without reading correctness outcomes.
Raw source hashes were recorded for preservation verification.

Registration requires drift flags and retaining the starting-baseline primary
calculation; the drift guard does not automatically delete finite windows.
Listed registered retain-and-flag and amendment-dependent exclusion,
end/midpoint sensitivity and repetition options. No option was selected.

Drafted a new order: E0 with scoring, E0 analysis/eligibility, 40 matched
temperature-zero isolated calls, 100 loaded M3 generations with all M3 scoring
deferred, checkpoint. Built a separate inactive version-2 controller and
pending review record. Added offline order/stop tests. Old supervisor,
baseline-drift threshold, config, frozen stimuli, original preregistrations,
old manifests and raw journals were preserved. New baseline catalogue and
execution artifacts have new hashes; Git HEAD and this changelog change.

Exact future recovery command after review is
.\.venv313\Scripts\python.exe -u -m experiments.supervise_v2 recover.
It is currently gated by a pending review and energy-disposition decision.
No recovery, new generation, scoring of the existing E0 calls or M3 outcome
inspection was performed in this task.

Post-commit check found the new verifier normalised artifact bytes despite
the existing artifacts/** -text Git attribute. Corrected only the new draft
verifier to use exact artifact bytes and LF-normalised source text. The raw
run, old frozen manifests and original baseline threshold remain unchanged.

## Owner approvals recorded 2026-11-17T21:55:18+05:30

Owner approved version-2 order with an application gate blocking both the
40 isolated responses and 100 loaded M3 responses from scoring/inspection
before the completed checkpoint. Added guard wrappers to public scoring and
inspection entry points. Counts/timings remain visible. Neither a missing
checkpoint nor a drift/error checkpoint releases outcomes. The raw journals
retain ordinary local-file access; no claim of operating-system access
isolation is made. The registered low-level evaluator remains unchanged.

Owner selected primary retention of original gross/start-baseline net
estimates, with baseline_drift joined to every call in block
6e81165862424391b79b69d0bfbc2dca. Registered end-baseline, midpoint-baseline
and exclude-that-block sensitivities as explicitly post hoc secondary
analyses, with equations and matched-population denominators. The derived
affected-calls.csv remains the flag index. Raw values are unchanged.

Updated order-v2-review.json to approved, awaiting the owner's manual launch.
No requests will be repeated; the threshold is unchanged. No recovery,
generation or scoring of actual study responses was performed in this task.
Added offline tests of embargo before/after checkpoint and hash validation.

## Reliability diagnosis and approved repair recorded 2026-11-17T23:40:03+05:30

Second block c454e492249a474c97e04c3eb9db80f9 started at 10.363669410243912 W,
ended at 11.645168659877706 W and drifted +1.2814992496337947 W.
Its unchanged threshold is 1.0363669410243912 W. There are now 200 saved E0
calls and one invalid logical call. Process snapshots identify about 1487
CPU-seconds from OneDrive in this interval; diagnosis is reproducible in
analysis/utilisation_reliability_diagnosis.py. This supports a competing-load
concern, not a proven sole cause. OneDrive has not been paused automatically.

The invalid call received the identical Ollama token-repeat-limit abort on
six attempts. Added a terminal classification for future such responses,
preserving unavailable token measurements and all raw envelopes. Existing
six attempts and the invalid row remain untouched. Other transient errors
retain their original retry policy.

Owner approved 25-call measurement blocks and two adjacent stable 60-second
idle windows under the existing max(1 W,10%) criterion. Preparation is bounded
to six idle windows, each logged; no generation occurs during it.
New code maintains 40 isolated and 100 loaded M3 calls using smaller blocks
and preserves the outcome embargo. Richer drift checkpoints record actual
baselines, time windows, threshold, affected keys and any prior error.
No hard-stop override or drift-threshold change was introduced.
No recovery, model requests or rescoring occurred during these changes.
Extra baseline overhead invalidates the earlier 8–11-hour checkpoint estimate.

## Drift-as-flag approval recorded 2026-11-18T07:08:41+05:30

Owner approved flagging drift and continuing with fresh baselines. The latest
25-call block bfdaa8502c924436bbea9f6bb4d1661d went from 9.827067735632427 W to
11.395041307714285 W (+1.5679735720818577 W), above the unchanged 1 W threshold.
No claim is made that a single background process caused this drift.

Implement quality-events.jsonl and terminal flags, preserving original estimates
and block events. Continue after drift alone, preserving every other hard stop
and the final checkpoint. Fresh stable baselines remain mandatory every block.
Retain/flag is primary; extend explicitly post hoc end/midpoint/exclude-drifted
block sensitivities to all flagged blocks. Original frozen registration files
remain unchanged; the execution manifest and review record are refreshed.
No requests repeated, no recovery launched and no actual outcomes inspected.
Assumption: the existing next-block sensor factory supplies fresh idle windows;
tests must verify this rather than reuse a previous block's opening baseline.

Offline verification: 388 tests passed (14 existing dependency deprecation
warnings), Ruff clean; 15 original study hashes unchanged. The execution
manifest is refreshed to 21 entries, including the dated amendment and tests.
Saved counts: E0 225 calls/200 scores; M3-isolated and M3 zero calls/scores.

## CSV layout diagnosis recorded 2026-11-18T08:59:42+05:30

Read-only inspection of ver2_hwf.CSV found 328 header fields and persistent
329-field rows starting at row 67426, 08:19:36.117. The snapshot contained
4759 mismatched rows among 72183 data rows (72184 physical lines including
header). Cause unknown; not a transient partial tail. No skipped rows or
column-remapping workaround. Owner provided same folder/ver3_hwf.CSV.
Read-only new-file preflight passed growth, fresh timestamps and observed
median cadence 0.4985 seconds. No model API requests or generation launched.
Improve schema error details and checkpoint workflow ValueError/OSError failures
rather than leaving an unhandled traceback. This is an error-reporting repair,
not a change to measurement validity, thresholds or research parameters.

Verification: 392 tests passed (14 existing dependency warnings), Ruff clean.
All 15 original study hashes unchanged; updated execution manifest has 23
entries. Repair does not launch recovery or generate any study responses.

## Snapshot freshness diagnosis — 2026-11-19

Owner screenshot shows stop after 1825/1968 E0 calls. Read-only journals confirm
1825 unique calls and 1825 scores; isolated/loaded M3 have zero calls or scores.
ver4_hwf.CSV grew from 120262667 to 120271619 bytes over two observations
approximately three seconds apart, with current timestamps. A later snapshot
had 120313758 bytes and 81749 samples; read 0.0457882 s, parse 2.3258841 s.
Sample age was 0.1191952 s at read and 2.4450793 s after parsing. Full-history
parsing can therefore consume the freshness margin; the exact historical
cause is not established by the saved checkpoint.

Correct clock reference to snapshot read time; retain strict parsing and all
thresholds. Record validation delay separately. Synthetic tests exercise slow
parsing of both fresh and already-stale data. No actual model outcomes inspected,
no new generations or rescoring. Existing journals untouched.

Validation: corrected synthetic logger fixture to maintain 500 ms cadence;
final full suite 396 passed, 14 existing dependency warnings. Ruff clean.
Read-only preflight on ver4 passed: age 0.5396245 s, cadence 0.504 s,
validation delay 2.3703010 s. Original 15 study hashes unchanged.
