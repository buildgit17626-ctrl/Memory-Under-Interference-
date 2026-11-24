"""Deterministically selected code/witness checks, executed only in the restricted worker."""

import ast
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from analysis.memory_audit.design import ROOT
from analysis.memory_audit.records import indexed, save_json
from experiments.prepare_continuation import source
from prompt_energy.extraction import prepare_source
from prompt_energy.sandbox import run_solution
from prompt_energy.tasks import Task
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import digest


def audit_examples(destination: Path) -> None:
    cfg, tasks, _ = source()
    cross = pd.read_csv(destination / "cross-pass-per-response.csv")
    cross = cross[cross.condition.str.startswith("near_duplicate_")]
    calls = indexed(ROOT / "results/utilisation/continuation-v3/R2/full/calls.jsonl")
    alternatives = json.loads(
        (ROOT / "studies/utilisation/continuation-v3/R2/alternatives.json").read_text()
    )
    path = destination / "representative-witness-scores.jsonl"
    done = indexed(path)
    examples = []
    for (model, cell), g in cross.groupby(["model", "cell"]):
        if cell == "invalid_or_censored":
            continue
        chosen = None
        for _, row in g.sort_values(["task", "condition"]).iterrows():
            call = calls[row["key"]]
            entry = tasks[row.task]["entry_point"]
            try:
                ast.parse(call["extracted"][entry])
            except (SyntaxError, ValueError, RecursionError):
                continue
            chosen = row
            break
        if chosen is None:
            continue
        call = calls[chosen["key"]]
        task = tasks[chosen.task]
        definition = alternatives[chosen.task]["definition"]
        code = call["extracted"][task["entry_point"]]
        outcomes = {}
        for expected in ("target_expected", "alternative_expected"):
            lines = ["def check(candidate):"]
            for w in definition["witnesses"]:
                lines.append(f"    assert candidate(*{w['args']!r}) == {w[expected]}")
            check = "\n".join(lines)
            key = digest([call["key"], expected, check, code, cfg["evaluation"]])
            if key not in done:
                sandbox_task = Task(
                    chosen.task,
                    task["prompt"],
                    task["canonical_solution"],
                    check,
                    task["entry_point"],
                )
                result = run_solution(
                    sandbox_task,
                    prepare_source(sandbox_task, code),
                    timeout_seconds=60,
                    memory_mb=256,
                    seed=call["seed"],
                    exact_types=True,
                )
                record = {
                    "key": key,
                    "call_key": call["key"],
                    "suite": expected,
                    "check_sha256": digest(check),
                    **asdict(result),
                }
                append_json(path, record)
                done[key] = record
            outcomes[expected] = done[key]["status"]
        examples.append(
            {
                "model": model,
                "cell": cell,
                "task": chosen.task,
                "condition": chosen.condition,
                "call_key": call["key"],
                "code": code,
                "alternative_description": definition["description"],
                "witnesses": definition["witnesses"],
                "witness_outcomes": outcomes,
            }
        )
    save_json(destination / "representative-code-audit.json", examples)
    lines = [
        "# Representative code and distinguishing-case audit",
        "",
        "Posthoc, AI-assisted review sample: first parseable output by task/condition "
        "within each model/cross-pass cell. No claim of representative prevalence. "
        "Every candidate executes only through the existing restricted subprocess.",
        "",
    ]
    for e in examples:
        lines += [
            f"## {e['model']} / {e['cell']} / {e['task']}",
            "",
            f"Source call: {e['call_key']}; condition: {e['condition']}.",
            "",
            "Alternative: " + e["alternative_description"],
            "",
            "```python",
            e["code"],
            "```",
            "",
            "Expected distinguishing/control cases: " + repr(e["witnesses"]),
            "",
            "Separate authored witness-suite results: " + repr(e["witness_outcomes"]),
            "",
            "Both-pass in the original suites does not guarantee agreement on these "
            "authored boundaries. Treat coverage discrepancies as oracle sensitivity.",
            "",
        ]
    (destination / "REPRESENTATIVE_CODE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    from analysis.memory_audit.design import DESTINATION

    audit_examples(DESTINATION)
