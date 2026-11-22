"""Keep archived mock behavioral tests independent of the live calendar date."""

import pytest

LEGACY_MOCK_TESTS = {
    "test_supervisor_retry_budget_and_raw_preservation",
    "test_explicit_repeat_abort_is_not_retried",
    "test_drift_does_not_hide_original_hard_stop",
    "test_drift_flags_and_continues_with_fresh_blocks_without_repeating",
    "test_launch_callback_stops_between_calls_preserving_resume",
    "test_budget_stops_retry_and_preserves_attempt_for_recovery",
}


@pytest.fixture(autouse=True)
def legacy_mock_execution_window(request, monkeypatch):
    # These frozen-source tests exercise retries/drift, not the calendar gate.
    # The separate continuation test explicitly verifies that the old freeze
    # still halts production generation. No production artifact is modified.
    if request.path.name == "test_utilisation.py" and request.node.name in LEGACY_MOCK_TESTS:
        monkeypatch.setattr(
            "prompt_energy.utilisation_supervisor.FREEZE", "2099-01-01T00:00:00+05:30"
        )
