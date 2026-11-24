# Why E4 needed a separate workload amendment

The original pilot's early-ending call was a real saved response. It had the
right input count, a native cache hit and an energy reading, but only19 output
tokens. A budget64 caps generation; it does not compel a model to keep going.
The correct action was to preserve that feasibility result and stop, rather
than deleting it or repeatedly asking until a longer answer appeared.

The owner approved a new scope using native JSON-schema constraints. The
model must begin an array with1000 integers, with the same64-token budget.
The fresh pilot must demonstrate that the installed runtime produces64 tokens
for every condition. Output is intentionally incomplete synthetic JSON, not a
coding solution. Old pilot rows stay separate; the validity gate is retained.

Schema decoding introduces computation of its own. Both cache arms therefore
receive a matching grammar-setup request; warm alone then primes the measured
prefix. Both remain CPU-resident. Native cached-token counts still verify
the cache state; speed alone cannot establish it. Setup/priming electrical
energy is outside the measured request and no end-to-end saving is claimed.

New files are experiments/prepare_e4_schema.py, run_e4_schema.py and
watch_e4_schema.py, plus src/prompt_energy/e4_schema.py and e4_schema_worker.py.
The worker preserves frozen v4 retry and measurement code, changing only
which scoped validity checks it imports. The driver skips completed R2/M2,
runs the new pilot and gated full E4, then calls the unchanged E3 pilot.
Materials/protocol are in studies/utilisation/e4-schema-v5. Existing v3/v4
manifests stay untouched and are checked through the new manifest chain.

From the repository root, monitor/pause with:

```powershell
.\.venv313\Scripts\python.exe -m experiments.run_e4_schema monitor
.\.venv313\Scripts\python.exe -m experiments.run_e4_schema pause
```

Launch/recover after hash/host/live-sensor checks with:

```powershell
.\.venv313\Scripts\python.exe -u -m experiments.watch_e4_schema --resume --hwinfo-log "C:\Users\Dhruv Brahmbhatt\Downloads\New folder\ver11_hwf.CSV"
```

Questions to be able to answer:

1. Why was the19-token response not an input-truncation or cache failure?
2. Why are the old and new pilot results kept separate?
3. How could schema setup otherwise confound a cold/warm comparison?
4. What does the pilot actually verify, beyond the existence of API documentation?
5. Why do these measurements not establish ordinary coding or end-to-end energy savings?

Assumptions: runtime supports the schema constraints (pilot must verify); native
token counters keep their documented meaning; synthetic-output comparisons
remain narrow; every original safety/quality rule and E3 definition is unchanged;
preparation/test success is distinct from actual pilot validation.
