# Snapshot freshness repair — 2026-11-19

Files: hwinfo.py, utilisation_run.py, parser/sensor tests, SPEC, CHANGELOG,
learning note and execution manifest. No model calls or scoring during repair.

Compare sensor time against the clock captured immediately after reading its
byte snapshot, rather than the later time after parsing the whole file.
Keep full strict parsing, append-only growth checks and the same freshness and
cadence limits. Report parsing delay separately in preflight metadata. Apply
the same reference-clock correction to each before-request sensor check.
This checks snapshot freshness; it does not claim zero validation overhead or
validate that logging stayed live throughout parsing. Future parsing efficiency
work is outside this fix.

Evidence: ver4 log live in two read-only observations three seconds apart;
120313758-byte snapshot, 81749 samples, 2.3258841037750244 seconds parsing,
0.11919522285461426 seconds sensor age at read and 2.4450793266296387 after parse.
This shows a possible false-stop mechanism, not proof of the historical cause.

Risks: reading/parsing remains costly, and a real logger outage must still fail.
Tests simulate a slow parse of a fresh snapshot and an already-stale snapshot.
No threshold, measurement window, raw data or research design changes. No open
design questions; assumption is a shared Windows sensor/client wall clock.
