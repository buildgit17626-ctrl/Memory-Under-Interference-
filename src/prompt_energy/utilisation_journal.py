"""Append-only JSONL segments. Preserve torn writes as forensic evidence."""

import json
from pathlib import Path

from prompt_energy.records import append_json as durable_append


def segments(path: Path) -> list[Path]:
    return [path, *sorted(path.parent.glob(path.name + ".part-*"))]


def append_json(path: Path, row: dict) -> None:
    parts = segments(path)
    target = parts[-1]
    if target.exists() and target.stat().st_size:
        with target.open("rb") as stream:
            stream.seek(-1, 2)
            complete = stream.read() == b"\n"
        if not complete:
            target = path.with_name(f"{path.name}.part-{len(parts):08d}")
    durable_append(target, row)


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for part in segments(path):
        if part.exists():
            with part.open("rb") as stream:
                for line in stream:
                    if line.endswith(b"\n"):
                        rows.append(json.loads(line))
    return rows
