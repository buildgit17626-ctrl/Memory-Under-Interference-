# Running the two-stage continuation

The new queue runs E5 pilot, evaluates it, checks measurement validity, then runs
and scores E5 full. It repeats this process for semantic M3/R2. Completed E0,
M1, original M3 and R1 are never regenerated. No eight-hour cutoff remains;
completion, an explicit pause or a real validity/safety stop ends the queue.

Model calls are sequential. Tests run separately in the existing restricted
worker; modified reference code and tests are not part of model prompts. The
new continuation worker preserves the original retry/measurement behavior but
uses the owner's extended execution window. The frozen historical worker stays
unchanged, with its expired calendar freeze still visible for audit.

Source: experiments/prepare_continuation.py, experiments/run_continuation.py,
preference_materials.py, semantic_alternatives.py and continuation_queue.py.
Frozen inputs/methods: studies/utilisation/continuation-v3. Results/status/logs:
results/utilisation/continuation-v3. Every call, score and cross-pass has a key.

Run from the repository root using the fresh sensor path:

```powershell
.\.venv313\Scripts\python.exe -m experiments.watch_continuation --hwinfo-log "C:\Users\Dhruv Brahmbhatt\Downloads\New folder\ver9_hwf.CSV"
```

Read-only progress and graceful pause:

```powershell
.\.venv313\Scripts\python.exe -m experiments.run_continuation monitor
.\.venv313\Scripts\python.exe -m experiments.run_continuation pause
```

Pause finishes the current request/test, closes its baseline and prevents later
stages. PAUSE remains until the owner explicitly requests resume; never remove
it automatically. Unexpected process crashes have up to five automatic restarts;
documented quality stops and pilot failures do not restart automatically.

Five questions:
1. Why are code correctness and code-only adherence different measurements?
2. Why does each semantic alternative need an explicit distinguishing input?
3. Which data enter a model prompt, and which stay inside evaluation?
4. Why must a pilot gate ignore whether an effect looks favorable?
5. Why does matching filler tokens not prove equal complete-prompt tokens?

Assumptions: AC/Best performance, live500ms sensor, otherwise idle machine,
same pinned models/tokenizer/oracle and precommitted materials. Static histories
and authored task alternatives do not establish general human memory mechanisms.
An unattended queue can halt on a real error; no morning completion is guaranteed.
