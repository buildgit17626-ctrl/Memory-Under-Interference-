"""Draft recovery entry point; pending review gates prevent model requests."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from prompt_energy.ollama import Client, decode_response
from prompt_energy.records import directory_lock
from prompt_energy.utilisation_order_v2 import execute_v2, require_review
from prompt_energy.utilisation_outcome_access import inspect_outputs
from prompt_energy.utilisation_plan import ROOT, load_config
from prompt_energy.utilisation_supervisor import Halt, write_checkpoint

AMENDMENT = ROOT / "studies/utilisation/prereg/M3-ORDER-AMENDMENT-2026-11-17.md"
REVIEW = ROOT / "studies/utilisation/order-v2-review.json"


def verify_v2_artifacts() -> None:
    manifest = ROOT / "studies/utilisation/prereg/M3-ORDER-V2-2026-11-17.sha256"
    rel = manifest.relative_to(ROOT).as_posix()
    committed = subprocess.check_output(["git", "show", "HEAD:" + rel], cwd=ROOT)
    if manifest.read_bytes().replace(b"\r\n", b"\n") != committed:
        raise ValueError("Version-2 hash manifest differs from committed registration")
    for line in committed.decode().splitlines():
        expected, name = line.split("  ", 1)
        raw = (ROOT / name).read_bytes()
        canonical = raw if name.startswith("artifacts/") else raw.replace(b"\r\n", b"\n")
        actual = hashlib.sha256(canonical).hexdigest()
        if actual != expected:
            raise ValueError("Version-2 artifact changed: " + name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["recover", "check", "inspect"])
    parser.add_argument("--review", type=Path, default=REVIEW)
    parser.add_argument(
        "--hwinfo-log",
        type=Path,
        default=Path("C:/Users/Dhruv Brahmbhatt/Downloads/New folder/ver1_hwf.CSV"),
    )
    parser.add_argument("--phase", choices=["M3", "M3-isolated"], default="M3")
    args = parser.parse_args()
    verify_v2_artifacts()
    block = "6e81165862424391b79b69d0bfbc2dca"
    sha = hashlib.sha256(AMENDMENT.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    try:
        require_review(args.review, sha, block)
    except (ValueError, RuntimeError) as exc:
        print(str(exc))
        raise SystemExit(2) from exc
    if args.action == "inspect":
        root = ROOT / "results/utilisation/supervised"
        print(json.dumps(inspect_outputs(root / args.phase), indent=2))
        return
    if args.action == "check":
        print("Order and drift review recorded. No generation requested.")
        return
    cfg, config_hash = load_config()
    cfg["_session_hwinfo_log"] = str(args.hwinfo_log)
    root = ROOT / "results/utilisation/supervised"
    pipeline = json.loads((ROOT / "studies/utilisation/pipeline.json").read_text())
    baseline_file = ROOT / "studies/utilisation/stimuli/M3-isolated-v2.json"
    client = Client()
    tags = decode_response(client.exchange("/api/tags"))["models"]
    for model in cfg["models"]:
        if not any(
            m["name"] == model["tag"] and m["digest"] == model["expected_digest"] for m in tags
        ):
            raise ValueError("Model digest mismatch")
    try:
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            execute_v2(
                root, pipeline, cfg, config_hash, client, json.loads(baseline_file.read_text())
            )
    except Halt as exc:
        write_checkpoint(root, str(exc), {"entrypoint": "supervise_v2", "order": "draft-v2"})
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
