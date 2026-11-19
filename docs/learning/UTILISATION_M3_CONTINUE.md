# Reviewed M3 continuation

The original timing gate stays frozen at 100. A separate entry point verifies
the owner's review against the selected 240-call schedule, then resumes missing
calls only. The next six blocks contain up to 25 calls each (last block 15).
Each block obtains fresh stable baselines. A separate checkpoint records the
stop at 240; no later experiment or scoring starts.

Files: experiments/continue_m3.py, utilisation_m3_continue.py, the committed
m3-continuation-review.json and M3-CONTINUE hash manifest. Existing source
manifests and original checkpoint are checked, not overwritten.

Questions:
1. Why bind approval to a schedule hash?
2. Why keep the first-100 checkpoint unchanged?
3. How are saved calls skipped on resume?
4. Which checks can still stop the run?
5. Why does finishing M3 not start R1 or authorize extension?

Assumptions: owner launches with live HWiNFO and approved host state; raw logs
are unchanged. No new scientific conditions, settings or hypotheses introduced.
