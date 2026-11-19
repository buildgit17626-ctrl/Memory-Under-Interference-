"""Reviewed diagnostic M1 only: sequential generation, then offline scoring."""

import argparse
import hashlib
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.supervise_v2 import verify_v2_artifacts
from prompt_energy.hwinfo import LogFormat
from prompt_energy.ollama import Client, decode_response, utc_now
from prompt_energy.records import directory_lock
from prompt_energy.utilisation_eval import evaluate, load_dataset
from prompt_energy.utilisation_freeze import verify_registration
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import ROOT, digest, load_config, schedule
from prompt_energy.utilisation_reliability import SettledSensor, generate_short_block
from prompt_energy.utilisation_run import by_key


def require_material_review(jobs: list, review: dict) -> None:
    if review.get("owner_approved") is not True or review.get("schedule_hash") != digest(jobs):
        raise ValueError("Exact M1 materials await owner approval")
    if len(jobs) != 70 or any(not j["identity"].get("pilot") for j in jobs):
        raise ValueError("Require the approved diagnostic 70-call schedule")


def pilot_generation(
    root, jobs, client, log, *, generator=generate_short_block, sensor=SettledSensor
):
    """No following stage until every scheduled logical call has been saved."""
    keys = {j["key"] for j in jobs}
    saved = by_key(root / "calls.jsonl")
    if not set(saved) <= keys:
        raise ValueError("Foreign call in pilot journal")
    while len(saved) < len(jobs):
        generator(
            root,
            jobs,
            client,
            sensor(log, root, LogFormat(encoding="cp1252")),
            5,
            limit=min(25, len(jobs) - len(saved)),
        )
        updated = by_key(root / "calls.jsonl")
        if len(updated) <= len(saved) or not set(updated) <= keys:
            raise RuntimeError("No progress or foreign call in pilot")
        saved = updated


def report(root: Path) -> dict:
    calls, scores = by_key(root / "calls.jsonl"), by_key(root / "scores.jsonl")
    groups = defaultdict(list)
    for key, call in calls.items():
        groups[(call["model"], call["condition"])].append((call, scores.get(key)))
    summary = []
    for (model, condition), rows in sorted(groups.items()):
        target_pass = 0
        for call, score in rows:
            target = (score or {}).get("functions", {}).get(call["task_id"], {})
            target_pass += bool(target) and all(x["status"] == "passed" for x in target.values())
        summary.append(
            {
                "model": model,
                "condition": condition,
                "calls": len(rows),
                "scored": sum(s is not None for _, s in rows),
                "target_passed": target_pass,
                "all_requested_functions_passed": sum(
                    (s or {}).get("status") == "passed" for _, s in rows
                ),
                "mean_wall_seconds": statistics.mean(c["wall_seconds"] for c, _ in rows),
                "mean_output_tokens": statistics.mean(
                    c["output_tokens"] for c, _ in rows if c.get("output_tokens") is not None
                )
                if any(c.get("output_tokens") is not None for c, _ in rows)
                else None,
                "input_invalid": sum(not c["input_valid"] for c, _ in rows),
                "output_caps": sum("output_cap" in c["flags"] for c, _ in rows),
                "energy_available": sum(bool(c["energy_valid"]) for c, _ in rows),
            }
        )
    return {
        "diagnostic_only": True,
        "include_in_hypothesis_tests": False,
        "calls": len(calls),
        "scores": len(scores),
        "by_model_condition": summary,
        "interpretation": "No treatment-effect conclusions from this pilot",
        "timing_limit": (
            "Mean request time excludes baselines, sensor processing, gaps, retries and scoring"
        ),
    }


def verify_pilot_manifest(root: Path = ROOT) -> None:
    """Respect Git binary artifact bytes and source LF canonicalisation."""
    import subprocess

    manifest = "studies/utilisation/prereg/M1-PILOT-2026-11-20.sha256"
    committed = subprocess.check_output(["git", "show", "HEAD:" + manifest], cwd=root)
    if (root / manifest).read_bytes().replace(b"\r\n", b"\n") != committed:
        raise ValueError("Pilot manifest changed")
    for line in committed.decode().splitlines():
        expected, name = line.split("  ", 1)
        raw = (root / name).read_bytes()
        canonical = raw if name.startswith("artifacts/") else raw.replace(b"\r\n", b"\n")
        if hashlib.sha256(canonical).hexdigest() != expected:
            raise ValueError("Pilot artifact changed: " + name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "recover", "report"])
    parser.add_argument("--hwinfo-log", type=Path)
    args = parser.parse_args()
    verify_v2_artifacts()
    # The committed pilot manifest covers all new executable/material files.
    from experiments.continue_m3 import verify_continuation

    verify_continuation()
    verify_pilot_manifest()
    cfg, sha = load_config()
    stimulus = ROOT / "studies/utilisation/stimuli/M1-pilot.json"
    jobs = schedule(json.loads(stimulus.read_text()), cfg, sha)
    registration = verify_registration(jobs, stimulus, cfg)
    review = json.loads((ROOT / "studies/utilisation/m1-pilot-review.json").read_text())
    require_material_review(jobs, review)
    validation = json.loads(
        (ROOT / "results/utilisation/m1-pilot-validation/report.json").read_text()
    )
    if (
        validation.get("failed_keys")
        or validation.get("checks") != 35
        or validation.get("passed") != 35
        or validation.get("stimuli_hash") != digest(json.loads(stimulus.read_text()))
    ):
        raise ValueError("New M1 reference bundles have not passed the matching validation")
    root = ROOT / "results/utilisation/m1-pilot"
    if args.action == "check":
        print("M1 pilot verified:70 calls maximum; no generation requested.")
        return
    if args.action == "report":
        print(json.dumps(report(root), indent=2))
        return
    if args.hwinfo_log is None:
        parser.error("--hwinfo-log required")
    root.mkdir(parents=True, exist_ok=True)
    try:
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            client = Client()
            runtime_version = decode_response(client.exchange("/api/version"))["version"]
            tags = decode_response(client.exchange("/api/tags"))["models"]
            for model in cfg["models"]:
                if not any(
                    m["name"] == model["tag"] and m["digest"] == model["expected_digest"]
                    for m in tags
                ):
                    raise ValueError("Model digest mismatch")
            append_json(
                root / "sessions.jsonl",
                {
                    "started_at": utc_now(),
                    "ollama_version": runtime_version,
                    "hwinfo_log": str(args.hwinfo_log),
                    "registration": registration,
                    "schedule_hash": digest(jobs),
                    "diagnostic_pilot": True,
                },
            )
            pilot_generation(root, jobs, client, args.hwinfo_log)
            print("Pilot generation complete; beginning separate sandbox evaluation.", flush=True)
            tasks = load_dataset(
                ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz",
                cfg["benchmark"]["dataset_sha256"],
            )
            evaluate(root, tasks, cfg)
            result = report(root)
            (root / "pilot-report.json").write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8"
            )
            print(json.dumps(result, indent=2), flush=True)
            print("STOP: diagnostic M1 pilot complete; no full run or next experiment started.")
    except (RuntimeError, ValueError, OSError) as exc:
        (root / "CHECKPOINT.md").write_text(
            "# M1 pilot stopped\n\n" + str(exc) + "\n", encoding="utf-8"
        )
        print("STOP: " + str(exc), flush=True)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
