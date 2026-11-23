# Complete the remaining study queue - 2026-11-24

Status: owner approved M2 with length/relationship controls, E4, and E3 diagnostic
pilot on 2026-11-24. Preparation only; no new generation.
Owner clarified that the queue must include other remaining experiments after
the340 saved-schedule requests, rather than ending with revised M3/R2.
Existing continuation manifest verifies;700/1040 R2 full calls are saved,
all1040 target scores and the320 expected full cross-pass evaluations remain
to finish. E0, legacy M3, M1, R1 and E5 generation are skipped.

## Proposed outer sequence

1. Resume the unchanged frozen continuation to finish R2 and its scoring/audit.
2. M2 diagnostic pilot, separate scoring and validity-only gate.
3. M2 full generation, separate scoring/adherence diagnostics and audit.
4. E4 controlled cache pilot, verify counter semantics/workload and energy.
5. E4 full only if the cache pilot satisfies its precommitted validity gate.
6. The approved diagnostic E3 repair pilot; never automatic full E3.
7. Write final inventory, denominator/missingness/censoring audit and checkpoints.

No elapsed-time cutoff; user pause and existing safety/quality stops persist.
Do not change the running/frozen continuation entry or any completed artifact.
Create a new outer driver/authority/hash manifest for the additional stages.
No approval is inferred from silence on the scientific questions below.

## M2 proposal for review

Same40-task shared roster, two frozen models, T0, seed1729, context16384,
output2048,8CPU threads, no GPU, keep_alive0. Four static return-to-task
conditions: matched neutral history, one similar competing specification,
one other-task description, three other-task descriptions. Use fixed literal
user/acknowledgement transcripts, never generated intermediate answers or
reference code. Keep the target specification and final query identical.

Match complete input-token counts within task across the four history arms,
including template and transcript labels, with disclosed neutral padding.
This distinguishes the kind of interruption from total token length, while
remaining a static context-use test rather than actual execution suspension.
Use the validated computational alternatives for the similar specification;
audit similar pairs against the validated semantic alternative and choose other
tasks from an explicitly different computational domain. Publish the authored
domain labels/reasons, without claiming an independently human-rated similarity
scale. Three task descriptions also change diversity; count is not isolated.

The full matrix has320 loaded observations plus80 matched isolation controls.
Pilot has40 loaded plus10 controls on an independently seeded five-task prefix,
separate from the full data. Reuse control observations only when complete
request, model digest, temperature/seed/context/output and other decoding
settings match exactly. Reuse R2 controls only with a published source/key/hash
map, preserving pilot/full separation; never count a reused row as a new model
request. If prompt matching cannot be achieved, freeze required additional
isolation calls before generation. No post-outcome replacements.

Proposed primary contrasts are the three task-interruption arms minus the
length-matched neutral arm per model, Holm family6. Task-bootstrap2000/seed1732;
all40 tasks primary, independently baseline-solvable subsets secondary.
Correctness, tokens, latency and qualified generation energy are separate.
Output caps are censored/nonpass; no intentional-forgetting interpretation.

## E4 proposal for review

Prefix0/500/1000/2000/4000, cold/warm, both models,20 repeats =400 measured
requests. Pilot uses one repeat/cell=20 measured requests, kept separate.
Unload/preload before each measured request so both arms start model-resident;
warm also primes the shared prefix, while cold has no prefix reuse. Setup and
priming HTTP requests are additional and logged, never hidden in the call count.

The saved Ollama0.40.17 native responses include prompt_eval_cached_count.
Official metric documentation defines this as cached input tokens, total
prompt_eval_count as all input tokens and prompt_eval_duration as uncached
prompt evaluation time:
https://github.com/ollama/ollama/blob/main/docs/api/usage.mdx
Presence alone is not verified cache behavior. Pilot must demonstrate zero
cached tokens in cold and the intended shared-prefix reuse in warm, with
independently computed full-input/prefix token counts. A timing reduction alone
never proves a cache hit. If verification fails, checkpoint rather than relabel.

Keep identical scored input/seed/settings within a cold/warm pair and a64-token
output budget. Pilot must verify the intended64-token workload; the planned
budget cap is an efficiency-test endpoint, not a coding failure. Do not silently
raise output limits or discard shorter generations to make the test pass.
Freeze literal prefix/probe/priming texts before inference. Preload/prime is
outside the resident scored-request energy window; log its overhead separately
and do not claim unmeasured end-to-end savings.

Primary paired warm-minus-cold resident request energy and latency by prefix
and model; condition totals, gross/net, low-resolution/drift sensitivities.
Actual cached/input/output token counts accompany every comparison. A fixed
output workload cannot identify an independent output-token energy slope;
prefill/decode durations are not separate electrical phase measurements.

## Optional E3 diagnostic proposal, not full E3

Approved: five seeded tasks,two models,one temperature0.2
initial generation per task/model, retry versus failing-base-example feedback,
last-attempt versus full-history retention, up to three repairs. Maximum10
initial+5*2*2*2*3=130 generation requests. Share the initial response across
paired repair branches with explicit provenance/cumulative-cost accounting.
This one-sample diagnostic does not replace the old proposed three-sample full
E3 or its larger feedback/history catalogue; a full grid remains deferred.

Feedback uses two separately authored fixed examples per task, validated with
the restricted canonical reference. Remove any overlapping argument cases from
both final test partitions and publish removal denominators. Final tests stay
hidden until offline evaluation. Freeze first-failing-case selection,
unexecutable-code feedback, stop rules, seeds and literal messages before
pilot launch. Generate each round's batch, close measurement, then evaluate
feedback separately; no concurrent scoring during measured generation.
The pilot gate is validity/resource-based, never repair success or significance.

## Files, checks and remaining decisions

After scope approval: new stage preparation/material modules and scoped configs,
registrations, validation reports, a cache-control runner and outer queue;
tests for counter verification, equal inputs/workload, no leakage, exact control
reuse, pilot exclusion, branch provenance, pause and completed-stage skipping.
Commit/hash before any new model request; full pytest and Ruff required.
Write plain-English learning notes and exact launch/monitor/pause/recovery commands.

Owner approved all three scopes. Routine literal materials, seeds and validation
implementation below implement those approvals; no additional hypotheses.
ver10 is not reusable: header328 columns, a complete row has329. Keep it
unchanged; require fresh500ms CSV (suggest ver11), AC/Best performance and
all normal preflight checks. PAUSE remains until explicit resume with live log.

Assumptions: no changes to frozen settings/results, no duplicate generation
for reused controls, no new dependency/runtime, no effect-based pilot gate,
and no claim that preparation equals completed or validated execution.
