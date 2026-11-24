"""Versioned scientific claims, reviewer responses and deposit drafts."""

# Generated Markdown tables deliberately keep one complete table row per source line.
# ruff: noqa: E501

import json

import yaml

from analysis.memory_audit.records import save_json
from analysis.memory_release.common import AUDIT, MG_COMMIT, MODELS, RELEASE, TITLE, directories


def ci(values, scale=100):
    return (
        "unavailable"
        if values is None
        else "[" + ", ".join(f"{v * scale:.4g}" for v in values) + "]"
    )


def write(name, text):
    (RELEASE / name).write_text(text.strip() + "\n", encoding="utf-8")


def main():
    directories()
    effects = json.loads((AUDIT / "paired-effects.json").read_text())
    bounds = json.loads((RELEASE / "tables/cross-specification-sensitivities.json").read_text())
    conditions = json.loads((AUDIT / "conditions.json").read_text())
    ratios = json.loads((AUDIT / "energy-per-correct-differences.json").read_text())
    mg = json.loads((RELEASE / "tables/memorygraph-audit.json").read_text())
    counts = json.loads((RELEASE / "tables/source-counts.json").read_text())
    sensor = json.loads((RELEASE / "checks/public-energy-integration.json").read_text())
    findings = [
        "# Version 1 findings",
        "",
        "Release candidate: author interpretation/publication "
        "approval pending. This document freezes evidence-supported wording, not approval "
        "of an internal mechanism or a peer-reviewed claim.",
        "",
        f"Main-study logical requests verified directly from calls.jsonl: "
        f"**{counts['completed_main_logical_requests']:,}**. Pilots remain separate; "
        "E4 full is partial (76/400), E3/U-family/MG1 unrun.",
        "",
        "## A. Alternative-consistent failures (posthoc)",
        "",
        "|Model|Variant|Tasks|Competing minus irrelevant pp|95% task CI pp|Holm4 p|",
        "|---|---|---:|---:|---|---:|",
    ]
    for r in bounds:
        if r["comparison"] == "near-minus-irrelevant":
            findings.append(
                f"|{r['model']}|{r['variant']}|{r['n_units']}|{r['estimate'] * 100:.4g}|"
                f"{ci(r['ci95'])}|{r['holm_family4_p']:.5g}|"
            )
    findings += [
        "",
        "Complete-case evidence on 1.5B is suggestive and cap-sensitive. The adverse "
        "assignment loses corrected support; it is a missing-outcome scenario, not an "
        "observed repair. 0.5B is inconclusive. Isolation is also cross-scored to distinguish "
        "pre-existing alternative behavior. No cognition/intent claim. Sources: "
        "tables/cross-specification-sensitivities.json, data/audit/cross-pass-per-response.csv; "
        "generators: code/analysis/memory_release/analytics.py and "
        "code/analysis/memory_audit/mechanisms.py.",
        "",
        "## B. Task-description content (exploratory)",
        "",
        "|Model|Passive minus matched filler|Tasks|Difference pp|Conditional CI pp|Holm8 p|",
        "|---|---|---:|---:|---|---:|",
    ]
    for r in effects:
        if r["variant"] == "primary" and r["family"] == "M1_matched_filler_posthoc_8":
            findings.append(
                f"|{r['model']}|{r['name']}|{r['n_units']}|{r['estimate'] * 100:.4g}|"
                f"{ci(r['ci95'])}|{r['holm_p']:.5g}|"
            )
    findings += [
        "",
        "The contrasts are conditional on fixed companions. All bundle-membership graphs "
        "have one connected component; robust independent-component CIs are unavailable. "
        "Active mode requests more output and has different budgets. No universal multitasking "
        "penalty or causal internal mechanism is established. Sources: "
        "data/audit/paired-effects.json, m1-bundle-dependencies.json, "
        "m1-work-and-function-cost.json; generators: effects.py, mechanisms.py, robustness.py.",
        "",
        "## C. Retention and cost (descriptive/posthoc energy)",
        "",
        "|Model|Full-history net mWh/correct|Oracle net mWh/correct|Paired difference mWh|95% CI mWh|",
        "|---|---:|---:|---:|---|",
    ]
    for model in MODELS:
        selected = {
            r["condition"]: r for r in conditions if r["stage"] == "R1" and r["model"] == model
        }
        r = next(
            r
            for r in ratios
            if r["stage"] == "R1"
            and r["model"] == model
            and r["comparison"] == "oracle_selective minus full_history"
            and r["field"] == "net_wh"
            and r["variant"] == "primary"
        )
        full, oracle = (
            selected[p]["net_wh_per_correct_covered"]["estimate"] * 1000
            for p in ("full_history", "oracle_selective")
        )
        findings.append(
            f"|{model}|{full:.3f}|{oracle:.3f}|{r['difference'] * 1000:.3f}|{ci(r['ci95'], 1000)}|"
        )
    findings += [
        "",
        "Energy: HWiNFO CPU Package Power, trapezoidal approximate post-load integration, "
        "block-start idle subtraction. All 40 R1 calls per policy/model have readings. "
        "Correctness gains/equivalence are not established. Input length, position, instructions, "
        "output length, caps and privileged relevance knowledge are confounded. No retrieval "
        "overhead is measured. End/midpoint/drift/cap/short sensitivities remain separate; E4 "
        "primary energy evidence is incomplete. Sources: data/audit/conditions.json, "
        "energy-per-correct-differences.json, energy-sensitivities.json; generators "
        "statistics.py, effects.py, robustness.py.",
        "",
        "## D. Preference metric and null/contradictory results",
        "",
        "Original strict E5 adherence is **0/400**. It requires unfenced parseable code; "
        "the instruction did not explicitly ban Markdown fences. Secondary fence/comment/"
        "docstring audits preserve the original scores. Code comments/docstrings are not "
        "automatically explanations. No retention claim follows from the floor. "
        "Registered R1 replay/correctness comparisons and M2 comparisons are inconclusive "
        "after their family corrections; absence of rejection is not equivalence. "
        "Sources: data/audit/e5-joint-outcomes.csv, e5-joint-intervals.json, "
        "paired-effects.json; generators: mechanisms.py, supplement.py, effects.py.",
        "",
        "## E. Companion prototype, not an evaluated intervention",
        "",
        f"Pinned MemoryGraph {MG_COMMIT}: {mg['pairs']} labelled pairs, "
        f"{mg['fictional_users']} fictional profiles, {mg['queries']} queries. "
        f"Saved-score MRR reproduces: embeddings {mg['methods']['semantic']['mrr']:.6f}, "
        f"TF-IDF {mg['methods']['tfidf']['mrr']:.6f}. No new embeddings or model requests. "
        "Synthetic templates, globally fitted lexical benchmark vocabulary, and the "
        "different per-query interface vocabulary limit generality. The recorded pytest "
        "preference demonstration emits unittest; both successful generations are capped. "
        "Correctness/energy were unscored. Source: companion/*.csv/json/jsonl and "
        "tables/memorygraph-audit.json; generator: companion.py.",
        "",
        "## What would change interpretation?",
        "",
        "Alternative/oracle/extraction mistakes; cap assumptions; independent bundle "
        "replication; human semantic adherence annotations; different task populations; "
        "validated energy calibration and end-to-end retrieval overhead. Current findings "
        "do not measure internal memory, recognition, giving up or learned representations.",
    ]
    write("FINDINGS_FINAL.md", "\n".join(findings))
    claim_map = json.loads((RELEASE / "tables/manuscript-claim-map.json").read_text())
    lines = [
        "# Claims and evidence",
        "",
        "Every numerical figure also has a CSV in tables/. "
        "The following macros are generated by code/analysis/memory_release/texdata.py; "
        "rows identify the source and exact selector. Additional design constants are "
        "verified against frozen job fields, not estimated from outputs.",
        "",
        "|Manuscript macro|Value|Source|Selector|",
        "|---|---|---|---|",
    ]
    for name, r in claim_map.items():
        lines.append(f"|{name}|{r['rendered']}|{r['source']}|{r['field']}|")
    lines += [
        "",
        "Other displayed values: cap bounds come from "
        "tables/cross-specification-sensitivities.json; M1 K=6 from "
        "data/audit/paired-effects.json family M1_matched_filler_posthoc_8; R1 correctness "
        "from R1_primary_6; M2 other_three from M2_primary_6. E5 rates are literal counts in "
        "e5-joint-outcomes.csv. E4 counts/matched repeats are in inventory.json and "
        "e4-partial-paired.json. Tables retain pilot/main and model distinctions.",
        "",
        "Allowed: dataset-specific associations and measured descriptive costs, with uncertainty. "
        "Not allowed: internal cognition/capacity, intentional failures, universal optimality, "
        "equivalent accuracy from null tests, first-discovery claims, carbon/cloud/GPU claims, "
        "or an integrated MemoryGraph benefit. M1 independence and E5 semantic adherence "
        "are not supplied by the statistical code.",
    ]
    write("CLAIMS_AND_EVIDENCE.md", "\n".join(lines))
    write(
        "REVIEWER_RESPONSE.md",
        """# Skeptical reviewer audit and responses

|Concern|Response/action|Residual limitation|
|---|---|---|
|Cross-pass is a selected posthoc mechanism story|All target/alternative cells, isolation controls, four-test Holm family, matched IDs and adverse/favorable cap scenarios provided|Complete-case 1.5B association loses corrected support under adverse censoring; no cognition inference|
|M1 treats shared companions as independent|Membership graph and focal/per-function/bundle endpoints retained; conditional intervals labelled|One connected component prevents a robust independent-bundle CI|
|R1 attributes cheaper prompts to better memory|All five policies, accuracy intervals, tokens, ratio CIs and baseline/cap sensitivities shown|Oracle relevance, length, recency, instructions and output work confounded; no retrieval overhead|
|Energy is overstated|CPU-package tool/mode identified, missing/short/drift windows preserved; E4 incomplete explicitly|No physical calibration or whole-system/process isolation|
|E5 changed scoring after seeing failure|Original 0/400 metric preserved; secondary syntax features and joint outcomes separate|No human semantic annotation; floor cannot establish preference retention|
|Only positive results are shown|M2, E0, replay and cap reversals included|Statistical power and fixed-roster generalization limited|
|The narrative reads like an internal audit|Motivation, explicit research questions/contributions and practical interpretation reorganized around behavior and cost|Underlying revised/posthoc design and methodological limits are preserved|
|The diagnostic lacks a concrete example|Actual saved HumanEval/0 response, exact requirements, <= body and validated witness traced by full call key and hashes|Selected illustration is not a prevalence estimate or mechanism test|
|Appendix omits E5 primary entries|All four registered strict-adherence contrasts added with intervals and Holm4 values|All-zero empirical intervals cannot establish population equivalence|
|Public reproduction may depend on private local files|Fresh analysis-only environment and guarded release-only execution recorded|Saved-data reanalysis is not inference regeneration, universal portability or physical calibration|
|MemoryGraph is advertised as GraphRAG or a tested solution|Pinned source, saved synthetic scores, explicit approval and narrow conflicts audited|MG1 unrun; no correctness/energy/usability/trust claim|
|Related work already covers the idea|Fifteen primary publications verified, including recent direct overlap|No priority or exhaustive-review claim|
|Archive changes raw evidence|Public copies only, original/public hash map and explicit metadata/path redactions|Sanitized export is not byte-identical inference-resume evidence|
|Authorship/affiliation inflated|Owner-confirmed name, student status, independent work and contributions; AI help disclosed|Final author review required; no institutional endorsement|

Disposition: release candidate is scientifically supportable only with these limitations.
External publication remains unapproved. Final build and archive checks are recorded separately.
""",
    )
    write(
        "DATA_AVAILABILITY.md",
        f"""# Data availability and transformations

This local Version 1 candidate contains {counts["completed_main_logical_requests"]:,} main
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

**Energy:** {sensor["original_mirrors"]} overlapping sensor mirrors are represented by
{sensor["deduplicated_groups"]} deduplicated numerical CPU-package/time streams in
`data/energy/`. All {sensor["windows"]:,} recorded generation/idle windows are mapped;
{sensor["available_recorded_windows"]:,} available integrals reproduce within 1e-8 Wh,
and {len(sensor["unavailable_windows"])} unavailable windows remain missing. The largest
observed integration difference is {sensor["max_abs_error_wh"]:.3g} Wh. The approximately
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
""",
    )
    write(
        "VERSION_2_ROADMAP.md",
        """# Version 2 roadmap

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
""",
    )
    write(
        "RELEASE_NOTES_V1.md",
        """# Version 1.0 release candidate

Date: 24 November 2026. Status: prepared locally; not peer reviewed; not deposited.

- Frozen completed main scope: E0, M1, initial M3, revised M3/R2, M2, R1, E5.
- Diagnostic pilots separate; revised E4 76/400 and older feasibility versions separate.
- E3, U-family and MG1 unrun. No new Ollama/embedding inference or MemoryGraph features.
- Pinned prior audit source 4d6c60d591c88bfd4b22464e53583a081c40d5c6;
  public audit evidence commit 8275035; repository overview 51a9554.
- Pinned MemoryGraph c569143ec6be1c767a2c56c59c936f85bd1fc1cb.
- New offline work: cap/missingness scenario audit, saved synthetic-metric verification,
  figures, primary-source bibliography, manuscript, public derivatives and numerical
  sensor export. Previously accepted observations/designs/scores remain unchanged.
- Important new caveat: adverse censoring weakens the 1.5B cross-specification finding.
- Original report/data CC BY 4.0; original code MIT, with third-party exceptions retained.
- Local source/tag/build/verification hashes are in checks/RELEASE_STATUS.json and
  SHA256SUMS.json. No DOI/acceptance/endorsement is invented.
- Final rc2 communication revision: explicit research questions/contributions,
  verified 76.5%/67.4% descriptive energy-cost reductions, an actual saved
  target/distractor/code/witness example, selected exact prompt strings, four
  E5 strict-adherence primary rows, common model-comparison axes and clearer labels.
- Analysis-only dependency specifications and a fresh-environment, network/file-
  restricted verification harness distinguish saved-data reproduction from
  regeneration, rescoring or physical energy calibration. See checks/portable-environment.json.

External upload, publication, pushes and tag publication require owner approval.
""",
    )
    citation = {
        "cff-version": "1.2.0",
        "message": "Please cite the independent Version 1 preprint; not peer reviewed.",
        "type": "article",
        "title": TITLE,
        "version": "1.0.0",
        "date-released": "2026-11-24",
        "authors": [
            {
                "family-names": "Brahmbhatt",
                "given-names": "Dhruv",
                "affiliation": "Independent researcher; IIT Madras student",
            }
        ],
        "url": "https://github.com/buildgit17626-ctrl/Memory-Under-Interference-",
        "license": "CC-BY-4.0",
    }
    (RELEASE / "CITATION.cff").write_text(
        yaml.safe_dump(citation, sort_keys=False), encoding="utf-8"
    )
    metadata = {
        "title": TITLE,
        "upload_type": "publication",
        "publication_type": "preprint",
        "publication_date": "2026-11-24",
        "version": "1.0.0",
        "creators": [
            {
                "name": "Brahmbhatt, Dhruv",
                "affiliation": "Independent researcher; IIT Madras student (no institutional endorsement)",
            }
        ],
        "description": "Independent empirical preprint on context/specification utilization "
        "in two small local code models. Posthoc and measurement limitations "
        "are explicit. Not peer reviewed. MemoryGraph is a separate prototype, "
        "not an evaluated integrated intervention. No DOI or external deposit yet.",
        "license": "cc-by-4.0",
        "access_right": "open",
        "keywords": [
            "code language models",
            "context utilization",
            "specification interference",
            "inference efficiency",
            "CPU package energy",
            "memory retrieval",
        ],
        "notes": "DRAFT metadata: review against deposit form before upload. Original code MIT; "
        "third-party notices retained. External publication requires author approval.",
    }
    save_json(RELEASE / "zenodo-metadata-draft.json", metadata)
    write(
        "README.md",
        r"""# Memory Under Interference -- Version 1.0

Local scientific release candidate, 24 November 2026. Not peer reviewed. External
publication requires owner approval. Start with manuscript/main.pdf, FINDINGS_FINAL.md,
CLAIMS_AND_EVIDENCE.md, REVIEWER_RESPONSE.md and DATA_AVAILABILITY.md.

## Reproduce without inference

Use Python 3.13 in a new environment; install requirements-reanalysis.txt for
offline analysis. The historical full experiment lock remains in code/requirements-lock.txt.
requirements-reanalysis-lock.txt records every installed package in the fresh
Windows verification environment; it can be used instead of the shorter direct list.
Then:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-reanalysis-lock.txt
.\.venv\Scripts\python.exe -I verify_public.py --full
```

The guarded verifier restricts this trusted analysis run to the public tree and
Python/Windows runtime, and disables network and subprocess requests. It is not
an OS security sandbox for untrusted code. The simpler unguarded command is:

```powershell
python reproduce.py --full --energy --figures --output reproduced
```

Omit --full for the quicker principal-results check. No Ollama or embedding
server/model is required. Full mode also rebuilds all paired audit effects and
sensitivities, and checks their outcome estimates/CIs/tests against the frozen
audit. This checks 6,006 saved logical
records including separate pilots/diagnostics, verifies the 5,528 main calls, recomputes
the principal paired cross-pass/cost estimates and numerical energy, and regenerates
the eight figures. It never executes generated code. Re-scoring generated programs is
a separate Windows restricted-subprocess operation documented in code/docs/SAFETY.md.
Do not run historical recovery commands against accepted evidence.

Inspect SHA256SUMS.json and checks/public-export-provenance.json for identity and
transformations. Per-figure CSVs, per-task outcomes, raw journals, configs/protocols,
model digests, versions and licence notices are included. Sensor exports are CPU power
and time only; original multi-channel logs and model/runtime binaries are excluded.
The archive is not a byte-identical inference-resume package.

## Compile the manuscript

From this root, with Tectonic installed:

```powershell
tectonic --keep-logs --outdir manuscript manuscript/main.tex
```

An initial build may download standard TeX packages; manuscript/main.bbl is supplied.
The separate source archive retains manuscript/ and figures/ relative paths. No
conference template/acceptance is implied. Version 2 work is in VERSION_2_ROADMAP.md.
Original report/data CC BY 4.0, original code MIT, third-party exceptions retained.

The rc2 revision adds an evidence-linked worked example, exact selected prompt
strings, E5 registered primary contrasts and clearer common-scale policy figures.
See checks/portable-environment.json for the tested installation and filesystem/
network restrictions; these verify saved-data reanalysis, not inference regeneration.
""",
    )
    (RELEASE / "data/LICENSE.md").write_text(
        "Original study observations/derived data: CC BY 4.0. Benchmark and other third-party "
        "content retain their original notices; see THIRD_PARTY_NOTICES.md.\n",
        encoding="utf-8",
    )
    print(json.dumps({"release_documents_prepared": 9, "external_publication": False}), flush=True)


if __name__ == "__main__":
    main()
