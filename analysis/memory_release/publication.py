"""Final identity, scientific-freeze and public-export safety checks; no inference."""

import hashlib
import json
import re
import subprocess

import yaml

from analysis.memory_audit.records import save_json
from analysis.memory_release.common import DOI, DOI_URL, RELEASE, RELEASE_URL, ROOT
from analysis.memory_release.package import include


def main() -> None:
    reference = "v1.0.0-rc2"
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", reference, "--", "releases/v1/tables"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    unchanged = []
    for name in names:
        if name.endswith("manuscript-claim-map.json"):
            continue
        original = subprocess.check_output(["git", "show", reference + ":" + name], cwd=ROOT)
        current = (ROOT / name).read_bytes()
        if original != current:
            raise ValueError("Accepted numerical result table changed: " + name)
        unchanged.append(name)
    old = (
        subprocess.check_output(
            ["git", "show", reference + ":releases/v1/manuscript/main.tex"], cwd=ROOT
        )
        .decode()
        .replace("\r\n", "\n")
    )
    new = (RELEASE / "manuscript/main.tex").read_text(encoding="utf-8")
    for text in (old, new):
        if "\\begin{abstract}" not in text:
            raise ValueError("Manuscript abstract missing")

    def scientific_text(text: str) -> str:
        return text.split("\\begin{abstract}", 1)[1].split(
            "\\section{Data and Code Availability}", 1
        )[0]

    if scientific_text(old) != scientific_text(new):
        raise ValueError(
            "Scientific abstract/results/interpretation changed during publication prep"
        )
    cff = yaml.safe_load((RELEASE / "CITATION.cff").read_text())
    root_cff = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    metadata = json.loads((RELEASE / "zenodo-metadata-draft.json").read_text())
    if cff != root_cff or cff["doi"] != DOI or metadata["doi"] != DOI:
        raise ValueError("DOI/citation identity mismatch")
    for name in (
        "README.md",
        "CITATION.cff",
        "releases/v1/README.md",
        "releases/v1/RELEASE_NOTES_V1.md",
        "releases/v1/manuscript/main.tex",
    ):
        if DOI not in (ROOT / name).read_text(encoding="utf-8"):
            raise ValueError("Reserved DOI missing: " + name)
    if RELEASE_URL not in new or DOI_URL not in new or "reserved" not in new.lower():
        raise ValueError("Manuscript identity/publication-status disclosure missing")
    secret = re.compile(
        r"(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|"
        r"sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)"
    )
    personal_path = re.compile(r"[Cc]:[\\/]+Users[\\/]+(?:Dhruv Brahmbhatt|DHRUVB~1)")
    checked, flags = 0, []
    suffixes = {
        ".json",
        ".jsonl",
        ".csv",
        ".md",
        ".txt",
        ".yaml",
        ".yml",
        ".py",
        ".toml",
        ".sha256",
        ".cff",
        ".tex",
        ".bib",
        ".bbl",
    }
    for path in RELEASE.rglob("*"):
        if not path.is_file() or not include(path) or path.suffix not in suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        checked += 1
        if secret.search(text) or personal_path.search(text):
            flags.append(path.relative_to(RELEASE).as_posix())
    if flags:
        raise ValueError("Public release safety flags: " + ", ".join(flags))
    status = {
        "doi": DOI,
        "doi_status": "Reserved; registration/public accessibility not confirmed",
        "planned_release_url": RELEASE_URL,
        "numerical_tables_identical_to_rc2": unchanged,
        "scientific_abstract_results_interpretation_identical_to_rc2": True,
        "public_text_files_scanned": checked,
        "credentials_or_local_account_path_flags": flags,
        "original_input_preservation": "Separately verified by scientific-quality.json",
        "licences": "Owner-selected MIT/CC BY 4.0 plus retained upstream notices; "
        "permission-audit.json",
        "prior_public_history": "Preserved; historical audit CSVs/host notes/runners contain "
        "owner account-directory provenance. New derivatives redact it; history is preserved.",
        "manuscript_sha256": hashlib.sha256(
            (RELEASE / "manuscript/main.pdf").read_bytes()
        ).hexdigest(),
        "new_inference": 0,
        "release_record_published": False,
    }
    save_json(RELEASE / "checks/publication-safety.json", status)
    print(
        json.dumps(
            {
                "numerical_tables_unchanged": len(unchanged),
                "public_text_files_scanned": checked,
                "safety_flags": flags,
                "doi_status": status["doi_status"],
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
