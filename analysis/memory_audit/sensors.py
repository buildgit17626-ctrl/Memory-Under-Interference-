"""Audit captured sensor prefixes and recompute the actual used electrical windows."""

import csv
import hashlib
import io
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from analysis.memory_audit.design import ROOT, STAGES, stage_path
from analysis.memory_audit.records import file_hash, save_json
from prompt_energy.hwinfo import LogFormat
from prompt_energy.utilisation_journal import read_jsonl


def freeze_inputs(destination: Path) -> dict:
    roots = [ROOT / "results/utilisation", ROOT / "studies/utilisation"]
    paths = sorted(
        {
            p
            for root in roots
            for p in root.rglob("*")
            if p.is_file() and p.name != ".lock" and p.suffix not in {".pyc"}
        }
    )
    path = destination / "input-manifest.json"
    if path.exists():
        import json

        previous = json.loads(path.read_text())
        for name, record in previous.items():
            current = ROOT / name
            if current.stat().st_size != record["bytes"] or file_hash(current) != record["sha256"]:
                raise ValueError("Audit evidence changed: " + name)
        return previous
    manifest = {}
    for i, p in enumerate(paths):
        manifest[p.relative_to(ROOT).as_posix()] = {
            "bytes": p.stat().st_size,
            "sha256": file_hash(p),
        }
        if i % 100 == 0:
            print({"snapshot_files_hashed": i, "total": len(paths)}, flush=True)
    save_json(path, manifest)
    return manifest


def prefix_hashes(path: Path, requests: list[dict]) -> list[dict]:
    groups = defaultdict(set)
    for r in requests:
        groups[r["prefix_bytes"]].add(r["sha256"])
    result, h, position = [], hashlib.sha256(), 0
    with path.open("rb") as stream:
        for length, expected in sorted(groups.items()):
            remaining = length - position
            while remaining > 0:
                chunk = stream.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise ValueError("Short sensor mirror: " + str(path))
                h.update(chunk)
                position += len(chunk)
                remaining -= len(chunk)
            result.append(
                {
                    "path": str(path),
                    "bytes": length,
                    "references": len(expected),
                    "match": expected == {h.hexdigest()},
                    "sha256": h.hexdigest(),
                }
            )
    return result


def samples(path: Path) -> tuple[np.ndarray, np.ndarray, list[str]]:
    fmt = LogFormat(encoding="cp1252")
    data = path.read_bytes()
    notes = []
    if not data.endswith(b"\n"):
        notes.append("trailing incomplete line ignored in read-only live-parser equivalence")
        data = data[: data.rfind(b"\n") + 1]
    reader = csv.reader(io.StringIO(data.decode(fmt.encoding)), strict=True)
    header = [s.strip().lstrip("\ufeff") for s in next(reader)]
    if header.count(fmt.power_column) != 1:
        raise ValueError("Ambiguous power header: " + str(path))
    pi, di, ti = header.index(fmt.power_column), header.index("Date"), header.index("Time")
    dates, times, power = {}, [], []
    zone = timezone(timedelta(minutes=fmt.utc_offset_minutes))
    for number, row in enumerate(reader, 2):
        if not row:
            continue
        if len(row) != len(header):
            notes.append(f"strict schema violation at row{number}; no rows past violation used")
            break
        date = row[di].strip()
        if date not in dates:
            dates[date] = datetime.strptime(date, fmt.date_format).replace(tzinfo=zone).timestamp()
        hour, minute, second = row[ti].strip().split(":")
        stamp = dates[date] + int(hour) * 3600 + int(minute) * 60 + float(second)
        watts = float(row[pi])
        if not np.isfinite(watts) or watts < 0 or (times and stamp <= times[-1]):
            notes.append(f"invalid time/power row{number}; no later rows used")
            break
        times.append(stamp)
        power.append(watts)
    return np.array(times), np.array(power), notes


def integrate_many(times: np.ndarray, power: np.ndarray, windows: list[dict]) -> list[dict]:
    dt = np.diff(times)
    area = np.r_[0.0, np.cumsum((power[:-1] + power[1:]) * 0.5 * dt)]

    def integral_at(t):
        i = min(np.searchsorted(times, t, side="right") - 1, len(times) - 2)
        width = t - times[i]
        return area[i] + power[i] * width + (power[i + 1] - power[i]) / dt[i] * width**2 / 2

    result = []
    for window in windows:
        start, end = window["start"], window["end"]
        calculated, reason = None, None
        if len(times) < 2 or start < times[0] or end > times[-1]:
            reason = "coverage unavailable"
        else:
            left = max(0, np.searchsorted(times, start, side="right") - 1)
            right = min(len(times) - 1, np.searchsorted(times, end))
            if np.any(dt[left:right] > 1):
                reason = "sensor gap >1s"
            else:
                calculated = float((integral_at(end) - integral_at(start)) / 3600)
        expected = window["raw_wh"]
        error = calculated - expected if calculated is not None and expected is not None else None
        result.append(
            {
                **window,
                "recomputed_wh": calculated,
                "difference_wh": error,
                "agrees_within_1e_8_wh": abs(error) <= 1e-8 if error is not None else None,
                "unavailable_reason": reason,
            }
        )
    return result


def audit_sensors(destination: Path) -> None:
    windows, references = defaultdict(list), defaultdict(list)

    def collect(value):
        if isinstance(value, dict):
            if {"path", "prefix_bytes", "sha256"} <= set(value):
                references[Path(value["path"])].append(value)
            for v in value.values():
                collect(v)
        elif isinstance(value, list):
            for v in value:
                collect(v)

    for stage in STAGES:
        folder = stage_path(stage)
        calls = read_jsonl(folder / "calls.jsonl")
        for row in calls:
            energy = row.get("energy", {})
            collect(energy)
            snapshot = energy.get("snapshot")
            if snapshot:
                for kind, w in energy["windows"].items():
                    if kind in {"total", "post_load"}:
                        windows[Path(snapshot["path"])].append(
                            {
                                "stage": stage.name,
                                "key": row["key"],
                                "kind": kind,
                                **w,
                            }
                        )
        for name in ("blocks.jsonl", "idle-checks.jsonl"):
            collect(read_jsonl(folder / name))
    hashes, values, files = [], [], []
    for index, path in enumerate(sorted(references)):
        hashes.extend(prefix_hashes(path, references[path]))
        if path in windows:
            t, p, notes = samples(path)
            values.extend(integrate_many(t, p, windows[path]))
            files.append({"path": str(path), "samples": len(t), "notes": notes})
        if index % 10 == 0:
            print({"sensor_mirrors_audited": index + 1, "total": len(references)}, flush=True)
    save_json(destination / "sensor-prefix-audit.json", hashes)
    save_json(destination / "sensor-integration-audit.json", values)
    save_json(destination / "sensor-file-audit.json", files)
