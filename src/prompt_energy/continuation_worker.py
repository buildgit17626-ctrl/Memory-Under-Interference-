"""Scoped continuation fork: legacy generation semantics, owner-extended execution window.

The original frozen supervisor remains byte-for-byte unchanged. This worker
removes only its expired calendar freeze; the caller verifies new authority
and supplies the user-pause check before every new logical request/retry.
"""

import ctypes
import json
import shutil
import sys
import time
import uuid
from collections.abc import Callable
from pathlib import Path

from prompt_energy.utilisation_journal import append_json, read_jsonl
from prompt_energy.utilisation_run import by_key, outcome
from prompt_energy.utilisation_supervisor import (
    Halt,
    hard_stop,
    response_index,
    terminal_repeat_abort,
)


def continue_batch(
    root: Path,
    jobs: list,
    client,
    sensor,
    gap: float,
    limit: int = 100,
    *,
    sleep=time.sleep,
    disk=shutil.disk_usage,
    may_launch: Callable[[], bool] | None = None,
) -> int:
    """Caller owns study lock; return after at most limit logical completions."""
    complete = by_key(root / "calls.jsonl")
    done = 0
    reason = hard_stop(list(complete.values()), disk(root).free)
    if reason:
        raise Halt(reason)
    pending = [j for j in jobs if j["key"] not in complete]
    if not pending:
        return 0
    power = ctypes.windll.kernel32.SetThreadExecutionState
    if not power(0x80000001):
        raise Halt("Could not inhibit idle sleep")
    opened = False
    try:
        sensor.start()
        opened = True
        for job in pending[:limit]:
            reason = hard_stop(list(complete.values()), disk(root).free)
            if reason:
                raise Halt(reason)
            if may_launch is not None and not may_launch():
                break
            starts = [r for r in read_jsonl(root / "starts.jsonl") if r["key"] == job["key"]]
            saved = response_index(root / "responses.jsonl")
            successful = None
            terminal_abort = False
            # Recover saved API output without sending it a second time.
            for previous in starts:
                record = saved.get((job["key"], previous["attempt"]))
                if record:
                    parsed, response = outcome(job, record["raw"])
                    if response is not None:
                        successful = (record, parsed, response)
                        break
                    if terminal_repeat_abort(record["raw"]):
                        terminal_abort = True
                        break
            while successful is None and not terminal_abort and len(starts) < 6:
                if may_launch is not None and not may_launch():
                    # Retain retry journals; resume this logical call later.
                    append_json(
                        root / "supervisor.jsonl",
                        {
                            "event": "launch_budget_exhausted",
                            "key": job["key"],
                            "saved_attempts": len(starts),
                            "time": time.time(),
                        },
                    )
                    return done
                attempt = uuid.uuid4().hex
                start = {"key": job["key"], "attempt": attempt, "block": sensor.block}
                append_json(root / "starts.jsonl", start)
                starts.append(start)
                try:
                    sensor.before_request()
                    raw = client.exchange("/api/generate", job["request"], timeout=job["timeout"])
                    record = {**start, "raw": raw}
                    append_json(root / "responses.jsonl", record)
                    parsed, response = outcome(job, raw)
                    if response is not None:
                        successful = (record, parsed, response)
                        break
                    if terminal_repeat_abort(raw):
                        terminal_abort = True
                        break
                    append_json(
                        root / "supervisor.jsonl",
                        {
                            "event": "api_retry",
                            "key": job["key"],
                            "attempt": attempt,
                            "flags": parsed["flags"],
                        },
                    )
                except (OSError, ValueError, RuntimeError) as exc:
                    append_json(
                        root / "supervisor.jsonl",
                        {
                            "event": "retry",
                            "key": job["key"],
                            "attempt": attempt,
                            "error": str(exc),
                        },
                    )
                sleep(min(60, 5 * len(starts)))
            if successful is None:
                row = {
                    **job,
                    "attempts": len(starts),
                    "input_valid": False,
                    "call_failed": True,
                    "flags": ["generation_repeat_abort" if terminal_abort else "retry_exhausted"],
                    "energy_valid": False,
                    "energy": {"windows": {}},
                    "raw_output": None,
                    "extracted": {},
                    "wall_seconds": 0,
                }
            else:
                record, parsed, response = successful
                try:
                    if record["block"] != sensor.block:
                        raise ValueError("Recovered response; sensor block changed")
                    energy = sensor.measure(record["raw"], response)
                except (ValueError, OSError) as exc:
                    energy = {"windows": {}, "flags": ["missing_energy"], "reason": str(exc)}
                post = energy["windows"].get("post_load", {})
                row = {
                    **job,
                    **parsed,
                    "attempt": record["attempt"],
                    "block": record["block"],
                    "call_failed": False,
                    "attempts": len(starts),
                    "energy": energy,
                    "energy_valid": post.get("raw_wh") is not None,
                    "wall_seconds": record["raw"]["wall_seconds"],
                }
            append_json(root / "calls.jsonl", row)
            complete[job["key"]] = row
            done += 1
            print(
                json.dumps(
                    {
                        "finished": len(complete),
                        "planned": len(jobs),
                        "key": job["key"],
                        "attempts": row["attempts"],
                    }
                ),
                flush=True,
            )
            reason = hard_stop(list(complete.values()), disk(root).free)
            if reason:
                raise Halt(reason)
            sleep(gap)
    finally:
        primary_error = sys.exc_info()[1]
        try:
            if opened:
                sensor.close()
                endings = [b for b in read_jsonl(root / "blocks.jsonl") if b["event"] == "end"]
                if endings and "baseline_drift" in endings[-1].get("flags", []):
                    ending = endings[-1]
                    events = read_jsonl(root / "blocks.jsonl")
                    opening = next(
                        e for e in events if e["event"] == "start" and e["block"] == ending["block"]
                    )
                    from experiments.config import P4

                    start_w = opening["baseline"]["watts"]
                    threshold = max(P4["drift_absolute_w"], P4["drift_fraction"] * start_w)
                    details = {
                        "block": ending["block"],
                        "start_baseline": opening["baseline"],
                        "end_baseline": ending["baseline"],
                        "signed_drift_w": ending["drift_w"],
                        "threshold_w": threshold,
                        "affected_keys": [
                            r["key"]
                            for r in by_key(root / "calls.jsonl").values()
                            if r.get("block") == ending["block"]
                        ],
                    }
                    # Drift is a quality flag under the owner's dated amendment;
                    # retain the original estimates and never hide another stop.
                    append_json(
                        root / "quality-events.jsonl",
                        {"event": "baseline_drift", "action": "flag_and_continue", **details},
                    )
                    print(
                        json.dumps({"quality_flag": "baseline_drift", **details}),
                        flush=True,
                    )
                    if primary_error:
                        details["primary_error"] = str(primary_error)
                        raise Halt(
                            str(primary_error) + "; baseline drift also exceeded threshold", details
                        ) from primary_error
        finally:
            power(0x80000000)
    return done
