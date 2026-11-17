# Approved measurement reliability amendment · 2026-11-17

The owner approved shorter blocks and an idle stability check after the second
baseline-drift halt. This changes measurement scheduling only; the original
model tags/digests, decoding, task order, prompts, sample keys and the 100-M3
checkpoint limit remain fixed.

## Measurement blocks and idle check

Use at most 25 logical calls in a measurement block. Before opening the
scored window, collect two consecutive 60-second idle windows using HWiNFO.
Accept the latter as the starting baseline only if their absolute power
difference is <=max(1 W,10% of the earlier window). These are the original
absolute/fractional constants; the registered drift threshold is unchanged.

If a pair fails, record both and collect another idle window; compare adjacent
windows. Bound preparation to six windows (about 6.5 minutes including gaps)
and halt if none settles. No scored generation occurs during that wait.
Preserve all idle-window measurements and log window number and mean power.

Collect the ending 60-second baseline after each short block. If drift
exceeds the unchanged threshold, retain all observations and halt. Do not
automatically override or resume that hard stop. Additional idle windows and
shorter blocks add overhead, so earlier runtime forecasts must be revised.
An estimate of 8–11 hours to checkpoint no longer includes these additions.

The 40-isolated-call stage uses 25+15 calls. The loaded M3 stage uses four
25-call blocks, then stops at exactly 100 calls. Both outcome populations
remain embargoed until the completed checkpoint. E0 uses consecutive blocks
of at most 25 calls, with separate scoring between them.

## Runtime and error handling repairs

Ollama returned HTTP 500 "prediction aborted, token repeat limit reached"
for the same failed logical call on six attempts. Future explicit repeat-limit
aborts are terminal runtime failures, kept invalid with unavailable counts,
rather than sent identically five more times. Other transient API/transport
failures retain the original retry budget. Do not alter any existing attempts,
flags or scores retrospectively.

Future drift checkpoints contain block ID, starting/ending baseline windows,
signed drift, registered threshold and affected request keys. If another
failure triggered closure, report it as well rather than masking it with
the subsequent baseline-drift failure. Keep all original raw data.

## Environment finding and interpretation

The second block's surviving-process snapshots show OneDrive used about
1487 CPU-seconds. This is competing computation and a plausible contributor
to measurement variability, not proof that it alone caused drift. Pause
OneDrive syncing for the run and avoid other heavy work. Keep logs outside
live-sync folders and restore syncing afterwards. If drift persists after
removing that activity, revisit thermal settling and remaining background work.

No model requests or recovery are performed as part of this repair.
The existing 200 completed logical calls remain preserved, including the
single exhausted runtime-abort call. No model outcome is repaired or replaced.
