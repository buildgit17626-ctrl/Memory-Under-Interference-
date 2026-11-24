"""Record the audit revision, checks and byte hashes without changing evidence."""

import json
import platform
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from analysis.memory_audit.design import DESTINATION, ROOT
from analysis.memory_audit.records import file_hash, save_json
from analysis.memory_audit.sensors import freeze_inputs


def seal(destination=DESTINATION):
    if not (ROOT / "results/utilisation/continuation-v3/PAUSE").exists():
        raise RuntimeError("Generation must remain paused")
    original = freeze_inputs(destination)
    tests = (destination / "pytest-full.log").read_text(encoding="utf-8-sig")
    lint = (destination / "ruff-check.log").read_text(encoding="utf-8-sig")
    passed = re.search(r"(\d+) passed", tests)
    if (
        passed is None
        or re.search(r"\d+ (failed|error)", tests)
        or "All checks passed!" not in lint
    ):
        raise ValueError("Passing full-suite and Ruff logs required")
    source = list((ROOT / "analysis/memory_audit").glob("*.py"))
    source += [
        ROOT / p
        for p in [
            "analysis/memory_audit/README.md",
            "tests/test_memory_audit.py",
            "requirements.txt",
            "docs/SPEC.md",
            "docs/plans/MEMORY_FINAL_AUDIT_2026_11_24.md",
            "docs/learning/MEMORY_FINAL_AUDIT_2026_11_24.md",
        ]
    ]
    metadata = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "client_audit_date": "2026-11-24",
        "python": platform.python_version(),
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "branch": subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=ROOT, text=True
        ).strip(),
        "source_raw_sha256": {p.relative_to(ROOT).as_posix(): file_hash(p) for p in sorted(source)},
        "original_files_verified_unchanged": len(original),
        "original_bytes_verified_unchanged": sum(r["bytes"] for r in original.values()),
        "generation_paused": True,
        "new_model_generations": 0,
        "pytest_passed": int(passed.group(1)),
        "ruff": "passed",
        "interpretation_status": "provisional; owner review pending",
        "scope": "Phases 1-4 only; no literature novelty claim or manuscript submission",
    }
    save_json(destination / "AUDIT_STATUS.json", metadata)
    output_hashes = {
        p.name: {"bytes": p.stat().st_size, "sha256": file_hash(p)}
        for p in sorted(destination.iterdir())
        if p.is_file() and p.name != "audit-output-manifest.json"
    }
    save_json(destination / "audit-output-manifest.json", output_hashes)
    print(json.dumps({k: v for k, v in metadata.items() if k != "source_raw_sha256"}))


if __name__ == "__main__":
    seal()
