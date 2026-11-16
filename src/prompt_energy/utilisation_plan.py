"""Compile registered stimuli into model calls without contacting Ollama."""

import hashlib
import json
import random
from pathlib import Path

import yaml

from experiments.config import SYSTEM_PROMPT
from prompt_energy.prompts import build_prompt
from prompt_energy.tasks import Task

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "studies/utilisation/config.yaml"
# Each layout is an ordered list of named text sections. Placement, separators,
# turns and wording belong to the frozen stimulus, not a hidden default prompt.
SECTIONS = {
    "M1": {"tasks"},
    "M2": {"task", "history"},
    "M3": {"task", "filler"},
    "R1": {"task", "blocks"},
    "R2": {"task", "distractors"},
    "E3": {"task", "feedback", "history"},
    "E4": {"prefix", "task"},
    "E5": {"framing", "task"},
    "U1": {"hint", "task"},
    "U2": {"task", "options"},
    "U5": {"helper", "task"},
}


def digest(obj: object) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
    ).hexdigest()


def render(item: dict) -> str:
    exp = item["experiment"]
    if exp == "E0":
        if item["condition"] not in {"P1", "P3_1"}:
            raise ValueError("Unknown E0 arm")
        task = Task(item["task_id"], item["task"], "", "", item["entries"][0])
        return build_prompt(task, item["condition"])
    sections = item["sections"]
    if exp not in SECTIONS or set(sections) != SECTIONS[exp]:
        raise ValueError(f"Incorrect sections for {exp}")
    # Allow repeated section names for interspersed task/replay blocks.
    parts = {k: iter(v) for k, v in sections.items()}
    if any(not isinstance(v, list) for v in sections.values()):
        raise ValueError("Sections must contain lists of literal strings")
    try:
        prompt = "".join(next(parts[name]) for name in item["layout"])
    except (StopIteration, KeyError) as exc:
        raise ValueError("Layout exceeds supplied sections") from exc
    if any(list(rest) for rest in parts.values()):
        raise ValueError("Unused prompt sections")
    return prompt


def schedule(items: list[dict], config: dict, config_hash: str) -> list[dict]:
    jobs = {}
    identities = set()
    for item in items:
        exp = item["experiment"]
        opts = config["defaults"] | config["experiments"][exp]
        if "mode" in opts:
            raise ValueError(f"{exp} consumes offline records")
        entries = item["entries"]
        if exp != "U2" and (
            not entries
            or not all(e.isidentifier() for e in entries)
            or len(entries) != len(set(entries))
        ):
            raise ValueError("Unique entry points required")
        if exp == "M1" and (
            len(entries) not in {1, 2, 3, 4, 6}
            or len(item.get("identity", {}).get("task_ids", [])) != len(entries)
        ):
            raise ValueError("Bundle requires corresponding registered task_ids and entries")
        prompt = render(item)
        if exp == "M1":
            opts["num_predict"] = opts["num_predict_per_subtask"] * len(item["entries"])
        models = {m["tag"]: m for m in config["models"]}
        for model in item.get("models", list(models)):
            expected = item["prompt_tokens"][model]
            if type(expected) is not int or expected <= 0:
                raise ValueError("Independent rendered token count required")
            if expected + opts["num_predict"] > opts["num_ctx"]:
                raise ValueError("Input plus output reservation exceeds num_ctx")
            for repeat in range(opts.get("repeats", 1)):
                for sample in range(opts["samples"]):
                    seed = (
                        config["seeds"]["sampled_generation"][sample]
                        if opts["temperature"]
                        else config["seeds"]["structural_generation"]
                    )
                    request = {
                        "model": model,
                        "prompt": prompt,
                        "system": SYSTEM_PROMPT,
                        "stream": False,
                        "keep_alive": opts["keep_alive"],
                        "options": {k: opts[k] for k in ("temperature", "num_ctx", "num_predict")}
                        | {
                            "seed": seed,
                            "stop": opts["stop_sequences"],
                            "num_gpu": config["host"]["num_gpu"],
                            "num_thread": config["host"]["num_thread"],
                        },
                    }
                    job = {
                        "experiment": exp,
                        "condition": item["condition"],
                        "task_id": item["task_id"],
                        "entries": item["entries"],
                        "identity": item.get("identity", {}),
                        "config_hash": config_hash,
                        "model_digest": models[model]["expected_digest"],
                        "model": model,
                        "sample_idx": sample,
                        "repeat": repeat,
                        "seed": seed,
                        "expected_tokens": expected,
                        "request": request,
                        "timeout": opts["http_deadline_s"],
                    }
                    if exp == "E4":
                        if item["condition"] not in {"warm", "cold"}:
                            raise ValueError("E4 requires warm or cold")
                        job["prime_prefix"] = "".join(item["sections"]["prefix"])
                    design_id = digest(
                        [
                            exp,
                            item["condition"],
                            item["task_id"],
                            job["identity"],
                            model,
                            sample,
                            repeat,
                        ]
                    )
                    if design_id in identities:
                        raise ValueError("Duplicate design cell")
                    identities.add(design_id)
                    key = digest(job)
                    if key in jobs:
                        raise ValueError("Duplicate scheduled request")
                    jobs[key] = {"key": key, **job}
    ordered = [jobs[k] for k in sorted(jobs)]
    random.Random(config["seeds"]["order"]).shuffle(ordered)
    return ordered


def load_config() -> tuple[dict, str]:
    raw = CONFIG.read_bytes().replace(b"\r\n", b"\n")
    return yaml.safe_load(raw), hashlib.sha256(raw).hexdigest()
