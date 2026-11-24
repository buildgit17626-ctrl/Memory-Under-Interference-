# E4 constrained-workload amendment - 24 November 2026

Owner explicitly approved revised E4 followed by the unchanged E3 diagnostic
after reviewing docs/plans/E4_WORKLOAD_AMENDMENT_2026_11_24.md. This is a new
post-feasibility scope. The original v4 pilot, failed gate and configurations
remain unchanged; no old pilot rows enter these estimates. The scientific E4
question is unchanged. The probe and constrained-decoding mechanism change.

## Why the amendment exists

Original pilot:10/20 calls saved;9 produced64 output tokens; one0.5B warm
4000-prefix response stopped after19. Native input4055 and cached4030 matched
the scheduled input and shared prefix. HTTP200, selected CPU residency and
energy coverage verified. The output was unrelated Python code, with native
done_reason=stop. Its underlying cause is unknown. The original halt was correct.
An unconstrained64-token cap is a ceiling, not a guaranteed fixed output length.
This feasibility issue does not establish a cache failure or internal-memory
mechanism. No failed row is deleted or repeatedly generated until it passes.

## New frozen workload and controls

Ask for a JSON integer array with exactly1000 items. Supply the literal schema
in schema.json via native format, identical in cold and warm scored requests.
Do not score these partial arrays as coding answers. Keep budget64, T0,
seed1729, num_ctx16384, CPU8 threads/GPU0 and the same two model digests.
Native support must be verified on this installed runtime, not inferred from
web documentation. Exact64 output remains required; no weakened workload gate.

All measured cold/warm pairs have the identical input, template, decoding
schema/options, model and repeat identity. Prefix lengths remain0/500/1000/
2000/4000 literal tokenizer tokens. Randomized interleaving uses seed1730;
20 fresh pilot calls, then400 fresh full calls (20 repeats) only after all pilot
checks pass. Pilot and full keys/output folders are disjoint. The zero-prefix
warm condition still reuses template/query boilerplate, disclosed as before.

For each call: unload both registered models; preload selected model; perform
the same one-token grammar-setup request in BOTH conditions; warm alone then
primes the measured shared prefix with one output token. Grammar setup uses
the same schema/options and a fixed unrelated raw prompt whose first tokenizer
token differs from the measured template's. Check selected CPU residency and
wait5seconds before the measured exchange. Both measured arms remain resident.
All setup payloads/responses are append-only, linked to measured job keys.

Native cached count must be0 for cold and positive but no larger than the
independently computed prime/probe common prefix for warm. Full prompt count
must match independently. Record actual cached fraction; partial reuse is not
silently relabelled full reuse. Actual output must be64 and remain an unfinished
JSON-array prefix (not Python or a completed short array). Whitespace-only
prefixes are possible constrained outputs and have no semantic-success claim.
The same schema is checked in the raw scored request; common grammar setup
requires one native output token and an array-compatible prefix. A failure
checkpoints; no automatic backend/prompt/cap redesign or outcome-based retries.

There are400 full measured requests; additionally, each scored attempt has
two initial unloads, preload, schema setup, residency check and two closing
unloads (7 control HTTP exchanges), plus a warm-only prime. Final block-close
unloads and retries are additional too. Log these actual counts; never claim
400 is the total API count. Setup energy is outside the scored measurement.

## Outcomes, analysis and limits

Unchanged owner question/competing predictions: verified prefix reuse may reduce
resident-request latency or CPU package energy, have no benefit, or add overhead.
Record input/output/cached tokens, native prefill/decode/load/total time, wall
time, gross and baseline-subtracted HWiNFO CPU-package energy, flags and setup.

Pair cold/warm by model,prefix,repeat; report each actual pair denominator.
Bootstrap2,000/seed1732 paired repeats,95% percentile intervals; report
within-machine repeatability, not task or hardware generalization. Primary
resident-request energy/prefill-latency comparisons have separate Holm families
of10 if tests are reported. Tokens/decode/total/wall time are accompanying
diagnostics. Retain all invalid/failed/early-ending rows in the audit. Missing
energy is not imputed and energy-only denominators remain explicit. Short-call
per-call energy is secondary; show condition totals and the inherited
low-resolution/drift sensitivities. Original start baseline stays primary;
end/midpoint and exclude-drift-block sensitivities stay secondary. Neither
output-token energy slopes nor separate electrical phase energy are identified.

Grammar/sampler costs are included in measured requests. Common schema setup
addresses a potential extra state difference, but cannot establish all backend
state is identical. This experiment concerns constrained synthetic output,
not unconstrained coding costs. Preload/setup/priming energy is outside the
measurement; no end-to-end energy-saving claim. Persistent state, numerical
differences, partial cache hits, output shape, background load, sensor resolution
or sensitivity results could change interpretation. These need owner review
before substantive synthesis. Two small models, one probe, one CPU machine.

## Queue and unchanged E3

Skip complete R2 and M2 by exact key/score audits; never repeat their requests.
Run new E4 pilot -> full on validity-only gate -> unchanged E3 pilot. A failed
gate or safety stop halts later stages. No elapsed-time cutoff; existing pause,
fresh sensor/AC/Best performance, stable baselines, disk, coverage and API
limits persist. Drift remains a flag at its unchanged threshold. Do not start
unregistered experiments or full E3. E3 retains its frozen v4 config, inputs,
feedback examples, exclusion sets, derived schedule algorithm and maximum130.

## Sources and authorization

Ollama native schema format:
https://ollama.com/blog/structured-outputs
Upstream converter and tests for minItems/maxItems:
https://github.com/ggml-org/llama.cpp/blob/master/common/json-schema-to-grammar.cpp
https://github.com/ggml-org/llama.cpp/blob/master/tests/test-json-schema-to-grammar.cpp
These are supporting implementation sources, not proof of this runtime's
behavior. New source/config/stimulus/schedule hashes are committed and verified
before the first schema-constrained model request. Original hashes stay intact.
