"""Pause-aware offline scoring with the unchanged restricted oracle."""

from pathlib import Path

from prompt_energy.preference_materials import format_adherence
from prompt_energy.utilisation_eval import score_function
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_run import by_key


def evaluate_stage(root: Path, tasks: dict, config: dict, pause: Path, alternatives: dict) -> bool:
    """Caller holds global lock; no model output executes in this process."""
    calls = by_key(root / "calls.jsonl")
    scores = by_key(root / "scores.jsonl")
    adherence = by_key(root / "adherence.jsonl")
    cross = by_key(root / "cross-pass.jsonl")
    for key, call in calls.items():
        if pause.exists():
            return False
        tid = call["task_id"]
        if key not in scores:
            result = {"key": key, "functions": {}}
            if not call["input_valid"]:
                result["status"] = "invalid_input"
            elif "output_cap" in call["flags"]:
                result["status"] = "truncated"
            else:
                entry = tasks[tid]["entry_point"]
                pair = score_function(
                    tasks[tid], call["extracted"][entry], config["evaluation"], call["seed"]
                )
                result["functions"][tid] = pair
                result["status"] = (
                    "passed" if all(p["status"] == "passed" for p in pair.values()) else "failed"
                )
            append_json(root / "scores.jsonl", result)
            scores[key] = result
        if call["experiment"] == "E5" and key not in adherence:
            result = {
                "key": key,
                "input_valid": call["input_valid"],
                "output_capped": "output_cap" in call["flags"],
                **format_adherence(call.get("raw_output"), tasks[tid]["entry_point"]),
            }
            append_json(root / "adherence.jsonl", result)
        if call["identity"].get("similarity") == "near_duplicate" and key not in cross:
            if pause.exists():
                return False
            pair = {}
            if call["input_valid"] and "output_cap" not in call["flags"]:
                pair = score_function(
                    alternatives[tid]["row"],
                    call["extracted"][tasks[tid]["entry_point"]],
                    config["evaluation"],
                    call["seed"],
                )
            append_json(
                root / "cross-pass.jsonl",
                {
                    "key": key,
                    "task": tid,
                    "partitions": pair,
                    "target_status": scores[key]["status"],
                    "alternative_pass": all(p["status"] == "passed" for p in pair.values())
                    if pair
                    else None,
                    "censored_or_invalid": not bool(pair),
                },
            )
    return True


def validity_gate(calls: list[dict], scores: list[dict], expected: int) -> dict:
    """Use measurement/evaluator validity, never successes or effect direction."""
    keys = {r["key"] for r in calls}
    scorekeys = {r["key"] for r in scores}
    bad = sum(
        not r["input_valid"] or r.get("call_failed", False) or "output_cap" in r["flags"]
        for r in calls
    )
    infrastructure = sum(
        p["status"] == "infrastructure_error"
        for r in scores
        for t in r["functions"].values()
        for p in t.values()
    )
    covered = sum(bool(r["energy_valid"]) for r in calls)
    return {
        "pass": len(calls) == len(keys) == len(scores) == len(scorekeys) == expected
        and keys == scorekeys
        and bad == 0
        and covered == expected
        and infrastructure == 0,
        "expected": expected,
        "calls": len(calls),
        "scores": len(scores),
        "bad_or_capped": bad,
        "energy_available": covered,
        "infrastructure_errors": infrastructure,
        "uses_correctness": False,
    }
