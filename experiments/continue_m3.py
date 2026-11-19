"""Terminal-only continuation of the reviewed M3 first-100 checkpoint."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.supervise import load_jobs
from experiments.supervise_v2 import verify_v2_artifacts
from prompt_energy.ollama import Client, decode_response
from prompt_energy.records import directory_lock
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_m3_continue import continue_m3, validate_review
from prompt_energy.utilisation_order_v2 import select_m3
from prompt_energy.utilisation_outcome_access import require_outcome_access
from prompt_energy.utilisation_plan import ROOT, load_config


def verify_continuation() -> None:
    manifest = "studies/utilisation/prereg/M3-CONTINUE-2026-11-19.sha256"
    committed = subprocess.check_output(["git", "show", "HEAD:" + manifest], cwd=ROOT)
    if (ROOT / manifest).read_bytes().replace(b"\r\n", b"\n") != committed:
        raise ValueError("Continuation manifest is not committed")
    for line in committed.decode().splitlines():
        expected, name = line.split("  ", 1)
        if (
            hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            != expected
        ):
            raise ValueError("Continuation artifact changed: " + name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "recover"])
    parser.add_argument("--hwinfo-log", type=Path, required=True)
    args = parser.parse_args()
    verify_v2_artifacts()
    verify_continuation()
    root = ROOT / "results/utilisation/supervised"
    cfg, sha = load_config()
    pipeline = json.loads((ROOT / "studies/utilisation/pipeline.json").read_text())
    labels = json.loads((root / "analysis/heldout-labels.json").read_text())
    order = json.loads((ROOT / cfg["scope"]["task_orders"]).read_text())["sweeps"]["M3"][
        "task_order"
    ]
    jobs = select_m3(load_jobs(pipeline["m3_stimuli"], cfg, sha), labels, order, cfg["models"])
    review = json.loads((ROOT / "studies/utilisation/m3-continuation-review.json").read_text())
    require_outcome_access(root / "M3")
    validate_review(root, jobs, review)
    if args.action == "check":
        print("Continuation verified: original 240-call M3 schedule; no requests made.")
        return
    try:
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            client = Client()
            tags = decode_response(client.exchange("/api/tags"))["models"]
            for model in cfg["models"]:
                if not any(
                    m["name"] == model["tag"] and m["digest"] == model["expected_digest"]
                    for m in tags
                ):
                    raise ValueError("Model digest mismatch")
            result = continue_m3(root, jobs, review, client, args.hwinfo_log)
            reason = "STOP: Focused M3 complete; scoring and later stages deferred"
    except (RuntimeError, ValueError, OSError) as exc:
        result = {
            "error_type": type(exc).__name__,
            "error": str(exc),
            "details": getattr(exc, "details", {}),
        }
        reason = "STOP: " + str(exc)
    # Preserve the original checkpoint hash which released the first-100 gate.
    record = {"reason": reason, "hwinfo_log": str(args.hwinfo_log), **result}
    append_json(root / "m3-continuation.jsonl", record)
    (root / "M3-CONTINUATION.md").write_text(
        "# M3 continuation checkpoint\n\n"
        + reason
        + "\n\n```json\n"
        + json.dumps(record, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )
    print(reason, flush=True)
    if "error" in result:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
