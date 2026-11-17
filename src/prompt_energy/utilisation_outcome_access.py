"""Application-level embargo on M3 scoring and output inspection until checkpoint."""

import hashlib
import json
from pathlib import Path

from prompt_energy.records import write_once

PROTECTED = frozenset({"M3", "M3-isolated"})


def initialise_embargo(root: Path) -> None:
    path = root / "outcome-access-v2.json"
    if not path.exists():
        write_once(path, {"state": "embargoed", "protected": sorted(PROTECTED)})


def require_outcome_access(folder: Path) -> None:
    if folder.name not in PROTECTED:
        return
    gate = folder.parent / "outcome-access-v2.json"
    if not gate.exists():
        raise PermissionError("M3 outcomes embargoed until the completed checkpoint")
    record = json.loads(gate.read_text())
    checkpoint = folder.parent / "CHECKPOINT.md"
    if (
        record.get("state") != "checkpoint_published"
        or not checkpoint.exists()
        or hashlib.sha256(checkpoint.read_bytes()).hexdigest() != record.get("checkpoint_sha256")
    ):
        raise PermissionError("M3 outcomes embargoed until the completed checkpoint")


def publish_checkpoint(root: Path) -> None:
    # A drift/error checkpoint never releases the embargo.
    from prompt_energy.utilisation_run import by_key

    if len(by_key(root / "M3-isolated/calls.jsonl")) != 40:
        raise ValueError("Require 40 completed isolated calls")
    if len(by_key(root / "M3/calls.jsonl")) != 100:
        raise ValueError("Require 100 completed loaded calls")
    for phase in PROTECTED:
        if by_key(root / phase / "scores.jsonl"):
            raise ValueError("M3 outcomes were scored before checkpoint")
    checkpoint = root / "CHECKPOINT.md"
    data = checkpoint.read_bytes()
    if b"STOP: 40 isolated baselines and 100 M3 generations; scoring deferred" not in data:
        raise ValueError("Checkpoint is not the completed generation-only checkpoint")
    path = root / "outcome-access-v2.json"
    pending = root / "outcome-access-v2.pending"
    pending.write_text(
        json.dumps(
            {
                "state": "checkpoint_published",
                "checkpoint_sha256": hashlib.sha256(data).hexdigest(),
                "protected": sorted(PROTECTED),
            },
            indent=2,
        )
        + "\n",
        encoding="utf8",
    )
    pending.replace(path)


def inspect_outputs(folder: Path) -> list[dict]:
    require_outcome_access(folder)
    from prompt_energy.utilisation_run import by_key

    return list(by_key(folder / "calls.jsonl").values())


def evaluate(folder: Path, tasks: dict, config: dict) -> None:
    require_outcome_access(folder)
    from prompt_energy.utilisation_eval import evaluate as legacy_evaluate

    legacy_evaluate(folder, tasks, config)
