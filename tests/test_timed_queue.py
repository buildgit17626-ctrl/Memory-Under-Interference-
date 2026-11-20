"""Availability cutoffs preserve pending records and complete more than one block."""

import pytest

from prompt_energy.timed_queue import TimeBudget, timed_queue
from prompt_energy.utilisation_journal import append_json, read_jsonl


def test_budget_reserves_request_and_closing_time_and_observes_wall_resume():
    budget = TimeBudget(30000, 30000, 3600)
    assert budget.may_launch(lambda: 0, lambda: 0)
    assert not budget.may_launch(lambda: 26000, lambda: 0)
    assert not budget.may_launch(lambda: 0, lambda: 26000)


def test_queue_uses_window_across_many_blocks_and_resumes(tmp_path):
    jobs = [{"key": str(i), "timeout": 3600} for i in range(100)]
    clock = [0]
    sizes = []

    def generator(root, jobs, client, sensor, gap, limit, may_launch):
        have = {r["key"] for r in read_jsonl(root / "calls.jsonl")}
        todo = [j for j in jobs if j["key"] not in have][:limit]
        sizes.append(len(todo))
        for row in todo:
            append_json(root / "calls.jsonl", row)
        clock[0] += 1000

    result = timed_queue(
        tmp_path,
        jobs,
        None,
        tmp_path / "log",
        hours=7.5,
        now=lambda: clock[0],
        monotonic=lambda: clock[0],
        generator=generator,
        sensor=lambda *a: None,
    )
    assert result["completed"] == 100 and sizes == [25] * 4
    timed_queue(tmp_path, jobs, None, tmp_path / "log", generator=generator, sensor=lambda *a: None)
    assert sizes == [25] * 4


def test_time_cutoff_keeps_stage_incomplete(tmp_path):
    jobs = [{"key": "x", "timeout": 3600}]
    result = timed_queue(tmp_path, jobs, None, tmp_path / "log", hours=1)
    assert result["reason"] == "time_budget" and result["remaining"] == 1
    with pytest.raises(ValueError):
        timed_queue(tmp_path, jobs, None, tmp_path / "log", hours=9)
