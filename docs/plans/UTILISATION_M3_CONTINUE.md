# M3 continuation after reviewed checkpoint — 2026-11-19

Owner reviewed first-100 verification and requested continuation, with ver5 log.
Files: utilisation_m3_continue.py, continue_m3.py CLI, tests, schedule-bound review
receipt, execution hashes, SPEC, CHANGELOG and learning note.

Verify original study/execution hashes, checkpoint receipt/hash, completed E0
1968 plus 40 isolated baselines and the selected M3 schedule. Freeze owner review
against that selected 240-call schedule. Continue missing calls only in original
order, at most 25 per block with existing stable baselines, drift flags and all
other hard stops. Finish at exactly 240, write a separate continuation checkpoint
without overwriting the original first-100 gate. No scoring, new task selection,
extension or later experiment. No generation during implementation/testing.

Risk: journal interruption, logger failure, unavailable runtime, insufficient
idle settling and experiment freeze can halt collection. Tests cover resume,
wrong receipt/schedule, extra keys and no stages beyond 240. Assumptions: owner
launches in terminal with live HWiNFO, fixed model digests and approved power
state. No research design question or parameter change; this executes remaining
calls in the originally approved M3 grid. Later stimuli remain separately gated.
