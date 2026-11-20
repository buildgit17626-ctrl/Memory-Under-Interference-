# Full M1 timed protocol - 2026-11-21

Owner-approved1040-call grid and7.5-hour resumable segment. See scoped config,
prereg/M1.json, exact stimuli.json, owner-review.json and committed execution
manifest. Original40 targets, both models, nested companions and K2/3/4/6.
Twenty targets first, twenty last, identical across conditions/models. Input
matching includes full chat template; fallback padding repeats neutral x tokens.
No benchmark reference solutions or expanded tests appear in model prompts.
Active output cap2048*K; single-target caps2048. Context32768, T0, seed1729,
8CPU threads, keepalive0,3600s maximum HTTP; fixed original oracle.

Pilot all70 rows excluded. Complete new reference bundles must pass before run.
Per-model/condition target correctness is distinct from whole-bundle success.
Analyses specified in prereg/M1.json are exploratory post-pilot, no causal claim.
Report incomplete cells and all failed/invalid/truncated requests, raw+net CPU
package energy, drift and low-resolution sensitivity. Baseline-solvable subsets
use E0 P1 sample0 labels; not these new outcomes. E0/M3 never rerun or relabel.

Timer checks before every HTTP attempt, preserving per-call retry budgets.
3600s request +600s close reserve means last new launch about6h20m into7.5h
window. No active request killed just for reaching launch cutoff. Sensor/clock
failure, invalid input, failed calls, coverage, disk and freeze still halt.
Twenty-five-call blocks have fresh stable baselines. Drift flagged, not repaired.
No scoring concurrent with generation. No R1/E5 or unnamed stage auto-starts.

The request for multiple targets is met by continuing the frozen queue across
blocks until time budget or completion. A partial stage is never marked complete.
Resume uses saved logical keys. No outcomes guide task ordering or cutoff.
