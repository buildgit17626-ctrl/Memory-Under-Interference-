# Read-only Memory Under Interference audit

Scope: owner-authorized Phases 1–4, 24 November 2026. The global PAUSE must
remain present. No step sends model-generation requests. `secondary` and
`examples` execute existing saved code only through the existing restricted
subprocess evaluator. Do not replace it with ordinary Python execution.

Use the repository root and pinned Python 3.13 virtual environment:

```powershell
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run freeze
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run schedules
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run records
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run secondary
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run sensors
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run effects
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run robustness
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run supplement
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run examples
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run environment
.\.venv313\Scripts\python.exe -m analysis.memory_audit.run report
```

`all` runs those computations in dependency order. `summaries` refreshes only
condition summaries from `calls-with-adherence.csv`. Freeze verifies an existing
manifest instead of replacing it. The two secondary scoring journals resume by
content-derived unique keys. No original result, registration or frozen library
is modified. No added dependencies.

Main outputs in `artifacts/memory-audit/2026-11-24-v1`:

- `REVIEWER_AUDIT.md`: provisional observations, contradictions and limits.
- `PHASES_1_4_REPORT.md`: inventory, primary effects and sensitivity changes.
- `CONDITION_TABLES.md`, `conditions.json/csv`: all condition denominators,
  correctness, tokens, prefill/decode/wall time, gross/net energy and ratio CIs.
- `paired-effects.json/csv`: matched task IDs, transition source keys, pointwise
  paired intervals, tests and declared Holm families.
- `cross-pass-*`: target/alternative outcome cells and matched posthoc contrasts.
- `e5-*`, `r1-prompt-audit.csv`, `m1-*`: format, literal prompt and bundle audits.
- `energy-sensitivities.*`, `energy-per-correct-differences.json`: primary and
  sensitivity energy populations. Undefined ratio intervals are not hidden.
- `secondary-scores.jsonl`, `representative-witness-scores.jsonl`: separately
  sandboxed posthoc outcomes; never substitutions for original scores.
- `input-manifest.json`, `schedule-audit.json`, `sensor-*-audit.json`: provenance.

Bootstrap: 2,000 draws, seed 1732. Task-resampling uncertainty is not sensor
calibration. M1 intervals are conditional on fixed overlapping companions;
E4 intervals concern synthetic repeat variability, not a task population.
Tests and plan explain limitations beside their estimates.

```powershell
.\.venv313\Scripts\python.exe -m pytest -q
.\.venv313\Scripts\python.exe -m ruff check .
.\.venv313\Scripts\python.exe -m analysis.memory_audit.seal
```

The original results and 11 GB sensor snapshot remain local and git-ignored.
These derived files alone are not a complete public reproduction archive.
See `docs/plans/MEMORY_FINAL_AUDIT_2026_11_24.md` for estimands and labels.
