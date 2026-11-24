"""Prepare local, checksummed candidate archives. Never uploads or creates a DOI."""

import hashlib
import json
import re
import shutil
import subprocess
import zipfile

from analysis.memory_audit.records import save_json
from analysis.memory_release.common import MG_COMMIT, RELEASE, ROOT, TITLE, directories

ARCHIVES = (
    "Memory_Under_Interference_v1_source.zip",
    "Memory_Under_Interference_v1_reproducibility.zip",
)


def include(path):
    rel = path.relative_to(RELEASE)
    if rel.name in ARCHIVES or rel.name == "SHA256SUMS.json":
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
    if not json.loads((RELEASE / "checks/visual-review.json").read_text())["passed"]:
        raise ValueError("Rendered PDF review not passed")
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    status = {
        "title": TITLE,
        "version": "1.0.0",
        "candidate_tag": "v1.0.0-rc1",
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
        "external_publication": False,
        "scientific_blockers": [],
        "release_gate": "Final author interpretation/upload approval",
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
    save_json(RELEASE / "checks/RELEASE_STATUS.json", status)
    decision = "# Publication readiness\n\n**READY WITH DISCLOSED LIMITATIONS** "
    decision += "for final author review.\n\n"
    decision += (
        "No remaining compilation, missing-reference, numerical-reproduction or archive-data "
    )
    decision += (
        "blocker is identified by the recorded gates. This is not peer review or a guarantee of "
    )
    decision += "publication. External upload and tag/repository publication remain unapproved.\n\n"
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
    (RELEASE / "PUBLICATION_READINESS.md").write_text(decision, encoding="utf-8")
    shutil.copyfile(RELEASE / "manuscript/main.pdf", RELEASE / "Memory_Under_Interference_v1.pdf")
    output = ROOT / "output/pdf"
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RELEASE / "manuscript/main.pdf", output / "Memory_Under_Interference_v1.pdf")
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
            b"separate reproducibility archive. Not peer reviewed; "
            b"external release needs author approval.\n",
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
    print(json.dumps(status), flush=True)
    print(json.dumps(archive_records), flush=True)


if __name__ == "__main__":
    main()
