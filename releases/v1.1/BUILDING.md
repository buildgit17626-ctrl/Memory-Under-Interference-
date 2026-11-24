# Manuscript source compilation

Manuscript Version 1.1; proposed package v1.1.0. This is a local preparation package. DOI 10.5281/zenodo.24500468 remains reserved. Do not claim the tag or DOI is publicly available before publication.

## Required tools and fonts

- Python 3.13; Tectonic 0.17.0 (XeTeX/LaTeX engine) on PATH.
- Actual licensed Microsoft Times New Roman: times.ttf, timesbd.ttf, timesi.ttf, timesbi.ttf. Windows system Fonts supplies these in the verified build. No substitute font is accepted. Microsoft font files are not distributed here.
- fontspec and unicode-math; compatible TeX Gyre Termes Math for symbols; Latin Modern Mono for code. Tectonic resolves these open TeX resources through its bundle/cache; the first build may need network access.

From the extracted source archive on Windows:

```powershell
python compile_manuscript.py
```

This verifies the Times New Roman family names in all four TrueType files, copies them into the build-only manuscript/local-fonts directory, and compiles manuscript/main.tex. Other platforms must supply licensed standard-named files explicitly:

```text
python compile_manuscript.py --font-directory /path/to/licensed/TimesNewRoman
```

Only Windows source compilation has been demonstrated. The font directory is excluded from both release archives. Do not redistribute the build-only font files. If fonts or Tectonic are absent the command fails; it does not substitute another family. Final output is manuscript/main.pdf. Compare PDF text and rendered pages rather than expecting identical PDF metadata timestamps.

The paper uses 10-point body text in a two-column A4 layout, 19 mm margins and a 6 mm column gap. Headings, captions, tables, notes and references inherit Times New Roman. Equations use TeX Gyre Termes Math; code and prompt examples remain monospace. Existing scientific plot labels remain embedded DejaVu Serif. Two diagrams have only blank PDF margins cropped in the manuscript; their scientific image files remain byte-identical.
