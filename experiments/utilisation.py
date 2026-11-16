"""Run with python -m experiments.utilisation. No generation on prepare/monitor/score."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from prompt_energy.hwinfo import LogFormat
from prompt_energy.ollama import Client, decode_response
from prompt_energy.records import directory_lock
from prompt_energy.utilisation_eval import evaluate, load_dataset
from prompt_energy.utilisation_plan import ROOT, digest, load_config, schedule
from prompt_energy.utilisation_run import Sensor, monitor, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run", "score", "monitor", "references"])
    parser.add_argument("--stimuli", type=Path)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--hwinfo-log", type=Path)
    parser.add_argument("--encoding", default="cp1252")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--validation-sha256", help="Offline reference validation only")
    parser.add_argument("--power-index", type=int)
    args = parser.parse_args()
    cfg, sha = load_config()
    gap = cfg["energy"]["inter_request_gap_s"]
    if args.action == "monitor":
        print(json.dumps(monitor(args.session, gap), indent=2))
        return
    if args.action in {"score", "references"}:
        if not args.dataset:
            parser.error("--dataset is required")
        checksum = cfg["benchmark"]["dataset_sha256"]
        if args.action == "references" and args.validation_sha256:
            checksum = args.validation_sha256
        tasks = load_dataset(args.dataset, checksum)
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            if args.action == "references":
                from prompt_energy.utilisation_eval import audit_references

                audit_references(args.session, tasks, cfg, checksum)
            else:
                evaluate(args.session, tasks, cfg)
        return
    if not args.stimuli:
        parser.error("--stimuli is required")
    items = json.loads(args.stimuli.read_text(encoding="utf-8"))
    jobs = schedule(items, cfg, sha)
    if args.action == "prepare":
        from collections import Counter

        print(
            json.dumps(
                {
                    "requests": len(jobs),
                    "per_experiment": Counter(j["experiment"] for j in jobs),
                    "config_hash": sha,
                    "schedule_hash": digest(jobs),
                    "first": jobs[:1],
                },
                indent=2,
            )
        )
        return
    if any(v == "REQUIRED_BEFORE_FREEZE" for v in cfg["benchmark"].values()):
        parser.error("Approved config has unresolved benchmark pins")
    if not args.hwinfo_log:
        parser.error("--hwinfo-log is required")
    from prompt_energy.utilisation_freeze import verify_registration

    registration = verify_registration(jobs, args.stimuli, cfg)
    from urllib.parse import urlsplit

    endpoint = urlsplit(cfg["host"]["endpoint"])
    if endpoint.path != "/api/generate":
        raise ValueError("Unexpected Ollama generation endpoint")
    client = Client(endpoint._replace(path="").geturl())
    registration["ollama_version"] = decode_response(client.exchange("/api/version"))["version"]
    actual = decode_response(client.exchange("/api/tags"))["models"]
    for model in cfg["models"]:
        if not any(
            m["name"] == model["tag"] and m["digest"] == model["expected_digest"] for m in actual
        ):
            parser.error("Model digest mismatch")
    sensor = Sensor(
        args.hwinfo_log,
        args.session,
        LogFormat(encoding=args.encoding, power_index=args.power_index),
    )
    with directory_lock(ROOT / cfg["paths"]["sessions"]):
        from prompt_energy.records import write_once

        args.session.mkdir(parents=True, exist_ok=True)
        registration_path = args.session / "registration.json"
        if registration_path.exists():
            if json.loads(registration_path.read_text()) != registration:
                raise ValueError("Registration changed on resume")
        else:
            write_once(registration_path, registration)
        run(args.session, jobs, client, sensor, gap)


if __name__ == "__main__":
    main()
