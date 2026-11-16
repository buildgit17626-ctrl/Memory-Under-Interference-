"""Deterministic M3 stimulus catalogue; generate before any scored requests."""

import json
import re
from pathlib import Path

from tokenizers import Tokenizer

from experiments.utilisation_pilot import template
from prompt_energy.utilisation_plan import ROOT


def padded_prompt(
    task: dict, other_tasks: list[dict], kind: str, total: int, tokenizer: Tokenizer
) -> tuple[str, dict]:
    name = task["entry_point"]
    target = f"\n[TARGET TASK: complete only {name}]\n{task['prompt']}\n[END TARGET]\n"
    suffix = f"\nReturn only the Python code defining {name}.\n"
    if kind == "irrelevant":
        block = (
            "\n[BACKGROUND NOTES]\nThe notebook lists weather observations, colours and dates.\n"
        )
        content = block * 2000
    elif kind == "other_tasks":
        content = "".join("\n[OTHER TASK, DO NOT SOLVE]\n" + t["prompt"] for t in other_tasks) * 20
    elif kind == "near_duplicate":
        # Preserve the algorithm, vary its name. This tests competing named
        # specifications and redundancy, not contradictory requirements.
        content = "".join(
            "\n[OTHER TASK, DO NOT SOLVE]\n"
            + re.sub(r"\b" + re.escape(name) + r"\b", f"alternate_{i}_{name}", task["prompt"])
            for i in range(200)
        )
    else:
        raise ValueError("Unknown filler")
    tokens = tokenizer.encode(content).ids
    target_tokens = len(tokenizer.encode(target).ids)
    header_tokens = len(tokenizer.encode(template("")).ids)
    before = max(0, total // 2 - header_tokens - target_tokens // 2)
    after = max(
        0, total - before - header_tokens - target_tokens - len(tokenizer.encode(suffix).ids)
    )
    for _ in range(15):
        left = tokenizer.decode(tokens[:before], skip_special_tokens=False)
        right = tokenizer.decode(tokens[before : before + after], skip_special_tokens=False)
        prompt = left + target + right + suffix
        rendered = template(prompt)
        count = len(tokenizer.encode(rendered).ids)
        # Avoid any partial target text; adjust background only.
        if count == total:
            midpoint = len(tokenizer.encode(template(left)).ids) - header_tokens + header_tokens
            midpoint += target_tokens / 2
            return prompt, {
                "independent_tokens": count,
                "target_midpoint_token_approx": midpoint,
                "filler_boundary_fragments": True,
            }
        if count < total:
            # The padding atom is independently counted after full rendering.
            for n in range(max(0, total - count - 3), total - count + 4):
                adjusted = left + target + right + (" x" * n) + suffix
                if len(tokenizer.encode(template(adjusted)).ids) == total:
                    return adjusted, {
                        "independent_tokens": total,
                        "target_midpoint_token_approx": before + target_tokens / 2 + header_tokens,
                        "filler_boundary_fragments": True,
                    }
        after += total - count
        if count > total:
            after -= 4
        if after < 0:
            raise ValueError("Target cannot fit token budget")
    raise ValueError(f"Unable to match {total} tokens for {task['task_id']}/{kind}")


def build(tasks: dict, tokenizer_path: Path, output: Path) -> list:
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    ids = [f"HumanEval/{i}" for i in range(164)]
    items = []
    for index, tid in enumerate(ids):
        task = tasks[tid]
        others = [tasks[ids[(index + k) % len(ids)]] for k in range(1, 11)]
        for total in (1000, 4000):
            for kind in ("irrelevant", "other_tasks", "near_duplicate"):
                prompt, audit = padded_prompt(task, others, kind, total, tokenizer)
                items.append(
                    {
                        "experiment": "M3",
                        "condition": f"{kind}/{total}",
                        "task_id": tid,
                        "entries": [task["entry_point"]],
                        "identity": {
                            "context_length": total,
                            "position": "middle",
                            "filler": kind,
                            "audit": audit,
                        },
                        "sections": {"task": [prompt], "filler": []},
                        "layout": ["task"],
                        "prompt_tokens": dict.fromkeys(
                            ["qwen2.5-coder:0.5b", "qwen2.5-coder:1.5b"], total
                        ),
                    }
                )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(items, indent=2) + "\n", encoding="utf8")
    return items


if __name__ == "__main__":
    from prompt_energy.utilisation_eval import load_dataset
    from prompt_energy.utilisation_plan import load_config

    cfg, _ = load_config()
    dataset = ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz"
    tasks = load_dataset(dataset, cfg["benchmark"]["dataset_sha256"])
    items = build(
        tasks,
        ROOT / "results/utilisation/validation/tokenizer.json",
        ROOT / "studies/utilisation/stimuli/M3.json",
    )
    print({"potential_stimulus_rows": len(items), "focused_calls_after_selection": 240})
