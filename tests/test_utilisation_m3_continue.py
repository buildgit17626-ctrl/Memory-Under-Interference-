"""Mock-only tests of scope-bound M3 continuation and resume."""

import hashlib
import json

import pytest

from prompt_energy.utilisation_journal import append_json, read_jsonl
from prompt_energy.utilisation_m3_continue import continue_m3, validate_review
from prompt_energy.utilisation_plan import digest
from prompt_energy.utilisation_supervisor import Halt


def setup(root):
    jobs = [{"key": str(i)} for i in range(240)]
    for phase, count in [("E0", 1968), ("M3-isolated", 40), ("M3", 100)]:
        folder = root / phase
        folder.mkdir(parents=True)
        text = "".join(json.dumps({"key": str(i)}) + "\n" for i in range(count))
        (folder / "calls.jsonl").write_text(text)
        if phase == "E0":
            (folder / "scores.jsonl").write_text(text)
    (root / "CHECKPOINT.md").write_text("first 100 checkpoint")
    review = {
        "owner_approved": True,
        "schedule_hash": digest(jobs),
        "checkpoint_sha256": hashlib.sha256((root / "CHECKPOINT.md").read_bytes()).hexdigest(),
    }
    return jobs, review


def test_continue_only_missing_140_and_completed_resume_makes_no_calls(tmp_path):
    jobs, review = setup(tmp_path)
    old = (tmp_path / "M3/calls.jsonl").read_bytes()
    checkpoint = (tmp_path / "CHECKPOINT.md").read_bytes()
    block_sizes = []
    sensors = []

    def sensor(*args):
        marker = object()
        sensors.append(marker)
        return marker

    def generate(folder, jobs, client, sensor, gap, limit):
        existing = {r["key"] for r in read_jsonl(folder / "calls.jsonl")}
        missing = [j for j in jobs if j["key"] not in existing][:limit]
        block_sizes.append(len(missing))
        for job in missing:
            append_json(folder / "calls.jsonl", job)

    for _ in range(2):
        result = continue_m3(
            tmp_path,
            jobs,
            review,
            None,
            tmp_path / "log.csv",
            generator=generate,
            sensor_factory=sensor,
        )
        assert result["M3_finished"] == 240 and result["next_stage_started"] is False
    assert block_sizes == [25, 25, 25, 25, 25, 15]
    assert len(sensors) == 6 and len({id(s) for s in sensors}) == 6
    assert (tmp_path / "M3/calls.jsonl").read_bytes().startswith(old)
    assert (tmp_path / "CHECKPOINT.md").read_bytes() == checkpoint
    assert not (tmp_path / "M3/scores.jsonl").exists()
    assert not (tmp_path / "R1").exists()


def test_wrong_review_and_foreign_call_block_continuation(tmp_path):
    jobs, review = setup(tmp_path)
    with pytest.raises(Halt, match="owner review"):
        validate_review(tmp_path, jobs, review | {"owner_approved": False})
    with pytest.raises(Halt, match="owner review"):
        validate_review(tmp_path, list(reversed(jobs)), review)
    append_json(tmp_path / "M3/calls.jsonl", {"key": "foreign"})
    with pytest.raises(Halt, match="schedule prefix"):
        validate_review(tmp_path, jobs, review)


def test_no_progress_halts_without_following_stages(tmp_path):
    jobs, review = setup(tmp_path)
    with pytest.raises(Halt, match="No progress"):
        continue_m3(
            tmp_path,
            jobs,
            review,
            None,
            tmp_path / "log.csv",
            generator=lambda *a, **k: None,
            sensor_factory=lambda *a: None,
        )
    assert len(read_jsonl(tmp_path / "M3/calls.jsonl")) == 100
