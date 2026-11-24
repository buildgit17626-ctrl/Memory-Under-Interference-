# Version 2 roadmap

1. Freeze a separate MG1 study on genuinely held-out scenarios. Compare full history,
   oracle retention, TF-IDF and the existing MemoryGraph retriever at matched generation
   settings. Measure retrieval evidence, correctness, adherence and complete overhead.
2. Preserve conflicting/hard-negative cases and register the annotation protocol before
   collecting results. Keep approved context visible to a human reviewer when relevant.
3. Separate retention selection, prompt length/position/instructions and output budgets.
   Test whether practical retrieval approaches the privileged reference, without assuming it.
4. Replace M1 overlapping designs with independently replicated bundles or a registered
   dependency-aware sampling design; keep function and whole-bundle outcomes distinct.
5. Validate a semantic preference-adherence rubric with independent annotations and
   agreement measurements. Do not retroactively replace Version 1's registered metric.
6. Improve CPU energy measurement/calibration and baseline controls; finish or redesign
   cache experiments only under a new registration. Count retrieval/indexing overhead.
7. Replicate on additional models/tasks/hardware only after fixed analysis choices and
   compute budgets. Human-side work requires institutional consent where applicable.

These are future plans, not completed experiments or implied capabilities. Version 1
does not depend on additional E3/U-family/MemoryGraph inference and launches none.
