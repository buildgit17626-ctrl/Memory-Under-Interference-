# Final preprint revision, 24 November 2026

The revision changes communication and release checks, not experiments. The
manuscript now starts with the practical problem of selecting context, states
three research questions and three contributions, and discusses what execution
outcomes imply for memory systems before collecting the broader limitations.

An actual HumanEval/0 response uses <= where the target requires <. Its archived
alternative-suite and distinguishing-witness outcomes support the worked example.
`analysis/memory_release/examples.py` copies exact prompts and code from public
journals, removes only a docstring for one labelled listing, and records source
keys/hashes. It never executes generated code. Repeated alternative descriptions
are explicitly visible as part of the original context construction.

`texdata.py` computes observed energy-cost reductions from the original R1 ratios
and includes the four registered E5 strict-adherence contrasts. Zero E5 differences
do not establish population equivalence. The two reductions are descriptive;
accuracy uncertainty, privileged relevance and instruction/length/output
confounding remain. Figure model panels now use common scales for each metric.

The public `reproduce.py` checks integrity before recomputing outcomes, paired
effects, ratios, example-linked quantities and numerical energy. Analysis-only
dependencies support a fresh venv. `verify_public.py` uses Python audit hooks to
block access outside the public tree/runtime, network and subprocesses during
this trusted run; it is not an OS security sandbox. Its original-data probe and
observed environment are recorded, not assumed. No inference regeneration,
new program rescoring, cross-platform replication or physical energy calibration
is claimed by a successful saved-data reanalysis.

Owner questions:
1. How does an alternative-suite pass add information to a target failure?
2. Why is the exact repeated-background prompt relevant to interpreting the example?
3. Why do 76.5% and 67.4% lower observed estimated costs not establish safe savings?
4. Why do E5's four null primary contrasts not establish retained preferences?
5. Which parts are reproduced from public records, and which require new execution?

Assumptions: the previously confirmed author details, contribution statement and
licences remain valid. Final interpretation and external publication still need
owner approval. The rc1 tag and all original observations remain unchanged.
