"""Draft builders cannot silently choose materials or invoke a model."""

import pytest

from prompt_energy.memory_revision import (
    condition_matrix,
    interference_prompt,
    m1_prompt,
    r1_prompt,
)

TASK = {
    "task_id": "A",
    "entry_point": "a",
    "prompt": 'def a(x):\n    """Return x."""',
    "canonical_solution": "SECRET_REFERENCE",
    "test": "SECRET_TEST",
}
OTHER = {"task_id": "B", "entry_point": "b", "prompt": 'def b(x):\n    """Return twice x."""'}


def test_exact_revised_matrices_and_no_repeated_baseline():
    ids = [str(i) for i in range(40)]
    models = ["m0", "m1"]
    assert len(condition_matrix("M1", ids, models)) == 960
    assert len(condition_matrix("R1", ids, models)) == 400
    assert len(condition_matrix("M3R2_v2", ids, models)) == 960
    assert len(condition_matrix("M1", ids[:5], models, ks=(2, 4))) == 60
    with pytest.raises(ValueError, match="unique"):
        condition_matrix("R1", ["A", "A"], models)


def test_multitask_output_budgets_and_target_score_identity():
    for mode in ["active", "passive"]:
        result = m1_prompt(TASK, [OTHER], mode, 1)
        assert "SECRET" not in result["prompt"]
        assert result["target_task_id"] == "A"
        assert result["bundle_task_ids"] == ["B", "A"]
        assert result["entries"] == (["b", "a"] if mode == "active" else ["a"])
        assert result["num_predict"] == (4096 if mode == "active" else 2048)
    with pytest.raises(ValueError, match="distinct"):
        m1_prompt(TASK, [TASK], "active", 0)
    with pytest.raises(ValueError, match="token-matched"):
        m1_prompt(TASK, [OTHER], "filler", 0, filler="short", count=len)


def test_r1_requires_reviewed_summary_and_preserves_task():
    material = {
        "target": "TARGET",
        "query": "QUERY",
        "before": "D1",
        "preference": "PREF",
        "after": "D2",
    }
    for policy in ["full_history", "no_history", "verbatim_replay", "oracle_selective"]:
        prompt = r1_prompt(material, policy)
        assert "TARGET" in prompt and prompt.endswith("QUERY")
    assert r1_prompt(material, "no_history") == "TARGET\nQUERY"
    assert r1_prompt(material, "verbatim_replay").count("TARGET") == 2
    with pytest.raises(ValueError, match="reviewed"):
        r1_prompt(material, "compact_summary")
    assert (
        r1_prompt(
            material | {"summary": "TASK COMPLETE SUMMARY", "summary_reviewed": True},
            "compact_summary",
        )
        == "TASK COMPLETE SUMMARY\nQUERY"
    )


def test_new_interference_needs_validated_distinguishing_materials():
    kwargs = {"similarity": "near_duplicate", "expected_filler_tokens": 4, "count": len}
    with pytest.raises(ValueError, match="distinguishing"):
        interference_prompt("TARGET", "FILL", "end", **kwargs)
    review = {
        "compatible_signature": True,
        "distinguishing_case_ids": ["case1"],
        "audit_path": "validated.json",
    }
    assert (
        interference_prompt("TARGET", "FILL", "end", distractor_review=review, **kwargs)
        == "FILL\nTARGET"
    )
