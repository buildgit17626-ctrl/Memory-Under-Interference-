# Final publication verification — 24 November 2026

Manuscript Version 1.1; proposed GitHub package v1.1.0. The four local artifacts are prepared for review. No push, tag creation, GitHub release or Zenodo publication has been performed. Existing v1.0.0 and v1.0.1 remain unchanged.

| Check | Assessment | Evidence / boundary |
|---|---|---|
| Scientific consistency | PASS | 673 evidence/code/figure/table/example/companion files byte-identical; numerical TeX, configs and scoring preserved. |
| Numerical accuracy | PASS | Principal paired cross-specification effects, retention ratios/CIs and numerical energy reproduced from clean public derivatives; manuscript quantities retained. |
| Statistical transparency | PASS | Post-hoc status, censoring scenarios, paired dependencies, confidence intervals, p-values and correction families remain explicit. Earlier full saved-data rebuild verified 976 effects; this formatting cycle rechecks principal findings with identical scientific inputs. |
| Abstract readability | PASS | Motivation, HumanEval+-based tasks, models, 5,528 requests, cross-scoring, 8.97 pp and interval, natural energy wording and essential qualifications retained. |
| Research storytelling | PASS | Approved narrative retained with only the requested final corrections. |
| Explanation of Prompt-Energy | PASS | Purpose, separate dataset, motivation and verified repository link present. |
| Explanation of MemoryGraph | PASS | Retrieval/ML/graph components, user control, synthetic evaluation and untested downstream benefits remain clear. |
| Natural authorial voice | PASS | Sole-author singular voice, with neutral constructions; no owner/editor instructions in manuscript prose. |
| Times New Roman usage and embedding | PASS | Installed regular/bold/italic/bold-italic faces verified as actual Times New Roman. Used regular/bold/italic faces embedded; compatible Termes math and LM Mono code. No Microsoft font files in either ZIP. |
| Professional page layout | PASS | All 13 pages rendered and inspected; two-column A4, 10-point body, 19 mm margins; no overfull boxes, clipped characters or unresolved references. Blank diagram margins cropped without changing image files. |
| Bibliographic accuracy | PASS | All 15 primary publication identities/author lists/identifiers rechecked; venue years/DOIs and ACL page ranges checked against primary sources. |
| Authorship metadata | PASS | PDF author/title/subject/keywords correct; minimal title retained; singular contribution statement and accurate independent/IIT Madras student citation metadata preserved. |
| Data and code availability | FAIL (public-link gate) | Archive contents/instructions and analysis boundaries are documented and tested, but proposed v1.1.0 tag and release returned 404. Reserved DOI is not confirmed publicly registered. Manuscript carries publication identifiers without temporary workflow commentary; links must resolve at publication. |
| Standalone source compilation | PASS | Clean extracted source compiled with documented command, licensed installed Times fonts and Tectonic. All 13 rendered pages matched delivered manuscript at 35 dpi. Windows demonstrated; other platforms not verified. |
| Reproducibility archive | PASS | Clean extracted archive reproduced 6,006 saved records including 5,528 main requests, four cross-pass effects, paired retention ratios/CIs and 12,479 available energy windows; two energy windows remain unavailable. Network/original-data/subprocess accesses blocked. Not inference regeneration, independent rescoring or calibration. |
| Release integrity | PASS (local) | Inner SHA-256 manifest, outer asset hashes and ZIP CRC checks regenerated/verified. Final version metadata and canonical asset names agree. No fonts or credentials intentionally distributed; public derivatives retain provenance. |
| Publication readiness | FAIL (external link gate) | Local manuscript/build/analysis checks pass. Public release cannot be called ready until separately authorized v1.1.0 publication and Zenodo completion, followed by public link/asset checks. |

## Exact build and fonts

Final page count: **13** (main text and references through page 10; appendices through page 13).
Engine: **Tectonic 0.17.0+20260731, XeTeX/LaTeX with fontspec and unicode-math**.
Embedded font families: **Times New Roman regular, bold and italic; TeX Gyre Termes Math; Latin Modern Mono regular and bold; DejaVu Serif inside unchanged scientific figures**. All used fonts are embedded. Headings, abstract, body, tables, captions, notes and references use Times New Roman. Code remains monospace. Bold italic is installed and configured but not used by current text.

Fourteen underfull warnings remain in narrow cells/long identifiers. Visual inspection found no clipping/overlap. A Fontconfig default-configuration diagnostic is emitted by this Tectonic installation; explicit font-file loading and PDF embedding checks demonstrate the requested fonts were used. No substitute font was accepted.

## Local artifacts

The four canonical filenames are listed in README.md and UPLOAD_GUIDE.md. Exact workstation paths are supplied in the local handoff report outside this public-safe archive.

## Remaining publication blockers

1. The proposed https://github.com/buildgit17626-ctrl/Memory-Under-Interference-/releases/tag/v1.1.0 is absent, as is its tag. New-release publication is not authorized by this request.
2. DOI 10.5281/zenodo.24500468 remains reserved. Zenodo publication/registration/public accessibility is not confirmed; no record has been published by this work.
3. Public asset downloads/tag target/latest status cannot be verified before authorized publication (NOT VERIFIED). These are publication-state gates, not unresolved scientific findings.

Tests: 494 passed; Ruff clean. Fourteen existing matplotlib/Pyparsing deprecation warnings remain. No new model inference, experiments, MemoryGraph features or scientific changes were made.
