"""Recorded host/process snapshots are evidence, not per-call energy attribution."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from analysis.memory_audit.design import DESTINATION, STAGES, stage_path
from analysis.memory_audit.records import save_json
from prompt_energy.utilisation_journal import read_jsonl


def process_deltas(before, after):
    starts = {(r["pid"], r["name"]): r for r in before if r["pid"] != 0}
    rows, resets = [], []
    for end in after:
        identity = end["pid"], end["name"]
        start = starts.get(identity)
        if start is None or start.get("cpu_times") is None or end.get("cpu_times") is None:
            continue
        # Windows psutil user/system CPU seconds; child counters are not added again.
        delta = sum(end["cpu_times"][:2]) - sum(start["cpu_times"][:2])
        if delta < 0:
            resets.append(identity)
        else:
            rows.append({"pid": end["pid"], "name": end["name"], "cpu_seconds_delta": delta})
    return rows, resets


def environment_audit(destination=DESTINATION):
    rows, settings = [], []
    for stage in STAGES:
        blocks = {}
        for event in read_jsonl(stage_path(stage) / "blocks.jsonl"):
            blocks.setdefault(event["block"], {})[event["event"]] = event
        for block, events in blocks.items():
            start, end = events.get("start", {}), events.get("end", {})
            host = start.get("host") or {}
            deltas, resets = process_deltas(start.get("processes", []), end.get("processes", []))
            rows.append(
                {
                    "stage": stage.name,
                    "block": block,
                    "host": host,
                    "ac_best_performance_observed": host.get("ac_line_status") == 1
                    and host.get("power_mode") == "Best performance",
                    "start_w": (start.get("baseline") or {}).get("watts"),
                    "end_w": (end.get("baseline") or {}).get("watts"),
                    "drift_w": end.get("drift_w"),
                    "flags": end.get("flags", []),
                    "negative_process_counter_deltas": resets,
                    "comparable_processes": len(deltas),
                    "ollama_cpu_seconds_delta": sum(
                        r["cpu_seconds_delta"] for r in deltas if "ollama" in r["name"].lower()
                    ),
                    "other_cpu_seconds_delta": sum(
                        r["cpu_seconds_delta"] for r in deltas if "ollama" not in r["name"].lower()
                    ),
                    "top_observed_cpu_deltas": sorted(
                        deltas, key=lambda r: r["cpu_seconds_delta"], reverse=True
                    )[:8],
                    "limitation": "Endpoint snapshots omit exited/new processes. "
                    "PIDs can be reused. Non-Ollama includes OS, harness and telemetry. "
                    "No per-call energy attribution or CPU-time-based energy subtraction.",
                }
            )
        unique = {}
        for call in read_jsonl(stage_path(stage) / "calls.jsonl"):
            settings_row = {
                "model": call["model"],
                "model_digest": call["model_digest"],
                "options": call["request"]["options"],
                "config_hash": call["config_hash"],
            }
            text = json.dumps(settings_row, sort_keys=True)
            unique.setdefault(text, {"stage": stage.name, **settings_row, "calls": 0})["calls"] += 1
        settings.extend(unique.values())
    save_json(destination / "environment-block-audit.json", rows)
    save_json(destination / "observed-model-settings.json", settings)
    print(
        json.dumps(
            {
                "recorded_blocks": len(rows),
                "host_check_unconfirmed": sum(not r["ac_best_performance_observed"] for r in rows),
                "negative_counter_blocks": sum(
                    bool(r["negative_process_counter_deltas"]) for r in rows
                ),
            }
        )
    )


if __name__ == "__main__":
    environment_audit()
