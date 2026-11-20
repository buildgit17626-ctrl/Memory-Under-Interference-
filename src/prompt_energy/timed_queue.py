"""Run an already registered schedule for an explicit availability window."""

import json
import time
from dataclasses import dataclass
from pathlib import Path

from prompt_energy.hwinfo import LogFormat
from prompt_energy.records import write_once
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import digest
from prompt_energy.utilisation_reliability import SettledSensor, generate_short_block
from prompt_energy.utilisation_run import by_key
from prompt_energy.utilisation_supervisor import Halt


@dataclass(frozen=True)
class TimeBudget:
    wall_end: float
    monotonic_end: float
    max_request_seconds: float
    close_reserve_seconds: float = 600

    def may_launch(self, now=time.time, monotonic=time.monotonic) -> bool:
        remaining = min(self.wall_end - now(), self.monotonic_end - monotonic())
        return remaining > self.max_request_seconds + self.close_reserve_seconds


def timed_queue(
    root: Path,
    jobs: list[dict],
    client,
    log: Path,
    *,
    hours: float = 7.5,
    now=time.time,
    monotonic=time.monotonic,
    generator=generate_short_block,
    sensor=SettledSensor,
) -> dict:
    """Caller verifies registration/approval and owns the global study lock."""
    if not 0 < hours <= 8 or not jobs or len({j["key"] for j in jobs}) != len(jobs):
        raise ValueError("Require a unique registered schedule and window up to eight hours")
    root.mkdir(parents=True, exist_ok=True)
    identity = {"schedule_hash": digest(jobs)}
    path = root / "queue-schedule.json"
    if path.exists():
        if json.loads(path.read_text()) != identity:
            raise ValueError("Timed queue schedule changed")
    else:
        write_once(path, identity)
    budget = TimeBudget(
        now() + hours * 3600, monotonic() + hours * 3600, max(j["timeout"] for j in jobs)
    )

    def allowed():
        return budget.may_launch(now, monotonic)

    keys = {j["key"] for j in jobs}
    saved = by_key(root / "calls.jsonl")
    if not set(saved) <= keys:
        raise Halt("Foreign calls in timed queue")
    append_json(
        root / "queue-events.jsonl",
        {
            "event": "start",
            **identity,
            "wall_end": budget.wall_end,
            "max_request_seconds": budget.max_request_seconds,
            "close_reserve_seconds": budget.close_reserve_seconds,
        },
    )
    while len(saved) < len(jobs) and allowed():
        generator(
            root,
            jobs,
            client,
            sensor(log, root, LogFormat(encoding="cp1252")),
            5,
            limit=min(25, len(jobs) - len(saved)),
            may_launch=allowed,
        )
        updated = by_key(root / "calls.jsonl")
        if not set(updated) <= keys:
            raise Halt("Foreign calls in timed queue")
        if len(updated) <= len(saved) and allowed():
            raise Halt("No progress in timed queue")
        saved = updated
    result = {
        **identity,
        "planned": len(jobs),
        "completed": len(saved),
        "remaining": len(jobs) - len(saved),
        "reason": "schedule_complete" if len(saved) == len(jobs) else "time_budget",
        "evaluation": "deferred",
        "later_unregistered_stages_started": False,
    }
    (root / "QUEUE_STATUS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    append_json(root / "queue-events.jsonl", {"event": "stop", **result})
    return result
