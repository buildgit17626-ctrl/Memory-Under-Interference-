# Memory Under Interference -- Version 1.0

Local scientific release candidate, 24 November 2026. Not peer reviewed. External
publication requires owner approval. Start with manuscript/main.pdf, FINDINGS_FINAL.md,
CLAIMS_AND_EVIDENCE.md, REVIEWER_RESPONSE.md and DATA_AVAILABILITY.md.

## Reproduce without inference

Use Python 3.13 in a new environment; install code/requirements-lock.txt. Then:

```powershell
python reproduce.py --full --energy --figures --output reproduced
```

Omit --full for the quicker principal-results check. No Ollama or embedding
server/model is required. Full mode also rebuilds all paired audit effects and
sensitivities, and checks their outcome estimates/CIs/tests against the frozen
audit. This checks 6,006 saved logical
records including separate pilots/diagnostics, verifies the 5,528 main calls, recomputes
the principal paired cross-pass/cost estimates and numerical energy, and regenerates
the eight figures. It never executes generated code. Re-scoring generated programs is
a separate Windows restricted-subprocess operation documented in code/docs/SAFETY.md.
Do not run historical recovery commands against accepted evidence.

Inspect SHA256SUMS.json and checks/public-export-provenance.json for identity and
transformations. Per-figure CSVs, per-task outcomes, raw journals, configs/protocols,
model digests, versions and licence notices are included. Sensor exports are CPU power
and time only; original multi-channel logs and model/runtime binaries are excluded.
The archive is not a byte-identical inference-resume package.

## Compile the manuscript

From this root, with Tectonic installed:

```powershell
tectonic --keep-logs --outdir manuscript manuscript/main.tex
```

An initial build may download standard TeX packages; manuscript/main.bbl is supplied.
The separate source archive retains manuscript/ and figures/ relative paths. No
conference template/acceptance is implied. Version 2 work is in VERSION_2_ROADMAP.md.
Original report/data CC BY 4.0, original code MIT, third-party exceptions retained.
