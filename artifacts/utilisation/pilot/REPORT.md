# Diagnostic timing pilot

This report describes 22 pilot requests. No full run was started.

## Measured results

| Model | Subset | n | Wall s | Output tok/s | Prefill s | Decode s | Energy | Low resolution |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-coder:0.5b | E0 | 10 | 4.527 | 50.20727377307354 | 0.585 | 2.969 | 10/10 | 6 |
| qwen2.5-coder:0.5b | context_probe | 1 | 20.886 | None | 19.953 | 0.000 | 1/1 | 0 |
| qwen2.5-coder:1.5b | E0 | 10 | 5.592 | 22.2471905494431 | 0.868 | 3.304 | 10/10 | 3 |
| qwen2.5-coder:1.5b | context_probe | 1 | 33.173 | None | 29.381 | 0.066 | 1/1 | 0 |

Means are across requests. Tokens/s uses output tokens divided by API decode duration for each request, then averages those rates.

## Scope scenarios awaiting owner choice

| Family | Scope | Calls | Short-rate hours | Long-rate hours |
|---|---|---:|---:|---:|
| MAIN | focused | 4808 | 13.4 | 47.0 |
| MAIN | balanced | 9048 | 25.3 | 88.4 |
| MAIN | catalogue | 16448 | 46.0 | 160.7 |
| APPENDIX | focused | 2180 | 6.1 | 21.3 |
| APPENDIX | balanced | 5400 | 15.1 | 52.7 |
| APPENDIX | catalogue | 12184 | 34.0 | 119.0 |

## Counts and timing formulas

Every count includes both models. report.json contains component counts. The scenarios() function in analysis/utilisation_pilot.py contains each multiplication and the exact scope definition.

The short scenario uses mean E0 wall time. The long scenario adds E0 mean decode time to probe wall time because the probes returned no code. Add the 5s gap and average models. Multiply each service rate by the proposed call count and divide by 3600.

- Scenarios are proposals; no full schedule was approved.
- U1 budgets all 164 tasks per model as an upper count; actual failure sets are unknown.
- E3 reduced scale uses 10/10/20 tasks per model and 2x2/4x4/4x4 feedback-memory cells.
- M3 focused/balanced/catalogue use 20/40/60 tasks; 2/3/4 lengths; 1/2/3 positions.
- R1 uses 3/7/13 distinct cells; zero replay is counted once. Catalogue is 1+4*3.
- R2 uses 3/7/10 cells; zero distractors is counted once. Catalogue is 1+3*3.
- M1 uses 15/30/60 bundles PER K and 1/2/2 orders; K sets 2,4 / 2,3,4 / 2,3,4,6.
- M2 budgets four target conditions plus four interruption calls per task, pending protocol.
- E4 count excludes priming/unload/preload, which require additional setup time.
- U3 and U4 require scoring time, not model calls.
- Short rates use E0 wall+5s; long rates use probe wall+E0 decode+5s. Models receive equal weights.
- Timing range is not a confidence interval or a guarantee; long repair/bundle outputs can exceed it.
- Excluded time includes independent calibration, reference scoring, baselines, priming, retries and downtime.
- All figures are pilot diagnostics; no correctness or hypothesis claims are inferred.

The 4000-token probes returned empty text (0.5B) and 0 (1.5B). Their counts matched, but they supply no coding-workload decode evidence. Probe tokens/s is suppressed for fewer than ten output tokens. Long repair or bundled outputs can take substantially longer than these forecasts.

## Sensor baseline records

- start baseline 16.441 W; flags [].
- end baseline 15.472 W; flags [].