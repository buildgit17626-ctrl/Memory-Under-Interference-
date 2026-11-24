# Memory Under Interference

**Evaluating context utilization and inference efficiency in small code language models.**

This repository contains the experiment harness, frozen designs and a versioned
audit of existing observations from two local Qwen2.5-Coder models. It asks how
available context, competing task descriptions and retention policies relate to
test-suite correctness, token use, latency and estimated CPU-package energy.

The study measures observable behavior and computation. It does not measure
internal memory capacity, inspect cognition or establish intentional giving up.

## Start here

- [Skeptical review and provisional interpretations](artifacts/memory-audit/2026-11-24-v1/REVIEWER_AUDIT.md)
- [Phases 1–4 audit and paired-effect tables](artifacts/memory-audit/2026-11-24-v1/PHASES_1_4_REPORT.md)
- [Methods, settings and populations](artifacts/memory-audit/2026-11-24-v1/METHODS_AND_POPULATIONS.md)
- [Per-condition results](artifacts/memory-audit/2026-11-24-v1/CONDITION_TABLES.md)
- [Audit code and reproduction commands](analysis/memory_audit/README.md)
- [Representative code and distinguishing cases](artifacts/memory-audit/2026-11-24-v1/REPRESENTATIVE_CODE_AUDIT.md)

**Status, 24 November 2026:** Phases 1–4 of the evidence audit are complete for
available records. Scientific interpretations await owner review. This is a
research repository and provisional report, not a submitted or peer-reviewed
publication. Generation is paused.

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

The audit verified 625 original local evidence files unchanged and reported
489 passing tests with Ruff clean. Exact revision, file hashes and check records
are in [AUDIT_STATUS.json](artifacts/memory-audit/2026-11-24-v1/AUDIT_STATUS.json).
It made no new model-generation requests.

**Data availability:** derived audit evidence is included. The complete original
journals and approximately 11 GB of sensor mirrors remain local and git-ignored;
this repository alone is not yet a complete public reproduction archive.
Full audit regeneration requires those inputs at the registered paths.
Historical local paths and commit identifiers are retained as provenance, not
presented as downloadable data. A complete archive remains future release work.

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
MemoryGraph is a separate retrieval project; it is not evaluated here.

AI assistance was used in experiment setup, autonomous Ollama execution,
engineering, distractor construction and this audit's coding and drafting.
Frozen validation records, raw-output provenance and explicit limitations
support review; AI assistance is not independent scientific validation.
No author affiliation, contribution allocation or publication acceptance is claimed.

For the Version 1 release candidate, the owner selected MIT for original code
and CC BY 4.0 for original report/data. Third-party datasets and software retain
their existing notices; see the release's THIRD_PARTY_NOTICES.md. HumanEval and
HumanEval+/EvalPlus are not relicensed by that grant.

Version 1 scientific preparation is on a local review branch. Its manuscript,
public derivatives and archives require owner approval before upload or release;
no Zenodo/TechRxiv deposit or DOI is implied by these files.
