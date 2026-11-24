# E4 workload amendment proposal - 24 November 2026

Status: owner approved "revised E4, then E3" on24 November2026, after reviewing
the concrete fresh20-call pilot/400-call full scope and unchanged64-token gate.

## Verified problem

The original pilot has10 saved calls out of20:9 reached64 output tokens;
one0.5B/warm/4000-prefix call ended at19 with native done_reason=stop,
HTTP200 and no transport error. Input4055 matched; cached4030 matched the
independent shared prefix; selected CPU model residency verified. All10 have
energy readings. Native responses reproduce the workload failure and halt.
The response was unrelated Python code. Its cause is unknown; this is not
evidence of a cache failure or a general model-memory mechanism.

The original instruction requested a long sequence but could not guarantee
the model would generate until64 tokens. The failure is useful feasibility
evidence. Preserve every old row and the failed gate, not just the nine long
outputs. Do not resume that invalid schedule or overwrite frozen v4 artifacts.

## Approved revision

Use a separately scoped, schema-constrained synthetic E4 workload. Ask for a
JSON array with exactly1000 integer items and supply that same JSON schema
through Ollama's native format parameter in both measured arms. Keep output
budget64. A legitimate completed array should require longer than this budget;
the pilot must verify the installed runtime actually sustains64 tokens rather
than assuming support from documentation. No claim that a prompt alone forces
length. These are intentional partial synthetic outputs, not coding solutions.

Keep prefix lengths0/500/1000/2000/4000, both models, temperature0, seeds,
context16384,64-token budget, native cache verification, CPU residency,
measurement rules and cold/warm interleaving. Do not relax the exact64-token
validity rule. Freeze new literal prompts/schema/configs/hashes before inference.

Run20 fresh diagnostic calls, then400 fresh full measured calls only if every
pilot validity check passes. Old10 rows stay a failed feasibility pilot and
never enter the revised pilot or full estimates. No retries of successful
early-ending rows to obtain a preferred workload. All setup/priming requests
remain additional and append-only.

Give BOTH conditions an identical grammar-setup request with the same schema,
one output token and an unrelated raw prompt before the scored request. The
setup prompt starts with a different token than the measured template; verify
cold cached-token count remains0. Warm then primes the measured prefix with
the same schema. Log all setup details. This addresses grammar setup as an
additional state difference; residual runtime/kernel/sampling effects remain
limitations. Do not claim the same absolute costs as unconstrained decoding.

Inference is limited to resident prefix reuse under this constrained synthetic
workload. Grammar/sampling overhead is included in measured request costs;
preload/grammar-setup/priming energy is outside them. No claim of end-to-end
energy savings or ordinary coding-workload energy scaling.

## E3 and execution order

Proposed order: revised E4 pilot -> full only on validity -> the already
approved unchanged E3 diagnostic pilot. No completed R2/M2 request is repeated.
If revised E4 is infeasible, checkpoint; do not silently relax its gate or
skip to a different study. Alternative owner decision: defer E4 and run only
the unchanged E3 diagnostic now, recording the order amendment explicitly.
Full E3 remains unauthorized in either option.

## Implementation after approval

New scoped E4 folder, preparation entry, amended driver/watcher and focused
tests; reuse unchanged cache/energy/retry/sandbox infrastructure. Never edit
frozen v3/v4 inputs/source. Add dated SPEC/CHANGELOG/learning notes; commit and
verify the new chained manifest before generation. New grammar setup is
outside measured windows. Keep old complete raw-file checksums for preservation.

Test fresh pilot/full separation, identical pair requests and schemas, setup
parity, cold/no-cache versus warm/native-hit checks, early-ending rejection,
raw preservation, completed-stage skipping and unchanged E3 bounded protocol.
No heavy dependency or backend change. All normal host/sensor/safety gates apply.

## Approval record

AGENTS.md says: "If a question is about research design, stop and ask."
The owner's global rules also prohibit design-parameter changes without asking.
Native format/schema and the workload prompt are new decoding/material choices;
they need specific review rather than interpreting a general repair instruction
as approval for an unseen scientific design. This document made that choice
concrete; the owner then explicitly approved it. No silence was treated as approval.

## Sources and assumptions

Ollama documents native JSON-schema format constraints:
https://ollama.com/blog/structured-outputs
The upstream llama.cpp converter/tests include array minItems/maxItems:
https://github.com/ggml-org/llama.cpp/blob/master/common/json-schema-to-grammar.cpp
https://github.com/ggml-org/llama.cpp/blob/master/tests/test-json-schema-to-grammar.cpp
These establish plausibility, not verification of the installed Ollama build.
Runtime support, request length matching, cache state and sustained output
must pass the new pilot. No new effect hypothesis or predicted benefit is added.
