"""Audit computations must preserve paired populations and immutable primary outcomes."""

import numpy as np
import pandas as pd
import pytest

from analysis.memory_audit.effects import complete_units
from analysis.memory_audit.environment import process_deltas
from analysis.memory_audit.mechanisms import format_features
from analysis.memory_audit.records import scored_value
from analysis.memory_audit.sensors import integrate_many, prefix_hashes
from analysis.memory_audit.statistics import components, holm, interval, paired, paired_ratio, ratio
from prompt_energy.energy import integrate
from prompt_energy.hwinfo import Sample


def test_paired_missingness_and_transition_direction():
    result = paired(np.array([1, 0, 1, np.nan]), np.array([0, 1, 1, 0]), binary_test=True)
    assert result["n_units"] == 3
    assert result["estimate"] == 0
    assert result["pass_to_fail"] == result["fail_to_pass"] == 1
    assert result["p_value"] == 1
    assert result["n_missing_pairs"] == 1


def test_triplet_task_swaps_do_not_treat_samples_as_independent():
    result = paired(np.ones(5), np.zeros(5))
    assert result["n_units"] == 5 and result["p_value"] == 2 / 2**5


def test_holm_is_monotone_and_keeps_unavailable_family_member():
    assert holm([0.01, 0.03, 0.04]) == [0.03, 0.06, 0.06]
    assert holm([0.01, None]) == [0.02, None]


def test_ratio_includes_failed_attempt_energy_and_zero_correct_draws():
    result = ratio(np.array([2, 9]), np.array([1, 0]))
    assert result["estimate"] == 11
    assert result["upper_unbounded"]
    assert result["zero_correct_bootstrap_draws"] > 0
    assert ratio(np.array([2]), np.array([0]))["estimate"] is None


def test_negative_energy_is_not_clipped():
    assert ratio(np.array([-2, -1]), np.array([1, 1]))["estimate"] == -1.5


def test_single_unit_interval_is_not_fake_zero_width_ci():
    assert interval(np.array([1.0]))["ci95"] is None


def test_bundle_components_preserve_shared_tasks():
    assert components([["a", "b"], ["b", "c"], ["d"]]) == [["a", "b", "c"], ["d"]]


def test_complete_units_requires_all_seeds_and_both_cells():
    rows = pd.DataFrame(
        {"task": ["a", "a", "b"], "condition": ["x", "y", "x"], "passed": [1.0, 0.0, 1.0]}
    )
    assert complete_units(rows, ["x", "y"], "passed", 1) == {"a": 0.5}
    rows.loc[0, "passed"] = np.nan
    assert complete_units(rows, ["x", "y"], "passed", 1) == {}


def test_caps_nonpass_but_api_and_infrastructure_are_missing():
    call = {"input_valid": True, "flags": ["output_cap"]}
    assert scored_value({"status": "truncated"}, call) == 0
    call["input_valid"] = False
    assert np.isnan(scored_value({"status": "truncated"}, call))
    call = {"input_valid": True, "flags": []}
    score = {"status": "failed", "functions": {"t": {"base": {"status": "infrastructure_error"}}}}
    assert np.isnan(scored_value(score, call))


def test_code_comments_are_features_not_automatic_primary_violations():
    raw = 'def f():\n    """Explanation in valid code."""\n    # comment\n    return 1'
    result = format_features(raw, raw, "f")
    assert result["plain_code"] and result["fence_tolerant_syntax_adherence"]
    assert result["comment_tokens"] == result["docstrings"] == 1
    assert not result["comment_docstring_free_proxy"]


def test_fenced_code_remains_original_nonadherent_secondary_audited():
    code = "def f():\n    return 1"
    result = format_features("```python\n" + code + "\n```", code, "f")
    assert not result["plain_code"] and result["fence_tolerant_syntax_adherence"]
    result = format_features("Here is an explanation.\n```python\n" + code + "\n```", code, "f")
    assert result["outside_fence_text"] and not result["fence_tolerant_syntax_adherence"]


def test_independent_vector_integration_matches_registered_trapezoids():
    times = np.arange(0, 10, 0.5)
    power = 4 + times**2
    windows = [{"start": 0.25, "end": 6.2, "raw_wh": None}]
    reference = integrate([Sample(t, p) for t, p in zip(times, power, strict=True)], 0.25, 6.2)
    windows[0]["raw_wh"] = reference["raw_wh"]
    result = integrate_many(times, power, windows)[0]
    assert result["agrees_within_1e_8_wh"]
    assert result["recomputed_wh"] == pytest.approx(reference["raw_wh"], abs=1e-12)


def test_prefix_hashes_check_used_bytes_not_unrelated_later_tail(tmp_path):
    import hashlib

    path = tmp_path / "sensor.csv"
    path.write_bytes(b"valid-prefix\nlater-data")
    requested = [{"prefix_bytes": 13, "sha256": hashlib.sha256(b"valid-prefix\n").hexdigest()}]
    assert prefix_hashes(path, requested)[0]["match"]


def test_paired_ratio_preserves_shared_task_resampling_and_missingness():
    result = paired_ratio(
        np.array([2, 4, np.nan]),
        np.array([1, 1, 1]),
        np.array([1, 3, 100]),
        np.array([1, 1, 1]),
    )
    assert result["n_units"] == 2
    assert result["difference"] == 1
    assert result["ci95"] == [1, 1]
    result = paired_ratio(np.array([2, 9]), np.array([1, 0]), np.array([1, 3]), np.array([1, 1]))
    assert result["undefined_bootstrap_draws"] > 0
    assert result["ci95"] is None


def test_process_snapshots_do_not_subtract_idle_or_negative_reused_counters():
    before = [
        {"pid": 0, "name": "idle", "cpu_times": [0, 100]},
        {"pid": 1, "name": "ollama", "cpu_times": [10, 2]},
        {"pid": 2, "name": "other", "cpu_times": [20, 3]},
    ]
    after = [
        {"pid": 0, "name": "idle", "cpu_times": [0, 200]},
        {"pid": 1, "name": "ollama", "cpu_times": [15, 3]},
        {"pid": 2, "name": "other", "cpu_times": [1, 0]},
    ]
    rows, resets = process_deltas(before, after)
    assert rows == [{"pid": 1, "name": "ollama", "cpu_seconds_delta": 6}]
    assert resets == [(2, "other")]
