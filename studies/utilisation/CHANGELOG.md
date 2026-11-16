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
