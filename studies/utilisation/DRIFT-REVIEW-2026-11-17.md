# Drift review and recovery · 2026-11-17

No recovery or generation was performed during this change.

CHECKPOINT.md contains "Baseline power drift beyond registered threshold".
The checkpoint itself contains no numeric baseline measurements; those are
recovered from the matching start/end events in E0/blocks.jsonl and joined by
block ID to all affected calls. evidence.json and affected-calls.csv reproduce
the numbers and all 100 request/window identities.

The registered start baseline is 11.26919846134594 W and end baseline is
9.59877406792041 W. Signed drift is -1.670424393425531 W, beyond the unchanged
1.1269198461345942 W threshold. The block-level flag applies to all 100 calls,
rather than locating a known drift onset. All 100 windows have finite readings.

Choices remain open. Retaining original gross/net values with the drift flag
is registered. Excluding the block's energy, substituting end/midpoint
sensitivities or rerunning equivalent requests each needs a separately
documented amendment. None was selected. Generated answers are preserved.

The new execution order is a draft in
studies/utilisation/prereg/M3-ORDER-AMENDMENT-2026-11-17.md. The legacy entry
point is preserved. Do not use its recovery command for the proposed order.
The separate version-2 entry point requires an explicit owner review record,
including the chosen energy disposition. Its current review record is pending
and contains no selection.

After approving that draft and resolving the disposition, the exact command
from the repository root is:

    .\.venv313\Scripts\python.exe -u -m experiments.supervise_v2 recover

The current command would halt at the review gate before contacting Ollama.
The version-2 implementation presently supports the registered retain-and-flag
option; alternative energy treatments require their corresponding analysis
amendment before this command can proceed. No default option is selected by
the draft review record.

The order tests invoke mocked stage operations and the full injected workflow.
They require 40 baseline calls before any loaded M3 call, prohibit M3 scoring,
stop at exactly 100 loaded calls, block pending reviews and prevent proceeding
after an isolated-baseline failure. All new source, baseline catalogue and
amendment text have a separate manifest. Original frozen hashes stay unchanged.
