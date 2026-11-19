# Sensor snapshot freshness

The log snapshot may be fresh when read, but parsing a long history takes time.
The old check counted parsing time as sensor age. Now freshness uses the clock
immediately after reading; preflight reports parsing delay separately. Strict
CSV validation, the freshness threshold and logging-growth checks are unchanged.
No raw data or completed requests are rewritten. Read-time freshness does not
prove the logger continued during validation, and full-history parsing remains
an overhead to address separately.

Key files: hwinfo.py (preflight), utilisation_run.py (before-request check),
test_hwinfo.py and test_utilisation.py (fresh/stale slow-parse cases).

Five questions:
1. How is sensor age different from parsing delay?
2. Which clock time is used now?
3. Does an already-stale snapshot still fail?
4. What does append-growth preflight establish?
5. Why does this not establish continuous logging during validation?

Assumptions: sensor timestamps and client wall clock share the registered local
time interpretation. No threshold changes or new generation are part of repair.
