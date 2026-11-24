"""Prepare final checksummed artifacts; never publish a release record or reserve a DOI."""

import hashlib
import json
import re
import shutil
import subprocess
import zipfile

from analysis.memory_audit.records import save_json
from analysis.memory_release.common import (
    DOI,
    DOI_URL,
    MANUSCRIPT_VERSION,
    MG_COMMIT,
    RELEASE,
    RELEASE_TAG,
    RELEASE_URL,
    ROOT,
    TITLE,
    directories,
)

ARCHIVES = (
    "Memory_Under_Interference_v1_source.zip",
    "Memory_Under_Interference_v1_reproducibility.zip",
)


def include(path):
    rel = path.relative_to(RELEASE)
    if rel.name in ARCHIVES or rel.name in {"SHA256SUMS.json", "SHA256SUMS.txt"}:
        return False
    if rel.as_posix() == "checks/archive-deliverables.json":
        return False
    if rel.parent.name == "manuscript" and rel.suffix == ".log":
        return False
    if rel.suffix in {".aux", ".out", ".xdv", ".blg", ".pyc"} or "__pycache__" in rel.parts:
        return False
    if rel.parts[0] == "literature" and rel.suffix == ".html":
        return False
    return True


def add(archive, name, data):
    info = zipfile.ZipInfo(name, date_time=(2026, 11, 24, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def main():
    directories()
    quality = json.loads((RELEASE / "checks/scientific-quality.json").read_text())
    pdf = quality["pdf"]
    tests = (RELEASE / "checks/pytest-full.log").read_text(encoding="utf-8-sig")
    lint = (RELEASE / "checks/ruff.log").read_text(encoding="utf-8-sig")
    passed = re.search(r"(\d+) passed", tests)
    if (
        passed is None
        or re.search(r"\d+ (failed|error)", tests)
        or "All checks passed!" not in lint
    ):
        raise ValueError("Passing full tests and Ruff logs required")
    if not (RELEASE / "checks/visual-review.json").exists():
        raise ValueError("Rendered-page review record required")
    visual = json.loads((RELEASE / "checks/visual-review.json").read_text())
    if not visual["passed"]:
        raise ValueError("Rendered PDF review not passed")
    if (
        visual["pdf_sha256"]
        != hashlib.sha256((RELEASE / "manuscript/main.pdf").read_bytes()).hexdigest()
    ):
        raise ValueError("Visual review does not describe the current PDF")
    if "fresh_environment_public_reproduction" not in quality:
        raise ValueError("Final revision requires the recorded fresh-environment reproduction")
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    status = {
        "title": TITLE,
        "version": MANUSCRIPT_VERSION,
        "github_release_version": "1.0.1",
        "release_tag": RELEASE_TAG,
        "artifact_status": "Final Version 1 artifacts verified",
        "doi": DOI,
        "doi_url": DOI_URL,
        "doi_status": "Reserved by owner; registration/public accessibility not confirmed",
        "planned_github_release": RELEASE_URL,
        "source_commit": source_commit,
        "memorygraph_commit": MG_COMMIT,
        "readiness": "READY WITH DISCLOSED LIMITATIONS",
        "main_text_pages": pdf["main_text_pages"],
        "total_pdf_pages": pdf["pages"],
        "main_logical_requests": 5528,
        "pytest_passed": int(passed.group(1)),
        "ruff": "passed",
        "pdf_compiled_and_rendered": True,
        "new_model_or_embedding_inference": 0,
        "build_stage": "Verified artifacts prepared for authorized GitHub publication",
        "zenodo_publication_performed": False,
        "github_publication_authorized": True,
        "scientific_blockers": [],
        "repository_main_push_authorized": True,
        "release_gate": "Verify GitHub upload/tag/latest state; Zenodo remains owner-only",
        "limitations": [
            "Posthoc cross-pass finding sensitive to adverse censoring",
            "M1 overlapping fixed bundles; no robust component CI",
            "R1 oracle/length/position/instruction/output confounding",
            "E5 strict-metric floor; no human semantic annotation",
            "CPU-package estimates uncalibrated; E4 incomplete",
            "Synthetic MemoryGraph rankings are not integrated MG1 evidence",
            "Two quantized models, one benchmark and one CPU",
        ],
    }
    repository_check = RELEASE / "checks/repository-preflight.json"
    if repository_check.exists():
        status["repository_preflight"] = json.loads(repository_check.read_text())
    save_json(RELEASE / "checks/RELEASE_STATUS.json", status)
    decision = "# Publication readiness\n\n**READY WITH DISCLOSED LIMITATIONS** "
    decision += "for final Version 1 artifacts.\n\n"
    decision += (
        "No remaining compilation, missing-reference, numerical-reproduction or archive-data "
    )
    decision += (
        "blocker is identified by the recorded gates. This is not peer review or a guarantee of "
    )
    decision += (
        "publication. GitHub packaging release v1.0.1 is authorized. The approved research "
        "manuscript remains Version 1.0; Zenodo publication is left to the author.\n\n"
    )
    decision += (
        f"Reserved DOI: {DOI} ({DOI_URL}); registration/public accessibility is not "
        f"confirmed. Version-specific GitHub release: {RELEASE_URL}.\n\n"
    )
    decision += (
        "The strongest 1.5B complete-case result is cap-sensitive; M1 independence is unresolved; "
    )
    decision += (
        "R1 energy is descriptive/confounded; E5 has a scoring floor; E4 is incomplete; MG1 is "
    )
    decision += "unrun. These constrain claims rather than disappear at release.\n\n"
    decision += (
        f"Validation: {passed.group(1)} tests; Ruff clean; {pdf['main_text_pages']} main pages "
    )
    decision += f"and {pdf['pages']} total PDF pages. See checks/ for evidence.\n"
    decision += (
        "\nSaved-data reanalysis was verified from an extracted public archive in a fresh "
        "Windows/Python environment, with original-data/network access blocked. This is not "
        "inference regeneration, independent rescoring, sensor calibration or demonstrated "
        "Linux/macOS portability. Original multi-channel sensor mirrors are excluded; "
        "numerical CPU power/time samples are included.\n"
    )
    decision += (
        "\nGitHub v1.0.1 supersedes v1.0.0 without changing its tag target "
        "51a95541e9f9c94ef8c2ca35a743bd3dfd41dc16. Only a superseded notice is added "
        "to the old release; its original body/history are retained. Public asset hashes, "
        "new tag target and latest status are checked after upload. This build report "
        "records pre-publication artifact checks; it does not publish Zenodo.\n"
    )
    (RELEASE / "PUBLICATION_READINESS.md").write_text(decision, encoding="utf-8")
    shutil.copyfile(RELEASE / "manuscript/main.pdf", RELEASE / "Memory_Under_Interference_v1.pdf")
    output = ROOT / "output/pdf"
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RELEASE / "manuscript/main.pdf", output / "Memory_Under_Interference_v1.pdf")
    (RELEASE / "UPLOAD_GUIDE.md").write_text(
        "# Version 1 upload guide\n\n"
        f"Final release tag: {RELEASE_TAG}. DOI: {DOI} (reserved, not confirmed published "
        "or publicly accessible). The exact final main commit is reported separately to "
        "avoid a self-referential commit hash.\n\n"
        "Upload these files from this directory to both the GitHub release and Zenodo:\n\n"
        "- Memory_Under_Interference_v1.pdf\n"
        "- Memory_Under_Interference_v1_source.zip\n"
        "- Memory_Under_Interference_v1_reproducibility.zip\n"
        "- SHA256SUMS.txt (SHA-256 hashes of the upload assets)\n\n"
        "Use zenodo-metadata-draft.json to populate/review the reserved Zenodo record; "
        "use RELEASE_NOTES_V1.md for the GitHub release body. PUBLICATION_READINESS.md "
        "records the checks and disclosed scientific limitations. SHA256SUMS.json is the "
        "inner file manifest, also inside the reproducibility archive. Licences, notices, "
        "raw-response derivatives and numerical sensor samples are inside that archive.\n\n"
        "This packaging command performs no uploads. The separate authorized handoff "
        "publishes GitHub v1.0.1 and marks v1.0.0 superseded without moving its tag. "
        "Zenodo must be published manually by the author. "
        "Do not treat the reserved DOI as registered or publicly accessible.\n",
        encoding="utf-8",
    )
    files = sorted(p for p in RELEASE.rglob("*") if p.is_file() and include(p))
    hashes = {
        p.relative_to(RELEASE).as_posix(): {
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        for p in files
    }
    save_json(RELEASE / "SHA256SUMS.json", hashes)
    source_files = [
        p
        for p in files
        if (p.parent.name == "manuscript" and p.suffix in {".tex", ".bib", ".bbl"})
        or (p.parent.name == "figures" and p.suffix == ".pdf")
        or p.parent.name == "examples"
        or p.parent.name == "licenses"
    ]
    with zipfile.ZipFile(RELEASE / ARCHIVES[0], "w") as archive:
        for p in source_files:
            add(archive, p.relative_to(RELEASE).as_posix(), p.read_bytes())
        add(
            archive,
            "README.txt",
            b"Manuscript source bundle: compile manuscript/main.tex with Tectonic. "
            b"Relative figures/ and bibliography files are supplied. For data reanalysis use the "
            b"separate reproducibility archive. Final Version 1 artifacts; not peer reviewed. "
            b"DOI 10.5281/zenodo.24500468 is reserved, not confirmed publicly accessible. "
            b"GitHub package v1.0.1; manuscript Version 1.0. Zenodo publication is manual.\n",
        )
    with zipfile.ZipFile(RELEASE / ARCHIVES[1], "w") as archive:
        for p in files + [RELEASE / "SHA256SUMS.json"]:
            add(archive, p.relative_to(RELEASE).as_posix(), p.read_bytes())
    archive_records = []
    for name in ARCHIVES:
        path = RELEASE / name
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError("Archive CRC failed: " + bad)
            archive_records.append(
                {
                    "file": name,
                    "bytes": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "members": len(archive.infolist()),
                }
            )
    save_json(RELEASE / "checks/archive-deliverables.json", archive_records)
    # The fourth release asset is the manifest itself; never hash it recursively.
    uploads = ["Memory_Under_Interference_v1.pdf", *ARCHIVES]
    (RELEASE / "SHA256SUMS.txt").write_bytes(
        "".join(
            hashlib.sha256((RELEASE / name).read_bytes()).hexdigest() + "  " + name + "\n"
            for name in uploads
        ).encode("utf-8")
    )
    print(json.dumps(status), flush=True)
    print(json.dumps(archive_records), flush=True)


if __name__ == "__main__":
    main()
