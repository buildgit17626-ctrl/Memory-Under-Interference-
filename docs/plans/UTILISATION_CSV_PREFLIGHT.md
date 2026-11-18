# CSV preflight repair — 2026-11-18

Files: hwinfo.py, supervise_v2.py, parser/entry-point tests, SPEC, supervisor
guide, CHANGELOG and execution hashes. No generation in this repair.

Design: keep strict CSV schema validation. Include expected/observed column
counts and a new-file instruction in the error. Convert workflow ValueError
and OSError failures into a durable checkpoint with the actual sensor path
and error type, print a concise reason, then exit with failure status.
Never skip malformed complete rows or infer a sensor mapping.

Evidence: ver2 header has 328 fields; row 67426 at 2026-11-18 08:19:36.117
and subsequent complete rows have 329 fields. Persistent change, not a partial
tail. Cause of the layout change is unknown. Owner starts a new ver3_hwf.CSV
with its own matching header; old file and all saved study rows stay untouched.

Risks: a sensor schema change still stops collection, as necessary; a new log
must independently pass format, cadence, freshness and append-growth checks.
No scientific design, threshold or invalid-window rule changes. No unresolved
research design question. Verify with synthetic malformed rows and a mocked
CLI failure, full tests, linter and hashes. Check the new live file read-only.
