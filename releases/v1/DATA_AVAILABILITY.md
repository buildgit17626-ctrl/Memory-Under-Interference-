# Data availability and transformations

This local Version 1 candidate contains 5,528 main
logical requests plus separate pilots and partial diagnostics. `data/raw/results/utilisation/`
contains transformed raw call/start/response/scoring/block/validation records, benchmark
and tokenizer artifacts. `data/audit/` contains source-linked derived analysis. Preserved
HTTP response bodies and generated code are untrusted data, never executable instructions.

Original observations/frozen designs remain unchanged. `checks/public-export-provenance.json`
maps original/public SHA256, size and transformations. Known account/root path prefixes,
process snapshots, usernames/hostnames and unnecessary process identifiers are removed in
public copies. JSON whitespace serialization changes are logged; numeric field values
and outcomes remain intact. No metadata deletion is interpreted as a measurement change.
Frozen original hash manifests still identify original bytes, not sanitized copies.

**Energy:** 240 overlapping sensor mirrors are represented by
12 deduplicated numerical CPU-package/time streams in
`data/energy/`. All 12,481 recorded generation/idle windows are mapped;
12,479 available integrals reproduce within 1e-8 Wh,
and 2 unavailable windows remain missing. The largest
observed integration difference is 2.74e-13 Wh. The approximately
11 GB original multi-channel CSV mirrors are not included; unrelated sensor channels
cannot be reconstructed. CPU energy integration can be independently recomputed from
the supplied numerical samples; physical calibration/process-specific energy cannot.

MemoryGraph's pinned original source snapshot, fictional synthetic data, saved scores,
metrics and both demonstration journals are supplied separately under `companion/`.
No trained pickle, pretrained model weights or new inference is required to recompute
its saved-score MRR. It is not pooled with HumanEval+ observations.

`reproduce.py --energy --figures` checks raw-score/call links, main counts, principal
cross-pass effects, paired retention ratios and numerical energy, and regenerates figures.
It does not start Ollama, embeddings or supervisor recovery. Full original execution
would require the original Windows/HWiNFO/runtime environment and original frozen
metadata; the sanitized archive is explicitly an analysis release, not a resume archive.

Original report/data: CC BY 4.0; original code: MIT, as owner-approved. HumanEval MIT
and HumanEval+/EvalPlus Apache-2.0 notices remain applicable. No model/tool binaries
or publisher HTML/PDF caches are distributed. See THIRD_PARTY_NOTICES.md.

No Zenodo/TechRxiv upload or DOI exists as part of preparation. Archive hashes and local
version tag identify the prepared bytes; public availability requires owner approval.
