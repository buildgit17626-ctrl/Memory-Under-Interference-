"""Owner-approved full M1 queue, bounded by availability, never outcome."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.prepare_full_m1 import BASE, configuration
from experiments.supervise_v2 import verify_v2_artifacts
from prompt_energy.ollama import Client, decode_response, utc_now
from prompt_energy.records import directory_lock
from prompt_energy.timed_queue import timed_queue
from prompt_energy.utilisation_freeze import verify_registration
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import ROOT, digest, schedule


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "recover", "monitor"])
    parser.add_argument("--hwinfo-log", type=Path)
    args = parser.parse_args()
    root = ROOT / "results/utilisation/m1-full"
    if args.action == "monitor":
        from prompt_energy.utilisation_run import by_key

        print(json.dumps({"completed": len(by_key(root / "calls.jsonl")), "planned": 1040}))
        return
    verify_v2_artifacts()
    path = "studies/utilisation/full-m1/execution.sha256"
    committed = subprocess.check_output(["git", "show", "HEAD:" + path], cwd=ROOT)
    if (ROOT / path).read_bytes().replace(b"\r\n", b"\n") != committed:
        raise ValueError("Uncommitted execution manifest")
    for line in committed.decode().splitlines():
        sha, name = line.split("  ", 1)
        if hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() != sha:
            raise ValueError("Execution artifact changed: " + name)
    cfg, sha = configuration()
    items = json.loads((BASE / "stimuli.json").read_text())
    jobs = schedule(items, cfg, sha)
    registration = verify_registration(jobs, BASE / "stimuli.json", cfg)
    review = json.loads((BASE / "owner-review.json").read_text())
    if (
        not review.get("owner_approved")
        or review.get("schedule_hash") != digest(jobs)
        or len(jobs) != 1040
    ):
        raise ValueError("Full M1 approval mismatch")
    validation = json.loads(
        (ROOT / "results/utilisation/m1-full-validation/report.json").read_text()
    )
    if (
        validation["failed_keys"]
        or validation["checks"] != 640
        or validation["stimuli_hash"] != digest(items)
    ):
        raise ValueError("Full M1 references not validated")
    if args.action == "check":
        print("Verified:1040 calls; 640 reference checks; 7.5h availability; no model calls.")
        return
    if args.hwinfo_log is None:
        parser.error("--hwinfo-log required")
    root.mkdir(parents=True, exist_ok=True)
    try:
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            client = Client()
            version = decode_response(client.exchange("/api/version"))["version"]
            tags = decode_response(client.exchange("/api/tags"))["models"]
            for model in cfg["models"]:
                if not any(
                    t["name"] == model["tag"] and t["digest"] == model["expected_digest"]
                    for t in tags
                ):
                    raise ValueError("Model digest mismatch")
            append_json(
                root / "sessions.jsonl",
                {
                    "started_at": utc_now(),
                    "ollama_version": version,
                    "hwinfo_log": str(args.hwinfo_log),
                    "registration": registration,
                },
            )
            result = timed_queue(root, jobs, client, args.hwinfo_log, hours=review["hours"])
            print(json.dumps(result, indent=2), flush=True)
    except (RuntimeError, ValueError, OSError) as exc:
        (root / "CHECKPOINT.md").write_text(
            "# Timed M1 stopped\n\n" + str(exc) + "\n", encoding="utf-8"
        )
        print("STOP: " + str(exc), flush=True)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
