"""Prepare the approved diagnostic M1 grid, without any model requests."""

import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tokenizers import Tokenizer

from experiments.config import TASK_IDS
from experiments.utilisation_pilot import template
from prompt_energy.memory_revision import m1_prompt
from prompt_energy.utilisation_eval import load_dataset
from prompt_energy.utilisation_plan import ROOT, digest, load_config, schedule

TARGETS = ("HumanEval/89", "HumanEval/94", "HumanEval/105", "HumanEval/144", "HumanEval/39")


def matched_filler(target: dict, companions: list, position: int, tokenizer) -> str:
    """Find a neutral prefix matching the full passive prompt, including template."""

    def count(text):
        return len(tokenizer.encode(template(text)).ids)

    passive = m1_prompt(target, companions, "passive", position)["prompt"]
    desired = count(passive)
    neutral = tokenizer.encode(
        "Background notes list weather observations, colours, dates and notebook page numbers.\n"
        * 1000
    ).ids
    for n in range(min(len(neutral), desired * 2)):
        text = tokenizer.decode(neutral[:n], skip_special_tokens=False)
        try:
            m1_prompt(target, companions, "filler", position, filler=text, count=count)
        except ValueError:
            continue
        return text
    raise ValueError("Cannot match complete passive/filler inputs without editing target")


def build(tasks: dict, tokenizer, cfg: dict) -> list[dict]:
    """Deterministic companions and declared partial position counterbalance."""
    order = [f"HumanEval/{i}" for i in range(164)]
    seed = int.from_bytes(hashlib.sha256(b"1729/M1").digest()[:8], "big")
    random.Random(seed).shuffle(order)
    roster = [tid for tid in order if tid in TASK_IDS]
    if tuple(roster[:5]) != TARGETS:
        raise ValueError("Approved pilot target prefix changed")
    models = [m["tag"] for m in cfg["models"]]
    items = []

    def add(tid, condition, result, identity):
        prompt = result["prompt"]
        items.append(
            {
                "experiment": "M1",
                "condition": condition,
                "task_id": tid,
                "entries": result["entries"],
                "models": models,
                "identity": {
                    "pilot": True,
                    "include_in_main_analysis": False,
                    "task_ids": result["task_ids"],
                    **identity,
                },
                "sections": {"tasks": [prompt]},
                "layout": ["tasks"],
                "prompt_tokens": dict.fromkeys(models, len(tokenizer.encode(template(prompt)).ids)),
            }
        )

    for index, tid in enumerate(TARGETS):
        target = tasks[tid]
        control = {
            "prompt": (
                f"Read the background. Complete only {target['entry_point']}. "
                f"Return only Python code.\n[TARGET]\n{target['prompt']}"
            ),
            "entries": [target["entry_point"]],
            "task_ids": [tid],
        }
        add(tid, "isolated", control, {"k": 1, "target_task_id": tid})
        for k in (2, 4):
            candidates = roster[roster.index(tid) + 1 :] + roster[: roster.index(tid)]
            companions = []
            used = {target["entry_point"]}
            for candidate in candidates:
                task = tasks[candidate]
                if task["entry_point"] not in used:
                    companions.append(task)
                    used.add(task["entry_point"])
                if len(companions) == k - 1:
                    break
            if len(companions) != k - 1:
                raise ValueError("Not enough distinct-entry-point companions")
            position = 0 if index % 2 == 0 else k - 1
            filler = matched_filler(target, companions, position, tokenizer)
            for mode in ("passive", "active", "filler"):
                result = m1_prompt(
                    target,
                    companions,
                    mode,
                    position,
                    filler=filler,
                    count=lambda text: len(tokenizer.encode(template(text)).ids),
                )
                add(
                    tid,
                    f"{mode}/K{k}",
                    result,
                    {
                        "k": k,
                        "mode": mode,
                        "target_task_id": tid,
                        "bundle_task_ids": result["bundle_task_ids"],
                        "target_position": position,
                    },
                )
    return items


def main() -> None:
    cfg, sha = load_config()
    tokenpath = ROOT / "results/utilisation/validation/tokenizer.json"
    if (
        hashlib.sha256(tokenpath.read_bytes()).hexdigest()
        != cfg["benchmark"]["tokenizer_and_template_hashes"]["tokenizer_sha256"]
    ):
        raise ValueError("Tokenizer changed")
    tasks = load_dataset(
        ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz",
        cfg["benchmark"]["dataset_sha256"],
    )
    items = build(tasks, Tokenizer.from_file(str(tokenpath)), cfg)
    jobs = schedule(items, cfg, sha)
    if len(jobs) != 70:
        raise ValueError("Expected 70 pilot calls")
    path = ROOT / "studies/utilisation/stimuli/M1-pilot.json"
    text = json.dumps(items, indent=2) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    record = {
        "date": "2026-11-20",
        "hypotheses": "Diagnostic only; excluded from hypothesis tests",
        "competing_predictions": "M1-PILOT-2026-11-20.md",
        "conditions": sorted({i["condition"] for i in items}),
        "outcomes": (
            "Target and bundle correctness, truncation, token counts, latency "
            "and qualified energy coverage"
        ),
        "analysis": "Pilot denominators and measured runtime; no treatment-effect inference",
        "exclusions": (
            "All pilot rows excluded from main hypothesis analyses; retain every failed/capped call"
        ),
        "config_hash": sha,
        "stimuli_hash": hashlib.sha256(text.encode()).hexdigest(),
        "schedule_hash": digest(jobs),
    }
    (ROOT / "studies/utilisation/prereg/M1.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    review = ROOT / "docs/PROMPTS_M1_PILOT.md"
    review.write_text(
        "# M1 diagnostic pilot - material review\n\n"
        "Status: owner-approved diagnostic grid; exact prompts available for inspection.\n\n"
        + "\n".join(
            f"## {i['task_id']} / {i['condition']}\n\n"
            f"Input tokens: {next(iter(i['prompt_tokens'].values()))}\n\n"
            f"```text\n{i['sections']['tasks'][0]}\n```\n"
            for i in items
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "calls": len(jobs),
                "schedule_hash": digest(jobs),
                "input_tokens_min": min(j["expected_tokens"] for j in jobs),
                "input_tokens_max": max(j["expected_tokens"] for j in jobs),
                "materials": str(review),
                "status": "grid_approved_materials_published",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
