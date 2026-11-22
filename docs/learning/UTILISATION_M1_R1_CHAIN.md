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

## Completion verification - 2026-11-22

The chain has exited with reason `finished`. Full R1 contains 400 unique calls
and 400 unique scores: 40 tasks in every model-policy cell (two models, five
policies). The 50-call pilot has its own 50 scores and stays separate. No calls
were missing or duplicated, no inputs were invalid, and no API calls failed.
The full scoring ledger contains 199 passes, 196 failures and 5 output-capped
responses; these are counts, not an interpretation of policy effects.

HWiNFO CPU-package energy estimates are available for 400/400 full calls, but
availability does not mean precise or unflagged measurement. There are 78
post-load low-resolution flags and 21 total-window low-resolution flags. Two
closed blocks containing 50 calls have baseline-drift flags. Preserve these
records and apply the registered sensitivity analyses when interpreting energy.
No estimates or thresholds were changed to obtain completion.

Reproduce counts, schedule/hash checks and preservation of the previous 375
raw records from the repository root:

```powershell
.\.venv313\Scripts\python.exe -m analysis.verify_r1_completion --prefix-bytes 2181300 --prefix-sha256 9e01126c4f9514bf042c8ef995400317da4645b0de45da54bf6c780da0ff1b71
```

The derived report is `results/utilisation/r1-v2/completion-audit.json`;
`calls.jsonl`, `scores.jsonl` and `blocks.jsonl` remain the source records in
each pilot/full directory. The script reads them without altering them. Frozen
manifests still verify, and the pre-resume byte prefix is unchanged. There were
no scoring infrastructure-error statuses. Test timeouts remain recorded outcomes.

Completion assumptions: this audit establishes ledger completeness under the
existing oracle, not general correctness or a causal memory effect. No semantic
summarization arm or later experiment was added; no policy conclusion is drawn.
