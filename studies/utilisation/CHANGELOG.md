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

## M3 checkpoint reviewed; continuation prepared — 2026-11-19

Owner requested begin now after counts/validity/timing review and supplied
ver5_hwf. Freeze a selected-schedule-bound owner receipt; finish only original
240 M3 calls (140 remaining). Preserve first-100 checkpoint and immutable call
keys; no E0/isolated repeats, scoring, extension or later stages. New terminal
entry point checks old manifests plus a committed continuation manifest and
uses unchanged block/retry/energy rules. Later stimuli need their own readiness
checks. Model/prompt/task/config files are unchanged. No generation in this
implementation task; owner launches from terminal.

Verification: 399 tests passed (14 existing dependency warnings), Ruff clean.
Fixed mock fixture directory creation before final suite. Read-only ver5
preflight passed: cadence 0.5 s, age 0.1592927 s. Existing execution manifest
verified; continuation adds a separate five-artifact committed manifest.

## Revised structure and skip-completed instruction — 2026-11-20

Owner supplied revised architecture and explicitly requested skipping completed
experiments. Preserve completed E0/legacy M3 and all 40 isolation responses.
Owner approved original fixed 40-task roster shared across models and reduced
pilot-first M1. Supersede pending three-cell R1 proposal with five-policy R1;
do not treat old M3 renamings as contradictory near-duplicate tasks. Exact
revised generation factors and materials are still drafts.

Run the existing sandboxed evaluator on saved M3/isolated responses only,
separate from inference. Add offline audit and review matrices plus modular
draft builders, without model calls or changing original config/hashes.
Full M1 stated factors produce 960 calls rather than provisional 480. Other
planner budgets remain provisional until exact matrices and validation exist.
The eight-hour idle window is not a scientific design approval or a guarantee.

## Approved reduced M1 pilot and completed offline evaluation — 2026-11-20

Owner approved five named tasks/K2,K4/three modes/two models/max70 including
up to10 controls. Prepare all70, since old isolation controls differ in context.
Reuse original M1 config: context32768, T0, seed1729, threads8, per-function
output2048, timeout3600s. Companions are seeded distinct-entry-point prefixes;
target first for3 tasks, last for2, matched across modes/models. This is partial
order balance, not a fully balanced design. Exact input counts131..897.
Receipt records grid approval; no individual prompt-review claim. All exact
texts published; no references/tests in prompts. Validate new reference bundles
before generation; generation-only blocks followed by separate evaluation,
then stop. No full run/later stage automatically starts.

Completed offline scoring on40 isolated and240 loaded M3 responses. Reproducible
audit CLI prints all counts/denominators/settings and call hashes; there are no
missing score keys. E0 grid1968/1968, M3-isolated40/40, loadedM3 240/240,
all unique. Raw calls are unchanged. No interpretation from aggregate counts.

Preparation verified:406 tests passed,14 existing dependency warnings; Ruff
clean. New reference bundles35/35 checks pass. Exact pilot schedule70 calls,
hash a63f1965ac3cf87155beb25378798cee607d470598b18b6667ffc2a59a70121f.
ver6 supplied by owner passes live-log checks. Initial host was battery/Balanced;
owner subsequently confirmed plugged in/Best performance; recheck before launch.
No completed E0/M3 requests repeated. Fresh pilot generation remains separate
from all full-run studies and will stop at70 after offline evaluation.

Pre-launch check caught binary artifact CRLF vs source LF hashing difference.
Correct verifier to preserve artifacts exact bytes as Git -text requires; add
regression test. No generation preceded this correction. Owner-confirmed power
state rechecked as AC/Best performance. Original scientific settings unchanged.

Final verifier regression suite:407 tests passed (14 existing dependency
warnings), Ruff clean. Pilot session journal records Ollama version, source
registration and active sensor path before generation. All scientific settings
unchanged by the hash-check correction; fresh host/sensor checks precede launch.

## Timed full-M1 approval - 2026-11-21

Owner approved1040-call full-M1 queue and ver7 logging for7-8h availability.
Freeze new scoped inputs/config before generation; skip completedE0/M3 and
exclude pilot. Keep original decoding/oracle, nested seeded companion prefixes,
20/20 first/last target position balance. Matched irrelevant filler uses neutral
prose prefixes or repeated x padding when exact token count needs it; log exact
texts/counts. This differs in filler construction for some full-grid items and
is disclosed before new generation. Report all paired analyses exploratory
post-pilot; don't choose tasks/cells by outcome.

Add optional time callback to shared supervisor, default unchanged. Check before
logical requests and retries; preserve incomplete attempt journals at cutoff.
Window7.5h; reserve3600s HTTP and600s baseline close allowance. Later stages
remain gated; user explicitly confirmed Best performance after host initially
reported Better battery. Sensorver7 passes growing500ms checks.

Final pre-launch validation:412 tests passed,14 existing dependency warnings;
Ruff clean.640/640 new canonical reference checks passed.1040 unique jobs,
520 stimulus items,40 target items per condition,160 exactly matched passive/
filler pairs; all input+output reservations fit32768. Scoped config differs
from original only in file/registration paths; original15 study hashes retained.
Preparatory token matching was accelerated before freeze, without any model
calls or outcome-guided selection; final frozen schedule hash
6b000743a2ffa13d6e30514e31fc75627bc157eb11e5d4748ac99839ff1ddf0c.

## Unattended finish sequence - 2026-11-22

Owner unavailable7-8h requests continuation after269 remaining M1 calls.
Prepare finish_m1_sprint driver: frozen M1 generation -> offline sandbox scoring
-> count/hash-independent verification. No additional permission between ready
phases. No unfrozen R1/E5 generation. Overall7.75h clock bound, owned-process
termination at cutoff with retained journals; incomplete phase never success.
No changes to frozen M1 settings/inputs or the scientific design. Active sensor
path and AC/Best performance still required for launch.

Sequence verification:415 tests passed (14 existing dependency warnings),
Ruff clean. Current launch is blocked by physical host setup: AC0/Balanced
and no fresh sensor file as of readiness check. No model requests made.
Driver will proceed automatically through approved generation/evaluation/audit
without another gate once the active sensor and power setup pass.

## R1 connection approved - 2026-11-22

Owner approved five memory policies, lossless compaction, same40 roster and
eight fixed seeded distractor specifications, automatic50-call pilot gate then
400 full calls if validation/remaining time pass. All pilot data excluded.
Semantic summaries requested if feasible: deferred because essential-requirement
and loss audits are unavailable; no unaudited sixth arm launched. Exact token
matching is reported where naturally possible; no causal length-isolation claim.
Precomputed oracle selection/formatting do not measure realistic retrieval or
preparation energy. Generation-only energy boundary explicit.

Build exact policy inputs, scoped configs/registrations and one7.75h chain.
Compaction first exposed adjacent closing quotes in a doctest; fixed with
explicit newline boundaries before freezing inputs, no model outputs involved.
All40 reference checks passed, reused only byte-matched code/oracle checks.
Mechanically checked word/example preservation is not claimed as human summary
review. Pilot gate uses validity/coverage/time, not task success.

Chain verification:418 tests passed (14 existing dependency warnings), Ruff
clean. R1 pilot50/full400 cells and all40 reference checks verified. There are
zero naturally exact-token policy pairs in frozen materials; length-adjusted
comparisons remain exploratory and cannot isolate pure memory effects. No new
token-matching arm added silently to the approved five-policy budget.
Machine prerequisites still unavailable: AC0/Balanced and last sensorver7 stopped
yesterday. The chain is prepared, not launched; no R1 model request made.

## R1 completion audit - 2026-11-22 12:41 IST

Owner requested completion of R1. Rechecked AC/Best performance, growing ver8
sensor log and frozen manifests, then resumed the existing approved chain.
It skipped completed M1 and the 50-call R1 pilot, appended only the remaining
25 full R1 requests, closed the measurement block and scored all 400 full rows.
The chain exited successfully with reason `finished`; no further stage launched.

Read-only verification: pilot 50 calls/50 scores; full 400 calls/400 scores;
unique expected keys match, all ten model-policy cells have 40 full calls,
zero missing/duplicate calls or scores, zero invalid inputs/API failures.
Full scoring counts: 199 passed, 196 failed, 5 capped/truncated. No scoring
infrastructure errors; original timeout and runtime-error outcomes retained.
Energy estimates available 400/400, with 78 post-load and 21 total-window
low-resolution flags. Two drift-flagged closed blocks contain 50 calls.
The final block cd0ba0a5356d482f9722b0fa3df7793e measured start 9.7872128742009 W
and end 11.926920165410593 W: signed drift +2.1397072912096924 W, above the
unchanged 1 W threshold. Drift remains a flag under the approved rule.

Added analysis/verify_r1_completion.py to reproduce all counts, frozen schedule
verification and raw-prefix preservation, writing a derived JSON audit. The
previous 2181300 bytes (375 calls) still hash to
9e01126c4f9514bf042c8ef995400317da4645b0de45da54bf6c780da0ff1b71.
No frozen artifact, raw record, generation setting or research definition changed.
No effect interpretation or new hypothesis added. Semantic summaries remain
deferred; pilot rows remain separate from the full experiment.

Completion checks: 418 tests passed (14 existing dependency deprecation warnings),
Ruff clean, formatting and diff checks passed. Completion audit exited zero;
both frozen phase manifests and all recorded pre-resume bytes verified.

## Continued-execution request - 2026-11-23

Owner requests finishing planned work without an arbitrary seven/eight-hour
stoppage, until he pauses. Record execution-window extension beyond the prior
22 November freeze; do not change scientific definitions or completed frozen
artifacts. No new model request made in this readiness audit. Per-request
timeouts/retries and every safety/data-validity stop remain required.

Verified completed call/score ledgers: E0 1968/1968, original M3 isolation
40/40, original M3 240/240, full M1 1040/1040 and full R1 400/400; separate
M1 pilot 70/70 and R1 pilot 50/50. Zero missing score keys in these sessions.
Remaining revised stages lack reviewed exact materials/validation. Proposed
E5 code-only-preference scope and automatic pilot gate sent for owner decision;
no scope approval inferred. Fresh sensor path requested because ver8 stopped
logging yesterday. Current-generation status: not launched.

## E5 -> revised semantic M3/R2 preparation - 2026-11-23

Owner requested both stages sequentially without an elapsed-time stop. He
rejected the proposed output-contract distractor and required computational
alternatives, hidden reference/tests, validated distinguishing inputs and
pre-generation exclusion of unreliable constructions. Three examples were
shown: strict/inclusive threshold, XOR/XNOR and empty-prefix inclusion.

Prepared E5 pilot50/full400 and R2 pilot130/full1040 (960 loaded+80 compatible
isolation calls). All40 original target references passed; all40 computational
alternatives passed authored expected-output fixtures and modified-reference
argument suites.80 authored fixtures include differing witnesses and shared
controls, checked on both references. No task excluded. Refined validation to
include distinguishing inputs in the modified scoring suite and key audits by
the exact modified row before freezing. Earlier validation records remain
append-only; the curated report selects the current40 construction hashes.

Added separate continuation worker/queue, literal preference builder/adherence
proxy, semantic alternative catalogue, pause-aware offline target/cross scoring,
phase preparation/validation and a crash watcher. Historical frozen worker and
completed raw data remain unchanged. AST parity test checks the worker differs
only by removing the calendar-freeze check. User pause persists; pilot gates
ignore correctness, retain output caps and stop on invalidity. No new inference
has run during material preparation or reference validation.

Pre-launch verification: full suite431 passed (14 existing dependency warnings),
then15 continuation tests passed after adding the parent sleep-inhibition guard;
Ruff clean. Six archived mock tests needed a test-only future execution window
because the original production freeze has now expired. Their frozen source
and the original worker remain untouched; a separate test confirms an expired
legacy freeze still prevents all model calls. The new watcher inhibits idle
sleep throughout generation and scoring, releasing it at exit.

Host preflight observed AC1/Best performance,151.37GiB free, live ver9 sensor
cadence0.501s and age0.242s; both model digests matched and Ollama0.40.17 was
recorded. All four new schedules have unique keys and fit input+2048 output
reservation. Largest inputs: E5 full1684, R2 full2390 tokens. These are preparation
checks, not measured model-performance results. Materials and source hashes are
committed before the first new inference request.
