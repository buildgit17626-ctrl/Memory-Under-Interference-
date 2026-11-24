# SPEC: The cost of a correct answer

## Authorized Memory Under Interference evidence audit (2026-11-24)

Owner requests Phases 1–4 of a final empirical audit before interpreting or
drafting a preprint. Generation stays paused. Read-only analysis code is in
`analysis/memory_audit`; outputs are isolated in
`artifacts/memory-audit/2026-11-24-v1`. Preserve original journals, scores,
hypotheses and frozen configurations. New sandboxed cross-scoring and extraction
checks are explicitly posthoc, recorded separately. Reproduce registered contrasts
without relabeling the entire audit as preregistered. State task/bundle dependencies,
all denominators, missingness, model-specific uncertainty and energy sensitivities.
Plan and learning record have the name `MEMORY_FINAL_AUDIT_2026_11_24.md`.

Actual collected scopes supersede the original broad experimental wish list:
E0, initial selected-population M3, full M1, five-policy R1, semantic revised
M3/R2, static length-matched M2, preference-placement E5 and partial constrained
E4. Pilots stay separate. E3/U-family and MemoryGraph interventions are unrun.
No new inference, literature novelty claim, manuscript or submission is added by
this milestone. Interpretations remain provisional pending owner review.

Publication follow-up (2026-10-28): owner authorizes pushing necessary study
materials to the existing GitHub repository and making it public. The
`artifacts/` export includes reports, all 840 scored rows, saved response bodies,
redacted metadata, selected CPU package power readings and supporting analyses.
Original local journals remain unchanged. Source/export hashes distinguish
redaction and reduced telemetry from originals; exports are not inference-resume
archives. No new generation, rescoring, hypothesis or interpretation is added.

Post-collection presentation note (2026-10-27): owner requested supplementary
P4 figures and a combined expectations/observations review. These are descriptive
views of the existing stage-1 data, not changes to H1-H5, scoring, grouping or
exclusions. Presentation families P0/P1/P5, P3_1/P3_3 and P2/P4 show individual
arms, not pooled estimates. Methods and pending-approval interpretation are in
docs/analysis/P4_SETUP.md and docs/analysis/P4_EXPECTATIONS_OBSERVATIONS.md.
No conclusion is accepted until the owner reviews it; the original brief remains
unchanged. No new experiment or next milestone is authorized by this note.

Working title: **Prompt design and the cost of a correct answer: tokens, estimated energy and verified yield in small-model code generation**

## 1. Research question
How do common prompt design choices (instruction style, few-shot examples, reasoning requests, output-length constraints, instruction verbosity) change token use, latency, estimated energy and task success for small open-weight code models running locally, and what is the energy cost per *correct* solution?

## 2. What is already known (read first; this is a replication-plus-extension)
Earlier work reports that inference energy is driven mainly by output length and response time, that targeted prompt phrases which shorten outputs can cut energy while preserving quality, and that prompt characteristics themselves show weak association with energy. Our contribution is deliberately modest:
1. A **verified-yield metric**: energy (and tokens) per correct solution, not per response.
2. A **controlled comparison of prompt variants** on code tasks with automatic correctness checks.
3. A replication across 2 to 3 small model sizes on consumer hardware.
Do not claim novelty beyond this.

## 3. Hypotheses (fixed before any run)
- **H1:** Output tokens explain most of the variation in latency and estimated energy across prompt variants.
- **H2:** Concise-output prompts reduce tokens and energy with little loss in pass rate on easy tasks, but may lower pass rate on harder tasks.
- **H3:** Few-shot examples raise input tokens and may raise pass rate; the net effect on energy per correct solution depends on whether it removes failures.
- **H4:** Step-by-step reasoning prompts raise tokens and energy substantially; benefits concentrate on harder tasks, so energy per correct solution may be worse overall.
- **H5:** Longer instructions with the same demand raise prompt-processing cost but change total energy little because output length dominates. Compare the long code-only P5 instruction with the shorter code-only P1 instruction. P2 records tokens and timings; energy is assessed only in later milestones.
Report results against each hypothesis, including negative results.

## 4. Scope
- Environment: Python 3.13 (64-bit), per the owner's 2026-10-17 update; validated exact patch version is recorded in `docs/ENVIRONMENT.md`.
- Local inference only. Open-weight models of roughly 0.5B to 3B parameters that run on a laptop (exact choices fixed in `config.py`, with licences checked).
- Tasks: 30 to 60 short Python programming tasks with unit tests, from a permissively licensed benchmark subset (for example HumanEval or MBPP, after checking licences), split into easy and harder groups by a baseline pass rate. Note possible training-data contamination as a limitation.
- API models: out of scope for energy (it cannot be measured). Optional token-count-only comparison, clearly labelled as such.

## 5. Protocol
- **Prompt variants (pre-registered):** P0 minimal baseline; P1 "return only code"; P2 "explain, then code"; P3 few-shot with 1 and 3 examples; P4 step-by-step reasoning then code; P5 long code-only instructions. Exact wording and assembly are in `docs/PROMPTS.md` and config.
- **Decoding:** deterministic (temperature 0 or fixed seeds), fixed `max_new_tokens`, identical stop rules.
- **Correctness:** extract code, run unit tests in a restricted sandbox (see AGENTS.md safety rules), record pass or fail, timeouts and extraction failures separately.
- **Repeats:** revised P4 two-stage design: one repeat on all 40 tasks, plus two extra repeats on a preselected 10-task subset.
- **Measurement:** Primary: **CPU Package Power** logged by HWiNFO (confirmed available on the owner's Intel i5-13420H laptop) to CSV at a 500 ms interval and integrated over each generation window. The runner records start and end timestamps on the same clock, and an idle baseline measured for 60 seconds before each batch is subtracted. CodeCarbon was tested in P3 and is disabled for the prospective full run after the owner's 2026-10-20 amendment below. Also record tokens in, tokens out, wall time and tokens per second. CPU package power excludes memory, display, storage and the rest of the laptop, so say so clearly and treat results as relative comparisons on one machine. Flag any generation shorter than about 3 seconds as low resolution. If a plug-in wall power meter is available, calibrate on a small subset and report it.
- **Machine rules:** plugged in, Windows Power mode set by the owner to Best performance, close other heavy apps, fixed thread count, cool-down gaps between batches. Record actual observed power mode and AC state; do not replace observations with the intended setting.
- **Scale check:** P4 has 560 stage-1 requests plus 280 stage-2 requests = 840. This supersedes the earlier 1,680-request proposal for run-time feasibility, decided from timing rather than outcomes. Historical sections below retain the original proposal for provenance.

### Owner decisions before P3 (2026-10-19; measurement not started)

- **Exclude all P2 smoke rows from research analysis.** The 35 smoke rows are
  harness validation only, not part of the 1,680 main-run generations. Descriptive
  smoke summaries are labelled as such and do not test the hypotheses. Warm-up,
  determinism and calibration records also stay outside the main analysis.
- With scored keep_alive=0, report two baseline-adjusted CPU package energy
  estimates from the HWiNFO log: **total request energy** over [request_start,
  response_end], including model loading; and **estimated post-load energy**
  over [request_start + load_duration/1e9, response_end]. The owner selects the
  latter as the prospective **primary** measure; total request energy remains
  available alongside it. Keep the raw power readings and timings unchanged.
- API durations are aggregate measurements, not synchronized phase timestamps.
  Anchoring load to the client request start assumes negligible queue/transport
  offset. Therefore the post-load window is an approximate proxy, not a directly
  observed loading boundary or proof that all loading energy has been removed.
  Report client wall time minus API total_duration separately. Retain overhead;
  do not distribute it among phases or force their times to add up.
- The optional **approximate phase split** uses seconds L=load_duration/1e9,
  P=prompt_eval_duration/1e9, G=eval_duration/1e9 and D=total_duration/1e9.
  Prompt processing is placed at [request_start+L, request_start+L+P]; decoding
  at [request_start+L+P, request_start+L+P+G]. These are duration-aligned proxies,
  not independent direct measurements of input/output energy. Always label them
  approximate and preserve the signed residual D-(L+P+G).
- **Owner-approved tolerance:** flag a phase-sum mismatch when
  abs(D-(L+P+G)) > max(0.1 seconds, 0.05*D). This is a timing consistency flag,
  not evidence of precise boundaries. Also flag invalid/out-of-request windows,
  missing/nonfinite/negative durations, missing sensor coverage, and windows
  shorter than about 3 seconds at the registered 500 ms sensor interval.
  Do not silently clip boundaries, repair durations or drop flagged rows.
- Report load_duration distributions by model and prompt, with counts and
  uncertainty/dispersion, so loading overhead remains visible. Subtract the
  measured idle baseline over the duration of each reported window separately.
  CodeCarbon remains a secondary cross-check; do not invent phase-specific
  CodeCarbon measurements from whole-request estimates.
- These are prospective P3 decisions only. Implement the windows, flags and
  explicit output columns in the P3 plan/config/schema change before any pilot;
  accepted P2 raw/result files remain unchanged. P3 extends executable fingerprints; resuming an old P2 batch requires its original commit.

Duration-field definitions: [Ollama generation API](https://docs.ollama.com/api/generate).

### P1 registration (2026-10-16)
- Models: `qwen2.5-coder:0.5b` and `qwen2.5-coder:1.5b` in Ollama; both exact tag pages list Apache 2.0. Record local digests in P2 because tags can change.
- HumanEval is MIT licensed. Use the unchanged archive at revision `6d43fb980f9fee3c892a914eda09951f772ad10d`, SHA-256 recorded in `data/manifest.json`; retain its licence notice.
- Sample 40 IDs without replacement from the numeric population 0..163 with `random.Random(1729)`, then sort numerically. Explicit IDs are in `experiments/config.py`. No task is replaced after reference checks.
- Prompt wording and three original synthetic examples are in config. P3_1 uses the first example; P3_3 uses all three in the recorded order. Actual prompt assembly and code extraction remain P2.
- The Windows test runner uses a five-second deadline, 256 MiB commit-memory cap, one-process Job Object, curated computation imports/builtins, socket/DNS audit denial, fresh temp directory and a minimal environment. Candidate script loading occurs only in the worker. Python hash and random seeds are 1729. Cleanup retries transient Windows locks for up to two seconds after reaping; persistent cleanup errors are logged as infrastructure failures. See `docs/SAFETY.md` for exact restrictions and the absence of an OS security boundary.
- HumanEval/160 uses eval in its original reference. The runner substitutes a numeric arithmetic AST interpreter for that builtin, equally for references and model solutions, without changing benchmark records. Policy rejection remains distinct from incorrectness.
- P2 runtime contract: local Ollama `/api/generate`, temperature 0, fixed seed 1729, one fixed `num_predict` output-token cap and identical stop rules. Register the cap and thread count before generation; P1 does not choose them through test performance. Read `prompt_eval_count`, `eval_count`, `total_duration`, `load_duration`, `prompt_eval_duration`, and `eval_duration` from responses; duration fields are nanoseconds. Do not estimate token counts from text. Persist raw response fields, local model digest and Ollama version. CPU-only execution is intended.
- Owner-decided difficulty rule (2026-10-17): group each task by whether `qwen2.5-coder:1.5b` passes with prompt P0 in a calibration run. Fix the calibration settings and resulting grouping in config before the main run. Exclude P0 from group-wise comparisons to avoid defining and assessing its performance on the same grouping criterion. Add a sensitivity grouping by reference solution length. Record this rule only in P1: no grouping code, calibration, labels or length threshold yet. Calibration generations are additional to the approximately 1,680 main-run generations.
- Few-shot examples must be original and not duplicate or specialize any selected task. The semantic audit is in `docs/FEW_SHOT_REVIEW.md`. The initial add-seven example was replaced before any inference because it specialized HumanEval/53.

## 6. Results schema (one row per generation)
### P2 registration, owner authorized proceeding on 2026-10-19

- Fixed decoding: temperature 0, seed 1729, num_thread=8, num_ctx=4096, num_predict=768, num_gpu=0, no custom stop strings. Seven arms and 40-task population are unchanged.
- Exact P5: "Please read the following Python function signature and docstring carefully. Complete the function so that it satisfies the docstring and handles edge cases correctly. Return only the code for the completed function, with no explanation."
- Select the last complete python/py/unlabelled fenced block that parses and defines the required top-level function; otherwise use the whole stripped response. Prepend everything in the trusted task prompt before its target function, including imports/helpers, before sandbox checks and execution. No reference body is supplied. Validate the new path on all 40 reference solutions.
- Determinism compares text, prompt_eval_count and prompt_eval_duration on two identical requests. Conservative operational cache signal: either count or duration decreases on the second request (a duration decrease is not proof of cache reuse). If either model signals reuse, use keep_alive=0 for all scored runs; otherwise -1. Persist the decision before the smoke run and reuse it on resume. Invalid probe fields stop the run. Unload/verify absence of probe and warm-up models before the first scored call when zero is selected; record load_duration separately for every request.
- The 1.5b smoke run covers task IDs 0, 1, 11, 13, 14 across seven arms once (35 scored rows). Calibration/warm-up/determinism outputs are labelled and excluded from scored rows but retained in raw JSONL. Energy columns and difficulty_group remain empty.
- Warm-up: one saved, unscored READY call per used model per process session, with keep_alive=-1. For a fresh batch it precedes that model's determinism pair. The resolved cache decision then governs scored requests. Explicit unload checks use a 10-second deadline and 0.1-second polling. Responses from control requests are audited too.
- Persistence: immutable manifest and cache_policy.json; append-only requests.jsonl (intent), raw.jsonl (HTTP status, exact response bytes in base64, request and UTC/monotonic timings), sessions.jsonl (observed environment), results.jsonl (SPEC row plus reason/sandbox details). results.csv is a derived view. Raw references use raw.jsonl#request_id relative to the batch folder.
- Resume reuses saved raw responses and skips every completed row, including failures. It rejects changed registration/runtime/model metadata, damaged journals, duplicate IDs and uncertain in-flight requests. An OS file lock excludes concurrent writers. Interrupted requests without a saved response require investigation, never automatic regeneration. A completed resume makes no API calls.
- Failure precedence: transport/API error; truncated at done_reason=length or eval_count >=768; no_code for empty/unrecognizable output; syntax_error for recognizable malformed function source; no_code for no required top-level function; policy_rejected; sandbox test_failed (including candidate runtime errors), timeout, memory_limit or infrastructure_error. Details are preserved. HTTP timeout stops the batch after recording its failed row to avoid overlapping server work.
- tokens_per_second is eval_count / (eval_duration / 1e9), not wall-time throughput. wall_seconds spans sending the HTTP request through receiving the body; it excludes code testing. All native API timings, including load_duration, remain in raw responses. No phase energy is inferred from timings in P2.

### Scored row columns
`run_id, timestamp, model, model_hash, prompt_id, task_id, difficulty_group, repeat, seed, input_tokens, output_tokens, wall_seconds, tokens_per_second, cpu_pkg_energy_wh, codecarbon_wh, idle_baseline_w, co2e_kg, passed, failure_type, raw_output_path, python, runtime_version, codecarbon, cpu_model, os, power_mode`

### P3 pilot registration (2026-10-19; owner approved 2026-10-20)

The pilot selects 20 of the existing 40 tasks with random.Random(1729), sorted
numerically: 0, 11, 13, 14, 29, 46, 53, 55, 76, 90, 92, 94, 105, 117, 122, 128,
133, 140, 143, 160. Cross P0/P1/P2/P4 with both models and two repeats, then shuffle
with seed 1729: **320 requests**. Pilot rows are diagnostic and excluded from the
main analysis. Prompts, extraction and decoding remain unchanged. keep_alive=0
applies to every scored request. Config fixes the accepted P2 Ollama version and
model digests; mismatches stop execution. No pilot starts without owner approval.

HWiNFO must log CPU Package Power in watts at 500 ms. Explicit CSV encoding,
delimiter, decimal separator, date/time formats, UTC offset and sensor column
are recorded; ambiguous headers require an explicit column index. Do not guess
dates, sort timestamps or repair bad readings. Preflight checks observed AC/Best
performance, Python 3.13 64-bit, log growth and advancing timestamps over 3 s,
freshness within 3 s and recent median cadence within 20% of 500 ms.

Each process session, including a resumed session with remaining requests,
warms/unloads both models, waits 5 s, then collects a 60 s quiet baseline.
Baseline watts are time-weighted trapezoidal energy divided by duration.
A minimum 5 s gap follows previous testing/unload before the next scored call.
Integration interpolates window boundaries between samples, never extrapolates.
Subtract baseline watts times window seconds / 3600 independently for each
window. Retain and flag negative adjusted values. Gaps exceeding 1 s invalidate
the affected energy estimate; windows shorter than 3 s are low resolution.
Invalid/missing estimates remain empty with flags, never silently dropped.

Total, primary post-load and approximate phase windows and the approved mismatch
tolerance follow the owner decisions above. UTC/monotonic discrepancy is also
flagged at max(0.1 s, 5% wall time). Preserve the signed API phase residual and
wall time minus API total. Sensor polling does not guarantee internal sensor
refresh frequency or accurate sub-second phase energy.

CodeCarbon 3.0.4 uses offline machine mode, country IND, one-second sampling,
no external reporting, and named baseline/request tasks. Preserve its native
record and actual task envelope duration. Subtract its own idle rate over its
own envelope; do not substitute HWiNFO idle watts or allocate CodeCarbon energy
to phases. It is a secondary CPU/RAM hardware estimate, not measured wall power;
Windows fallbacks can make it insensitive to workload. Check native observations
and runtime diagnostics during the approved pilot before interpreting it.

Persist request intents, exact raw responses and original answer rows unchanged.
Append baselines.jsonl and measurements.jsonl. Copy the live CSV to an append-only
per-session mirror in sensors/; record each used byte-prefix length and SHA-256.
The original sensor file is never modified. Resume reuses saved responses; an
uncertain request is never retried automatically. Completed resume makes no API
calls. Missing sensor/secondary measurements retain the answer and stop new work
for inspection. Sensor capture waits at most 10 s for a trailing boundary sample.

P3 energy.csv is a derived join: the original 26 scored columns followed by
`record_kind, include_in_main_analysis, energy_tool, energy_mode, primary_window,
cpu_pkg_total_raw_wh, cpu_pkg_total_wh, cpu_pkg_post_load_raw_wh,
cpu_pkg_prompt_eval_wh, cpu_pkg_decode_wh, energy_flags, load_seconds,
phase_residual_seconds, wall_minus_api_seconds, baseline_id, codecarbon_tool_mode,
codecarbon_raw_wh, codecarbon_idle_w, codecarbon_seconds`.
Here cpu_pkg_energy_wh is primary adjusted post-load energy; codecarbon_wh and
co2e_kg are secondary, independently baseline-adjusted whole-envelope estimates.
Raw phase energy and boundaries remain in measurements.jsonl. Empty CSV fields
mean unavailable, not zero. All rows carry pilot/main-analysis exclusion labels.

energy-summary.json reports load count/mean/sample SD/min/max/missing by model
and prompt, paired-repeat primary energy spread and flagged/missing counts.
The full-run time proxy is 1,680 times mean(request wall time + 5 s), plus 60 s.
It excludes test, warm-up, control and sensor-wait overhead and extrapolates only
four arms; it is not a promised runtime. No hypothesis analysis is implemented.

## 7. Analysis plan (the owner writes this)
1. Per model and prompt: mean and 95% bootstrap interval for input tokens, output tokens, energy and pass rate.
2. Energy per correct solution; Pareto plot of pass rate versus energy.
3. Regression of energy on output tokens and on input tokens (H1); report R squared and residuals.
4. Breakdown by the owner-decided calibration group (H2, H4), excluding P0 from group-wise comparisons; sensitivity grouping by reference solution length. No grouping is implemented in P1.
5. Measurement noise from repeats; check whether conclusions hold when the noisiest runs are removed.
6. Limitations: estimated energy, one machine, small models, small task set, benchmark contamination.
Avoid strong significance claims; use descriptive statistics and bootstrap intervals.

## 8. Milestones and acceptance criteria
**P1: Scaffold, tasks and sandboxed test runner.**
- Repo layout, pinned requirements, `config.py` with the pre-registered prompts, models and task list, task loader, restricted-subprocess test runner (`docs/SAFETY.md`).
- *Accept:* reference solutions for all tasks pass, deliberately wrong solutions fail, a runaway or malicious test sample is killed by the timeout; tests pass.

**P2: Local model runner and prompt variants.**
- Chosen runtime (justified in the plan), deterministic decoding, exact token counting, prompt builder for all variants, raw generations saved as JSONL.
- *Accept:* a smoke run on 5 tasks across all prompts completes; token counts match the runtime's own counts; failures are logged.

**P3: Energy tracking.**
- CodeCarbon integration, idle baseline subtraction, repeats, machine metadata, run-time estimate for the full run.
- *Accept:* owner-approved 320-request pilot completes; energy columns filled or explicitly flagged missing; the report command gives spread across repeats and load summaries; measurement modes are stated. Offline tests alone do not complete live acceptance.

**P4: Full run and analysis scripts.**
- Resumable full run (skips completed rows), analysis scripts for section 7 producing CSV and PNG.
- *Accept:* an interrupted run resumes without duplicates; every plot labels the tool and mode.

**P5: Report scaffold and reproducibility.**
- `docs/REPORT_TEMPLATE.md`, README with exact commands, `docs/REFERENCES.md`.
- *Accept:* a fresh clone can reproduce a one-task-subset run following the README.

## 9. Report outline (3 to 4 pages, written by the owner)
1. Question, prior work and hypotheses.
2. Method: tasks, models, prompts, correctness checks, energy measurement and its limits.
3. Results: three or four figures and one summary table.
4. Discussion: which hypotheses held; practical guidance on prompts that save energy without losing correctness.
5. Limitations and next steps (larger models, GPU measurements, real power meters, other tasks, links to the validity and solvability studies).
6. References.

## 10. Background reading (find by title and verify)
- "Towards Sustainable NLP: Insights from Benchmarking Inference Energy in Large Language Models" (2025).
- MELODI: an inference-time energy profiling framework (arXiv 2407.16893).
- TokenPowerBench: benchmarking power consumption of LLM inference (AAAI).
- "Green AI" (Schwartz et al.); "Energy and Policy Considerations for Deep Learning in NLP" (Strubell et al.).
- "Evaluating Large Language Models Trained on Code" (the HumanEval paper).
- CodeCarbon documentation, especially how it estimates power.

## 11. How this extends (for pitches)
With more resources: GPU measurements with real power meters, larger models, other task types, and a link to the owner's studies on LLM-generated problem validity and solvability (energy and token cost per verified problem).


## P3 execution audit (2026-10-20)

Owner-approved pilot completed 320/320 requests using the registered settings.
No-op resume made zero requests. Primary estimates exist for 319 rows; the
remaining row is retained with a sensor-gap flag. All prompt-eval windows are
low resolution; CodeCarbon native power was constant across requests, so it
cannot corroborate workload-dependent energy differences. See
`docs/P3_PILOT_REVIEW.md`. These observations do not change the pre-registered
protocol, exclusions or thresholds. P4 has not been started.


## Owner amendment after P3, before any full run (2026-10-20)

This prospective amendment explicitly supersedes the phase-energy and secondary
CodeCarbon parts of the historical pilot protocol, based on pilot diagnostics.
Keep the historical registration and raw evidence intact; do not recalculate or
repair pilot results. FULL_RUN_MEASUREMENT in config records these decisions.
This is not authorization to execute P4 or change prompts/tasks/repeats.

- Drop prompt-versus-decode energy estimates from the full run: all 320 pilot
  prompt windows and 46 decode windows were low resolution. API phase durations
  and token counts may still be retained as metadata, not measured phase energy.
- Primary measure: whole estimated post-load CPU package energy per request.
  Report gross and baseline-adjusted net post-load energy; also retain total
  request gross/net energy and load durations. The start+load-duration boundary
  remains approximate. Input and output token counts are predictors, not separate
  energy meters. H5 cannot establish input-phase energy from these data.
- Disable CodeCarbon entirely for full-run execution. Its constant native CPU
  42.5 W/RAM 10 W estimates cannot corroborate prompt effects. Retain old records
  and the pinned dependency only for historical pilot reproduction. The future
  full-run path must never construct or start its tracker.
- Pre-register all-row reporting with all available energy (including failures
  and low-resolution estimates), and a sensitivity analysis excluding rows with
  post_load:low_resolution. Missing/invalid energy stays missing, never zero;
  report denominators and flags. Correctness reporting keeps every row. Do not
  filter by phase flags or remove negative net values. Pilot illustration uses
  319 available energies; sensitivity uses 285 after excluding 34 short windows.
- Owner declined the new two-minute idle check. The pilot baseline remains
  15.4201366935 W; the earlier ~6.5 W figure lacks a supplied comparable source.
  Do not attribute the difference to power mode without evidence. Future batches
  still require their registered 60-second idle baseline. Gross/net reporting
  makes the dependence on baseline subtraction visible.
- The owner's current screenshot shows 10.864 W current CPU Package Power and
  13.643 W displayed average, but no controlled quiet-window provenance. It is
  contextual evidence, not a replacement baseline.

The requested pilot scatterplots and repeat comparisons are diagnostic only,
not hypothesis tests. They do not authorize dropping tasks or tuning prompts.
Changing config updates source fingerprints; historical resume requires the
original pilot commit 38f9c15 (or 87d1f46, with identical executable sources).


## P4 registration (2026-10-20; implementation approved, live run NOT approved)

P3 is accepted by the owner. Stage 1: 40 registered tasks x seven prompt arms x
two models x repeat 1 = 560. Stage 2: 10 tasks x seven arms x two models x
extra repeats 2 and 3 = 280. Total 840 scored requests. Reason: run-time
feasibility based on timing, not correctness/energy outcomes. Select the subset
using random.Random(1729).sample(existing 40 IDs,10), then numeric-sort:
HumanEval/{11,13,53,55,92,105,117,122,128,143}. No substitutions.
Independently shuffle each stage with seed 1729; complete stage 1 before stage 2.
Stage-1 hypothesis scaffolds do not pool stage-2 repeats, so the subset is not
overweighted. Noise diagnostics use repeat pairs within stage 2 separately.
Smoke, pilot, warm-up and any calibration generations are excluded.

Primary energy is whole estimated post-load CPU package energy per request,
reported gross and net; also retain total-request gross/net. No input/output
phase-energy attribution: all pilot prompt-eval windows were low resolution.
CodeCarbon is not imported or started by the full-run path; old pilot evidence
is retained and CodeCarbon is discussed only as a limitation. Native API phase
durations may be logged for timing diagnostics, never interpreted as phase energy.
Both all-available and primary-low-resolution-excluded analyses are required;
missing energy is not imputed, failures stay visible, report counts explicitly.

Each explicitly approved run-block invocation stops launching requests after
3 hours, finishes the current bounded request and closes the block. A 4-hour
safety ceiling reserves request/baseline/cleanup time before new launches.
No automatic next block. Elapsed limits use monotonic time; OS suspension can
cause an overrun that is flagged rather than hidden. Each block starts/ends with
60-second idle baselines after model unload and a 5-second quiet gap. Net uses
the starting baseline. Flag baseline drift if abs(end-start)>max(1 W,0.1*start).
Retain signed drift. Never replace the starting baseline after seeing results.
Missing end baselines are flagged for every affected row; interrupted blocks
are not retroactively assigned a later idle measurement. Fresh blocks obtain
new baselines. Existing 500 ms growth/freshness checks and hardware requirements
remain. Failed preflight makes no model call. Failed/uncertain requests are
never automatically regenerated. Completed resume makes zero API requests.

Append-only block events, request intents, exact raw responses, answer outcomes,
measurements and byte-preserving sensor mirrors support audit. A derived full-run
CSV has the original scored fields except CodeCarbon/co2 fields, plus stage,
block_id, record_kind, include_in_main_analysis, energy_tool, energy_mode,
primary_window, cpu_pkg_total_raw_wh, cpu_pkg_total_wh,
cpu_pkg_post_load_raw_wh, energy_flags, load_seconds, wall_minus_api_seconds,
end_idle_baseline_w, baseline_drift_w and block_status. cpu_pkg_energy_wh is
net post-load energy; idle_baseline_w is the starting baseline. Missing values
are empty. Stage 2 is labelled noise-only. End-baseline flags are joined by
block ID without modifying earlier answer/measurement journals.

Analysis scaffolds: seeded task-level bootstrap (seed 1729, 2,000 draws,
95% percentile intervals), per-model/arm mean tokens, gross/net energy and pass
rate; ratio of total energy/tokens to number correct, with zero-correct or
missing-energy ratios explicitly unavailable; per-model OLS with intercept and
both input/output tokens, R2/residual plots; pass-rate/energy Pareto plots;
stage-2 repeat spread; optional frozen calibration and reference-length maps.
Difficulty/length-group outputs remain unavailable until owner supplies a frozen
map and rule; P0 is excluded from all group-wise comparisons. No difficulty
labels are inferred from scored outcomes. No statistical significance claims or
written interpretation are generated. Report scaffold repeats limitations and
leaves interpretation to the owner. Calibration/group definition may require a
separate registered step; no such inference requests are part of this command.


## P4 grouping registration (2026-10-21; before calibration/main outcomes)

Owner selected a separate calibration on all 40 tasks, 1.5b/P0, one repeat,
numeric task order, unchanged seed 1729/temperature 0/context 4096/token cap 768/
threads 8/CPU-only decoding and the accepted extraction/sandbox. keep_alive=0;
save an excluded warm-up, unload before each request. No energy measurement.
Successful sandbox outcomes label solved; all nonpassing candidate outcomes label
failed, preserving failure types. Infrastructure/HTTP errors stop for investigation
and block label export. No automatic retries or replacement tasks. Freeze the
complete map and provenance in P4_GROUPING before the main run. P0 is excluded
from both grouping comparisons. Separate calibration avoids defining labels from
main outcomes, but does not establish stochastic independence or intrinsic task
difficulty. Counts are unknown: the pooled pilot pass rate does not predict the
1.5b/P0 calibration pass rate. Small groups are descriptive and noisy.

Reference length: count physical lines of canonical_solution only, excluding
blank lines and lines whose stripped form starts with #. Inline-comment code
lines and string/docstring lines count. Split at the median of all 40 lengths;
length <= median is short, otherwise long. Freeze counts, median and explicit
labels before calibration. No threshold selection from generated outcomes.

Owner clarified the earlier ~6.5 W observation was under Energy saver, unlike
the Best performance pilot baseline. It is not a matched idle comparison or
basis for replacing 15.4201366935 W. A new quiet two-minute check is pending owner
readiness and log path; preserve original pilot measurements.

Planning estimate: 105 minutes / 320 * 840 = 275.625 minutes (4.59 hours), before
allowing for arm mix, different tasks, block baselines and machine conditions.
Two blocks may suffice; this is not a completion guarantee. Few-shot input
processing adds work even if output is shorter. Full-run approval remains pending.

Reference-length computation frozen before generation: median 6.0 lines, 21 short
and 19 long. Explicit labels/counts are in P4_GROUPING. The main runner now
requires both complete maps before making any request. Calibration and full-run
execution were deferred by the owner until night; no calibration outcomes exist.


Owner execution authorization (2026-10-21): run only the separate 40-task
calibration now through `python -m experiments.run_p4 calibrate --owner-approved`.
This command needs no HWiNFO and never dispatches run-block. Freeze resulting
maps before any scored run. Main execution is planned for tonight, not started:
ask the owner whether HWiNFO logging has begun and confirm its full new CSV path
before preflight. Check 500 ms growth/freshness, AC/Best performance, awake/lid
settings, runtime/digests and frozen registration before the main program.


## P4 grouping freeze: 2026-10-21T13:00:18+05:30

Owner-approved calibration completed all 40 registered tasks using 1.5b/P0,
one repeat and unchanged registered decoding/extraction/sandbox (source commit
cc12c44). No energy measurement or scored P4 block occurred. Raw evidence:
`results/p4-calibration-2026-10-21`. One excluded warm-up; 40 calibration responses.

Calibration grouping: **26 solved, 14 failed** (13 test_failed, 1 sandbox timeout).
Solved means the saved outcome passed all tests; failed means the saved candidate
did not pass. No retries, repairs, substitutions or main-run outcomes were used.
No infrastructure/API failures occurred. Completed resume made zero HTTP calls;
requests/raw/results/sessions/manifest SHA-256 values remained unchanged.

Reference-length grouping: **21 short, 19 long**, median **6.0** qualifying lines.
Count canonical_solution physical lines excluding blank and comment-only lines
(stripped prefix #). Inline-comment code and string/docstring lines count.
Short means count <= median across the fixed 40, including ties; otherwise long.
Counts/labels were frozen before calibration and remain unchanged. Both explicit
maps, freeze timestamp and calibration evidence hashes are now in P4_GROUPING.
P0 stays excluded from group-wise comparisons. These small groups are descriptive;
a single calibration outcome is not intrinsic difficulty or guaranteed stability.

| Task | Calibration group | Reference lines | Length group |
| --- | --- | ---: | --- |
| HumanEval/0 | solved | 7 | long |
| HumanEval/1 | solved | 14 | long |
| HumanEval/11 | solved | 6 | short |
| HumanEval/13 | solved | 3 | short |
| HumanEval/14 | solved | 4 | short |
| HumanEval/24 | solved | 3 | short |
| HumanEval/29 | solved | 1 | short |
| HumanEval/39 | solved | 15 | long |
| HumanEval/43 | solved | 5 | short |
| HumanEval/46 | solved | 7 | long |
| HumanEval/53 | solved | 1 | short |
| HumanEval/55 | solved | 5 | short |
| HumanEval/57 | failed | 3 | short |
| HumanEval/73 | solved | 5 | short |
| HumanEval/74 | solved | 10 | long |
| HumanEval/76 | failed | 6 | short |
| HumanEval/89 | failed | 8 | long |
| HumanEval/90 | failed | 2 | short |
| HumanEval/92 | solved | 5 | short |
| HumanEval/94 | solved | 13 | long |
| HumanEval/96 | failed | 10 | long |
| HumanEval/101 | failed | 10 | long |
| HumanEval/102 | failed | 7 | long |
| HumanEval/105 | solved | 19 | long |
| HumanEval/115 | failed | 1 | short |
| HumanEval/116 | solved | 1 | short |
| HumanEval/117 | failed | 9 | long |
| HumanEval/122 | failed | 1 | short |
| HumanEval/127 | failed | 15 | long |
| HumanEval/128 | solved | 3 | short |
| HumanEval/133 | solved | 5 | short |
| HumanEval/140 | failed | 20 | long |
| HumanEval/143 | solved | 11 | long |
| HumanEval/144 | failed | 7 | long |
| HumanEval/148 | solved | 9 | long |
| HumanEval/150 | solved | 8 | long |
| HumanEval/156 | solved | 14 | long |
| HumanEval/158 | solved | 1 | short |
| HumanEval/160 | failed | 4 | short |
| HumanEval/162 | solved | 2 | short |

Calibration evidence SHA-256:

- `manifest.json`: `b1350499514a04579059ff3d426daa2d446bb2158d581c3d181ad67fd915552b`
- `raw.jsonl`: `d20989f0f3fca69705381accafdaf2c070b4ff0e6190bbc25d4dcb8c02162889`
- `results.jsonl`: `03bc609b86f31f8a8058e9d39a1c8bec6e22d7115850e8f2244954a1b638e893`

The main run remains unstarted. Before tonight's main execution, ask whether
HWiNFO logging has begun and confirm the new CSV path; run the registered
preflight and obtain main-block approval. Calibration does not grant that approval.


## Post-collection manuscript amendment (2026-10-27)

Owner requested a revised professor-facing experiment paper. This supersedes the
presentation note's instruction to leave the old brief unchanged, not the original
protocol. No new model calls, task exclusions or rescoring are authorized.

Post-hoc analyses, chosen after results were available: five task-paired contrasts
per model (P1-P0, P2-P1, P4-P1, P3_1-P0, P5-P1), task-bootstrap ratio intervals
for total energy / total correct, failed-attempt energy shares, energy / generated
token, and alternate constant end/midpoint baselines. Use 2,000 draws, seed 1729,
95% percentile intervals; paired contrasts align tasks and resample whole pairs.
Intervals are pointwise, not multiplicity-adjusted, and do not capture systematic
baseline error. Report discordant pass counts and do not claim equivalence from
an interval containing zero. Zero-success bootstrap draws are counted explicitly;
if any occur, mark the ratio interval unavailable rather than drop draws.

P1-P0 is the lead contrast. P3-P0 is an example-guided prompt comparison: exact
wording also changes to following the example(s), so it does not isolate examples.
Stage 1 alone supplies the primary descriptive results. Stage-2 repeats remain
separate; add pilot repeat diagnostics (not hypothesis evidence) without pooling.

Use saved post-load window seconds for end and midpoint baseline scenarios;
keep registered start-baseline estimates and all raw files unchanged. Endpoint
scenarios cannot reveal or correct the baseline trajectory. Low-resolution
exclusion is duration-dependent selection, disproportionately removing cheap
requests; energy per token is a complement, not a repair or decode-phase estimate.

Review 64 selected stage-1 failures: first three failures by run ID per model/arm,
plus all cap/no-code cases and all NameError/timeout cases. An AI-assisted source
review is not independent human adjudication; owner review remains pending.
Record categories and concrete evidence in P4_FAILURE_REVIEW.csv, distinguish
all-row machine labels from sample mechanisms, and never infer sample prevalence.
No fixed scoring/extraction rule or saved outcome changes. Draft conclusions
remain subject to final author review before external sharing.


## Professor packet formatting amendment (2026-10-27)

Owner requests external-facing presentation with 14-point Times New Roman body,
continuous page flow, explicit comparisons within P0/P1/P5, P3_1/P3_3 and P2/P4,
and P1/P3_3/P2 across output, energy and per-correct metrics. Existing categories
organize separate arms; no pooled category estimates or new treatment definitions.
Missing requested views appear once in a single large-format landscape final
comparison sheet (30 panels). Chart captions retain measurement mode, stage,
denominators and drift caveat. This changes presentation, not design or outcomes.
The owner's removal of the author line is preserved. AI-assisted annotation
provenance remains explicit; no independent human second review is implied.
An outreach email draft is local only. No sending or new generation authorized.


Editorial addition (2026-10-27): owner requested an opening rationale before the
abstract explaining why prompt-related resource use merits evaluation alongside
correctness. The opening states the small exploratory scope and separates
measured CPU package estimates from unmeasured battery, financial or carbon
outcomes. No experimental or statistical registration changes.


## Report wording and summary amendment (2026-10-28)

Owner selected the exact report title: Report and code: Prompt design and the
energy cost of correct code. Rewrite abstract/conclusion in plain language and
retain concrete findings and caveats; P1-P0 is one comparison, not the headline.
Use report terminology. Describe AI-assisted setup, automated Ollama requests,
figures/text and source-review annotations accurately, without the phrase
analysis implementation or implying independent human annotation. Add a two-page
Times New Roman overview with why/hypotheses/observations/plots/conclusion.
This is presentation only: existing data, H1-H5 and statistical rules unchanged.

## Utilisation core harness (2026-11-16)

The separately registered follow-up uses studies/utilisation/config.yaml. The
CLI and journal contract are in studies/utilisation/HARNESS.md. Compilation and
offline validation were authorised. Live generation requires the resolved
benchmark pins, dated preregistrations and a frozen stimulus schedule.

## Pilot authorisation, 2026-11-16

The owner authorised a diagnostic 22-call pilot: five tasks, P1 and P3_1,
one sample on each model, and one exactly 4000-input-token request per model.
The plan is docs/plans/UTILISATION_PILOT.md and entry point is
experiments/utilisation_pilot.py. The pilot uses explicit raw rendering of the
inspected Qwen template and an independently hashed tokenizer. Measurements
are excluded from later hypothesis tests. HWiNFO must be live before calls.

## Focused amendment · 2026-11-16

Owner chose MAIN Focused and deferred APPENDIX. The fixed sweep permutations,
prefix extension rule, energy aggregation and E0 preregistration are recorded
in studies/utilisation/task-orders.json and studies/utilisation/prereg/.
The first 100 completed M3 calls require a timing report and owner review
before continuation. Owner approved width threshold 0.20 on 2026-11-17. Freeze is
2026-11-22 23:59 IST; all pending work plus extension must fit within 70%
of remaining wall-clock hours. This timing gate applies to every extension. Task-only extension retains
the Focused factors; it does not use the earlier expanded-grid Balanced count.
E4 remains primary energy evidence and remains deferred with APPENDIX.

## Terminal supervisor (2026-11-17)

experiments/supervise.py launches the terminal worker, retries unexpected
worker exits and preserves per-call retry budgets across recovery. It runs
generation in batches followed by offline evaluation. The pipeline stops after
100 M3 calls and writes CHECKPOINT.md. The pipeline manifest must include
approved M3 stimuli, held-out policy and benchmark-reference decision before
live execution. Missing decisions produce a checkpoint with no generation.

Hard stops are input-count mismatch, fewer than 18 energy-covered observations
in the last 20 calls, more than 3% exhausted logical API calls, registered
baseline drift or less than 5 GiB available disk. The caller's explicit go
does not supply missing stimulus choices. Known reference anomalies remain
visible. See studies/utilisation/SUPERVISOR.md for commands and limits.

2026-11-17 follow-up approvals: Focused M3 uses 1000/4000 complete input tokens,
middle target position and all three filler types (240 calls).
Keep HumanEval/32 with original scoring in the primary 164-task analysis and
report a separate sensitivity excluding it. Held-out policy remains pending.

2026-11-17 delegated launch amendment: P1 sample 0 is the held-out label;
samples 1/2 form subsequent independent generation comparisons. E0 primary
analysis retains samples 0/1/2. M3 texts for every task are frozen before E0,
then filtered using the previously registered eligible prefix rule.
M3 duplicate filler uses renamed copies of the target specification. Report
this operationalisation and its redundancy/confusion limitations explicitly.

## Measurement reliability amendment approved 2026-11-17

Use at most 25 calls per measurement block and require two consecutive
60-second idle windows within the unchanged max(1 W,10%) stability criterion
before the first scored call. See the dated reliability preregistration.
The 40-isolated/100-loaded final checkpoint and outcome embargo remain.
The drift hard stop remains active. Preparation waits up to six idle windows
without generation. Explicit Ollama repeat-limit aborts are future terminal
runtime failures, preserving unavailable counts; completed old attempts are
never rewritten. Report checkpoint baseline details and any initiating error.


## Owner-approved drift quality-flag amendment (2026-11-18)

For the utilisation supervisor, baseline drift is now a quality flag rather
than a hard stop. This supersedes the historical drift-stop wording above.
The threshold stays abs(end-start)>max(1 W,10% of start). Preserve gross and
start-baseline net energy as primary; join baseline_drift by block and retain
all raw data. End/midpoint baselines and excluding drifted blocks are explicitly
post hoc secondary sensitivities, extending the earlier named-block rule.
See studies/utilisation/prereg/DRIFT-AS-FLAG-2026-11-18.md.

Continue after a drift-only close, then obtain a new stable pair of 60-second
idle windows before the next at-most-25-call block. The six-window settling
limit, all other hard stops, outcome embargo and 40-isolated/100-loaded
checkpoint remain active. No generation or recovery is part of this change.


## CSV preflight diagnostics repair (2026-11-18)

Strict schema validation is unchanged: every complete row must match the CSV
header. A persistent width change requires a new HWiNFO log with a fresh header;
no malformed rows are skipped and no power-column mapping is inferred.
The v2 workflow now records ValueError/OSError failures in CHECKPOINT.md with
the active CSV path and prints the reason before exiting. Original sensor
logs and saved generations remain unchanged. Owner supplied ver3_hwf.CSV as
the new session source after ver2 developed 329-field rows under a 328-field
header. New source still needs all normal live-log and baseline checks.


## Snapshot freshness clock correction (2026-11-19)

Live CSV freshness is evaluated against wall time captured immediately after
reading the byte snapshot, before parsing it. Parsing delay is not sensor age;
preflight records snapshot_read_at and validation_delay_seconds separately.
The same correction applies before a utilisation request. Full strict parsing,
3-second freshness limit, cadence and append-growth checks remain unchanged.
This verifies the snapshot at read time, not continuous logger availability
during parsing. No energy window, raw data or research parameter changes.


## Reviewed M3 continuation (2026-11-19)

Owner reviewed the first-100 verification and requested continuation with ver5
logging. A committed review receipt binds approval to the original selected
240-call M3 schedule and published checkpoint hash. experiments.continue_m3
finishes only the remaining 140 calls, resuming append-only without repeats,
using existing short blocks, fresh stable baselines and unchanged hard stops.
Stop at 240 with a separate M3-CONTINUATION.md; preserve CHECKPOINT.md and its
outcome-access hash. No scoring, task extension or later experiment is launched.
This is execution of the remaining registered grid, not a design amendment.


## Revised memory study preparation (2026-11-20; draft, not launched)

Owner supplied revised architecture: Memory Under Interference in Small Code
Language Models, task memory/interference, behavioural memory, selective
retention and computational efficiency. Completed E0 and original M3 generation
are skipped; raw data and original registrations stay immutable. Revised grids
are separate prospective studies, never relabelled as old conditions.
Owner approved the original fixed 40-task roster shared by both models, with
independent baseline-solvable subset reporting, and reduced pilot-first M1.
The five-policy R1 replaces the earlier pending three-cell question. Exact
pilot factors, histories, summaries, preference rules, semantic distractors,
feedback sets and cache verification still require separate review/freeze.

Draft builders and an offline audit/matrix CLI do not invoke Ollama. The stated
full M1 grid requires 960 calls plus missing compatible controls; revised reduced
M3/R2 also 960; five-policy R1 400. These are calculated matrix sizes, not
authorised execution budgets or measured results. The proposed five-task M1
pilot with K=2/4 requires 60 plus up to 10 controls, pending approval.
Reuse isolation calls only with exact full request, task and model-digest
matches. E0 temperature 0.2 is not deterministic isolation; existing M3 T0
controls use num_ctx=8192, unlike revised M1/R1 defaults. No automatic reuse
across changed settings. Do not change the existing freeze without approval.
E4 fixed output length cannot identify a separate generated-token slope;
API timing regressions also do not directly measure separate phase energy.


M1 pilot approval (2026-11-20): owner approved maximum70 diagnostic calls on
HumanEval/89,94,105,144,39; K2/K4; passive/active/exact-token-matched filler;
two models and10 missing same-setting isolated controls. Exclude pilot from
main hypothesis tests. Seeded companion/partial3-first2-last position rules
and exact prompts are published before inference. Do not claim individual
owner review of every prompt; receipt records the actual grid approval.
Use unchanged registered M1 settings and evaluate new reference bundles first.


## Owner-approved timed full M1 (2026-11-21)

Owner approved1040 logical calls: original40 targets shared by both models;
K2/3/4/6; passive/active/token-matched irrelevant conditions plus80 isolated
controls. Diagnostic pilot stays excluded. New scoped config and output keep
all old registrations/results unchanged. Companion prefixes follow the seeded
fixed-roster order; target first/last balanced20/20, identical across modes and
models. If neutral-prose prefixes cannot match full input count exactly, use
repeated neutral x padding and disclose this construction. Reference bundles
must pass before generation. Exploratory post-pilot paired analyses are labelled
as such; no confirmation claim from selecting a design after pilot inspection.

Run a registered queue with7.5-hour availability ceiling. Reserve the existing
maximum request timeout3600s plus600s close allowance before every new attempt,
including retries. Approximate latest launch is6h20m after queue start. Finish
active requests, close baselines, and record incomplete pending work for resume.
No time-based task replacement or raw-data change. Scoring deferred. Sequential
25-call blocks and every original hard stop remain; drift remains a flag.
Do not start unresolved R1/E5 or invent M4/M5 stages. No reuse of pilot rows in
main estimates; M1 has a new output directory. Freeze at22Nov23:59IST remains.


## Unattended M1 completion sequence (2026-11-22)

Owner requests continued work without another permission after remaining269
M1 calls. A7.75h parent sequence invokes the unchanged frozen timed-M1 worker,
then evaluates existing responses with the same oracle only if all1040 calls
are saved, then writes verification counts/flags. No R1 or new model condition
is authorised by this sequence. Existing generation hard stops prevent later
phases. Parent time cutoff terminates only its owned subprocess tree, retains
journals and reports incomplete scoring for resume. No raw-data repair.


## Approved M1-to-R1 unattended chain (2026-11-22)

Owner approved five-policy R1 on the shared original40 tasks and an automatic
50-call diagnostic pilot gate, followed by400 fresh full calls only when
validation and remaining-time tests pass. Inputs/config/registrations are
separate in studies/utilisation/r1-v2. Semantic sixth policy is deferred until
essential requirements/information loss can be audited. Compaction preserves
words and examples and is labelled lossless formatting; selective retention is
oracle, not realistic retrieval. Natural exact token matches are listed; broad
policy comparisons remain confounded by length, recency and preference. Energy
measures generation only; unmeasured preprocessing cost precludes end-to-end
energy claims. See PROTOCOL.md for definitions, outcomes and gate.

One driver chains approved M1 completion/scoring/verification into R1 without
another permission pause. Gate uses no correctness/effect direction. Original
freeze and hard stops unchanged; partial stages/checkpoints remain resumable.
Pilot rows never promote into full analysis. No new R1 generation until frozen
manifest/reference/host/sensor checks pass. No unregistered later experiment.

## Owner-requested continued execution (2026-11-23)

Owner now requests finishing remaining planned stages without a seven/eight-hour
automatic cutoff, until he pauses. This supersedes the historical execution
freeze for separately prepared new stages; it does not modify frozen completed
experiments, their data, settings, exclusion rules or effect-based extensions.
Safety, per-request timeouts, retry limits, sequential measurement and quality
checks remain active. New exact designs still require the working agreement's
review, dated registration, validation and commit before generation.
See docs/plans/UTILISATION_CONTINUATION_2026_11_23.md for the verified inventory,
remaining preparation and proposed next scope. Completed stages are skipped.

## E5 and semantic M3/R2 continuation (2026-11-23)

Owner requested E5 then revised M3/R2 in one sequential unattended chain, and
required meaningful computational alternatives rather than output wrappers.
Exact new configs/materials/registrations are in studies/utilisation/continuation-v3.
E5 code-only preference: pilot50/full400. Revised M3/R2: pilot130, full960 loaded
plus80 matched isolation controls; all40 authored alternatives validated, none
excluded. Model sees description/signature only, never alternative reference or
tests. Three boundary examples were shown before any generation.

New stages use temperature0, one sample, fixed seeds and2048 output limit;
E5 num_ctx8192, R2 num_ctx16384. The old E5 situation framing is superseded only
for this separately scoped new preference study. No completed config is changed.
The new execution worker forks the frozen supervisor only to remove its expired
calendar stop under explicit owner authority; its hard stops/retries/measurement
semantics stay unchanged. A user PAUSE persists, stops after active work/closing
baseline, and never automatically clears. No elapsed-time queue cutoff remains.
See PROTOCOL.md for outcome definitions, pilot gate, inference boundaries and
energy caveats. Output-contract interference and other preference families remain
deferred. No results or morning completion are promised by the call budget.

## Approved remaining M2/E4/E3 queue (2026-11-24)

Owner approved M2 with four static return-to-task conditions and matched complete
input counts: neutral, similar computational alternative, one other-domain task,
three other-domain tasks. Same target/query, literal descriptions only, no
distractor solutions/tests. Publish the authored relationship audit and limits
of isolating similarity/count/length. Five-task50-call pilot, then400 full calls
including80 new exact-setting isolation controls, only after validity gate.

E4: prefix0/500/1000/2000/4000, cold/warm, both CPU models,20 repeats;400
measured calls after a separate20-call pilot. Both measured arms model-resident;
unload/preload and native cache counters distinguish residency from prefix reuse.
Setup/priming requests are additional, logged and outside measured-request
energy. Intentional64-token budget is a workload endpoint, not coding truncation.

E3: approved diagnostic only; five seeded tasks, two models, generic retry or
validated failing-example feedback, last or full history, maximum130 calls.
Share initial generations across branches. Fixed feedback cases are removed
from final scoring partitions; hidden outcomes do not drive repairs or stopping.
Round materials are deterministically derived from raw parents, hashed before
generation; algorithm/config/templates committed first. No automatic full E3.

The new outer driver completes and scores saved R2 first, then these stages
sequentially. Existing frozen v3 artifacts remain unchanged. New scoped configs,
protocol, manifest and validation are in studies/utilisation/remaining-v4.
Keep global PAUSE until explicit owner resume with live500ms sensor log, AC and
Best performance. No elapsed-time cutoff; quality/safety stops and five retries
remain. Maximum1000 new measured calls beyond340 currently remaining R2 calls;
E4 setup/priming overhead is additional. Failed gates halt later stages.

## Approved E4 workload amendment (2026-11-24)

The original E4 v4 pilot correctly stopped after10 calls: a0.5B warm4000-prefix
request returned19 tokens at native done_reason=stop rather than the required64.
Input/cache/residency and energy checks passed. Preserve the failed feasibility
pilot and frozen artifacts. Owner explicitly approved a fresh constrained E4
scope then the unchanged E3 diagnostic, after reviewing the concrete proposal.

New E4-schema-v5 asks for a1000-integer JSON array with the same native format
schema in both arms. Keep64 output, native cache verification and every safety
gate. Both arms receive identical one-token grammar setup with a distinct raw
prefix before warm-only priming; all controls logged outside measured energy.
New20-call pilot then400 fresh full calls only if validity passes. No old pilot
pooling or weakened gate. Limit inference to the constrained synthetic workload,
including sampling/grammar costs. No end-to-end energy claim. Completed R2/M2
are audited/skipped; no requests repeated. Full E3 remains unauthorized. New
source/config/registration hashes chain to unchanged v4; commit before inference.
