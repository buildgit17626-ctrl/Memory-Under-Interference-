# Memory Under Interference

**Evaluating context utilization and inference efficiency in small code language models.**

This repository contains the experiment harness, frozen designs and a versioned
audit of existing observations from two local Qwen2.5-Coder models. It asks how
available context, competing task descriptions and retention policies relate to
test-suite correctness, token use, latency and estimated CPU-package energy.

The study measures observable behavior and computation. It does not measure
internal memory capacity, inspect cognition or establish intentional giving up.

## Version 1 preprint candidate

Prepared locally on 24 November 2026; not peer reviewed or deposited. Final
interpretation and external publication approval remain with the author.
Generation is paused. The rc1 candidate is preserved; the final revision is
prepared as `v1.0.0-rc2` on the local review branch.

- [Manuscript PDF](releases/v1/Memory_Under_Interference_v1.pdf)
- [Manuscript source bundle](releases/v1/Memory_Under_Interference_v1_source.zip)
- [Sanitized public reproducibility archive](releases/v1/Memory_Under_Interference_v1_reproducibility.zip)
- [Findings and uncertainty](releases/v1/FINDINGS_FINAL.md)
- [Publication-readiness report](releases/v1/PUBLICATION_READINESS.md)
- [Claim-to-evidence mapping](releases/v1/CLAIMS_AND_EVIDENCE.md)
- [Reproduction instructions and boundaries](releases/v1/README.md)

The manuscript reports seven completed studies and **5,528 main logical requests,
including documented failures**. Its posthoc cross-specification analysis finds
an 8.97 percentage-point alternative-consistent failure difference on 1.5B
(95% task-bootstrap interval [3.21, 16.67], 39 complete paired tasks); adverse
censoring weakens this result. Oracle retention has lower observed estimated
CPU-package cost per correct solution, but accuracy preservation is uncertain
and input length, position, instructions and output work are confounded.
MemoryGraph is a separate companion prototype, with no integrated MG1 result.

## Collected main-study evidence

| Study | Saved logical calls | Scope |
|---|---:|---|
| E0 | 1,968 | 164 tasks, two strategies, three samples, two models |
| Initial M3 | 280 | 240 loaded requests plus 40 matched isolation calls |
| M1 | 1,040 | Passive/active task load and matched filler, including isolation |
| R1 | 400 | Five context-retention policies |
| Revised M3/R2 | 1,040 | Semantic competing specifications, including isolation |
| M2 | 400 | Constructed return-to-task interference, including isolation |
| E5 | 400 | Preference placement and adherence |
| Revised E4 | 76 of 400 planned | Partial constrained prefix-cache workload |

Diagnostic pilots, retries, invalid calls and output caps are identified
separately in [the inventory](artifacts/memory-audit/2026-11-24-v1/inventory.json).
Logical calls are not independent tasks. E3, U-family studies and a MemoryGraph
intervention have no evaluated outcomes in this release.

## Reading the results responsibly

Registered contrasts are reproduced separately from additional posthoc analyses.
Tables retain model-specific denominators, paired task IDs, bootstrap intervals,
transition records and family-wise test corrections. M1 bundle overlap limits
independent-population inference. E5's original strict adherence metric has an
observed floor; secondary syntax/format audits preserve the original definition.
R1's oracle retention has privileged relevance information and is not an
automated retrieval system.

Energy uses HWiNFO CPU Package Power and block idle-baseline subtraction.
It estimates CPU-package energy, not whole-device electricity. Drift, short
windows, missing readings and alternate baseline sensitivities remain visible.
Task-bootstrap intervals do not calibrate the sensor. E4 was designated primary
energy evidence and is incomplete; other cost comparisons remain descriptive or
posthoc. No claim of a universal optimal memory policy is made.

## Code, data and provenance

- Python 3.13; pinned [direct](requirements.txt) and [locked](requirements-lock.txt) dependencies.
- Harness: [src/prompt_energy](src/prompt_energy), [experiments](experiments).
- Frozen designs and amendments: [studies/utilisation](studies/utilisation).
- Audit implementation: [analysis/memory_audit](analysis/memory_audit).
- Derived tables, separate scoring audits and integrity manifests:
  [artifacts/memory-audit/2026-11-24-v1](artifacts/memory-audit/2026-11-24-v1).
- [Safety and evaluator restrictions](docs/SAFETY.md),
  [project specification](docs/SPEC.md),
  [sources and third-party notices](docs/REFERENCES.md).

The original evidence audit verified 625 local files unchanged. The release
adds source-linked numerical checks, a worked target/distractor example, exact
selected prompts and an offline public-data reproduction path. Current tests,
compilation and clean-environment verification are recorded under
[release checks](releases/v1/checks).

**Data availability:** the public archive supplies sanitized raw-response
journals, exact prompts/configurations, per-task scores, numerical CPU power/time
samples, analysis code and integrity manifests. Its portable script reproduces
saved-data analyses without Ollama, embeddings or original data paths. See
[the tested environment](releases/v1/checks/portable-environment.json) for the
actual verification and its boundaries. Original approximately 11 GB overlapping
multi-channel sensor mirrors are excluded; their deduplicated CPU power/time
streams reproduce the included available integrals. Other sensor channels,
physical calibration, inference regeneration and unrestricted program rescoring
are outside that demonstrated reproduction. This is not a universal or
byte-identical inference-resume claim.

For local verification after dependency setup:

```powershell
.\.venv313\Scripts\python.exe -m pytest -q
.\.venv313\Scripts\python.exe -m ruff check .
```

Use the [audit instructions](analysis/memory_audit/README.md) for offline
reanalysis with the original inputs. Run generated code only through the
documented restricted evaluator. Do not run historical recovery commands against
accepted evidence.

## Project lineage and disclosure

The harness grew from [Prompt-Energy](https://github.com/buildgit17626-ctrl/Prompt-Energy).
Its earlier reports and source history remain available for provenance.
MemoryGraph is a separate retrieval project. Its saved synthetic ranking results
are described separately; integrated correctness/energy evaluation is unrun.

AI assistance was used in experiment setup, autonomous Ollama execution,
engineering, distractor construction and this audit's coding and drafting.
Frozen validation records, raw-output provenance and explicit limitations
support review; AI assistance is not independent scientific validation.
Dhruv Brahmbhatt is an IIT Madras student conducting this work independently.
Confirmed contributions are research questions/design decisions, experiment
oversight and interpretation review; no institutional supervision or endorsement
is implied. The manuscript discloses AI-assisted analysis and drafting as well.

For the Version 1 release candidate, the owner selected MIT for original code
and CC BY 4.0 for original report/data. Third-party datasets and software retain
their existing notices; see the release's THIRD_PARTY_NOTICES.md. HumanEval and
HumanEval+/EvalPlus are not relicensed by that grant.

Version 1 scientific preparation is on a local review branch. Its manuscript,
public derivatives and archives require owner approval before upload or release;
no Zenodo/TechRxiv deposit or DOI is implied by these files.
