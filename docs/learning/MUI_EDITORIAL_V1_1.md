# Version 1.1 editorial revision

The manuscript now leads with the problem: extra context supplies information but can also supply a competing requirement and incur more computation. Prompt-Energy motivates this question; MemoryGraph is presented as a practical next setting, with its synthetic ranking evidence kept separate. New definitions precede the statistical language, and the sole-author voice is singular.

No new model or embedding inference was run. The previous release directory and published history are preserved. The authoritative revised source is releases/v1.1/manuscript/main.tex. analysis/memory_release/editorial_v11.py checks evidence equality, numeric/citation coverage and packages files; editorial_pdfcheck.py checks the resulting PDF. These presentation checks do not establish scientific validity by themselves.

Data flow: preserved public evidence → unchanged saved-data analysis → numerical tables/figures → revised narrative → rendered PDF → source/reproduction ZIPs and SHA manifests. verify_public.py validates trusted saved-data analysis with original-data and network access blocked; it is not a sandbox for running generated programs.

Questions to defend:
1. Why is more context not equivalent to better utilization?
2. What does testing against the alternative specification reveal beyond target correctness?
3. Why does the conservative censoring analysis weaken the headline association?
4. Why do the retention cost reductions not establish preserved accuracy or a causal retention benefit?
5. What additional end-to-end evidence would MemoryGraph need?

Assumptions: Version 1.1 labels an editorial revision; v1.1.0 is only a proposed package tag. No publication is authorized. The reserved DOI is retained without asserting registration. Prior author details remain in citation metadata, while the PDF byline remains removed. Previously approved data, scoring and reference audits remain the scientific foundation; no independent rescoring or sensor calibration is claimed.

Final verification: the final extracted archive verified 737 inner-manifest files and reproduced principal effects and energy with no unexpected original-data access. The full saved-data audit verified 976 effects from the identical scientific inputs. The extracted source compiled independently, and all 14 page renderings matched the delivered PDF pixel-for-pixel at 35 dpi (PDF metadata bytes may differ). The three payload hashes in SHA256SUMS.txt passed. Tests: 494 passed; Ruff clean.
