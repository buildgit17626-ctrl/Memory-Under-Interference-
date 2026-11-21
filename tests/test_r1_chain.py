"""Lossless materials and outcome-independent automated pilot gate."""

from experiments.run_m1_r1_chain import pilot_gate
from prompt_energy.r1_materials import compact_specification


def test_compaction_keeps_quoted_spaces_and_examples():
    source = (
        'def f(x):\n    """Return the input.\n    Keep all spaces.\n\n'
        '    >>> f(" a   b ")\n    " a   b "\n    """\n'
    )
    result = compact_specification(source, "f")
    assert '" a   b "' in result
    assert "Return the input. Keep all spaces." in result
    import ast

    ast.parse(result)


def test_gate_never_uses_correctness_and_requires_complete_energy():
    calls = [
        {"input_valid": True, "energy_valid": True, "flags": [], "passed": False} for _ in range(50)
    ]
    a = pilot_gate(calls, 50, 300, 10000)
    for row in calls:
        row["passed"] = True
    assert pilot_gate(calls, 50, 300, 10000) == a
    assert a["pass"]
    calls[0]["energy_valid"] = False
    assert not pilot_gate(calls, 50, 300, 10000)["pass"]


def test_gate_caps_and_insufficient_time_block_full_run():
    calls = [{"input_valid": True, "energy_valid": True, "flags": []} for _ in range(50)]
    assert not pilot_gate(calls, 50, 300, 100)["pass"]
    calls[0]["flags"] = ["output_cap"]
    assert not pilot_gate(calls, 50, 300, 10000)["pass"]
