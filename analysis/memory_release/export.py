"""Separate, auditable public derivatives; never edits original evidence."""

import hashlib
import json
import re
import subprocess

from analysis.memory_audit.records import save_json
from analysis.memory_release.common import AUDIT, RELEASE, ROOT, directories

PREFIXES = (
    (str(ROOT), "SOURCE_ROOT"),
    (ROOT.as_posix(), "SOURCE_ROOT"),
    (str(ROOT).replace("\\", "\\\\"), "SOURCE_ROOT"),
    ("C:\\Users\\Dhruv Brahmbhatt", "LOCAL_USER_ROOT"),
    ("C:/Users/Dhruv Brahmbhatt", "LOCAL_USER_ROOT"),
    ("C:\\\\Users\\\\Dhruv Brahmbhatt", "LOCAL_USER_ROOT"),
    ("C:\\Users\\DHRUVB~1", "LOCAL_USER_ROOT"),
)
TEXT = {".json", ".jsonl", ".csv", ".md", ".txt", ".yaml", ".yml", ".py", ".toml", ".sha256"}


def sanitize_text(text: str) -> tuple[str, int]:
    count = 0
    # Remove only known account-path prefixes; task content/numeric fields remain unchanged.
    for before, after in PREFIXES:
        count += text.count(before)
        text = text.replace(before, after)
    return text, count


def sanitize_json(value, key=""):
    if isinstance(value, dict):
        return {
            k: sanitize_json(v, k)
            for k, v in value.items()
            if k not in {"processes", "hostname", "username", "power_overlay_guid", "pid"}
        }
    if isinstance(value, list):
        return [sanitize_json(v, key) for v in value]
    if isinstance(value, str):
        return sanitize_text(value)[0]
    return value


def public_copy(source, target, manifest):
    raw = source.read_bytes()
    transformed = raw
    operations = []
    if source.suffix in {".json", ".jsonl"}:
        try:
            if source.suffix == ".json":
                original = json.loads(raw)
                clean = sanitize_json(original)
                transformed = (json.dumps(clean, indent=2, ensure_ascii=False) + "\n").encode()
            else:
                original = [json.loads(line) for line in raw.splitlines() if line]
                clean = [sanitize_json(r) for r in original]
                transformed = (
                    "\n".join(json.dumps(r, ensure_ascii=False) for r in clean) + "\n"
                ).encode()
            if original != clean:
                operations.append("known local-path prefixes and process/account metadata redacted")
            if transformed != raw:
                operations.append("JSON serialization normalized; numerical values preserved")
        except (ValueError, UnicodeError):
            transformed = raw
    elif source.suffix in TEXT:
        try:
            clean, count = sanitize_text(raw.decode("utf-8-sig"))
            transformed = clean.encode("utf-8")
            if count:
                operations.append(f"known local-path prefixes replaced: {count}")
        except UnicodeError:
            pass
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(transformed)
    manifest.append(
        {
            "source_relative": source.relative_to(ROOT).as_posix(),
            "public_relative": target.relative_to(RELEASE).as_posix(),
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "public_sha256": hashlib.sha256(transformed).hexdigest(),
            "source_bytes": len(raw),
            "public_bytes": len(transformed),
            "operations": operations,
        }
    )


def main():
    directories()
    manifest = []
    for source in sorted((ROOT / "results/utilisation").rglob("*")):
        if not source.is_file() or "sensors" in source.parts or source.name == ".lock":
            continue
        if source.suffix in {".joblib", ".bin", ".pyc"}:
            continue
        public_copy(source, RELEASE / "data/raw" / source.relative_to(ROOT), manifest)
    for source in sorted(AUDIT.iterdir()):
        if source.is_file():
            public_copy(source, RELEASE / "data/audit" / source.name, manifest)
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    for name in tracked:
        include = name.startswith(
            ("src/", "experiments/", "analysis/", "studies/", "tests/", "data/")
        )
        include |= name.startswith("artifacts/utilisation/")
        include |= name in {
            "requirements.txt",
            "requirements-lock.txt",
            "pyproject.toml",
            "AGENTS.md",
            "README.md",
            "LICENSE",
            "CITATION.cff",
            "docs/SPEC.md",
            "docs/SAFETY.md",
            "docs/REFERENCES.md",
            "docs/ENVIRONMENT.md",
        }
        if include:
            public_copy(ROOT / name, RELEASE / "code" / name, manifest)
    # Include new, not-yet-committed release tooling, without importing or executing copied code.
    for source in sorted((ROOT / "analysis/memory_release").glob("*.py")):
        target = RELEASE / "code" / source.relative_to(ROOT)
        if not target.exists():
            public_copy(source, target, manifest)
    # Original audit manifests describe original bytes; the public hash mapping is authoritative
    # for redacted derivatives, not a claim of byte-identical raw or resumable execution.
    save_json(RELEASE / "checks/public-export-provenance.json", manifest)
    forbidden = re.compile(
        r"(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-proj-[A-Za-z0-9_-]{30,})"
    )
    flags = []
    for item in manifest:
        path = RELEASE / item["public_relative"]
        if path.suffix in TEXT:
            text = path.read_text(encoding="utf-8", errors="replace")
            if forbidden.search(text) or any(prefix in text for prefix, _ in PREFIXES):
                flags.append(item["public_relative"])
    save_json(RELEASE / "checks/public-export-scan.json", {"files": len(manifest), "flags": flags})
    if flags:
        raise ValueError("Public export has sensitive-pattern review flags")
    print(
        json.dumps(
            {
                "public_files": len(manifest),
                "public_bytes": sum(r["public_bytes"] for r in manifest),
                "sensitive_pattern_flags": len(flags),
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
