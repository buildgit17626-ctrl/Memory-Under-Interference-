# E5 and revised semantic M3/R2 - 2026-11-23

Prospective registration for new requests after the owner extended execution
beyond the historical 22 November freeze. Completed experiments remain unchanged.
No effect conclusions have been drawn from these stages before registration.

## Shared settings and execution

Both original Qwen2.5-Coder Q4_K_M digests, CPU eight threads, no GPU,
temperature zero, seed1729, one sample/cell, output cap2048, request timeout900s,
keep_alive0. Exact templated counts use the pinned tokenizer. E5 num_ctx8192;
R2 num_ctx16384; every input plus output reservation must fit before launch.
These preserve matched settings within each stage and detect input truncation;
the two stages are not a same-prompt cross-experiment contrast.

Randomize/interleave task/model/condition with seed1730. Preserve append-only
unique-key journals and resume without repeating saved requests. At most25 calls
per measurement block, two stable60s baselines before and60s after, unchanged
drift flag and energy/sensor/disk/failure hard stops. There is no elapsed-time
ceiling because the owner explicitly requested collection until paused.

Pilot and full prompts are fixed together before the pilot. Pilots have separate
config hashes, identities and output directories and never enter full estimates.
Automatic full continuation requires complete scoring, no input mismatch/API
failure/output cap, complete energy and no evaluator infrastructure failure.
Correctness and effect direction do not influence this gate; caps are retained
and must not be resolved by silently increasing budgets.

## E5: code-only preference retention

40 original fixed targets, two models, five conditions =400 full calls.
Five independently seeded roster-prefix pilot targets yield50 diagnostic calls.
History uses eight fixed other task specifications, without reference bodies
or expanded evaluation tests, and target/query stay identical in every arm.
All five arms retain that history: no preference, immediate code-only preference,
buried preference, buried plus replay, earlier explanation preference followed
by explicit code-only correction. This history-matched no-preference condition
prevents conflating removal of history with absence of a preference.

Primary adherence is a strict observable proxy: unfenced raw output parses as
Python and contains the required top-level function. It is not a semantic
guarantee that every comment/docstring avoids explanation; record fences and
parse/entry evidence separately. Correctness is the unchanged extracted-code
base-plus test outcome and is reported separately. Bounded caps remain nonpass
and censored; do not interpret them as refusal or intentional giving up.

Primary paired contrasts: buried minus immediate and replayed minus buried
adherence for each model; Holm family4. Task bootstrap2000, seed1732,95%.
Correctness, corrections and no-preference contrasts are secondary. A format
classifier error, weak preference manipulation, context-length/recency differences
or truncation could change interpretation; this is a static-history experiment,
not a human study or a complete test of conversational memory.

## Revised M3/R2: computational semantic interference

40 original targets, two models,1000/2000 filler tokens, beginning/end target
placement, irrelevant/related/near-duplicate =960 loaded full calls.80 new
same-setting isolated calls give1040 total full calls. A separate seeded5-task
pilot has120 loaded+10 isolated=130 calls. No E0/R1 baseline is reused across
different full prompts/settings, avoiding selection/outcome reuse as isolation.

Owner rejected output-format wrappers as the main interference manipulation.
Each near-duplicate has the same argument interface but an explicitly different
computational requirement: e.g. inclusive threshold, XNOR, empty-prefix inclusion,
changed tie-break, recurrence base case or operation. The visible background
function has a distinct `_alternative` name; instructions explicitly request
only the original TARGET. Thus the model receives competing specifications
without being asked to implement both or facing duplicate definitions.

Hidden modified reference and test fixtures are never rendered. The background
contains only signature/import declarations and descriptive task text, without
doctests, test inputs/outputs or reference implementations. The target benchmark
specification remains unchanged, including its original public examples. Related
background contains descriptions of other fixed tasks; irrelevant background
uses neutral notebook prose. Complete background descriptions are repeated to
fill the budget, then neutral x padding reaches exactly1000/2000 filler tokens.
No description is cut mid-specification. Record repetition and padding as
construction limitations; semantic similarity is an authored category, not an
independently calibrated numerical distance.

Before generation, all40 original references passed their benchmark checks.
Each alternative passed two explicit input/expected-output fixtures, checked
against both original and modified reference in restricted workers, plus the
inherited argument suites and distinguishing inputs against its modified oracle.
Every pair has at least one differing expected output; some additional fixtures
are shared-behavior controls. All40 constructions passed; exclusions are empty.
This is AI-assisted authoring/mechanical validation, not independent human review
or a proof that the oracle exhaustively captures every prose requirement.

Primary contrast: near-duplicate minus irrelevant target base-plus correctness,
averaging the two lengths and positions within task, per model; Holm family2.
Task bootstrap2000,seed1732,95%; report all40 and independently isolated-solvable
subsets separately, without redefining eligibility using loaded outcomes.
Secondary: related contrasts, load/position interactions, costs and cross-pass.
Cross-pass evaluates the target-named extracted function on the hidden modified
suites; tabulate target-only,alternative-only,both,neither, keeping caps/invalid
separate. A distractor pass counts as confusion evidence only alongside target
failure; both passing or ordinary failures are not silently relabelled.

Interpretation-changers: incomplete or ambiguous alternative specifications,
reference/test errors, signature incompatibility, unequal full input counts,
padding/repetition, target position, token caps and benchmark contamination.
Publish exact full input counts and the size of any naturally matched subset;
filler-token equality alone does not establish exact complete-input equality.
Output-contract interference stays deferred as a separately labelled optional
exploratory study, not an extra main condition.

## Energy and inference boundary

HWiNFO CPU-package power at500ms, trapezoidal integration and block-start idle
subtraction. Report gross/net post-load estimates, condition totals and energy
per correct including failed attempts; per-call short-window energy is secondary.
Keep negative net estimates, missingness, low-resolution flags and drift joins;
end/midpoint baseline and drift-block exclusion sensitivities are post hoc.
No phase-energy or end-to-end preprocessing-energy claim is supported.

Scope is two small local quantized models, one benchmark, one observation/cell
and the fixed authored conditions. Prior E0/R1 results motivated preparation;
new requests are prospectively frozen, not evidence of a broadly confirmed theory.
The owner writes interpretations and reviews conclusions before external use.
