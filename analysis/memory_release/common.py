"""Offline Version 1 preparation paths and immutable evidence references."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
AUDIT = ROOT / "artifacts/memory-audit/2026-11-24-v1"
RELEASE = ROOT / "releases/v1"
MEMORYGRAPH = Path(
    os.environ.get("MEMORYGRAPH_AUDIT_ROOT", str(ROOT / "companion-checkouts/MemoryGraph"))
)
MG_COMMIT = "c569143ec6be1c767a2c56c59c936f85bd1fc1cb"
AUDIT_COMMIT = "4d6c60d591c88bfd4b22464e53583a081c40d5c6"
TITLE = (
    "Memory Under Interference: Context Utilization, Specification Confusion, "
    "and Inference Efficiency in Small Code Language Models"
)
MODELS = ("qwen2.5-coder:0.5b", "qwen2.5-coder:1.5b")
DOI = "10.5281/zenodo.24500468"
DOI_URL = "https://doi.org/" + DOI
MANUSCRIPT_VERSION = "1.0"
RELEASE_TAG = "v1.0.1"
RELEASE_URL = (
    "https://github.com/buildgit17626-ctrl/Memory-Under-Interference-/releases/tag/" + RELEASE_TAG
)


def require_pause() -> None:
    if not (ROOT / "results/utilisation/continuation-v3/PAUSE").exists():
        raise RuntimeError("Generation must remain paused for release preparation")


def directories() -> None:
    require_pause()
    for name in ("manuscript", "figures", "tables", "checks", "data", "companion", "literature"):
        (RELEASE / name).mkdir(parents=True, exist_ok=True)
