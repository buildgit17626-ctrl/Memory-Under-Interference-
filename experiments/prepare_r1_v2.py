"""Prepare approved five-policy R1, separate pilot/full registrations."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml
from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.config import TASK_IDS
from experiments.utilisation_pilot import template
from prompt_energy.memory_revision import R1_POLICIES, r1_prompt
from prompt_energy.r1_materials import compact_specification
from prompt_energy.utilisation_eval import load_dataset, score_function
from prompt_energy.utilisation_plan import ROOT, digest, load_config, schedule
from prompt_energy.utilisation_run import by_key

BASE = ROOT / "studies/utilisation/r1-v2"


def configuration(phase):
    raw = (BASE / phase / "config.yaml").read_bytes().replace(b"\r\n", b"\n")
    return yaml.safe_load(raw), hashlib.sha256(raw).hexdigest()


def prepare():
    original, _ = load_config()
    tasks = load_dataset(
        ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz",
        original["benchmark"]["dataset_sha256"],
    )
    tokenpath = ROOT / "results/utilisation/validation/tokenizer.json"
    assert (
        hashlib.sha256(tokenpath.read_bytes()).hexdigest()
        == original["benchmark"]["tokenizer_and_template_hashes"]["tokenizer_sha256"]
    )
    tokenizer = Tokenizer.from_file(str(tokenpath))
    order = json.loads((ROOT / original["scope"]["task_orders"]).read_text())["sweeps"]["R1"][
        "task_order"
    ]
    roster = [t for t in order if t in TASK_IDS]
    all_items = []
    for index, tid in enumerate(roster):
        task = tasks[tid]
        entry = task["entry_point"]
        distractors = (roster[index + 1 :] + roster[:index])[:8]
        history = ["[EARLIER TASK SPECIFICATION]\n" + tasks[d]["prompt"] for d in distractors]
        target = "[TARGET SPECIFICATION]\n" + task["prompt"]
        preference = "[USER PREFERENCE]\nReturn only Python code, without explanation."
        material = {
            "target": target,
            "before": "\n".join(history[:4]),
            "after": "\n".join(history[4:]),
            "preference": preference,
            "query": f"[CURRENT QUERY]\nComplete the function {entry}.",
            "summary": "[COMPACT TARGET SPECIFICATION]\n"
            + compact_specification(task["prompt"], entry)
            + "\n"
            + preference,
            "summary_reviewed": True,
        }
        for policy in R1_POLICIES:
            prompt = r1_prompt(material, policy)
            all_items.append(
                {
                    "experiment": "R1",
                    "condition": "lossless_compaction" if policy == "compact_summary" else policy,
                    "task_id": tid,
                    "entries": [entry],
                    "identity": {
                        "task_ids": [tid],
                        "distractor_ids": distractors,
                        "compaction": "word_and_example_preserving_formatting",
                        "retention": "oracle" if policy == "oracle_selective" else "static_policy",
                    },
                    "sections": {"task": [prompt], "blocks": []},
                    "layout": ["task"],
                    "prompt_tokens": dict.fromkeys(
                        [m["tag"] for m in original["models"]],
                        len(tokenizer.encode(template(prompt)).ids),
                    ),
                }
            )
    for phase, n in [("pilot", 5), ("full", 40)]:
        folder = BASE / phase
        (folder / "prereg").mkdir(parents=True, exist_ok=True)
        cfg = json.loads(json.dumps(original))
        cfg["scope"]["current_experiment"] = "R1_v2"
        cfg["scope"]["current_stage"] = phase
        cfg["scope"]["current_stage_call_budget"] = n * 5 * 2
        cfg["scope"]["current_shared_task_count"] = n
        cfg["paths"]["config"] = str((folder / "config.yaml").relative_to(ROOT)).replace("\\", "/")
        cfg["paths"]["preregistrations"] = str((folder / "prereg").relative_to(ROOT)).replace(
            "\\", "/"
        )
        (folder / "config.yaml").write_text(
            yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8", newline="\n"
        )
        cfg, sha = configuration(phase)
        items = [json.loads(json.dumps(i)) for i in all_items if i["task_id"] in roster[:n]]
        for item in items:
            item["identity"].update(
                pilot=phase == "pilot", include_in_main_analysis=phase == "full"
            )
        text = json.dumps(items, indent=2) + "\n"
        (folder / "stimuli.json").write_text(text, encoding="utf-8", newline="\n")
        jobs = schedule(items, cfg, sha)
        record = {
            "date": "2026-11-22",
            "hypotheses": (
                "Owner: replay/selective retention may improve correctness or effi"
                "ciency versus full history; compaction is not semantic summarizat"
                "ion"
            ),
            "competing_predictions": (
                "No benefit; minimal-context advantage; length/recency/preference "
                "confounding; oracle advantage not practical retrieval"
            ),
            "conditions": sorted({i["condition"] for i in items}),
            "outcomes": (
                "Base-plus correctness, actual tokens, native API timing and quali"
                "fied CPU package energy"
            ),
            "analysis": (
                "Pilot diagnostic only. Full: paired task-bootstrap2000/seed1732; "
                "replay-full, oracle-full, compact-full per model; Holm family6. E"
                "xact-token matched subset if any, otherwise unavailable; length-a"
                "djusted fits exploratory, not causal."
            ),
            "exclusions": (
                "Pilot excluded from main analyses; bounded output caps non-pass; "
                "invalid/API observations disclosed; energy missing not imputed; d"
                "rift and low-resolution sensitivities"
            ),
            "config_hash": sha,
            "stimuli_hash": hashlib.sha256(text.encode()).hexdigest(),
            "schedule_hash": digest(jobs),
        }
        (folder / "prereg/R1.json").write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        print(phase, "calls", len(jobs), "max_input", max(j["expected_tokens"] for j in jobs))
    (BASE / "roster.json").write_text(
        json.dumps(
            {
                "tasks": roster,
                "pilot": roster[:5],
                "semantic_summary": "deferred; no audited semantic summaries available",
                "token_matched_controls": (
                    "No new arms; report exact-token matched pairs where available; no"
                    " causal input-length isolation claim"
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def validate():
    cfg, _ = configuration("full")
    tasks = load_dataset(
        ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz",
        cfg["benchmark"]["dataset_sha256"],
    )
    roster = json.loads((BASE / "roster.json").read_text())["tasks"]
    original = by_key(ROOT / "results/utilisation/m1-full-validation/references.jsonl")
    root = ROOT / "results/utilisation/r1-v2-validation"
    root.mkdir(parents=True, exist_ok=True)
    results = []
    for tid in roster:
        task = tasks[tid]
        code = task["prompt"] + task["canonical_solution"]
        key = digest([[tid], tid, code, cfg["evaluation"]])
        previous = original.get(key)
        parts = (
            previous["partitions"]
            if previous
            else score_function(task, code, cfg["evaluation"], 1729)
        )
        results.append(
            {
                "task": tid,
                "passed": all(x["status"] == "passed" for x in parts.values()),
                "reused_exact_reference_check": bool(previous),
            }
        )
    report = {
        "checks": len(results),
        "passed": sum(r["passed"] for r in results),
        "details": results,
        "pilot_stimuli": digest(json.loads((BASE / "pilot/stimuli.json").read_text())),
        "full_stimuli": digest(json.loads((BASE / "full/stimuli.json").read_text())),
    }
    (root / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": report["checks"], "passed": report["passed"]}))
    if report["passed"] != 40:
        raise SystemExit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "validate"])
    args = parser.parse_args()
    prepare() if args.action == "prepare" else validate()
