"""Differential HumanEval+ checks inside the existing Windows Job sandbox."""

import ast
import gzip
import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path

from prompt_energy.extraction import prepare_source
from prompt_energy.records import directory_lock
from prompt_energy.sandbox import run_solution
from prompt_energy.tasks import Task
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_run import by_key

# Trusted test body, never filled with candidate text. Mirrors EvalPlus 0.3.1
# HumanEval's polynomial-root oracle and scalar/vector tolerance conventions.
CHECK = """
from copy import deepcopy
import math

def close(actual, expected, tol):
    if isinstance(expected, (list, tuple)):
        return len(actual) == len(expected) and all(
            close(a, b, tol) for a, b in zip(actual, expected))
    return actual == expected or abs(actual - expected) <= tol + 1e-7 * abs(expected)

def check(candidate):
    tol = ATOL
    for arguments in CASES:
        expected = reference(*deepcopy(arguments))
        actual = candidate(*deepcopy(arguments))
        if IS_ROOT:
            assert abs(sum(c * math.pow(actual, i) for i, c in enumerate(arguments[0]))) <= tol
            continue
        floats = isinstance(expected, float) or (
            isinstance(expected, (list, tuple)) and expected
            and all(isinstance(x, float) for x in expected))
        if floats and tol == 0:
            tol = 1e-6
        if actual != expected:
            assert tol and type(actual) is type(expected) and close(actual, expected, tol)
"""


def load_dataset(path: Path, checksum: str) -> dict:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != checksum:
        raise ValueError("HumanEval+ dataset hash mismatch")
    if raw.startswith(b"\x1f\x8b"):
        raw = gzip.decompress(raw)
    rows = [json.loads(line) for line in raw.splitlines()]
    indexed = {r["task_id"]: r for r in rows}
    if len(rows) != 164 or set(indexed) != {f"HumanEval/{i}" for i in range(164)}:
        raise ValueError("Incomplete or duplicated HumanEval+ roster")
    return indexed


def score_function(row: dict, code: str, limits: dict, seed: int) -> dict:
    entry = row["entry_point"]
    if not entry.isidentifier():
        raise ValueError("Invalid benchmark entry")
    try:
        parsed = ast.parse(code)
    except (SyntaxError, ValueError, RecursionError):
        invalid = "syntax_error"
    else:
        invalid = (
            None
            if any(isinstance(n, ast.FunctionDef) and n.name == entry for n in parsed.body)
            else "no_code"
        )
    if invalid:
        return {
            part: {"status": invalid, "scheduled_cases": len(row[part])}
            for part in ("base_input", "plus_input")
        }
    reference = row["prompt"] + row["canonical_solution"]
    results = {}
    deadline = time.monotonic() + limits["per_candidate_wall_timeout_s"]
    for partition in ("base_input", "plus_input"):
        cases = row[partition]
        if not cases:
            raise ValueError("Empty HumanEval+ partition")
        check = (
            reference
            + f"\nreference = {entry}\nCASES = {cases!r}\n"
            + f"ATOL = {float(row['atol'])!r}\nIS_ROOT = {entry == 'find_zero'}\n"
            + CHECK
        )
        task = Task(row["task_id"], row["prompt"], row["canonical_solution"], check, entry)
        result = run_solution(
            task,
            prepare_source(task, code),
            seed=seed,
            exact_types=True,
            memory_mb=limits["candidate_memory_mb"],
            timeout_seconds=max(0.001, deadline - time.monotonic()),
        )
        results[partition] = {"scheduled_cases": len(cases), **asdict(result)}
    return results


def evaluate(root: Path, tasks: dict, config: dict) -> None:
    with directory_lock(root):
        scores = root / "scores.jsonl"
        done = by_key(scores)
        for key, call in by_key(root / "calls.jsonl").items():
            if key in done:
                continue
            result = {"key": key, "functions": {}}
            if not call["input_valid"]:
                result["status"] = "invalid_input"
            elif "output_cap" in call["flags"]:
                result["status"] = "truncated"
            elif call["experiment"] == "U2":
                choice = call["raw_output"].strip()
                answer = call["identity"].get("correct_option")
                if answer is None:
                    result["status"] = "missing_answer_key"
                elif choice not in {"A", "B", "C", "D"}:
                    result["status"] = "invalid_choice"
                else:
                    result["status"] = "passed" if choice == answer else "failed"
                result["choice"] = choice
            else:
                ids = call["identity"].get("task_ids", [call["task_id"]])
                passed = True
                for tid in ids:
                    task = tasks[tid]
                    pair = score_function(
                        task,
                        call["extracted"][task["entry_point"]],
                        config["evaluation"],
                        call["seed"],
                    )
                    result["functions"][tid] = pair
                    passed &= all(out["status"] == "passed" for out in pair.values())
                result["status"] = "passed" if passed else "failed"
            append_json(scores, result)


def audit_references(root: Path, tasks: dict, cfg: dict, checksum: str) -> None:
    """Exercise actual base/plus suites without issuing inference requests."""
    with directory_lock(root):
        path = root / "reference-audit.jsonl"
        done = by_key(path)
        for tid, task in tasks.items():
            key = f"{checksum}/{tid}"
            if key not in done:
                scores = score_function(
                    task,
                    task["prompt"] + task["canonical_solution"],
                    cfg["evaluation"],
                    cfg["seeds"]["structural_generation"],
                )
                append_json(path, {"key": key, "partitions": scores})
        rows = by_key(path)
        failed = [
            k
            for k, v in rows.items()
            if k.startswith(checksum + "/")
            and any(p["status"] != "passed" for p in v["partitions"].values())
        ]
        print(
            json.dumps({"total": len(tasks), "passed": len(tasks) - len(failed), "failed": failed})
        )
