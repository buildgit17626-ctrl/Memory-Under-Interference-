# Repeated-stop diagnosis and reliability repair · 2026-11-17

Investigate using block process snapshots and raw HTTP errors, with no recovery
or generation. Preserve the existing drift threshold and all saved attempts.
Improve checkpoint details and avoid retrying Ollama's explicit repeat-limit
abort as though it were a transient connection error. Test failure precedence.

Propose shorter 25-call blocks and a two-window idle check as an explicit
execution amendment. This adds idle overhead and does not guarantee zero
drift. Activate only if approved, because it changes the measurement protocol.
No automatic override or resume of the baseline-drift hard stop is proposed.
