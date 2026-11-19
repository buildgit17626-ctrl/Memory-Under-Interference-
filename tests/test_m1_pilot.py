"""Pilot budget, approval gate, resume and target/bundle separation."""

import pytest

from experiments.run_m1_pilot import pilot_generation, report, require_material_review
from prompt_energy.utilisation_journal import append_json, read_jsonl
from prompt_energy.utilisation_plan import digest


def test_pilot_review_requires_exact_schedule():
    jobs = [{"key": str(i), "identity": {"pilot": True}} for i in range(70)]
    with pytest.raises(ValueError, match="await"):
        require_material_review(jobs, {"owner_approved": False, "schedule_hash": digest(jobs)})
    require_material_review(jobs, {"owner_approved": True, "schedule_hash": digest(jobs)})
    with pytest.raises(ValueError, match="await"):
        require_material_review(jobs[::-1], {"owner_approved": True, "schedule_hash": digest(jobs)})


def test_pilot_finishes_only_missing_calls_and_does_not_score(tmp_path):
    jobs = [{"key": str(i)} for i in range(70)]
    for job in jobs[:10]:
        append_json(tmp_path / "calls.jsonl", job)
    blocks = []

    def generate(root, jobs, client, sensor, gap, limit):
        saved = {r["key"] for r in read_jsonl(root / "calls.jsonl")}
        missing = [j for j in jobs if j["key"] not in saved][:limit]
        blocks.append(len(missing))
        for job in missing:
            append_json(root / "calls.jsonl", job)

    for _ in range(2):
        pilot_generation(
            tmp_path, jobs, None, tmp_path / "log.csv", generator=generate, sensor=lambda *_: None
        )
    assert blocks == [25, 25, 10]
    assert len(read_jsonl(tmp_path / "calls.jsonl")) == 70
    assert not (tmp_path / "scores.jsonl").exists()


def test_report_keeps_target_success_separate_from_bundle(tmp_path):
    append_json(
        tmp_path / "calls.jsonl",
        {
            "key": "x",
            "model": "m",
            "condition": "active/K2",
            "task_id": "A",
            "wall_seconds": 2,
            "output_tokens": 20,
            "flags": [],
            "input_valid": True,
            "energy_valid": True,
        },
    )
    append_json(
        tmp_path / "scores.jsonl",
        {
            "key": "x",
            "status": "failed",
            "functions": {
                "A": {"base": {"status": "passed"}, "plus": {"status": "passed"}},
                "B": {"base": {"status": "failed"}, "plus": {"status": "failed"}},
            },
        },
    )
    result = report(tmp_path)
    assert result["include_in_hypothesis_tests"] is False
    row = result["by_model_condition"][0]
    assert row["calls"] == row["scored"] == row["target_passed"] == 1
    assert row["all_requested_functions_passed"] == 0
