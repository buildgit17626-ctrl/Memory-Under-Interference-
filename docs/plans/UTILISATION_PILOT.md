# Utilisation timing pilot, 2026-11-16

Owner authorised exactly 5 tasks × 2 arms × 1 sample × 2 models, plus
one 4,000-input-token probe per model, before choosing a full-run scope.
Use the first five original registered IDs, temperature 0.2 and sample seed
1729, approved 8192 context and 2048 output cap. The long probe is diagnostic,
not a benchmark outcome. Each long prompt contains the same task plus
explicit irrelevant padding. Render the Qwen system/user/assistant template
explicitly and use raw=true so independently counted bytes are sent unchanged.
Hash tokenizer files and every scheduled request before generation.
Compare all returned prompt counts to independent counts. Exclude pilot
data from later hypothesis tests. Input truncation is a count mismatch;
output-cap censoring stays separate. No intentionally undersized request is
added to the 22-call budget; forced-truncation detection is tested offline.
Use the existing energy baseline, coverage, drift and low-resolution rules.
Report durations from Ollama and gross/net post-load energy coverage.
Report runtime forecasts only after observing timing. Catalog totals with
unresolved denominators must be labelled scenario assumptions.
