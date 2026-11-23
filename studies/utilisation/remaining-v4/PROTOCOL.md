# Remaining approved studies: dated protocol, 24 November 2026

Owner approved the M2 refinements, E4 and diagnostic E3 on this date. These
new scoped studies do not rewrite any earlier registration or raw record.
The execution extension was explicitly authorized on 23 November; it has no
elapsed-time cutoff. PAUSE, host checks, sensor freshness, disk minimum,
sequential execution, five retries and registered quality stops remain.
Drift remains a flag under the owner's existing amendment; the threshold is
unchanged. No outcome or selection probability is predicted here.

## Queue, counts and gates

Finish the frozen R2 schedule and offline scoring first, skipping all saved
keys. Then M2 pilot (50), M2 full (400), E4 pilot (20 measured), E4 full
(400 measured), E3 pilot (10 initial and at most 120 repair calls). Maximum
new measured generations: 1,000, plus the currently pending 340 R2 calls.
E4 priming/setup and control HTTP requests are additional, recorded separately.
E3 has no authorized full run. U-family experiments and semantic R1
summarization are not silently appended: their exact materials remain unresolved.

Each M2/E4 pilot is excluded from full-study estimates. Their gates require
complete unique records, no invalid input/API failures, complete valid energy
coverage, and (M2) no output caps or evaluator infrastructure errors; (E4)
verified residency/cache state and the fixed workload. Gate decisions never
use correctness, effect direction, timing improvement or significance. A gate
failure checkpoints the entire queue for inspection; no automatic redesign.
Full-stage caps/missingness remain visible; existing hard stops still apply.

Commit this protocol, configs, literal stimuli, feedback validation and the
execution SHA256 manifest before any new inference. All complete request,
model digest and schedule hashes are verified on recovery. Runtime-generated
E3 round materials cannot exist before their parent responses: their derivation
algorithm is committed now; actual schedule hash, parent keys and feedback
history hash are written once before each round's generation. A changed
derived schedule is a hard stop. This is an adaptive diagnostic, not a new
confirmatory full E3 study.

## M2: return to a task in a static transcript

Hypothesis from owner C1: competing descriptions may reduce correct use of
the target specification. Alternatives include no difference, opposite effects,
or differences explained by content/recency rather than a memory mechanism.

Use the original fixed 40 targets for both models. The five-task pilot is a
seeded prefix of the existing M2 order. All four loaded arms contain the same
original target, three description/acknowledgement slots, final return-to-task
instruction, template and generation settings. Slots contain either neutral
prose, one similar computational alternative in the middle, one other-domain
task in the middle, or three other-domain tasks. Model sees descriptions only,
never distractor implementations or hidden tests. The target's original public
examples are retained. Acknowledgements are literal, not model-generated.

Similar distractors reuse the previously independently reference-validated
same-interface alternatives, with a computational requirement changed. Other
descriptions come from the opposite authored coarse domain (numeric versus
text/symbol/named-item processing). The relationship audit records IDs,
domain labels and construction reasons. This is an AI-assisted authored audit,
not independent human annotation or a calibrated similarity metric.

Neutral x padding matches each slot and complete template-inclusive input
token counts exactly within target across the four loaded arms. The target,
three slots and final instruction keep their order. Padding is disclosed
synthetic content and can itself influence a model. Three interruptions also
introduce more distinct descriptions, so count and diversity are not isolated.
This is not a live assistant workflow or proof of internal forgetting.

Matched isolation controls use the identical target, acknowledgement and final
instruction without intervening slots. Their shorter length is intentional.
Their full requests differ from R2, so 80 new full controls and 10 pilot controls
are frozen here; there is no approximate control reuse. Each task-arm has one
sample/model; T0, seed1729, context16384, output cap2048, CPU8 threads/GPU0,
keep_alive0. Full 40x2x(4+1)=400; pilot5x2x5=50.

Primary descriptive contrasts: similar-neutral, other_one-neutral and
other_three-neutral, separately for each model. Average binary correctness
differences by task, paired task-bootstrap 2,000/seed1732, 95% percentile
intervals. Exact discordant-pair/McNemar tests if reported; Holm family6.
Isolation and independently baseline-solvable subset results are secondary,
with all denominators. Do not substitute the eligibility sample as an outcome.
Tokens, latency and qualified energy are separate outcomes. Energy per correct
solution is total covered attempt energy / covered-attempt correct count;
also show full correctness and coverage, never silently mix denominators.

Interpretation changes if the domain/alternative audit is wrong, padding or
extraction dominates, output censoring differs, or effects change under energy
sensitivities. Boundary: two small Q4_K_M models, 40 fixed benchmark tasks,
one static transcript design, one generation per cell and one CPU laptop.

## E4: controlled resident prefix-cache reuse

Owner's question: how verified prefix reuse affects latency and CPU-package
energy for a controlled prompt/workload. No benefit, or overhead without a
benefit, remains reportable. This is not a claim about memory-policy correctness.

Prefix lengths 0/500/1000/2000/4000 literal tokenizer tokens, cold/warm, two
models and 20 repeats: 400 scored requests. Pilot has one repeat/cell, 20
requests, kept separate. Each scored request asks for a long integer sequence
with a 64-token output budget, same input/seed/options in each cold/warm pair.
The 64-token endpoint is intentional. An early EOS fails the workload gate;
it is not silently discarded or replaced. No change in cap after outcomes.
Zero prefix still includes shared template/probe boilerplate; call it a zero
added-prefix control, not a zero-cached-token warm condition.

Before each measurement, unload both registered models to clear prior state;
preload selected model in both arms using the same options. Warm alone primes
the shared prefix with a different final request and one output token. Check
/api/ps: exactly the selected digest resident, size_vram=0. Wait five seconds
after setup before measuring. Unload after each attempt and before closing
baseline. All control payloads/responses and elapsed times are append-only.
Setup, residency checks, priming and unloads are not scored measurements.

Both measured arms are resident. Record native prompt_eval_cached_count:
cold must equal0; warm must be positive and no larger than the independently
tokenized common prefix of prime and probe. Partial reuse is allowed and
reported as actual cached/shared-prefix tokens; do not claim full prefix reuse.
Missing native counter, wrong full input count, residency failure, cache-state
mismatch or non64 output checkpoints the study, preserving the saved output.
A timing reduction never establishes a cache hit by itself.

Ollama metric source (verified during preparation):
https://github.com/ollama/ollama/blob/main/docs/api/usage.mdx
prompt_eval_count counts total input; cached count records reused input;
prompt_eval_duration measures uncached prompt evaluation. Log server version,
actual input/output/cached tokens, prefill/decode and total durations.
Template is pinned explicitly through raw input to make prefix overlap auditable.

Randomized interleaving follows seed1730. Pair warm/cold by prefix, model and
repeat. Report resident-request warm-minus-cold differences, condition totals,
and paired-repeat bootstrap2,000/seed1732 intervals as within-machine
repeatability evidence. Repeats are not independent tasks or hardware samples.
If testing ten model-prefix contrasts for energy, Holm within that family;
latency is a separately declared family10. Do not claim precise general noise
or general energy scaling from this single probe/workload.

Measured energy excludes setup and priming. Their raw durations are logged,
but not their electrical energy; never claim end-to-end energy savings.
The unloaded idle subtraction and resident allocation are disclosed; show gross
as well as net. Fixed64 output cannot identify an output-token energy slope;
native prefill/decode time is not separately measured phase energy.
Counter anomalies, partial reuse, changing output counts, residency/load
differences, drift and low resolution would change interpretation.

## E3: diagnostic repairs, not a full experiment

Owner's question: retry versus failing-example feedback, crossed with
last-attempt versus full-history memory, can change repair success, repetition
and cumulative inference cost. No gain or regressions are equally reportable.

Five tasks from the pre-existing E3 task order filtered to the original40:
HumanEval/53,162,122,0,39. Both models; one initial generation each, shared
across four branches with explicit source keys. No selecting only failed tasks
or replacing easy tasks. Temperature0.2, context32768, cap2048, CPU8/GPU0;
initial seed1729; round1/2/3 seeds1729/2718/3141, same across paired branches.
At most10 initial+120 repair generations. Identical round1 memory inputs can
occur because both memory policies have only one prior attempt; those are not
independent evidence of a memory difference.

Two fixed authored feedback examples per task have literal expectations and
canonical-reference checks in restricted subprocesses before launch. Never
send reference code or hidden tests. Remove any matching arguments from BOTH
final base and plus suites, recording before/after counts. Therefore final
correctness uses this disclosed held-out subset, not unchanged HumanEval+.
No held-out suite outcome chooses a feedback example, repair continuation or
next prompt. No invented actual return value is shown to the model.

After each generation batch closes its measurement baseline, evaluate the two
feedback examples, in fixed order. Retry condition gets generic failure/retry;
example condition gets arguments and expected return of the first failed
example. Syntax/policy/runtime failures receive the same required-example
message, without claiming a fabricated actual output. Output-capped code is
marked censored and does not execute. A branch stops when both feedback cases
pass, or after three repairs. Final held-out scoring is deferred until all
repair generation has finished. This stopping rule may stop a branch which
still fails the held-out suite; disclose it.

Keep every raw attempt. Last retains prior output and current feedback; full
retains the complete attempt/feedback chain. Shared target and final query,
same budget/options. No semantic summaries or traceback variants added here.
Shared initial cost counts once in physical totals and once per hypothetical
policy trajectory. Report actual attempt counts, initial/final held-out
correctness, repaired/regressed/still-failed task-model counts, identical-code
repetition, tokens, latency, energy coverage and covered cumulative energy.
Do not present five tasks as a powered confirmation or generalize feedback
case success to solution correctness. Full E3 requires owner review.

## Energy, exclusions and interpretation review

HWiNFO CPU-package power,500ms logging: estimates of generation windows on one
laptop, not whole-device electricity or model-exclusive power. Keep original
start-baseline net estimates as primary, flag drift; end/midpoint baselines
and exclude-drift-block analyses are secondary sensitivities. For short calls,
per-call energy is secondary; primary energy evidence uses per-condition
totals and the inherited registered low-resolution sensitivity. Report removed
rows and selection bias (shorter/cheaper calls are preferentially removed).
Show energy per token only as a complement with explicit numerator/denominator.
E4 is the primary energy experiment; no causal energy conclusion from these
small unmatched workloads. Never sum missing values as if they were observed0:
any available-only total must carry its coverage and cannot be compared as a
complete total. Raw records stay append-only, failed/invalid/capped rows listed.

Before any substantive synthesis, tell the owner which validation, confounding
or sensitivity outcomes could change interpretation, then seek their review.
Preparing a frozen protocol is not evidence that the experiments ran or passed.
