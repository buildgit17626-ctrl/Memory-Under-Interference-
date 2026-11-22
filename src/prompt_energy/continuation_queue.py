"""Finite registered work until completion, explicit pause or unchanged hard stop."""

import json
import time
from pathlib import Path

from prompt_energy.continuation_worker import continue_batch
from prompt_energy.hwinfo import LogFormat
from prompt_energy.records import write_once
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import digest
from prompt_energy.utilisation_reliability import SettledSensor
from prompt_energy.utilisation_run import by_key
from prompt_energy.utilisation_supervisor import Halt


def continuation_queue(
    root: Path,
    jobs: list[dict],
    client,
    log: Path,
    pause: Path,
    *,
    generator=continue_batch,
    sensor=SettledSensor,
) -> dict:
    """Caller verifies committed authority/registration and owns the study lock."""
    keys = {j["key"] for j in jobs}
    if not jobs or len(keys) != len(jobs):
        raise ValueError("Require a unique frozen nonempty schedule")
    root.mkdir(parents=True, exist_ok=True)
    identity = {"schedule_hash": digest(jobs)}
    path = root / "continuation-schedule.json"
    if path.exists():
        if json.loads(path.read_text()) != identity:
            raise Halt("Continuation schedule changed")
    else:
        write_once(path, identity)
    append_json(root / "queue-events.jsonl", {"event": "start", **identity, "time": time.time()})
    saved = by_key(root / "calls.jsonl")
    if not set(saved) <= keys:
        raise Halt("Foreign calls in continuation queue")
    while len(saved) < len(jobs) and not pause.exists():
        generator(
            root,
            jobs,
            client,
            sensor(log, root, LogFormat(encoding="cp1252")),
            5,
            limit=min(25, len(jobs) - len(saved)),
            may_launch=lambda: not pause.exists(),
        )
        updated = by_key(root / "calls.jsonl")
        if not set(updated) <= keys:
            raise Halt("Foreign calls in continuation queue")
        if len(updated) <= len(saved) and not pause.exists():
            raise Halt("No progress in continuation queue")
        saved = updated
    result = {
        **identity,
        "planned": len(jobs),
        "completed": len(saved),
        "remaining": len(jobs) - len(saved),
        "reason": "schedule_complete" if len(saved) == len(jobs) else "user_pause",
        "elapsed_time_cutoff": None,
    }
    (root / "QUEUE_STATUS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    append_json(root / "queue-events.jsonl", {"event": "stop", **result, "time": time.time()})
    return result
