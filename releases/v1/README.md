# Memory Under Interference -- Version 1.0

Final Version 1 artifacts, 24 November 2026. Not peer reviewed. Main repository push
and GitHub v1.0.1 publication are authorized. The research manuscript remains Version 1.0;
Zenodo publication is left to the author and has not been performed.
Start with manuscript/main.pdf, FINDINGS_FINAL.md,
CLAIMS_AND_EVIDENCE.md, REVIEWER_RESPONSE.md and DATA_AVAILABILITY.md.

## Reproduce without inference

Use Python 3.13 in a new environment; install requirements-reanalysis.txt for
offline analysis. The historical full experiment lock remains in code/requirements-lock.txt.
requirements-reanalysis-lock.txt records every installed package in the fresh
Windows verification environment; it can be used instead of the shorter direct list.
The demonstrated environment is Windows 11/Python 3.13. Historical analysis imports
still require Windows modules; Linux/macOS portability has not been demonstrated.
Then:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-reanalysis-lock.txt
.\.venv\Scripts\python.exe -I verify_public.py --full
```

The guarded verifier restricts this trusted analysis run to the public tree and
Python/Windows runtime, and disables network and subprocess requests. It is not
an OS security sandbox for untrusted code. The simpler unguarded command is:

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

The final revision includes an evidence-linked worked example, exact selected prompt
strings, E5 registered primary contrasts and clearer common-scale policy figures.
See checks/portable-environment.json for the tested installation and filesystem/
network restrictions; these verify saved-data reanalysis, not inference regeneration.


Version 1 identifier: **10.5281/zenodo.24500468** (reserved; registration/public accessibility not confirmed), https://doi.org/10.5281/zenodo.24500468. Designated GitHub release: https://github.com/buildgit17626-ctrl/Memory-Under-Interference-/releases/tag/v1.0.1. GitHub v1.0.1 supersedes the older v1.0.0 package without moving its tag. The research manuscript remains Version 1.0. Zenodo publication is manual.
