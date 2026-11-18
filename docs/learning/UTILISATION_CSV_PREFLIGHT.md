# CSV preflight — 2026-11-18

A CSV header names the sensor columns. Each complete data row must have the
same number of fields; otherwise the parser cannot trust the power mapping.
ver2 changed from 328 fields to 329 without a matching header. We leave it
unchanged and use the owner's new ver3 file, which writes a fresh header.
The exact cause of the change is unknown.

The parser now explains the expected/observed width and how to recover.
The supervisor records workflow input/measurement errors in CHECKPOINT.md
with the selected file path. The parser still rejects malformed complete rows;
only an incomplete live tail is deferred as before. Saved generations are not
repeated. Fresh baselines are still required on recovery.

Key files: hwinfo.py validates the log; supervise_v2.py records the error;
test_hwinfo.py and test_utilisation_order_v2.py verify rejection and checkpointing.

Five questions:
1. Why must a row match the header width?
2. Why is skipping malformed rows unsafe?
3. How is an incomplete live tail different from a complete bad row?
4. What evidence establishes that a log is live?
5. Why does changing the sensor file not require repeating saved generations?

Assumptions: the owner keeps old logs unchanged and selects the actual new
logging file; a passing preflight does not guarantee continued sensor health.
No research settings or validity rules changed.
