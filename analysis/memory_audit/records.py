"""Read-only normalized evidence; preserve raw failures and registered score definitions."""

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.memory_audit.design import STAGES, stage_path
from prompt_energy.extraction import extract_code
from prompt_energy.ollama import decode_response
from prompt_energy.utilisation_journal import read_jsonl


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def indexed(path: Path) -> dict:
    rows = read_jsonl(path)
    result = {r["key"]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError("Duplicate key: " + str(path))
    return result


def scored_value(score: dict | None, call: dict, tid: str | None = None) -> float:
    if not call["input_valid"] or call.get("call_failed") or score is None:
        return np.nan
    if "output_cap" in call["flags"]:
        return 0.0
    functions = score.get("functions", {})
    selected = [functions.get(tid, {})] if tid is not None else list(functions.values())
    partitions = [p for result in selected for p in result.values()]
    if any(p["status"] == "infrastructure_error" for p in partitions):
        return np.nan
    if tid is not None:
        return float(all(p["status"] == "passed" for p in partitions)) if partitions else np.nan
    if score["status"] in {"invalid_input", "infrastructure_error"}:
        return np.nan
    return float(score["status"] == "passed")


def json_value(value):
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [json_value(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(json_value(value), indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def load_evidence(destination: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict, list[dict]]:
    rows, functions, inventory, issues = [], [], {}, []
    for stage in STAGES:
        folder = stage_path(stage)
        calls, scores = indexed(folder / "calls.jsonl"), indexed(folder / "scores.jsonl")
        if not set(scores) <= set(calls):
            raise ValueError("Foreign score keys: " + stage.name)
        blocks = {}
        for event in read_jsonl(folder / "blocks.jsonl"):
            block = blocks.setdefault(event["block"], {})
            if event["event"] in block:
                raise ValueError("Duplicate block event: " + stage.name)
            block[event["event"]] = event
        response_rows = read_jsonl(folder / "responses.jsonl")
        responses = {(r["key"], r["attempt"]): r for r in response_rows}
        if len(response_rows) != len(responses):
            raise ValueError("Duplicate response-attempt: " + stage.name)
        starts = read_jsonl(folder / "starts.jsonl")
        for key, call in calls.items():
            score = scores.get(key)
            raw = responses.get((key, call.get("attempt")), {}).get("raw")
            native = None
            if raw is not None:
                try:
                    native = decode_response(raw, generation=True)
                    for stored, field in (
                        ("prompt_tokens", "prompt_eval_count"),
                        ("output_tokens", "eval_count"),
                        ("prefill_ns", "prompt_eval_duration"),
                        ("decode_ns", "eval_duration"),
                        ("raw_output", "response"),
                    ):
                        if call.get(stored) != native[field]:
                            issues.append(
                                {
                                    "stage": stage.name,
                                    "key": key,
                                    "kind": "native_field_mismatch",
                                    "field": field,
                                }
                            )
                    if raw["request"] != call["request"]:
                        issues.append({"stage": stage.name, "key": key, "kind": "request_mismatch"})
                except (ValueError, KeyError, TypeError) as exc:
                    issues.append(
                        {
                            "stage": stage.name,
                            "key": key,
                            "kind": "native_decode_error",
                            "reason": str(exc),
                        }
                    )
            elif not call.get("call_failed"):
                issues.append({"stage": stage.name, "key": key, "kind": "missing_raw_response"})
            block = blocks.get(call.get("block"), {})
            opening, ending = block.get("start", {}), block.get("end", {})
            start_w = (opening.get("baseline") or {}).get("watts")
            end_w = (ending.get("baseline") or {}).get("watts")
            energy = call.get("energy", {})
            post = energy.get("windows", {}).get("post_load", {})
            total = energy.get("windows", {}).get("total", {})
            gross, duration = post.get("raw_wh"), post.get("seconds")
            body = call.get("raw_output") or ""
            for entry, extracted in call.get("extracted", {}).items():
                if extract_code(body, entry) != extracted:
                    issues.append(
                        {
                            "stage": stage.name,
                            "key": key,
                            "kind": "extraction_mismatch",
                            "entry": entry,
                        }
                    )
            members = call.get("identity", {}).get("bundle_task_ids", [call["task_id"]])
            usable = scored_value(score, call)
            row = {
                "stage": stage.name,
                "phase": stage.phase,
                "key": key,
                "source_folder": str(folder),
                "model": call["model"],
                "condition": call["condition"],
                "task": call["task_id"],
                "sample": call["sample_idx"],
                "repeat": call["repeat"],
                "input_valid": bool(call["input_valid"]),
                "api_failed": bool(call.get("call_failed")),
                "capped": "output_cap" in call["flags"],
                "passed": scored_value(score, call, call["task_id"])
                if stage.name.startswith("M1")
                else usable,
                "whole_passed": usable,
                "operational_pass": float(
                    scored_value(score, call, call["task_id"]) == 1
                    if stage.name.startswith("M1")
                    else usable == 1
                ),
                "score_status": score.get("status") if score else "not_scored",
                "prompt_tokens": call.get("prompt_tokens"),
                "output_tokens": call.get("output_tokens"),
                "prefill_s": call.get("prefill_ns", 0) / 1e9
                if call.get("prefill_ns") is not None
                else None,
                "decode_s": call.get("decode_ns", 0) / 1e9
                if call.get("decode_ns") is not None
                else None,
                "wall_s": call.get("wall_seconds"),
                "gross_wh": gross,
                "net_wh": post.get("adjusted_wh"),
                "window_s": duration,
                "total_gross_wh": total.get("raw_wh"),
                "total_net_wh": total.get("adjusted_wh"),
                "start_w": start_w,
                "end_w": end_w,
                "end_net_wh": gross - end_w * duration / 3600
                if all(v is not None for v in (gross, end_w, duration))
                else None,
                "midpoint_net_wh": gross - (start_w + end_w) / 2 * duration / 3600
                if all(v is not None for v in (gross, start_w, end_w, duration))
                else None,
                "drifted": "baseline_drift" in ending.get("flags", []),
                "low_resolution": "low_resolution" in post.get("flags", []),
                "block": call.get("block"),
                "bundle_members": json.dumps(members),
                "entries": json.dumps(call["entries"]),
                "identity": json.dumps(call["identity"]),
                "cached_tokens": native.get("prompt_eval_cached_count") if native else None,
                "output_budget": call["request"]["options"]["num_predict"],
                "context": call["request"]["options"]["num_ctx"],
            }
            if gross is not None and duration is not None and start_w is not None:
                recomputed = gross - start_w * duration / 3600
                if (
                    post.get("adjusted_wh") is not None
                    and abs(recomputed - post["adjusted_wh"]) > 1e-10
                ):
                    issues.append(
                        {"stage": stage.name, "key": key, "kind": "idle_subtraction_mismatch"}
                    )
            rows.append(row)
            task_ids = call["identity"].get("task_ids", [call["task_id"]])
            for tid in task_ids:
                partitions = (score or {}).get("functions", {}).get(tid, {})
                functions.append(
                    {
                        "stage": stage.name,
                        "model": call["model"],
                        "key": key,
                        "anchor_task": call["task_id"],
                        "task": tid,
                        "condition": call["condition"],
                        "capped": row["capped"],
                        "passed": scored_value(score, call, tid),
                        "partition_status": json.dumps(
                            {k: v["status"] for k, v in partitions.items()}
                        ),
                    }
                )
        inventory[stage.name] = {
            "phase": stage.phase,
            "expected": stage.expected,
            "calls": len(calls),
            "scores": len(scores),
            "responses": len(responses),
            "started_attempts": len(starts),
            "failed_calls": sum(bool(c.get("call_failed")) for c in calls.values()),
            "caps": sum("output_cap" in c["flags"] for c in calls.values()),
            "score_status": dict(Counter(s.get("status") for s in scores.values())),
            "calls_without_scores": len(set(calls) - set(scores)),
            "blocks_without_end": [k for k, v in blocks.items() if "start" in v and "end" not in v],
            "orphan_start_attempts": [s for s in starts if s["key"] not in calls],
        }
    frame, function_frame = pd.DataFrame(rows), pd.DataFrame(functions)
    frame.to_csv(destination / "calls.csv", index=False)
    function_frame.to_csv(destination / "functions.csv", index=False)
    save_json(destination / "inventory.json", inventory)
    save_json(destination / "integrity-issues.json", issues)
    return frame, function_frame, inventory, issues
