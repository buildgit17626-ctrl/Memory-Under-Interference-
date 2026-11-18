# Drift handling repair — 2026-11-18

A measurement block still compares its opening and closing idle power using
max(1 W, 10% of opening power). The owner approved changing the consequence:
record a quality flag and continue, rather than stop for drift alone.
The original estimates remain unchanged, so this does not correct drift.

The supervisor writes block details and affected keys to quality-events.jsonl.
The outer workflow then constructs a new sensor and requires fresh stable idle
windows. Code evaluation remains outside measured generation; neither M3
population is scored before the final checkpoint. Other hard stops still halt.

Key files: utilisation_supervisor.py (close handling), utilisation_reliability.py
(fresh stable idle windows and 25-call limit), utilisation_order_v2.py (stage
loops), and the dated DRIFT-AS-FLAG preregistration (approved rule and limits).
The refreshed execution manifest hashes the repair; original study hashes stay.

Questions the owner should be able to answer:
1. What threshold flags a block, and why is that different from correcting it?
2. Which baseline supplies primary net energy?
3. What must happen before the next block can generate?
4. Which conditions can still stop the supervisor?
5. Why are end/midpoint/exclude-block results labelled post hoc?

Assumptions: the active HWiNFO file remains growing at the registered cadence;
the owner launches recovery manually; stable adjacent idle windows do not prove
an unchanged idle trajectory during generation; energy is CPU package energy,
not whole-laptop power. Continuing does not guarantee overnight completion.
