# Version 1 scientific release: what was prepared

This offline milestone turns the accepted journals and prior audit into a local
scientific release candidate. It does not generate new answers, embeddings,
MemoryGraph features or user-study evidence. External publication remains gated.

## Data flow

1. `analysis/memory_release/analytics.py` counts original logical calls and
   reproduces complete-case cross-pass effects. New adverse/favorable censoring
   scenarios are posthoc and explicitly distinguish assigned from observed values.
2. `companion.py` checks the exact MemoryGraph source revision and recalculates
   retrieval ranks from saved scores. Its fictional synthetic dataset is separate.
3. `literature.py` verifies factual bibliography fields from primary pages and
   creates a bounded related-work table; publisher full-text caches are excluded.
4. `figures.py` saves static PDF/PNG figures with numerical CSV inputs. `texdata.py`
   binds manuscript numbers and tables to named source records.
5. `export.py` creates public derivatives and an original/public hash map. It
   removes unnecessary account paths/process metadata, preserving generated code,
   prompts, numerical measurements and outcomes. Original files never change.
6. `sensor_export.py` checks common log prefixes before deduplicating power/time
   streams. Numerical samples reproduce recorded request/idle integrals; they
   do not calibrate the sensor or recover other telemetry channels.
7. The standalone `releases/v1/reproduce.py` checks public raw-score links and
   recalculates principal effects, ratios, figures and energy without inference.
8. `quality.py`, `pdfcheck.py` and `package.py` verify evidence, PDF/build and
   archive identities. The final source/reproduction bundles are local files.

## What the new sensitivity changes

The complete-case 1.5B cross-pass association remains an observed result, but an
adverse assignment of censored outcomes weakens its corrected support. This is
central to the abstract and conclusion. It would be misleading to call the
effect universally robust or evidence of an internal cognitive mechanism.

Oracle retention's lower observed cost does not establish equal/better accuracy
or practical retrieval efficiency. The policies change input length, position,
instructions and output work; retrieval overhead is not measured. E4 remains
incomplete. M1's overlapping bundles and E5's original scoring floor remain
substantive limits. A synthetic retrieval MRR is not code correctness or user
benefit. These are boundaries of the claim, not reasons to hide the observations.

## Author and licence decisions

Owner confirmed Dhruv Brahmbhatt, IIT Madras student and independent researcher;
contributions: questions/design decisions, oversight and interpretation review.
No institutional sponsorship/supervision/endorsement is implied. AI setup,
execution, coding, distractor construction, analysis and drafting are disclosed.
Owner selected CC BY 4.0 for original report/data and MIT for original code.
HumanEval MIT and HumanEval+/EvalPlus Apache-2.0 exceptions remain intact.

## Five questions the owner should be able to answer

1. Which comparisons were registered, and why does Holm4 not cover all exploration?
2. Why do complete-case and adverse-censoring cross-pass results differ?
3. Why can't one connected M1 membership group supply independent-bundle uncertainty?
4. Why do task-bootstrap energy intervals not calibrate CPU power or remove drift?
5. What does MemoryGraph MRR measure, and why doesn't it show an integrated benefit?

Assumptions: the supplied finite test suites define operational correctness;
the release is a narrow observational/controlled-comparison report with explicit
posthoc limits; no recognition, intentional behavior or internal capacity is
measured. Unknown calibration, human annotation and external replication stay
unknown. Publication-readiness is conditional on final owner review, not peer review.
