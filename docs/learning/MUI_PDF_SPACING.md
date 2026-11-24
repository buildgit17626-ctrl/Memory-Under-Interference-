# Local PDF presentation corrections

The title-page status line was removed. The appendix heading now uses local
ragged-right alignment, avoiding justification that stretched the space between
its words. Availability URLs retain their exact clickable targets but display
short labels; scoped ragged-right text prevents large gaps around unbreakable
URLs. None of these changes modifies numerical results or interpretation.

The 13-page PDF was compiled and rendered; page bounds, references and numerical
checks passed. Local source/reanalysis archives and integrity manifests were
rebuilt. The published v1.0.1 tag and assets were left unchanged.

Owner questions:
1. Why can full justification stretch a heading or URL-containing paragraph?
2. Does a labelled hyperlink change its target?
3. Why do PDF changes require rebuilding source/archive checksums?
4. Which checks distinguish formatting changes from scientific changes?
5. Why do local corrected files differ from the published release until uploaded?

Assumptions: the comments concern only selected presentation elements, and no
replacement of already-published assets is requested in this local correction.
