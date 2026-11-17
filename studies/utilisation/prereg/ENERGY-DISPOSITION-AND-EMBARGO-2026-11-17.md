# Approved energy disposition and outcome embargo · 2026-11-17

Owner approved the revised execution order and chose the registered primary
energy disposition on 2026-11-17. This addendum activates the order described
in M3-ORDER-AMENDMENT-2026-11-17.md, subject to the existing hard stops.
No recovery is authorised by this documentation task; the owner launches it
after idle. No requests are repeated and no baseline-drift threshold changes.

## Primary energy

Retain every original gross and start-baseline-adjusted estimate. Join
baseline_drift to all calls in block 6e81165862424391b79b69d0bfbc2dca using
block membership. Do not alter the raw calls or their original flags in place.
affected-calls.csv is a derived flag index for the existing 100 E0 calls.
Finite coverage and a block-level drift warning are distinct attributes.
Keep original request IDs, denominators, power measurements and timestamps.
The primary net energy remains raw gross energy minus the starting idle
baseline times the measured window duration.

## Explicitly post hoc secondary analyses

The owner chose these after observing the drift and its magnitude. Label
every table, plot and estimate "post hoc secondary". They do not replace the
registered primary result or create additional confirmatory tests.

For a call in the specified drifted block, let G be its original post-load
gross Wh and d its recorded post-load window duration in seconds.
Let B_start and B_end be the measured block baselines in W.

- End-baseline net energy is G - B_end*d/3600.
- Midpoint-baseline net energy is G - ((B_start+B_end)/2)*d/3600.
- Exclude-block sensitivity removes that block's calls from energy summaries,
  paired energy contrasts and energy-per-correct numerators and denominators.

Outside that block, retain the original primary values for these targeted
sensitivities. Missing coverage stays missing. Signed estimates, including
negative values, stay signed and flagged. End and midpoint corrections assume
an alternative constant idle reference; they do not establish the unobserved
idle power during each request or a linear drift trajectory.

Report each sensitivity's number of calls, tasks, correct answers, covered
duration and energy sum by condition/model. For paired energy comparisons use
the corresponding shared task/arm population and disclose the reduced sample.
Do not remove a retained arm while keeping its excluded counterpart in a
paired contrast. Energy-per-correct uses exactly the retained attempt
population in both numerator and pass denominator; zero correct gives an
undefined ratio. Exclusion does not delete original correctness, token or
latency observations from their separate analyses.

Report the registered low-resolution sensitivity separately. Any combined
drift/low-resolution exclusion must be explicitly labelled as their
intersection with its own counts. A partial sum cannot be presented as a
fully observed condition total. Future drifted blocks require their own
review; this approval targets the named block.

## Outcome-access restriction

Generate 40 isolated calls, then 100 loaded M3 calls. Neither population is
scored, displayed through the inspection command or used for correctness
analysis before the completed generation-only checkpoint is written.
Counts, timing, token counts, censoring and energy validity remain visible.

The gate releases only after exactly 40 isolated and 100 loaded call records
exist, neither scores journal has entries, the checkpoint has the explicit
generation-only completion reason, and its bytes are hashed into the release
record. A drift/error checkpoint does not release it. A changed checkpoint
closes access again. No scoring is automatically started when it releases.

This is an application-level control on the project scoring/inspection
entry points. Append-only raw journals remain ordinary local files for
auditing; the gate does not impose Windows file permissions on the owner.
The legacy low-level scoring function is retained for the original evaluator
identity; callers must use the guarded public entry points for M3.
