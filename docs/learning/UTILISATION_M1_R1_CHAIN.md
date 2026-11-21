# Connecting M1 to R1

The chain finishes and verifies M1 before R1 starts. It runs a50-call diagnostic
R1 pilot and scores separately. Only validity, energy coverage, completed scores
and projected time can unlock the400-call full R1 stage. Pilot correctness is
never a gate input. All data are resumable; no new permission between phases.

R1 has five fixed context policies. Lossless compaction keeps wording/examples;
it is not semantic summarization. Oracle selection isn't realistic retrieval.
Policy differences include length, recency and retained preference. Actual
counts/timings/energy are logged; preparation energy is unmeasured, so this is
not an end-to-end compression energy result.

Key files: prepare_r1_v2.py, r1_materials.py, run_m1_r1_chain.py and
studies/utilisation/r1-v2/PROTOCOL.md. STATUS.json and R1_GATE.json explain stops.

Questions:
1. Why is compaction different from semantic summarization?
2. Why isn't oracle retention a tested retrieval system?
3. Which pilot measurements control automatic continuation?
4. Why are pilot rows excluded from main estimates?
5. What prevents a full-history difference from proving a pure memory effect?

Assumptions: fixed active sensor path, AC/Best performance and idle host; no
unreviewed later stages; all definitions frozen before calls. A full run may
not fit the window, in which case partial work remains explicitly incomplete.
