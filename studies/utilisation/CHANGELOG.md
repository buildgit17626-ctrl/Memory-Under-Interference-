# 2026-11-16 · Initial design approval

The owner approved the shared configuration. The dataset, evaluator and tokenizer pins still require verification. The local Ollama manifests reference both approved historical digests as layers and declare the same template digest (1e65450c30670713aa47fe23e8b9662bdf4065e81cc8e3cbfaa98924fcc0d320). Inspect the runtime identity and check rendered token counts before generating.

The dated design record uses SHA-256 over Git blob contents, which permits verification across Windows checkout newline settings. For each scored experiment, commit its dated preregistration, stimuli, roster, resolved config and SHA-256 manifest before its first generation. Record the commit and manifest hash in the session journal and verify both on resume. Log and obtain approval for parameter changes before scoring.
