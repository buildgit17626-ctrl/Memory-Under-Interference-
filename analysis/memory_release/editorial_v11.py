"""Verify and package the locally authored editorial revision; never publish or infer."""

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / "releases/v1"
NEW = ROOT / "releases/v1.1"
TAG = "v1.1.0"
URL = "https://github.com/buildgit17626-ctrl/Memory-Under-Interference-/releases/tag/" + TAG


def check() -> dict:
    unchanged = []
    for folder in ("data", "figures", "examples", "tables", "companion", "code"):
        for p in (OLD / folder).rglob("*"):
            if not p.is_file() or "__pycache__" in p.parts:
                continue
            q = NEW / p.relative_to(OLD)
            if (
                not q.exists()
                or hashlib.sha256(p.read_bytes()).digest()
                != hashlib.sha256(q.read_bytes()).digest()
            ):
                raise ValueError("Scientific evidence changed: " + str(p))
            unchanged.append(p.relative_to(OLD).as_posix())
    for name in ("numbers.tex", "inventory_table.tex", "primary_table.tex", "references.bib"):
        assert (OLD / "manuscript" / name).read_bytes() == (NEW / "manuscript" / name).read_bytes()
    for name in (
        "reproduce.py",
        "verify_public.py",
        "requirements-reanalysis.txt",
        "requirements-reanalysis-lock.txt",
    ):
        assert (OLD / name).read_bytes() == (NEW / name).read_bytes()
    old = (OLD / "manuscript/main.tex").read_text()
    new = (NEW / "manuscript/main.tex").read_text()

    def macro(s: str) -> set[str]:
        return set(re.findall(r"\\([A-Z][A-Za-z]+)\{\}", s))

    missing = sorted(macro(old) - macro(new))
    if missing:
        raise ValueError("Verified manuscript result macros omitted: " + str(missing))

    def citations(s: str) -> set[str]:
        return set(re.findall(r"\\cite[pt]?\{([^}]+)\}", s))

    if citations(old) - citations(new):
        raise ValueError("Prior reference omitted")
    if re.search(r"\b(We|we|Our|our)\b", new):
        raise ValueError("Plural authorial voice remains")
    # Release-link digits are metadata, not scientific quantities.
    scientific_old = re.sub(r"v1\.0\.1|Version 1\.0", "", old)
    scientific_new = re.sub(r"v1\.1\.0|Version 1\.1", "", new)

    def numbers(s: str) -> set[str]:
        return set(re.findall(r"(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)*(?![A-Za-z])", s))

    omitted_numbers = sorted(numbers(scientific_old) - numbers(scientific_new))
    if omitted_numbers:
        raise ValueError("Prior numerical literals omitted: " + str(omitted_numbers))
    result = {
        "missing_numerical_literals": omitted_numbers,
        "evidence_and_figure_files_byte_identical": len(unchanged),
        "missing_result_macros": missing,
        "references_retained": True,
        "first_person_singular": True,
        "new_inference": 0,
        "publication": "Not authorized/performed",
        "editorial_version": "1.1",
    }
    (NEW / "checks/editorial-integrity.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def package() -> None:
    check()
    shutil.copyfile(NEW / "manuscript/main.pdf", NEW / "Memory_Under_Interference_v1.pdf")
    files = sorted(
        p
        for p in NEW.rglob("*")
        if p.is_file()
        and p.name not in {"SHA256SUMS.json", "SHA256SUMS.txt"}
        and not (p.name.startswith("Memory_Under_Interference_v1") and p.suffix == ".zip")
        and p.suffix not in {".aux", ".out", ".xdv", ".blg", ".pyc", ".html"}
        and "__pycache__" not in p.parts
        and "local-fonts" not in p.parts
        and p.suffix not in {".ttf", ".otf"}
        and not (p.parent.name == "manuscript" and p.suffix == ".log")
    )
    hashes = {
        p.relative_to(NEW).as_posix(): {
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "bytes": p.stat().st_size,
        }
        for p in files
    }
    (NEW / "SHA256SUMS.json").write_text(json.dumps(hashes, indent=2) + "\n")
    names = [
        "Memory_Under_Interference_v1_source.zip",
        "Memory_Under_Interference_v1_reproducibility.zip",
    ]
    for i, name in enumerate(names):
        with zipfile.ZipFile(NEW / name, "w", zipfile.ZIP_DEFLATED) as z:
            for p in files + ([NEW / "SHA256SUMS.json"] if i else []):
                rel = p.relative_to(NEW)
                if (
                    i
                    or rel.parts[0] in {"manuscript", "figures", "examples", "licenses"}
                    or rel.name in {"compile_manuscript.py", "BUILDING.md", "README.md"}
                ):
                    if i or p.suffix != ".png":
                        z.write(p, rel.as_posix())
        with zipfile.ZipFile(NEW / name) as z:
            assert z.testzip() is None
    assets = ["Memory_Under_Interference_v1.pdf", *names]
    (NEW / "SHA256SUMS.txt").write_text(
        "".join(
            hashlib.sha256((NEW / n).read_bytes()).hexdigest() + "  " + n + "\n" for n in assets
        )
    )
    print(json.dumps({"assets": assets, "external_publication": False}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "package"])
    action = parser.parse_args().action
    if action == "check":
        print(json.dumps(check()))
    else:
        package()
