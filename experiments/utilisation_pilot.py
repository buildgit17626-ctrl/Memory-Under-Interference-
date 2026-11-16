"""Prepare, run or report the separately labelled 22-call pilot."""

import argparse
import hashlib
import json
from pathlib import Path

from tokenizers import Tokenizer

from experiments.config import TASK_IDS
from prompt_energy.hwinfo import LogFormat
from prompt_energy.ollama import Client, decode_response
from prompt_energy.records import directory_lock, write_once
from prompt_energy.tasks import load_tasks
from prompt_energy.utilisation_plan import ROOT, digest, load_config, schedule
from prompt_energy.utilisation_run import Sensor, by_key, run

VALIDATION = ROOT / "results/utilisation/validation"


def template(prompt: str) -> str:
    return (
        "<|im_start|>system\nYou are a helpful coding assistant.<|im_end|>\n"
        "<|im_start|>user\n" + prompt + "<|im_end|>\n<|im_start|>assistant\n"
    )


def make_jobs() -> tuple[list, dict]:
    cfg, checksum = load_config()
    tokenizer_path = VALIDATION / "tokenizer.json"
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    tasks = load_tasks(TASK_IDS[:5])
    items = []
    models = [m["tag"] for m in cfg["models"]]
    for task in tasks:
        for arm in ("P1", "P3_1"):
            items.append(
                {
                    "experiment": "E0",
                    "condition": arm,
                    "task_id": task.task_id,
                    "task": task.prompt,
                    "entries": [task.entry_point],
                    "prompt_tokens": dict.fromkeys(models, 1),
                }
            )
    # Use the approved scheduler, then select the first sampled seed only.
    jobs = [j for j in schedule(items, cfg, checksum) if j["sample_idx"] == 0]
    for j in jobs:
        text = template(j["request"]["prompt"])
        j["request"].pop("system")
        j["request"].update(prompt=text, raw=True)
        j["expected_tokens"] = len(tokenizer.encode(text).ids)
        j["identity"]["pilot"] = True
        j["key"] = digest({k: v for k, v in j.items() if k != "key"})
    import random

    base = jobs[0]
    for model in cfg["models"]:
        probe = json.loads(json.dumps(base))
        probe.update(
            model=model["tag"],
            model_digest=model["expected_digest"],
            experiment="context_probe",
            condition="4000_input_tokens",
            identity={"pilot": True, "diagnostic": True},
        )
        probe["request"]["model"] = model["tag"]
        plain = 'Complete this function. Return only code.\ndef identity(x):\n    """Return x."""'
        text = template(plain)
        # A repeated word has a stable token increment; assert exact final length.
        n = 4000 - len(tokenizer.encode(text).ids)
        text = template((" padding" * n) + "\n" + plain)
        count = len(tokenizer.encode(text).ids)
        text = template((" padding" * (n + 4000 - count)) + "\n" + plain)
        assert len(tokenizer.encode(text).ids) == 4000
        probe["request"]["prompt"] = text
        probe["expected_tokens"] = 4000
        probe["task_id"], probe["entries"] = "diagnostic/identity", ["identity"]
        probe["key"] = digest({k: v for k, v in probe.items() if k != "key"})
        jobs.append(probe)
    random.Random(cfg["seeds"]["order"]).shuffle(jobs)
    assert len(jobs) == 22 and len({j["key"] for j in jobs}) == 22
    metadata = {
        "requests": 22,
        "benchmark_calls": 20,
        "long_probes": 2,
        "schedule_sha256": digest(jobs),
        "config_sha256": checksum,
        "tokenizer_sha256": hashlib.sha256(tokenizer_path.read_bytes()).hexdigest(),
        "task_ids": list(TASK_IDS[:5]),
        "pilot_excluded_from_analysis": True,
    }
    return jobs, metadata


def report(root: Path) -> None:
    rows = list(by_key(root / "calls.jsonl").values())
    cfg, _ = load_config()
    for model in cfg["models"]:
        for subset in ("E0", "context_probe"):
            group = [r for r in rows if r["model"] == model["tag"] and r["experiment"] == subset]
            data = []
            for r in group:
                post = r["energy"]["windows"].get("post_load", {})
                data.append(
                    {
                        "key": r["key"],
                        "seconds": r["wall_seconds"],
                        "input_tokens": r["prompt_tokens"],
                        "output_tokens": r["output_tokens"],
                        "prefill_seconds": r["prefill_ns"] / 1e9 if r["prefill_ns"] else None,
                        "decode_seconds": r["decode_ns"] / 1e9 if r["decode_ns"] else None,
                        "tokens_s": r["output_tokens"] / (r["decode_ns"] / 1e9)
                        if r["decode_ns"]
                        else None,
                        "energy_valid": post.get("raw_wh") is not None,
                        "flags": r["flags"] + r["energy"]["flags"],
                    }
                )
            print(
                json.dumps(
                    {
                        "model": model["tag"],
                        "subset": subset,
                        "denominator": len(group),
                        "rows": data,
                    }
                )
            )
    print(json.dumps({"expected": 22, "recorded": len(rows)}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run", "report"])
    parser.add_argument("--session", type=Path, default=ROOT / "results/utilisation/pilot")
    parser.add_argument("--hwinfo-log", type=Path)
    args = parser.parse_args()
    if args.action == "report":
        report(args.session)
        return
    jobs, meta = make_jobs()
    args.session.mkdir(parents=True, exist_ok=True)
    for name, value in (("pilot-registration.json", meta), ("pilot-jobs.json", jobs)):
        p = args.session / name
        if p.exists():
            if json.loads(p.read_text()) != value:
                raise ValueError("Pilot registration changed")
        else:
            write_once(p, value)
    print(json.dumps(meta, indent=2))
    if args.action == "run":
        if not args.hwinfo_log:
            parser.error("A live --hwinfo-log is required")
        client = Client()
        actual = decode_response(client.exchange("/api/tags"))["models"]
        cfg, _ = load_config()
        for model in cfg["models"]:
            if not any(
                m["name"] == model["tag"] and m["digest"] == model["expected_digest"]
                for m in actual
            ):
                raise ValueError("Model digest mismatch")
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            sensor = Sensor(args.hwinfo_log, args.session, LogFormat(encoding="cp1252"))
            run(args.session, jobs, client, sensor, cfg["energy"]["inter_request_gap_s"])


if __name__ == "__main__":
    main()
