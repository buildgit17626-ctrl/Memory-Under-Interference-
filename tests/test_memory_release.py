"""Release derivation must expose censoring, preserve text and retain ranking ties."""

import pandas as pd
import pytest

from analysis.memory_release.analytics import cross_bounds, energy_reduction_percent
from analysis.memory_release.common import MODELS
from analysis.memory_release.companion import retrieval
from analysis.memory_release.examples import omit_function_docstring
from analysis.memory_release.export import sanitize_json, sanitize_text


def test_cost_reduction_is_relative_to_full_history_and_requires_positive_baseline():
    assert energy_reduction_percent(100, 25) == 75
    assert energy_reduction_percent(25, 100) == -300
    with pytest.raises(ValueError):
        energy_reduction_percent(0, 25)


def test_example_excerpt_removes_only_docstring_without_changing_comparator():
    code = 'def f(a, b):\n    """strict intent"""\n    return a <= b\n'
    excerpt = omit_function_docstring(code)
    assert excerpt == "def f(a, b):\n    return a <= b\n"
    assert omit_function_docstring(excerpt) == excerpt


def test_public_redaction_preserves_generated_content_and_numbers():
    code = "def f(x):\n    return x + 1"
    original = {
        "host": {"username": "private", "cpu": "i5", "pid": 123},
        "raw_output": code,
        "extracted": {"f": code},
        "path": "C:\\Users\\Dhruv Brahmbhatt\\Downloads\\log.csv",
        "energy": 0.12345678901234567,
        "processes": [{"pid": 1}],
    }
    clean = sanitize_json(original)
    assert clean["raw_output"] == code and clean["extracted"] == original["extracted"]
    assert clean["energy"] == original["energy"]
    assert clean["host"] == {"cpu": "i5"} and "processes" not in clean
    assert "Dhruv" not in clean["path"]
    assert original["host"]["username"] == "private"
    assert sanitize_text(code) == (code, 0)
    # A short Windows account prefix can occur as escaped text in copied source.
    assert sanitize_text(r"C:\\Users\\DHRUVB~1\\Temp")[0].startswith("LOCAL_USER_ROOT")
    assert sanitize_text(r"C:\\\\Users\\\\DHRUVB~1\\\\Temp")[0].startswith("LOCAL_USER_ROOT")


def test_synthetic_rank_audit_preserves_stable_tie_order():
    frame = pd.DataFrame(
        {"query_id": ["a", "a", "b", "b"], "relevant": [0, 1, 1, 0], "score": [1.0, 1.0, 2.0, 1.0]}
    )
    result = retrieval(frame, "score")
    assert result["queries"] == 2 and result["mrr"] == 0.75
    assert result["per_query"][0]["rr"] == 0.5


def test_censored_cross_pass_bounds_retain_tasks_without_inventing_observed_success():
    rows = []
    for model in MODELS:
        for task in ("one", "two"):
            for i in range(4):
                missing = task == "one" and i == 0
                rows.append(
                    {
                        "model": model,
                        "task": task,
                        "condition": "near_duplicate_" + str(i),
                        "cell": "invalid_or_censored" if missing else "both_fail",
                        "distractor_only": float("nan") if missing else 0.0,
                    }
                )
                rows.append(
                    {
                        "model": model,
                        "task": task,
                        "condition": "irrelevant_" + str(i),
                        "cell": "both_fail",
                        "distractor_only": 0.0,
                    }
                )
            rows.append(
                {
                    "model": model,
                    "task": task,
                    "condition": "isolated",
                    "cell": "both_fail",
                    "distractor_only": 0.0,
                }
            )
    results = cross_bounds(pd.DataFrame(rows))
    selected = {
        r["variant"]: r
        for r in results
        if r["model"] == MODELS[0] and r["comparison"] == "near-minus-irrelevant"
    }
    assert selected["complete_case"]["n_units"] == 1
    assert selected["unknown_lower_bound"]["n_units"] == 2
    assert selected["unknown_upper_bound"]["estimate"] == 0.125
    assert selected["unknown_lower_bound"]["estimate"] == 0
