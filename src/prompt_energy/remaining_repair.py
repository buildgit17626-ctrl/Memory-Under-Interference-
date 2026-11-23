"""A bounded diagnostic repair pilot; feedback is separate from final scoring."""

import json
from dataclasses import asdict
from pathlib import Path

from prompt_energy.continuation_evaluation import evaluate_stage
from prompt_energy.continuation_queue import continuation_queue
from prompt_energy.extraction import prepare_source
from prompt_energy.remaining_materials import keyed, repair_text, retry_feedback
from prompt_energy.sandbox import run_solution
from prompt_energy.tasks import Task
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import digest
from prompt_energy.utilisation_run import by_key
from prompt_energy.utilisation_supervisor import Halt


def check_feedback(call: dict, row: dict, examples: list[dict], limits: dict) -> dict:
    """Only these two frozen examples can influence the next prompt or stopping."""
    checks = []
    for case in examples:
        if not call["input_valid"] or "output_cap" in call["flags"]:
            checks.append({"status": "invalid_or_capped", "case": case})
            continue
        check = (
            "def check(candidate):\n"
            f"    assert candidate(*{case['args']!r}) == {case['expected']}\n"
        )
        task = Task(
            row["task_id"], row["prompt"], row["canonical_solution"], check, row["entry_point"]
        )
        result = run_solution(
            task,
            prepare_source(task, call["extracted"][row["entry_point"]]),
            timeout_seconds=limits["per_candidate_wall_timeout_s"],
            memory_mb=limits["candidate_memory_mb"],
            seed=call["seed"],
            exact_types=True,
        )
        if result.status == "infrastructure_error":
            raise Halt("E3 feedback sandbox infrastructure failure", asdict(result))
        checks.append({**asdict(result), "case": case})
    first = next((c["case"] for c in checks if c["status"] != "passed"), None)
    return {"key": call["key"], "checks": checks, "passed": first is None, "first_failure": first}


def feedback_batch(folder: Path, tasks: dict, examples: dict, cfg: dict, pause: Path) -> bool:
    done = by_key(folder / "feedback.jsonl")
    for key, call in by_key(folder / "calls.jsonl").items():
        if pause.exists():
            return False
        if key not in done:
            record = check_feedback(
                call, tasks[call["task_id"]], examples[call["task_id"]], cfg["evaluation"]
            )
            append_json(folder / "feedback.jsonl", record)
    return True


def derived_job(
    initial: dict,
    task: dict,
    history: list[dict],
    feedback: str,
    memory: str,
    round_index: int,
    tokenizer,
    template,
    seeds: list[int],
) -> dict:
    job = json.loads(json.dumps(initial))
    text = repair_text(task["prompt"], task["entry_point"], history, memory)
    expected = len(tokenizer.encode(template(text)).ids)
    options = job["request"]["options"]
    if expected + options["num_predict"] > options["num_ctx"]:
        raise Halt("E3 derived prompt exceeds frozen context; never silently truncate")
    seed = seeds[round_index - 1]
    job.update(condition=feedback + "_" + memory, seed=seed, expected_tokens=expected)
    job["request"]["prompt"] = text
    options["seed"] = seed
    job["identity"].update(
        round=round_index,
        feedback=feedback,
        memory=memory,
        initial_key=initial["key"],
        parent_keys=[h["key"] for h in history],
        feedback_history_hash=digest(history),
    )
    return keyed(job)


def save_derived(folder: Path, jobs: list[dict]) -> None:
    """Write each raw-dependent schedule once before its first generation."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "derived-schedule.json"
    record = {"algorithm": "remaining_repair_v4", "schedule_hash": digest(jobs), "jobs": jobs}
    if path.exists():
        if json.loads(path.read_text()) != record:
            raise Halt("E3 raw-dependent schedule changed on recovery")
    else:
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def run_pilot(
    root: Path,
    jobs: list[dict],
    cfg: dict,
    tasks: dict,
    examples: dict,
    heldout: dict,
    client,
    log: Path,
    pause: Path,
    tokenizer,
    template,
) -> None:
    initial_folder = root / "initial"
    if continuation_queue(initial_folder, jobs, client, log, pause)["remaining"]:
        raise Halt("User pause")
    if not feedback_batch(initial_folder, tasks, examples, cfg, pause):
        raise Halt("User pause")
    initial = by_key(initial_folder / "calls.jsonl")
    initial_feedback = by_key(initial_folder / "feedback.jsonl")
    branches = []
    for job in jobs:
        for feedback in ("retry", "example"):
            for memory in ("last", "full"):
                branches.append(
                    {
                        "initial": job,
                        "feedback": feedback,
                        "memory": memory,
                        "current": initial[job["key"]],
                        "check": initial_feedback[job["key"]],
                        "history": [],
                    }
                )
    for round_index in (1, 2, 3):
        pending = []
        for branch in branches:
            if branch["check"]["passed"]:
                continue
            previous, check = branch["current"], branch["check"]
            branch["history"].append(
                {
                    "key": previous["key"],
                    "output": previous.get("raw_output") or "",
                    "feedback": retry_feedback(branch["feedback"], check["first_failure"]),
                }
            )
            job = derived_job(
                branch["initial"],
                tasks[previous["task_id"]],
                branch["history"],
                branch["feedback"],
                branch["memory"],
                round_index,
                tokenizer,
                template,
                cfg["seeds"]["sampled_generation"],
            )
            pending.append(job)
            branch["next"] = job["key"]
        if not pending:
            break
        # Deterministic interleaving across task, feedback, memory and model.
        import random

        random.Random(cfg["seeds"]["order"] + round_index).shuffle(pending)
        folder = root / f"round-{round_index}"
        save_derived(folder, pending)
        if continuation_queue(folder, pending, client, log, pause)["remaining"]:
            raise Halt("User pause")
        if not feedback_batch(folder, tasks, examples, cfg, pause):
            raise Halt("User pause")
        calls, checks = by_key(folder / "calls.jsonl"), by_key(folder / "feedback.jsonl")
        for branch in branches:
            key = branch.pop("next", None)
            if key is not None:
                branch.update(current=calls[key], check=checks[key])
    # Hidden tests never determine branch continuation, feedback content or selection.
    for folder in [initial_folder, *(root / f"round-{i}" for i in (1, 2, 3))]:
        if (folder / "calls.jsonl").exists():
            if not evaluate_stage(folder, heldout, cfg, pause, {}):
                raise Halt("User pause")
    physical = [
        call
        for folder in root.iterdir()
        if folder.is_dir()
        for call in by_key(folder / "calls.jsonl").values()
    ]
    final_scores = {
        key: score
        for folder in root.iterdir()
        if folder.is_dir()
        for key, score in by_key(folder / "scores.jsonl").items()
    }
    summaries = []
    for b in branches:
        keys = list(
            dict.fromkeys(
                [b["initial"]["key"], *[h["key"] for h in b["history"]], b["current"]["key"]]
            )
        )
        selected = [r for r in physical if r["key"] in keys]
        net_values = [
            value
            for r in selected
            if (value := r["energy"]["windows"].get("post_load", {}).get("net_wh")) is not None
        ]
        # Shared initial cost counts once per hypothetical policy, once in the physical total.
        summaries.append(
            {
                "initial_key": b["initial"]["key"],
                "task": b["initial"]["task_id"],
                "model": b["initial"]["model"],
                "feedback": b["feedback"],
                "memory": b["memory"],
                "final_key": b["current"]["key"],
                "initial_heldout_status": final_scores[b["initial"]["key"]]["status"],
                "final_heldout_status": final_scores[b["current"]["key"]]["status"],
                "feedback_pass": b["check"]["passed"],
                "physical_keys": keys,
                "attempts": len(selected),
                "output_tokens_total": sum(r.get("output_tokens") or 0 for r in selected),
                "input_tokens_total": sum(r.get("prompt_tokens") or 0 for r in selected),
                "wall_seconds_total": sum(r["wall_seconds"] for r in selected),
                "energy_covered": sum(r["energy_valid"] for r in selected),
                "net_post_load_wh_total_available": sum(net_values) if net_values else None,
                "net_energy_observed_attempts": len(net_values),
                "net_energy_total_complete": len(net_values) == len(selected),
                "identical_code_repeats": len(selected)
                - len({digest(r.get("extracted")) for r in selected}),
            }
        )
    (root / "PILOT_REVIEW.json").write_text(
        json.dumps(
            {
                "physical_calls": len(physical),
                "maximum": 130,
                "branches": summaries,
                "full_E3_authorized": False,
                "energy_missing_not_imputed": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
