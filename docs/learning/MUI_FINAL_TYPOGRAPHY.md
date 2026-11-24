# Final typography and publication corrections

24 November 2026. The approved research narrative and science were retained. Only requested font, abstract, definition, metadata, availability and pagination corrections were made. Installed Microsoft Times New Roman files were verified and embedded; no font binaries are redistributed. TeX Gyre Termes Math and Latin Modern Mono retain mathematical/code readability. Two unchanged diagram PDFs have blank margins trimmed only at inclusion.

The build uses fontspec/unicode-math under Tectonic (XeTeX). compile_manuscript.py verifies the TrueType family names, stages licensed fonts locally and compiles; it fails if required fonts are absent. This avoids Windows absolute-font-path parsing problems. BUILDING.md explains the reproducible font prerequisites and the first-build cache/network requirement.

Data flow remains raw saved evidence → unchanged analysis → existing numerical tables/figures → final presentation → portable ZIPs/SHA manifests. The source ZIP compiled in a clean extraction and all 13 rendered pages matched. The saved-data reanalysis was isolated from original data and network. Neither validation regenerated models, executed generated code or calibrated sensors.

All 17 requested assessments are in releases/v1.1/PUBLICATION_READINESS.md. The scientific/local artifact gates pass; public availability fails because the proposed v1.1.0 tag/release is absent and DOI publication remains unconfirmed. No tag or external record was created.

Questions to defend:
1. How does the PDF font audit distinguish actual Times New Roman from a substitute?
2. Why are installed font files omitted from the source ZIP?
3. Why is the 8.97-point finding still post-hoc and censoring-sensitive?
4. Why does a passing local reproduction not establish inference regeneration?
5. Why do public-link checks remain blocked despite a completed local manuscript?

Assumptions: manuscript Version 1.1 and proposed tag v1.1.0 remain the identifiers; canonical v1 basenames are used as requested inside releases/v1.1. The prior public history and releases/v1 are preserved. PDF identity is metadata-only, with no restored visible affiliation block. Public publication requires separate approval. Other-platform compilation and public download verification remain unverified.

## Exact local artifact paths

- C:/Users/Dhruv Brahmbhatt/prompt-energy-study/releases/v1.1/Memory_Under_Interference_v1.pdf
- C:/Users/Dhruv Brahmbhatt/prompt-energy-study/releases/v1.1/Memory_Under_Interference_v1_source.zip
- C:/Users/Dhruv Brahmbhatt/prompt-energy-study/releases/v1.1/Memory_Under_Interference_v1_reproducibility.zip
- C:/Users/Dhruv Brahmbhatt/prompt-energy-study/releases/v1.1/SHA256SUMS.txt

These local paths belong only in this preparation report; the manuscript contains none. Microsoft font files are supplied by the reader's licensed installation; BUILDING.md documents the exact command and failure behavior.
