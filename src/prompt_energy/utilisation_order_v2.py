"""Proposed revision: matched isolation before M3; no M3 scoring before checkpoint."""

import copy
import json
from pathlib import Path

from tokenizers import Tokenizer

from experiments.supervise import load_jobs, timing_checkpoint
from experiments.utilisation_pilot import template
from prompt_energy.hwinfo import LogFormat
from prompt_energy.utilisation_e0_analysis import analyse
from prompt_energy.utilisation_eval import evaluate, load_dataset
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import ROOT, digest
from prompt_energy.utilisation_run import Sensor, by_key
from prompt_energy.utilisation_supervisor import Halt, generate_batch

STAGES = (
    "E0",
    "E0_analysis_and_eligibility",
    "isolated_baselines_40",
    "M3_generation_only_100",
    "checkpoint",
)


def ordered_workflow(operations: dict) -> None:
    """Execute exactly the reviewed order; failed stages cannot fall through."""
    if set(operations) != set(STAGES):
        raise ValueError("Supply exactly the five registered operations")
    for stage in STAGES:
        operations[stage]()


def select_m3(jobs: list, labels: dict, orders: list, models: list) -> list:
    keep = set()
    for model in models:
        tag = model["tag"]
        selected = [tid for tid in orders if labels[tag].get(tid, {}).get("solvable")][:20]
        if len(selected) != 20:
            raise Halt("Fewer than 20 eligible tasks")
        keep.update((tag, tid) for tid in selected)
    subset = [j for j in jobs if (j["model"], j["task_id"]) in keep]
    if len(subset) != 240:
        raise Halt("Expected 240 loaded M3 requests")
    return subset


def baseline_catalogue(tasks: dict, m3: list, tokenizer: Tokenizer) -> list:
    """Remove filler and preserve exact target wrapper, options and system."""
    selected = {}
    for source in m3:
        pair = (source["model"], source["task_id"])
        if pair in selected:
            continue
        task = tasks[source["task_id"]]
        entry = task["entry_point"]
        prompt = (
            f"\n[TARGET TASK: complete only {entry}]\n{task['prompt']}\n[END TARGET]\n"
            + f"\nReturn only the Python code defining {entry}.\n"
        )
        job = copy.deepcopy(source)
        job["condition"] = "isolated_no_filler"
        job["identity"] = {"baseline_task_id": source["task_id"], "amendment": "order-v2"}
        job["request"]["prompt"] = prompt
        job["expected_tokens"] = len(tokenizer.encode(template(prompt)).ids)
        job["identity"]["context_length"] = job["expected_tokens"]
        job["key"] = digest({k: v for k, v in job.items() if k != "key"})
        selected[pair] = job
    jobs = [selected[k] for k in sorted(selected)]
    import random

    random.Random(1730).shuffle(jobs)
    return jobs


def require_review(path: Path, amendment_hash: str, block: str) -> dict:
    record = json.loads(path.read_text())
    if (
        record.get("amendment_sha256") != amendment_hash
        or record.get("order_approved") is not True
        or record.get("drift_block") != block
        or not record.get("energy_decision")
    ):
        raise Halt("Pending owner review of execution amendment and drift disposition")
    # Alternatives that change estimands need their own approved implementation.
    if record["energy_decision"] != "retain_registered_start_baseline_and_flag":
        raise Halt("Chosen energy alternative needs a separately versioned analysis amendment")
    return record


def execute_v2(
    root: Path,
    pipeline: dict,
    cfg: dict,
    sha: str,
    client,
    baseline_jobs: list,
    *,
    sensor_factory=Sensor,
    generator=generate_batch,
    scorer=evaluate,
    analysis=analyse,
    checkpoint_writer=None,
) -> None:
    from prompt_energy.utilisation_supervisor import validate_pipeline, write_checkpoint

    validate_pipeline(root, cfg, pipeline)
    if by_key(root / "M3/scores.jsonl"):
        raise Halt("M3 scores already exist; cannot enforce unexamined-outcome order")
    if by_key(root / "M3/calls.jsonl") and len(by_key(root / "M3-isolated/calls.jsonl")) < 40:
        raise Halt("Loaded M3 calls precede completed isolated baseline stage")
    e0 = load_jobs(pipeline["e0_stimuli"], cfg, sha)
    tasks = load_dataset(ROOT / pipeline["dataset"], cfg["benchmark"]["dataset_sha256"])
    all_m3 = load_jobs(pipeline["m3_stimuli"], cfg, sha)
    log = Path(cfg["_session_hwinfo_log"])
    state = {}

    def phase_event(stage):
        append_json(root / "order-v2.jsonl", {"stage": stage, "event": "start"})

    def e0_stage():
        phase_event("E0")
        folder = root / "E0"
        folder.mkdir(parents=True, exist_ok=True)
        scorer(folder, tasks, cfg)
        while len(by_key(folder / "calls.jsonl")) < len(e0):
            generator(
                folder, e0, client, sensor_factory(log, folder, LogFormat(encoding="cp1252")), 5
            )
            scorer(folder, tasks, cfg)

    def labels_stage():
        phase_event("E0_analysis_and_eligibility")
        analysis(root / "E0", root / "analysis", heldout_policy=pipeline["heldout_policy"])
        labels = json.loads((root / "analysis/heldout-labels.json").read_text())
        order = json.loads((ROOT / cfg["scope"]["task_orders"]).read_text())["sweeps"]["M3"][
            "task_order"
        ]
        state["m3"] = select_m3(all_m3, labels, order, cfg["models"])

    def baseline_stage():
        phase_event("isolated_baselines_40")
        pairs = {(j["model"], j["task_id"]) for j in state["m3"]}
        selected = [j for j in baseline_jobs if (j["model"], j["task_id"]) in pairs]
        if len(selected) != 40:
            raise Halt("Expected 40 fresh isolated baseline calls")
        folder = root / "M3-isolated"
        folder.mkdir(parents=True, exist_ok=True)
        if len(by_key(folder / "calls.jsonl")) < 40:
            generator(
                folder,
                selected,
                client,
                sensor_factory(log, folder, LogFormat(encoding="cp1252")),
                5,
                limit=40,
            )
        if len(by_key(folder / "calls.jsonl")) != 40:
            raise Halt("Isolated baseline stage incomplete")
        # Scoring either M3 condition is intentionally deferred.

    def loaded_stage():
        phase_event("M3_generation_only_100")
        folder = root / "M3"
        folder.mkdir(parents=True, exist_ok=True)
        if by_key(folder / "scores.jsonl"):
            raise Halt("M3 outcomes already scored; outcome-access restriction cannot be claimed")
        done = len(by_key(folder / "calls.jsonl"))
        if done > 100:
            raise Halt("Existing M3 calls exceed checkpoint budget")
        if done < 100:
            generator(
                folder,
                state["m3"],
                client,
                sensor_factory(log, folder, LogFormat(encoding="cp1252")),
                5,
                limit=100 - done,
            )
        if len(by_key(folder / "calls.jsonl")) != 100:
            raise Halt("M3 100-call stage incomplete")

    def stop_stage():
        phase_event("checkpoint")
        details = timing_checkpoint(root, e0, state["m3"], pipeline)
        details["isolated_baseline_calls"] = 40
        details["M3_scoring"] = "deferred"
        details["remaining_MAIN_call_budget"] = (
            4848 - len(by_key(root / "E0/calls.jsonl")) - 40 - 100
        )
        (checkpoint_writer or write_checkpoint)(
            root, "STOP: 40 isolated baselines and 100 M3 generations; scoring deferred", details
        )

    ordered_workflow(
        dict(
            zip(
                STAGES,
                [e0_stage, labels_stage, baseline_stage, loaded_stage, stop_stage],
                strict=True,
            )
        )
    )
