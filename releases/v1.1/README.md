# Memory Under Interference — manuscript Version 1.1

Final formatting preparation for proposed GitHub release v1.1.0. No external publication or push has been performed. Published v1.0.0 and v1.0.1 are preserved. DOI 10.5281/zenodo.24500468 is reserved, with public registration/accessibility unconfirmed. The v1.1.0 tag/release was absent at the recorded check; publication links require a final check after approval.

## Four prepared assets

- Memory_Under_Interference_v1.pdf
- Memory_Under_Interference_v1_source.zip
- Memory_Under_Interference_v1_reproducibility.zip
- SHA256SUMS.txt

The manuscript retains approved science and adds final Times New Roman typography, accurate PDF metadata, concise definitions and publication-ready availability prose. See BUILDING.md for actual font requirements and the source compilation command. Microsoft font files are not bundled.

## Reproduce saved-data analyses

Extract the reproducibility ZIP into a clean directory. On the demonstrated Windows/Python 3.13 setup:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-reanalysis.txt
.\.venv\Scripts\python.exe -I verify_public.py --full
```

The full command checks hashes, 6,006 saved logical records including 5,528 main requests, principal paired estimates/intervals, numerical energy samples and the saved synthetic MemoryGraph rankings. It rebuilds statistical tables and figures without model or embedding inference. The saved-data run is not independent correctness rescoring or sensor calibration. See DATA_AVAILABILITY.md for excluded original multi-sensor records, sanitization provenance and reproduction boundaries.

PUBLICATION_READINESS.md contains the final PASS/FAIL/NOT VERIFIED assessment. Original report/data: CC BY 4.0; original code: MIT; third-party notices retained. Proposed publication URL: https://github.com/buildgit17626-ctrl/Memory-Under-Interference-/releases/tag/v1.1.0.
