# Revised memory-under-interference study — 2026-11-20

Authority: owner supplied revised structure and requested skipping completed
experiments. Owner approved original fixed 40-task roster shared by models and
reduced pilot-first M1. This supersedes the pending three-cell R1 question,
not immutable historical registrations. No full-run launch in preparation.

Files: modular draft stimulus builders (M1, revised M3/R2, five-policy R1),
audit/prepare CLI, unit tests, separate revision design/roster/condition files,
SPEC and CHANGELOG. Original config/stimuli/hashes/results remain untouched.

Completed E0 and original M3 are skipped. Offline evaluation of the saved
40 isolated and 240 loaded responses uses the accepted oracle. Audit rows,
denominators, settings, failures and exact-input reuse without changing calls.
Original E0 is temperature 0.2; M3 isolation is temperature 0, 20 selected tasks
per model, with a different context setting from some revised stages.

Prepare draft matrices, never silently treat planner budgets as observed counts.
M1 full stated grid costs 960 calls plus matching isolation. Reduced pilot:
propose five seed-selected fixed-roster tasks, K=2 and 4, passive/active/filler,
both models = 60 plus up to 10 isolation calls. This subset is proposed, not
owner-approved factors yet. Full matrices remain reviewable before generation.
R1 five policy matrix costs 400 calls on 40 tasks/two models; exact history,
preference, summary and retrieval texts need semantic validation and review.
Revised M3/R2 first reduced grid costs 960 calls, not a rerun of legacy M3;
contradictory compatible distractors and distinguishing tests remain required.

Design: builders require explicit task rosters, companions/filler/materials and
independent token counts. No references/tests enter prompts. M1 active outputs
require all named functions and K-scaled output budgets; target scores must be
reported separately from all-functions success. Counterbalance target ordering;
passive and length-matched controls share one target order per item. R1 accepts
owner-reviewed summaries rather than inventing a summary algorithm. New M3
rejects unverified near-duplicate materials. Pilots are diagnostic and excluded
from final hypothesis tests unless separately preregistered otherwise.

Risks: context overflow, signature collision, unequal filler lengths, summary
loss, oracle retrieval advantage, generation/scoring overlap and scope creep.
Tests verify no reference leakage, exact matrix counts, deterministic roster,
matching controls, output isolation and explicit material blockers. Research
questions remain pending for exact pilot factors and R1 material rules; ask
owner before freezing them. All full runs need new dated hashed registration,
small pilot, oracle validation and measured timing review first. E4 cannot fit
separate prefill/decode token slopes from fixed decode length alone.

Assumptions: review documents are drafts; no revised-generation authorization
is inferred from time availability. The old freeze stays until owner changes it.
