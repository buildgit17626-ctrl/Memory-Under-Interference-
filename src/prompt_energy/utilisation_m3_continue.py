"""Finish the reviewed Focused M3 schedule, without scoring or later stages."""

import hashlib
from pathlib import Path

from prompt_energy.hwinfo import LogFormat
from prompt_energy.utilisation_plan import digest
from prompt_energy.utilisation_reliability import SettledSensor, generate_short_block
from prompt_energy.utilisation_run import by_key
from prompt_energy.utilisation_supervisor import Halt


def validate_review(root: Path, jobs: list[dict], review: dict) -> None:
    """Bind continuation to the published timing checkpoint and frozen schedule."""
    if len(jobs) != 240 or len({j["key"] for j in jobs}) != 240:
        raise Halt("Require the original 240 unique M3 jobs")
    if review.get("owner_approved") is not True or review.get("schedule_hash") != digest(jobs):
        raise Halt("Missing or mismatched schedule-bound owner review")
    checkpoint = root / "CHECKPOINT.md"
    if hashlib.sha256(checkpoint.read_bytes()).hexdigest() != review.get("checkpoint_sha256"):
        raise Halt("First-100 checkpoint changed")
    if (
        len(by_key(root / "E0/calls.jsonl")) != 1968
        or len(by_key(root / "E0/scores.jsonl")) != 1968
    ):
        raise Halt("Require completed E0 generation and evaluation")
    if len(by_key(root / "M3-isolated/calls.jsonl")) != 40:
        raise Halt("Require 40 completed isolated baselines")
    saved = by_key(root / "M3/calls.jsonl")
    if not 100 <= len(saved) <= 240 or set(saved) != {j["key"] for j in jobs[: len(saved)]}:
        raise Halt("Saved M3 calls do not match the frozen schedule prefix")
    if by_key(root / "M3/scores.jsonl") or by_key(root / "M3-isolated/scores.jsonl"):
        raise Halt("This generation-only continuation requires unscored M3 journals")


def continue_m3(
    root: Path,
    jobs: list[dict],
    review: dict,
    client,
    log: Path,
    *,
    generator=generate_short_block,
    sensor_factory=SettledSensor,
) -> dict:
    """Retain per-call retry budgets and stop at the original 240-call boundary."""
    validate_review(root, jobs, review)
    folder = root / "M3"
    done = len(by_key(folder / "calls.jsonl"))
    while done < len(jobs):
        generator(
            folder,
            jobs,
            client,
            sensor_factory(log, folder, LogFormat(encoding="cp1252")),
            5,
            limit=min(25, len(jobs) - done),
        )
        updated = len(by_key(folder / "calls.jsonl"))
        if updated <= done or updated > len(jobs):
            raise Halt("No progress or excess calls in M3 continuation")
        validate_review(root, jobs, review)
        done = updated
    return {
        "M3_finished": done,
        "M3_planned": 240,
        "scoring": "deferred",
        "next_stage_started": False,
        "schedule_hash": digest(jobs),
    }
