"""Freeze the approved remaining M2/E4/E3 scopes without contacting a model."""

import argparse
import hashlib
import json
import random
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.config import TASK_IDS
from experiments.prepare_continuation import description_only, save, source
from experiments.utilisation_pilot import template
from prompt_energy.remaining_materials import (
    M2_ARMS,
    NEUTRAL,
    common_prefix,
    domain,
    e4_text,
    fixtures,
    heldout_row,
    keyed,
    m2_text,
    pad_to,
)
from prompt_energy.sandbox import run_solution
from prompt_energy.semantic_alternatives import alternative_catalog, specification
from prompt_energy.tasks import Task
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import ROOT, digest, schedule
from prompt_energy.utilisation_run import by_key

BASE = ROOT / "studies/utilisation/remaining-v4"
OUTPUT = ROOT / "results/utilisation/remaining-v4"
DATE = "2026-11-24"


def configuration(stage: str, phase: str) -> tuple[dict, str]:
    raw = (BASE / stage / phase / "config.yaml").read_bytes().replace(b"\r\n", b"\n")
    return yaml.safe_load(raw), hashlib.sha256(raw).hexdigest()


def roster(stage: str) -> list[str]:
    cfg, _, _ = source()
    orders = json.loads((ROOT / cfg["scope"]["task_orders"]).read_text())["sweeps"]
    if stage in orders:
        return [t for t in orders[stage]["task_order"] if t in TASK_IDS]
    items = list(TASK_IDS)
    random.Random(1729).shuffle(items)
    return items


def item(exp: str, condition: str, tid: str, entry: str, text: str, tokenizer, **identity) -> dict:
    sections = {"task": [text], "history": []}
    if exp == "E3":
        sections["feedback"] = []
    if exp == "E4":
        sections = {"prefix": [], "task": [text]}
    return {
        "experiment": exp,
        "condition": condition,
        "task_id": tid,
        "entries": [entry],
        "identity": {"task_ids": [tid], **identity},
        "sections": sections,
        "layout": ["task"],
        "prompt_tokens": dict.fromkeys(
            ["qwen2.5-coder:0.5b", "qwen2.5-coder:1.5b"],
            len(tokenizer.encode(template(text)).ids),
        ),
    }


def jobs_for(stage: str, phase: str, cfg: dict, checksum: str, tokenizer=None) -> list[dict]:
    stimuli = json.loads((BASE / stage / phase / "stimuli.json").read_text())
    jobs = schedule(stimuli, cfg, checksum)
    if stage != "E4":
        return jobs
    if tokenizer is None:
        _, _, tokenizer = source()
    primes = json.loads((BASE / "E4/priming.json").read_text())
    output = []
    for job in jobs:
        raw = template(job["request"]["prompt"])
        prime = template(primes[str(job["identity"]["prefix_tokens"])])
        job["request"].pop("system")
        job["request"].update(prompt=raw, raw=True)
        job["prime_prompt"] = prime
        job["shared_prefix_tokens"] = common_prefix(
            tokenizer.encode(raw).ids, tokenizer.encode(prime).ids
        )
        output.append(keyed(job))
    return output


def freeze(stage: str, phase: str, items: list[dict], task_ids: list[str]) -> None:
    original, _, tokenizer = source()
    folder = BASE / stage / phase
    cfg = json.loads(json.dumps(original))
    cfg["experiments"][stage] = {
        **cfg["experiments"][stage],
        "samples": 1,
        "temperature": 0.2 if stage == "E3" else 0,
        "num_ctx": 32768 if stage == "E3" else 16384,
        "num_predict": 64 if stage == "E4" else 2048,
        "keep_alive": -1 if stage == "E4" else 0,
        "http_deadline_s": 900,
        "repeats": 20 if stage == "E4" and phase == "full" else 1,
    }
    cfg["scope"].update(
        current_experiment=stage + "_v4",
        current_stage=phase,
        current_shared_task_count=len(task_ids),
        execution_deadline=None,
    )
    cfg["paths"].update(
        config=(folder / "config.yaml").relative_to(ROOT).as_posix(),
        preregistrations=(folder / "prereg").relative_to(ROOT).as_posix(),
    )
    save(folder / "config.yaml", cfg, yaml_text=True)
    for row in items:
        row["identity"].update(pilot=phase == "pilot", include_in_main_analysis=phase == "full")
    save(folder / "stimuli.json", items)
    cfg, checksum = configuration(stage, phase)
    jobs = jobs_for(stage, phase, cfg, checksum, tokenizer)
    hypothesis = {
        "M2": "Owner C1: competing task descriptions can reduce use of the original specification.",
        "E4": "Owner: prefix-cache reuse may change latency and CPU-package inference energy.",
        "E3": "Owner: repair feedback and retained history may change repair success and cost.",
    }[stage]
    save(
        folder / "prereg" / (stage + ".json"),
        {
            "date": DATE,
            "hypotheses": hypothesis,
            "competing_predictions": (
                "No improvement, reverse differences, or cost without benefit."
            ),
            "conditions": sorted({i["condition"] for i in items}),
            "outcomes": "See committed PROTOCOL.md; native timings/tokens, qualified CPU energy.",
            "analysis": (
                "PROTOCOL.md defines task/pair denominators, pilot exclusion and uncertainty."
            ),
            "exclusions": (
                "No outcome-based task replacement; missing energy never imputed; caps separate."
            ),
            "interpretation_changers": (
                "Reference/feedback errors; confounding; input mismatch; cache invalidity; "
                "censoring, incomplete data, baseline drift and low-resolution windows."
            ),
            "inference_boundary": "Two small Q4_K_M CPU models, fixed benchmark and one machine.",
            "config_hash": checksum,
            "stimuli_hash": hashlib.sha256((folder / "stimuli.json").read_bytes()).hexdigest(),
            "schedule_hash": digest(jobs),
            "call_count": len(jobs),
            "task_ids": task_ids,
            "E3_maximum_calls": 130 if stage == "E3" else None,
            "E3_dynamic_rounds": (
                "Round schedules follow committed deterministic algorithm; hash and raw parent "
                "provenance recorded before each round, never selected using final test results."
                if stage == "E3"
                else None
            ),
        },
    )
    print(
        json.dumps(
            {
                "stage": stage,
                "phase": phase,
                "initial_calls": len(jobs),
                "max_input": max(j["expected_tokens"] for j in jobs),
            }
        ),
        flush=True,
    )


def prepare_m2() -> None:
    _, tasks, tokenizer = source()
    ordered = roster("M2")

    def count(text: str) -> int:
        return len(tokenizer.encode(text).ids)

    definitions = alternative_catalog()
    items, audits = [], []
    for tid in ordered:
        target, entry = tasks[tid]["prompt"], tasks[tid]["entry_point"]
        others = [t for t in ordered if domain(t) != domain(tid)][:3]
        if len(others) != 3 or tid in others:
            raise ValueError("Unrelated-domain roster incomplete")
        similar = specification(tasks[tid], definitions[tid]["description"], background=True)
        distractors = [description_only(tasks[t]) for t in others]
        # Same three literal slots and acknowledgements; only their task-bearing content varies.
        slot_size = max(500, *(count(s) + 32 for s in [similar, *distractors]))
        neutral = pad_to(NEUTRAL, slot_size, count)
        arrangements = {
            "neutral": [neutral] * 3,
            "similar": [neutral, pad_to(similar, slot_size, count), neutral],
            "other_one": [neutral, pad_to(distractors[0], slot_size, count), neutral],
            "other_three": [pad_to(s, slot_size, count) for s in distractors],
        }
        texts = {arm: m2_text(target, entry, blocks) for arm, blocks in arrangements.items()}
        max_tokens = max(count(template(t)) for t in texts.values()) + 8
        # Equalize complete rendered inputs, not just isolated pieces.
        for arm in M2_ARMS:
            text = texts[arm]
            marker = "[RETURN TO ORIGINAL TARGET]"
            before, query = text.split(marker)
            for _ in range(12):
                missing = max_tokens - count(template(before + marker + query))
                if missing == 0:
                    break
                if missing < 0:
                    raise ValueError("Complete M2 input overshot")
                before += " x" * missing
            text = before + marker + query
            if count(template(text)) != max_tokens:
                raise ValueError("Could not match complete M2 input")
            items.append(
                item(
                    "M2",
                    arm,
                    tid,
                    entry,
                    text,
                    tokenizer,
                    isolation=False,
                    history_tasks=0 if arm == "neutral" else 3 if arm == "other_three" else 1,
                )
            )
        items.append(
            item(
                "M2", "isolated", tid, entry, m2_text(target, entry, []), tokenizer, isolation=True
            )
        )
        audits.append(
            {
                "task": tid,
                "target_domain": domain(tid),
                "other_tasks": others,
                "other_domains": [domain(t) for t in others],
                "similarity_reason": definitions[tid]["description"],
                "similarity_validation": (
                    "Same interface; validated computational requirement change."
                ),
                "unrelated_reason": (
                    "Different authored coarse domain; no numeric similarity claim."
                ),
                "full_input_tokens_all_four": max_tokens,
                "slot_tokens": slot_size,
            }
        )
    save(BASE / "M2/relationship-audit.json", audits)
    for phase, ids in (("pilot", ordered[:5]), ("full", ordered)):
        selected = json.loads(json.dumps([i for i in items if i["task_id"] in ids]))
        freeze("M2", phase, selected, ids)


def prepare_e4() -> None:
    _, _, tokenizer = source()
    items, primes = [], {}
    for length in (0, 500, 1000, 2000, 4000):
        probe, prime, _ = e4_text(length, tokenizer)
        primes[str(length)] = prime
        for state in ("cold", "warm"):
            items.append(
                item(
                    "E4", state, f"prefix/{length}", "probe", probe, tokenizer, prefix_tokens=length
                )
            )
    save(BASE / "E4/priming.json", primes)
    for phase in ("pilot", "full"):
        freeze("E4", phase, json.loads(json.dumps(items)), [])


def prepare_e3() -> None:
    _, tasks, tokenizer = source()
    ids = roster("E3")[:5]
    examples = fixtures()
    if set(ids) != set(examples):
        raise ValueError("Feedback examples do not match the seeded E3 five-task roster")
    heldout, removed = {}, {}
    items = []
    for tid in ids:
        heldout[tid], removed[tid] = heldout_row(tasks[tid], examples[tid])
        entry = tasks[tid]["entry_point"]
        text = (
            f"[TARGET]\n{tasks[tid]['prompt']}\n[QUERY]\n"
            f"Complete {entry}. Return only Python code.\n"
        )
        items.append(item("E3", "initial", tid, entry, text, tokenizer, round=0))
    save(BASE / "E3/feedback-examples.json", examples)
    save(BASE / "E3/heldout-tasks.json", heldout)
    save(BASE / "E3/feedback-exclusion-counts.json", removed)
    freeze("E3", "pilot", items, ids)


def validate_feedback() -> None:
    cfg, tasks, _ = source()
    path = OUTPUT / "validation/feedback.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    done = by_key(path)
    for tid, cases in fixtures().items():
        for i, case in enumerate(cases):
            key = digest([tid, tasks[tid], case, cfg["evaluation"]])
            if key in done:
                continue
            lines = (
                "def check(candidate):\n"
                f"    assert candidate(*{case['args']!r}) == {case['expected']}\n"
            )
            row = tasks[tid]
            task = Task(tid, row["prompt"], row["canonical_solution"], lines, row["entry_point"])
            result = run_solution(
                task,
                row["prompt"] + row["canonical_solution"],
                timeout_seconds=60,
                memory_mb=256,
                seed=1729,
                exact_types=True,
            )
            record = {"key": key, "task": tid, "example": i, **asdict(result)}
            append_json(path, record)
            print(json.dumps(record), flush=True)
    rows = list(by_key(path).values())
    if len(rows) != 10 or any(r["status"] != "passed" for r in rows):
        raise ValueError("Independent feedback/reference validation failed")
    save(BASE / "feedback-validation.json", rows)


def manifest() -> None:
    paths = sorted(p for p in BASE.rglob("*") if p.is_file() and p.name != "execution.sha256")
    paths += [
        ROOT / p
        for p in (
            "experiments/prepare_remaining.py",
            "experiments/run_remaining.py",
            "experiments/watch_remaining.py",
            "src/prompt_energy/remaining_materials.py",
            "src/prompt_energy/remaining_cache.py",
            "src/prompt_energy/remaining_cache_worker.py",
            "src/prompt_energy/remaining_repair.py",
            "tests/test_remaining.py",
            "studies/utilisation/continuation-v3/execution.sha256",
        )
    ]
    # Every imported library/experiment helper is frozen, including new modules
    # absent from the older manifest. This does not rewrite that manifest.
    paths = sorted(
        set(
            paths
            + list((ROOT / "src/prompt_energy").glob("*.py"))
            + list((ROOT / "experiments").glob("*.py"))
        )
    )
    blob = "".join(
        hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        + "  "
        + p.relative_to(ROOT).as_posix()
        + "\n"
        for p in paths
    )
    path = BASE / "execution.sha256"
    if path.exists() and path.read_text() != blob:
        raise ValueError("Frozen manifest differs; use a dated amendment, never overwrite")
    path.write_text(blob, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "manifest_entries": len(paths),
                "manifest_sha256": hashlib.sha256(blob.encode()).hexdigest(),
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "validate", "manifest"])
    action = parser.parse_args().action
    if action == "prepare":
        prepare_m2()
        prepare_e4()
        prepare_e3()
    elif action == "validate":
        subprocess.run([sys.executable, "-m", "experiments.run_continuation", "check"], check=True)
        validate_feedback()
    else:
        manifest()
