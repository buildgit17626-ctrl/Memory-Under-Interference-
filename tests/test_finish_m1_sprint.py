"""Unattended continuation requires complete generation and successful phases."""

from experiments.finish_m1_sprint import phase_order


def test_complete_generation_continues_without_another_gate():
    events = []
    result = phase_order(lambda p: events.append(p) or 0, lambda _: 1040)
    assert events == ["generation", "evaluation"]
    assert result["reason"] == "verification_ready"


def test_partial_or_failed_generation_never_scores():
    events = []
    result = phase_order(lambda p: events.append(p) or 0, lambda _: 1000)
    assert events == ["generation"] and result["reason"] == "generation_incomplete"
    result = phase_order(lambda _: 2, lambda _: 1040)
    assert result["reason"] == "phase_stopped" and result["exit_code"] == 2


def test_deadline_in_evaluation_is_not_success():
    result = phase_order(lambda p: 0 if p == "generation" else 124, lambda _: 1040)
    assert result["reason"] == "phase_stopped" and result["phase"] == "evaluation"
