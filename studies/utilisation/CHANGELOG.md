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
