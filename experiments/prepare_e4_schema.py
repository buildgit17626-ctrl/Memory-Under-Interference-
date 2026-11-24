"""Prepare a new approved E4 scope; never overwrite the failed pilot or v4 hashes."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.prepare_continuation import save, source
from experiments.prepare_remaining import configuration as old_configuration
from experiments.utilisation_pilot import template
from prompt_energy.e4_schema import SCHEMA, SETUP
from prompt_energy.remaining_materials import common_prefix, keyed
from prompt_energy.utilisation_plan import ROOT, digest, schedule

BASE = ROOT / "studies/utilisation/e4-schema-v5"
OUTPUT = ROOT / "results/utilisation/e4-schema-v5"


def configuration(phase: str) -> tuple[dict, str]:
    data = (BASE / phase / "config.yaml").read_bytes().replace(b"\r\n", b"\n")
    return yaml.safe_load(data), hashlib.sha256(data).hexdigest()


def jobs_for(phase: str, cfg: dict, checksum: str) -> list[dict]:
    _, _, tokenizer = source()
    stimuli = json.loads((BASE / phase / "stimuli.json").read_text())
    primes = json.loads((BASE / "priming.json").read_text())
    jobs = schedule(stimuli, cfg, checksum)
    final = []
    for job in jobs:
        request = job["request"]
        raw_prompt = template(request["prompt"])
        prime = template(primes[str(job["identity"]["prefix_tokens"])])
        if tokenizer.encode(SETUP).ids[0] in {
            tokenizer.encode(raw_prompt).ids[0],
            tokenizer.encode(prime).ids[0],
        }:
            raise ValueError("Schema setup must not share the measured prompt's first token")
        request.pop("system")
        request.update(prompt=raw_prompt, raw=True, format=SCHEMA)
        job.update(
            prime_prompt=prime,
            schema_setup_prompt=SETUP,
            shared_prefix_tokens=common_prefix(
                tokenizer.encode(raw_prompt).ids, tokenizer.encode(prime).ids
            ),
        )
        final.append(keyed(job))
    return final


def prepare() -> None:
    _, _, tokenizer = source()
    items, primes = [], {}
    for length in (0, 500, 1000, 2000, 4000):
        prefix = " archive" * length
        if len(tokenizer.encode(prefix).ids) != length:
            raise ValueError("Literal prefix token count changed")
        shared = "[ARCHIVE; IGNORE ITS CONTENT]\n" + prefix + "\n[CURRENT REQUEST]\n"
        text = shared + (
            "Output a JSON array containing exactly 1000 integers. "
            "Return only the array, with no explanation or code fences."
        )
        primes[str(length)] = shared + "Output a JSON array containing exactly 1000 zeros."
        for state in ("cold", "warm"):
            items.append(
                {
                    "experiment": "E4",
                    "condition": state,
                    "task_id": f"prefix/{length}",
                    "entries": ["probe"],
                    "sections": {"prefix": [], "task": [text]},
                    "layout": ["task"],
                    "identity": {
                        "task_ids": [f"prefix/{length}"],
                        "prefix_tokens": length,
                        "workload": "schema_constrained_integer_array",
                    },
                    "prompt_tokens": dict.fromkeys(
                        ["qwen2.5-coder:0.5b", "qwen2.5-coder:1.5b"],
                        len(tokenizer.encode(template(text)).ids),
                    ),
                }
            )
    save(BASE / "priming.json", primes)
    save(BASE / "schema.json", SCHEMA)
    save(BASE / "schema-setup.json", {"prompt": SETUP, "output_budget": 1, "both_conditions": True})
    for phase in ("pilot", "full"):
        cfg, _ = old_configuration("E4", phase)
        folder = BASE / phase
        cfg["scope"].update(
            current_experiment="E4_schema_v5",
            current_stage=phase,
            workload_amendment="2026-11-24_owner_approved",
        )
        cfg["paths"].update(
            config=(folder / "config.yaml").relative_to(ROOT).as_posix(),
            preregistrations=(folder / "prereg").relative_to(ROOT).as_posix(),
        )
        save(folder / "config.yaml", cfg, yaml_text=True)
        selected = json.loads(json.dumps(items))
        for item in selected:
            item["identity"].update(
                pilot=phase == "pilot", include_in_main_analysis=phase == "full"
            )
        save(folder / "stimuli.json", selected)
        cfg, checksum = configuration(phase)
        jobs = jobs_for(phase, cfg, checksum)
        save(
            folder / "prereg/E4.json",
            {
                "date": "2026-11-24",
                "hypotheses": (
                    "Unchanged owner E4 question: prefix reuse may change latency and CPU energy."
                ),
                "competing_predictions": (
                    "No savings; overhead; opposite effects; unchanged causal limits."
                ),
                "conditions": ["cold", "warm"],
                "outcomes": (
                    "Resident request timings/tokens/cache count and qualified package energy."
                ),
                "analysis": (
                    "AMENDMENT.md; paired repeat differences and condition totals; pilot excluded."
                ),
                "exclusions": (
                    "No early-ending replacement, no missing-energy imputation, "
                    "no old pilot pooling."
                ),
                "interpretation_changers": (
                    "Cache mismatch, grammar setup/sampling cost, drift, workload failures."
                ),
                "inference_boundary": (
                    "Two CPU models and one schema-constrained synthetic probe on one laptop."
                ),
                "config_hash": checksum,
                "stimuli_hash": hashlib.sha256((folder / "stimuli.json").read_bytes()).hexdigest(),
                "schedule_hash": digest(jobs),
                "call_count": len(jobs),
                "retains_output_budget": 64,
                "schema_setup_in_both_arms": True,
            },
        )
        print(
            json.dumps(
                {
                    "phase": phase,
                    "calls": len(jobs),
                    "max_input": max(j["expected_tokens"] for j in jobs),
                }
            )
        )


def manifest() -> None:
    paths = sorted(p for p in BASE.rglob("*") if p.is_file() and p.name != "execution.sha256")
    paths += [
        ROOT / p
        for p in (
            "experiments/prepare_e4_schema.py",
            "experiments/run_e4_schema.py",
            "experiments/watch_e4_schema.py",
            "src/prompt_energy/e4_schema.py",
            "src/prompt_energy/e4_schema_worker.py",
            "tests/test_e4_schema.py",
            "studies/utilisation/remaining-v4/execution.sha256",
        )
    ]
    blob = "".join(
        hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        + "  "
        + p.relative_to(ROOT).as_posix()
        + "\n"
        for p in paths
    )
    path = BASE / "execution.sha256"
    if path.exists() and path.read_text() != blob:
        raise ValueError("Frozen v5 manifest changed")
    path.write_text(blob, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {"manifest_entries": len(paths), "sha256": hashlib.sha256(blob.encode()).hexdigest()}
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "manifest"])
    action = parser.parse_args().action
    if action == "prepare":
        subprocess.run([sys.executable, "-m", "experiments.run_remaining", "check"], check=True)
        prepare()
    else:
        manifest()
