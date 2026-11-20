"""Freeze and validate full M1 independently of the diagnostic pilot."""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

import yaml
from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.config import TASK_IDS
from experiments.utilisation_pilot import template
from prompt_energy.memory_revision import m1_prompt
from prompt_energy.utilisation_eval import load_dataset, score_function
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import ROOT, digest, load_config, schedule
from prompt_energy.utilisation_run import by_key

BASE = ROOT / "studies/utilisation/full-m1"


def configuration():
    raw = (BASE / "config.yaml").read_bytes().replace(b"\r\n", b"\n")
    return yaml.safe_load(raw), hashlib.sha256(raw).hexdigest()


def prepare():
    cfg, _ = load_config()
    cfg["paths"]["config"] = "studies/utilisation/full-m1/config.yaml"
    cfg["paths"]["preregistrations"] = "studies/utilisation/full-m1/prereg"
    BASE.mkdir(parents=True, exist_ok=True)
    (BASE / "prereg").mkdir(exist_ok=True)
    (BASE / "config.yaml").write_text(
        yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8", newline="\n"
    )
    cfg, sha = configuration()
    tasks = load_dataset(
        ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz",
        cfg["benchmark"]["dataset_sha256"],
    )
    tokenpath = ROOT / "results/utilisation/validation/tokenizer.json"
    if (
        hashlib.sha256(tokenpath.read_bytes()).hexdigest()
        != cfg["benchmark"]["tokenizer_and_template_hashes"]["tokenizer_sha256"]
    ):
        raise ValueError("Tokenizer changed")
    tokenizer = Tokenizer.from_file(str(tokenpath))
    order = [f"HumanEval/{i}" for i in range(164)]
    random.Random(int.from_bytes(hashlib.sha256(b"1729/M1").digest()[:8], "big")).shuffle(order)
    roster = [t for t in order if t in TASK_IDS]
    models = [m["tag"] for m in cfg["models"]]
    items = []
    for index, tid in enumerate(roster):
        target = tasks[tid]
        cases = [
            (
                "isolated",
                {
                    "prompt": (
                        f"Read the background. Complete only {target['entry_point']}. "
                        f"Return only Python code.\n[TARGET]\n{target['prompt']}"
                    ),
                    "entries": [target["entry_point"]],
                    "task_ids": [tid],
                },
                {"k": 1},
            )
        ]
        for k in (2, 3, 4, 6):
            companions, used = [], {target["entry_point"]}
            for candidate in roster[index + 1 :] + roster[:index]:
                if tasks[candidate]["entry_point"] not in used:
                    companions.append(tasks[candidate])
                    used.add(tasks[candidate]["entry_point"])
                if len(companions) == k - 1:
                    break
            position = 0 if index % 2 == 0 else k - 1
            desired = len(
                tokenizer.encode(
                    template(m1_prompt(target, companions, "passive", position)["prompt"])
                ).ids
            )
            plain = (
                f"Read the background. Complete only {target['entry_point']}. "
                "Return only Python code.\n"
                + (
                    "[TARGET]\n" + target["prompt"] + "\n"
                    if position == 0
                    else "\n[TARGET]\n" + target["prompt"]
                )
            )
            estimate = desired - len(tokenizer.encode(template(plain)).ids)
            neutral = tokenizer.encode(
                "Background notes list weather, colours and dates.\n" * 500
            ).ids
            filler = None
            for padding in (False, True):
                for n in range(max(0, estimate - 24), max(1, estimate + 25)):
                    candidate = (
                        " x" * n
                        if padding
                        else tokenizer.decode(neutral[:n], skip_special_tokens=False)
                    )
                    try:
                        m1_prompt(
                            target,
                            companions,
                            "filler",
                            position,
                            filler=candidate,
                            count=lambda p: len(tokenizer.encode(template(p)).ids),
                        )
                    except ValueError:
                        continue
                    filler = candidate
                    break
                if filler is not None:
                    break
            if filler is None:
                raise ValueError(f"No exact filler match for {tid}/K{k}")
            for mode in ("passive", "active", "filler"):
                result = m1_prompt(
                    target,
                    companions,
                    mode,
                    position,
                    filler=filler,
                    count=lambda p: len(tokenizer.encode(template(p)).ids),
                )
                cases.append(
                    (
                        f"{mode}/K{k}",
                        result,
                        {
                            "k": k,
                            "mode": mode,
                            "bundle_task_ids": result["bundle_task_ids"],
                            "target_position": position,
                        },
                    )
                )
        for condition, result, identity in cases:
            items.append(
                {
                    "experiment": "M1",
                    "condition": condition,
                    "task_id": tid,
                    "entries": result["entries"],
                    "models": models,
                    "identity": {
                        "pilot": False,
                        "include_in_main_analysis": True,
                        "target_task_id": tid,
                        "task_ids": result["task_ids"],
                        **identity,
                    },
                    "sections": {"tasks": [result["prompt"]]},
                    "layout": ["tasks"],
                    "prompt_tokens": dict.fromkeys(
                        models, len(tokenizer.encode(template(result["prompt"])).ids)
                    ),
                }
            )
    jobs = schedule(items, cfg, sha)
    assert len(jobs) == 1040
    text = json.dumps(items, indent=2) + "\n"
    (BASE / "stimuli.json").write_text(text, encoding="utf-8", newline="\n")
    record = {
        "date": "2026-11-21",
        "hypotheses": (
            "Owner: increasing task load may reduce per-task correctness; batc"
            "hing may improve overall efficiency"
        ),
        "competing_predictions": (
            "No degradation or improved correctness; active output work and or"
            "der remain alternative explanations"
        ),
        "conditions": sorted({i["condition"] for i in items}),
        "outcomes": (
            "Target pass, per-function pass, all-functions pass, latency, toke"
            "ns, qualified gross/net energy and cost per correct"
        ),
        "analysis": (
            "Exploratory post-pilot task-paired comparisons, not confirmatory;"
            " 2000 task-bootstrap draws seed1732; Holm over passive-isolation "
            "and active-passive at K2/3/4/6 per model (16 contrasts); explorat"
            "ory other contrasts; report all and independently E0-solvable sub"
            "sets"
        ),
        "exclusions": (
            "Exclude pilot data; report invalid/API/cap/missing energy; capped"
            " bounded generations non-pass; no replacement; partial timed cell"
            "s explicit; retain raw records"
        ),
        "config_hash": sha,
        "stimuli_hash": hashlib.sha256(text.encode()).hexdigest(),
        "schedule_hash": digest(jobs),
    }
    (BASE / "prereg/M1.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (BASE / "owner-review.json").write_text(
        json.dumps(
            {
                "owner_approved": True,
                "scope": "Owner approved timed full-M1 queue in chat 2026-11-21",
                "schedule_hash": digest(jobs),
                "hours": 7.5,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "calls": len(jobs),
                "schedule_hash": digest(jobs),
                "targets": roster,
                "input_tokens_range": [
                    min(j["expected_tokens"] for j in jobs),
                    max(j["expected_tokens"] for j in jobs),
                ],
            }
        )
    )


def validate():
    cfg, _ = configuration()
    tasks = load_dataset(
        ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz",
        cfg["benchmark"]["dataset_sha256"],
    )
    items = json.loads((BASE / "stimuli.json").read_text())
    root = ROOT / "results/utilisation/m1-full-validation"
    root.mkdir(parents=True, exist_ok=True)
    done, expected = by_key(root / "references.jsonl"), set()
    for item in items:
        if not (item["condition"] == "isolated" or item["condition"].startswith("active/")):
            continue
        ids = item["identity"]["task_ids"]
        code = "\n\n".join(tasks[t]["prompt"] + tasks[t]["canonical_solution"] for t in ids)
        for tid in ids:
            key = digest([ids, tid, code, cfg["evaluation"]])
            expected.add(key)
            if key not in done:
                result = score_function(tasks[tid], code, cfg["evaluation"], 1729)
                done[key] = {"key": key, "task": tid, "bundle": ids, "partitions": result}
                append_json(root / "references.jsonl", done[key])
    failed = [
        k for k in expected if any(x["status"] != "passed" for x in done[k]["partitions"].values())
    ]
    report = {
        "checks": len(expected),
        "passed": len(expected) - len(failed),
        "failed_keys": failed,
        "stimuli_hash": digest(items),
    }
    (root / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "validate"])
    args = parser.parse_args()
    prepare() if args.action == "prepare" else validate()
