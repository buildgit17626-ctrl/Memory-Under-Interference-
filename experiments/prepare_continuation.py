"""Prepare and validate E5 and semantic M3/R2 before any model inference."""

import argparse
import ast
import hashlib
import json
import random
import re
import sys
from pathlib import Path

import yaml
from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.config import TASK_IDS
from experiments.utilisation_pilot import template
from prompt_energy.preference_materials import POLICIES, preference_prompt
from prompt_energy.sandbox import run_solution
from prompt_energy.semantic_alternatives import alternative_catalog, specification, variant_row
from prompt_energy.tasks import Task
from prompt_energy.utilisation_eval import load_dataset, score_function
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import ROOT, digest, load_config, schedule
from prompt_energy.utilisation_run import by_key

BASE = ROOT / "studies/utilisation/continuation-v3"
VALIDATION = ROOT / "results/utilisation/continuation-validation"


def configuration(stage: str, phase: str) -> tuple[dict, str]:
    raw = (BASE / stage / phase / "config.yaml").read_bytes().replace(b"\r\n", b"\n")
    return yaml.safe_load(raw), hashlib.sha256(raw).hexdigest()


def source() -> tuple[dict, dict, Tokenizer]:
    cfg, _ = load_config()
    tasks = load_dataset(
        ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz",
        cfg["benchmark"]["dataset_sha256"],
    )
    path = ROOT / "results/utilisation/validation/tokenizer.json"
    if (
        hashlib.sha256(path.read_bytes()).hexdigest()
        != cfg["benchmark"]["tokenizer_and_template_hashes"]["tokenizer_sha256"]
    ):
        raise ValueError("Tokenizer changed")
    return cfg, tasks, Tokenizer.from_file(str(path))


def save(path: Path, value, *, yaml_text=False) -> None:
    text = (
        yaml.safe_dump(value, sort_keys=False) if yaml_text else json.dumps(value, indent=2) + "\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise ValueError("Prepared artifact already exists with different contents: " + str(path))
    if not path.exists():
        path.write_text(text, encoding="utf-8", newline="\n")


def ordered_roster(stage: str) -> list[str]:
    original, _ = load_config()
    orders = json.loads((ROOT / original["scope"]["task_orders"]).read_text())["sweeps"]
    if stage == "R2":
        return [t for t in orders["R2"]["task_order"] if t in TASK_IDS]
    roster = list(TASK_IDS)
    seed = int.from_bytes(hashlib.sha256(b"1729/E5-preference").digest()[:8], "big")
    random.Random(seed).shuffle(roster)
    return roster


def build_item(exp, condition, tid, entry, text, tokenizer, models, **identity):
    sections = (
        {"framing": [], "task": [text]} if exp == "E5" else {"task": [text], "distractors": []}
    )
    return {
        "experiment": exp,
        "condition": condition,
        "task_id": tid,
        "entries": [entry],
        "identity": {"task_ids": [tid], **identity},
        "sections": sections,
        "layout": ["task"],
        "prompt_tokens": dict.fromkeys(models, len(tokenizer.encode(template(text)).ids)),
    }


def freeze_stage(stage: str, roster: list[str], items: list[dict], original: dict) -> None:
    for phase, n in (("pilot", min(5, len(roster))), ("full", len(roster))):
        folder = BASE / stage / phase
        cfg = json.loads(json.dumps(original))
        cfg["experiments"][stage] = {
            **cfg["experiments"][stage],
            "temperature": 0,
            "samples": 1,
            "num_ctx": 8192 if stage == "E5" else 16384,
            "num_predict": 2048,
            "http_deadline_s": 900,
        }
        cfg["scope"].update(
            current_experiment=stage + "_v3",
            current_stage=phase,
            current_shared_task_count=n,
            execution_deadline=None,
        )
        cfg["paths"]["config"] = (folder / "config.yaml").relative_to(ROOT).as_posix()
        cfg["paths"]["preregistrations"] = (folder / "prereg").relative_to(ROOT).as_posix()
        save(folder / "config.yaml", cfg, yaml_text=True)
        cfg, checksum = configuration(stage, phase)
        subset = json.loads(json.dumps([i for i in items if i["task_id"] in roster[:n]]))
        for item in subset:
            item["identity"].update(
                pilot=phase == "pilot", include_in_main_analysis=phase == "full"
            )
        save(folder / "stimuli.json", subset)
        jobs = schedule(subset, cfg, checksum)
        primary = (
            "Buried-immediate and replayed-buried plain-code adherence, each model; Holm family4. "
            "Correctness, corrected-immediate and no-preference comparisons secondary."
            if stage == "E5"
            else (
                "Near-duplicate minus irrelevant target correctness, "
                "average lengths/positions within task, "
                "each model; Holm family2. Related and load/position interactions exploratory. "
                "Cross-pass on hidden modified argument suites, "
                "target-only/distractor-only/both/neither."
            )
        )
        save(
            folder / "prereg" / (stage + ".json"),
            {
                "date": "2026-11-23",
                "hypotheses": (
                    "Owner: preferences may be lost in history and recovered by replay/correction."
                    if stage == "E5"
                    else (
                        "Owner C1: semantically similar distractors may impair "
                        "target correctness more than irrelevant filler."
                    )
                ),
                ("competing_predictions"): (
                    "No difference, opposite direction, "
                    "length/recency/instruction effects; no inference "
                    "about internal memory."
                ),
                "conditions": sorted({i["condition"] for i in subset}),
                ("outcomes"): (
                    "Target base-plus correctness, raw tokens/native "
                    "timings, qualified generation-only CPU-package "
                    "energy; E5 format adherence; R2 cross-pass."
                ),
                ("analysis"): (
                    "Pilot diagnostic only. Paired "
                    "task-bootstrap2000/seed1732, 95% percentile "
                    "intervals. "
                )
                + primary,
                ("exclusions"): (
                    "Pilot separate; invalid input/API/infrastructure "
                    "disclosed; caps bounded nonpass, not giving up; "
                    "missing energy no imputation; drift and "
                    "low-resolution sensitivities. R2 material exclusions "
                    "frozen before generation, never selected by model "
                    "outcome."
                ),
                ("interpretation_changers"): (
                    "Oracle/reference or classifier errors, incomplete "
                    "distinguishing cases, censoring, input "
                    "length/position differences, drift and benchmark "
                    "contamination."
                ),
                ("inference_boundary"): (
                    "Two small Q4_K_M models, one fixed benchmark roster, "
                    "one sample per task-cell. Custom distractor suites "
                    "are not a new validated benchmark."
                ),
                "config_hash": checksum,
                "stimuli_hash": hashlib.sha256((folder / "stimuli.json").read_bytes()).hexdigest(),
                "schedule_hash": digest(jobs),
                "call_count": len(jobs),
                "tasks": roster[:n],
            },
        )
        print(
            json.dumps(
                {
                    "stage": stage,
                    "phase": phase,
                    "calls": len(jobs),
                    "tasks": n,
                    "max_input": max(j["expected_tokens"] for j in jobs),
                }
            ),
            flush=True,
        )
    save(BASE / stage / "roster.json", {"tasks": roster, "pilot": roster[:5]})


def prepare_e5() -> None:
    cfg, tasks, tokenizer = source()
    roster = ordered_roster("E5")
    history_order = json.loads((ROOT / "studies/utilisation/r1-v2/roster.json").read_text())[
        "tasks"
    ]
    models = [m["tag"] for m in cfg["models"]]
    items = []
    for tid in roster:
        index = history_order.index(tid)
        distractors = (history_order[index + 1 :] + history_order[:index])[:8]
        history = ["[EARLIER TASK SPECIFICATION]\n" + tasks[d]["prompt"] for d in distractors]
        target = "[TARGET SPECIFICATION]\n" + tasks[tid]["prompt"]
        entry = tasks[tid]["entry_point"]
        query = f"[CURRENT QUERY]\nComplete the function {entry}."
        for policy in POLICIES:
            text = preference_prompt(target, query, history, policy)
            items.append(
                build_item(
                    "E5", policy, tid, entry, text, tokenizer, models, distractor_ids=distractors
                )
            )
    freeze_stage("E5", roster, items, cfg)


def witness_check(task: dict, definition: dict, *, modified: bool, cfg: dict) -> dict:
    row = variant_row(task, definition) if modified else task
    expected_key = "alternative_expected" if modified else "target_expected"
    lines = ["def check(candidate):"]
    for witness in definition["witnesses"]:
        lines.append(f"    assert candidate(*{witness['args']!r}) == {witness[expected_key]}")
    check = Task(
        task["task_id"],
        row["prompt"],
        row["canonical_solution"],
        "\n".join(lines),
        task["entry_point"],
    )
    from dataclasses import asdict

    return asdict(
        run_solution(
            check,
            row["prompt"] + row["canonical_solution"],
            timeout_seconds=cfg["evaluation"]["per_candidate_wall_timeout_s"],
            memory_mb=cfg["evaluation"]["candidate_memory_mb"],
            seed=1729,
            exact_types=True,
        )
    )


def validation_key(task: dict, definition: dict, cfg: dict) -> str:
    return digest([task, definition, variant_row(task, definition), cfg["evaluation"]])


def validate() -> None:
    cfg, tasks, _ = source()
    VALIDATION.mkdir(parents=True, exist_ok=True)
    previous = by_key(ROOT / "results/utilisation/m1-full-validation/references.jsonl")
    reference_results = []
    for tid in TASK_IDS:
        task = tasks[tid]
        code = task["prompt"] + task["canonical_solution"]
        key = digest([[tid], tid, code, cfg["evaluation"]])
        prior = previous.get(key)
        parts = (
            prior["partitions"] if prior else score_function(task, code, cfg["evaluation"], 1729)
        )
        reference_results.append(
            {
                "task": tid,
                "passed": all(p["status"] == "passed" for p in parts.values()),
                "reused_exact_reference_check": bool(prior),
            }
        )
    save(VALIDATION / "target-references.json", reference_results)
    if not all(r["passed"] for r in reference_results):
        raise ValueError("Target reference validation failed")
    path = VALIDATION / "alternatives.jsonl"
    done = by_key(path)
    definitions = alternative_catalog()
    if set(definitions) != set(TASK_IDS):
        raise ValueError("Alternative catalogue does not match original roster")
    for tid in ordered_roster("R2"):
        task, definition = tasks[tid], definitions[tid]
        key = validation_key(task, definition, cfg)
        if key in done:
            continue
        target = witness_check(task, definition, modified=False, cfg=cfg)
        modified = witness_check(task, definition, modified=True, cfg=cfg)
        variant = variant_row(task, definition)
        parts = (
            score_function(
                variant, variant["prompt"] + variant["canonical_solution"], cfg["evaluation"], 1729
            )
            if target["status"] == modified["status"] == "passed"
            else {}
        )
        result = {
            "key": key,
            "task": tid,
            "target_witnesses": target,
            "alternative_witnesses": modified,
            "expanded_partitions": parts,
            "specification": specification(task, definition["description"], background=True),
            "witnesses": definition["witnesses"],
            "passed": target["status"] == modified["status"] == "passed"
            and bool(parts)
            and all(p["status"] == "passed" for p in parts.values()),
        }
        append_json(path, result)
        print(
            json.dumps(
                {
                    "validation_task": tid,
                    "passed": result["passed"],
                    "checks_completed": len(by_key(path)),
                }
            ),
            flush=True,
        )


def description_only(task: dict) -> str:
    node = next(n for n in ast.parse(task["prompt"]).body if isinstance(n, ast.FunctionDef))
    doc = ast.get_docstring(node) or ""
    doc = re.split(
        r">>>|(?i:examples?|for example|\[input/output\]|it must be implemented)", doc, maxsplit=1
    )[0]
    return specification(task, doc.strip(), background=False)


def matched_filler(blocks: list[str], tokens: int, tokenizer: Tokenizer) -> str:
    def count(s: str) -> int:
        return len(tokenizer.encode(s).ids)

    text = "[BACKGROUND SPECIFICATIONS; DO NOT IMPLEMENT]\n"
    index = 0
    while count(text + blocks[index % len(blocks)] + "\n") < tokens - 8:
        text += blocks[index % len(blocks)] + "\n"
        index += 1
    if index == 0:
        raise ValueError("Complete distractor does not fit filler budget")
    text += "[NEUTRAL PADDING]"
    for _ in range(8):
        missing = tokens - count(text)
        if missing == 0:
            return text
        if missing < 0:
            raise ValueError("Filler overshot without truncation")
        text += " x" * missing
    raise ValueError("Unable to match exact filler token budget")


def prepare_r2() -> None:
    cfg, tasks, tokenizer = source()
    definitions = alternative_catalog()
    checks = by_key(VALIDATION / "alternatives.jsonl")
    checked = [
        checks[key]
        for tid in TASK_IDS
        if (key := validation_key(tasks[tid], definitions[tid], cfg)) in checks
    ]
    valid = {r["task"] for r in checked if r["passed"]}
    if {r["task"] for r in checked} != set(TASK_IDS):
        raise ValueError("All 40 construction audits must finish before exclusion decisions")
    roster = [t for t in ordered_roster("R2") if t in valid]
    if not roster:
        raise ValueError("No validated semantic alternatives")
    exclusions = [r for r in checked if not r["passed"]]
    save(BASE / "R2/material-exclusions.json", exclusions)
    save(
        BASE / "R2/alternatives.json",
        {
            t: {"definition": definitions[t], "row": variant_row(tasks[t], definitions[t])}
            for t in roster
        },
    )
    items, models = [], [m["tag"] for m in cfg["models"]]
    full_order = ordered_roster("R2")
    for tid in roster:
        task = tasks[tid]
        entry = task["entry_point"]
        target = "[TARGET SPECIFICATION]\n" + task["prompt"]
        instruction = (
            f"Implement only the TARGET function {entry}. "
            "Background specifications are distractors; do not implement them. "
            "Return only Python code.\n"
        )
        query = f"\n[CURRENT QUERY]\nComplete only {entry} from the TARGET specification."
        items.append(
            build_item(
                "R2",
                "isolated",
                tid,
                entry,
                instruction + target + query,
                tokenizer,
                models,
                isolation=True,
            )
        )
        i = full_order.index(tid)
        others = (full_order[i + 1 :] + full_order[:i])[:8]
        types = {
            "irrelevant": [
                (
                    "A neutral notebook records ordinary observations "
                    "about weather, furniture and walking routes. No "
                    "programming requirement is stated here.\n"
                )
            ],
            "related": [description_only(tasks[t]) for t in others],
            "near_duplicate": [
                specification(task, definitions[tid]["description"], background=True)
            ],
        }
        for length in (1000, 2000):
            for kind, blocks in types.items():
                filler = matched_filler(blocks, length, tokenizer)
                for position in ("beginning", "end"):
                    text = (
                        instruction
                        + (
                            target + "\n" + filler
                            if position == "beginning"
                            else filler + "\n" + target
                        )
                        + query
                    )
                    items.append(
                        build_item(
                            "R2",
                            f"{kind}_{length}_{position}",
                            tid,
                            entry,
                            text,
                            tokenizer,
                            models,
                            isolation=False,
                            filler_tokens=length,
                            similarity=kind,
                            target_position=position,
                            distractor_ids=[tid + "/semantic-alternative"]
                            if kind == "near_duplicate"
                            else others
                            if kind == "related"
                            else [],
                        )
                    )
    freeze_stage("R2", roster, items, cfg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["E5", "validate", "R2"])
    args = parser.parse_args()
    {"E5": prepare_e5, "validate": validate, "R2": prepare_r2}[args.action]()
