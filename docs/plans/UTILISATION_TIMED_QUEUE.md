# Time-bounded research queue preparation - 2026-11-21

Owner requested a 7-8-hour segment, preserving completed experiments and using
available time rather than stopping at one/two targets. Full M1 grid approval
and active sensor path are requested; R1/E5 materials remain unresolved.

Files: optional launch callback in shared supervisor, timed-queue helper/tests,
SPEC and CHANGELOG. No generation until a concrete queue, dated registration,
materials, reference validation and owner grid approval are ready.

Queue takes a fixed registered list, resumes missing keys, uses unchanged
25-call blocks, stable idle baselines, drift flags and every other hard stop.
Time cutoff checks occur before scheduling a new logical request, not by killing
an active call. Reserve configured maximum HTTP duration and a measured/bounded
baseline close allowance when deciding whether there is time for another call.
A7.5-hour allocation therefore stops launching earlier, retaining time to close
safely. Publish separate launch cutoff and finish ceiling. Log exact stop reason
and pending counts; never mark an incomplete stage complete. Do not erase
checkpoint gates or silently chain unprepared experiments.

Risks: original3600s HTTP ceiling needs a substantial time reserve. Idle settling
can legitimately halt, output invalidity and input truncation remain visible,
and missing cells at cutoff require explicit reporting. No outcome-dependent
selection. Tests cover callback cutoff, already-complete resume, correct counts
and unchanged hard-stop precedence. Do not modify generated raw data or the
running worker. No scientific prompt/model/token budget changes in this helper.

Unresolved design question: which subsequent full grid is authorised? The user
has been asked explicitly; do not infer unnamed M4/M5 experiment definitions.
