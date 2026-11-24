"""New E4 amendment, then the unchanged approved E3 diagnostic; no finished-stage replay."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiments.prepare_continuation import source
from experiments.prepare_e4_schema import BASE, OUTPUT, configuration, jobs_for
from experiments.prepare_remaining import BASE as PREVIOUS_BASE
from experiments.prepare_remaining import OUTPUT as PREVIOUS_OUTPUT
from experiments.run_continuation import PAUSE
from experiments.run_continuation import verify as verify_continuation
from experiments.run_remaining import verify as verify_previous
from experiments.utilisation_pilot import template
from prompt_energy.continuation_queue import continuation_queue
from prompt_energy.e4_schema import SchemaCacheClient, pilot_gate
from prompt_energy.e4_schema_worker import cache_batch
from prompt_energy.full_run import check_host
from prompt_energy.hwinfo import LogFormat, preflight_log
from prompt_energy.metadata import host_metadata
from prompt_energy.ollama import Client, decode_response, utc_now
from prompt_energy.records import directory_lock
from prompt_energy.remaining_repair import run_pilot
from prompt_energy.utilisation_freeze import verify_registration
from prompt_energy.utilisation_journal import append_json, read_jsonl
from prompt_energy.utilisation_plan import ROOT
from prompt_energy.utilisation_run import by_key
from prompt_energy.utilisation_supervisor import Halt, write_checkpoint


def verify() -> tuple[dict, tuple]:
    previous = verify_previous()
    path = BASE / "execution.sha256"
    blob = subprocess.check_output(
        ["git", "show", "HEAD:" + path.relative_to(ROOT).as_posix()], cwd=ROOT
    )
    if path.read_bytes().replace(b"\r\n", b"\n") != blob:
        raise ValueError("Uncommitted E4 amendment manifest")
    for line in blob.decode().splitlines():
        checksum, name = line.split("  ", 1)
        if (
            hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            != checksum
        ):
            raise ValueError("Frozen E4 amendment changed: " + name)
    prepared = {}
    for phase in ("pilot", "full"):
        cfg, checksum = configuration(phase)
        jobs = jobs_for(phase, cfg, checksum)
        prepared[phase] = cfg, jobs, verify_registration(jobs, BASE / phase / "stimuli.json", cfg)
    return prepared, previous[("E3", "pilot")]


def completed_audit() -> dict:
    """Check exact finished keys, not just a matching denominator, without re-scoring."""
    previous = verify_previous()
    legacy = verify_continuation()
    groups = [
        (ROOT / "results/utilisation/continuation-v3/R2/full", legacy[("R2", "full")][1]),
        (PREVIOUS_OUTPUT / "M2/pilot", previous[("M2", "pilot")][1]),
        (PREVIOUS_OUTPUT / "M2/full", previous[("M2", "full")][1]),
    ]
    result = {}
    for folder, jobs in groups:
        expected = {j["key"] for j in jobs}
        calls, scores = by_key(folder / "calls.jsonl"), by_key(folder / "scores.jsonl")
        if set(calls) != expected or set(scores) != expected:
            raise Halt("A prerequisite stage has incomplete or foreign keys: " + str(folder))
        result[folder.relative_to(ROOT).as_posix()] = {"calls": len(calls), "scores": len(scores)}
    return result


def snapshot() -> dict:
    result = {}
    for phase in ("pilot", "full"):
        folder = OUTPUT / phase
        calls = list(by_key(folder / "calls.jsonl").values())
        result["E4_schema/" + phase] = {
            "planned": 20 if phase == "pilot" else 400,
            "saved": len(calls),
            "valid": sum(r["input_valid"] for r in calls),
            "energy_available": sum(r["energy_valid"] for r in calls),
            "output_64": sum(r.get("output_tokens") == 64 for r in calls),
            "setup_HTTP_requests": len(read_jsonl(folder / "controls.jsonl")),
        }
    result["E3/pilot"] = {
        "saved": sum(
            len(by_key(PREVIOUS_OUTPUT / "E3/pilot" / name / "calls.jsonl"))
            for name in ("initial", "round-1", "round-2", "round-3")
        ),
        "maximum": 130,
    }
    return result


def sequential_steps(pilot, full, e3) -> None:
    pilot()
    full()
    e3()


def recover(log: Path, prepared: dict, e3_prepared: tuple) -> None:
    _, tasks, tokenizer = source()
    status = {
        "reason": "running",
        "started_at": utc_now(),
        "sensor": str(log),
        "elapsed_time_cutoff": None,
    }

    def record(**updates):
        status.update(updates)
        (OUTPUT / "STATUS.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    def check_models(client, cfg):
        installed = decode_response(client.exchange("/api/tags"))["models"]
        if any(
            not any(
                m["name"] == wanted["tag"] and m["digest"] == wanted["expected_digest"]
                for m in installed
            )
            for wanted in cfg["models"]
        ):
            raise Halt("Model digest mismatch")

    def stage(phase):
        if PAUSE.exists():
            raise Halt("User pause")
        cfg, jobs, registration = prepared[phase]
        folder = OUTPUT / phase
        folder.mkdir(parents=True, exist_ok=True)
        record(stage="E4_schema", phase=phase, operation="generation")
        client = Client()
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            check_models(client, cfg)
            append_json(
                folder / "sessions.jsonl",
                {
                    "time": utc_now(),
                    "registration": registration,
                    "sensor": str(log),
                    "version": decode_response(client.exchange("/api/version")),
                },
            )
            proxy = SchemaCacheClient(client, folder, [m["tag"] for m in cfg["models"]], PAUSE)
            result = continuation_queue(folder, jobs, proxy, log, PAUSE, generator=cache_batch)
            if result["remaining"]:
                raise Halt("User pause", result)
            calls = list(by_key(folder / "calls.jsonl").values())
            if phase == "pilot":
                gate = pilot_gate(calls, len(jobs))
                (folder / "GATE.json").write_text(
                    json.dumps(gate, indent=2) + "\n", encoding="utf-8"
                )
                if not gate["pass"]:
                    raise Halt("Constrained E4 pilot validity gate failed", gate)
            print(json.dumps({"completed": phase, "calls": len(calls)}), flush=True)

    def e3():
        if PAUSE.exists():
            raise Halt("User pause")
        cfg, jobs, registration = e3_prepared
        folder = PREVIOUS_OUTPUT / "E3/pilot"
        folder.mkdir(parents=True, exist_ok=True)
        client = Client()
        record(stage="E3", phase="pilot", operation="unchanged_diagnostic")
        with directory_lock(ROOT / cfg["paths"]["sessions"]):
            check_models(client, cfg)
            append_json(
                folder / "sessions.jsonl",
                {
                    "time": utc_now(),
                    "registration": registration,
                    "sensor": str(log),
                    "via": "owner_approved_E4_amendment",
                },
            )
            run_pilot(
                folder,
                jobs,
                cfg,
                tasks,
                json.loads((PREVIOUS_BASE / "E3/feedback-examples.json").read_text()),
                json.loads((PREVIOUS_BASE / "E3/heldout-tasks.json").read_text()),
                client,
                log,
                PAUSE,
                tokenizer,
                template,
            )

    record()
    try:
        audit = completed_audit()
        append_json(
            OUTPUT / "events.jsonl",
            {"event": "skipped_completed", "time": utc_now(), "audit": audit},
        )
        sequential_steps(lambda: stage("pilot"), lambda: stage("full"), e3)
    except (Halt, OSError, ValueError) as exc:
        record(reason="stopped", stop_reason=str(exc))
        write_checkpoint(
            OUTPUT,
            str(exc),
            {"state": status, "counts": snapshot(), "details": getattr(exc, "details", {})},
        )
        print("STOP: " + str(exc), flush=True)
        return
    record(reason="finished", operation="E3_pilot_owner_review")
    write_checkpoint(
        OUTPUT, "Amended E4 and E3 diagnostic finished; no full E3 authorized", snapshot()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "recover", "monitor", "pause"])
    parser.add_argument("--hwinfo-log", type=Path)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.action == "pause":
        PAUSE.write_text(utc_now() + "\n", encoding="utf-8")
        print("Pause requested; wait for active work and closing baseline.")
        return
    if args.action == "monitor":
        print(json.dumps(snapshot(), indent=2))
        if (OUTPUT / "STATUS.json").exists():
            print((OUTPUT / "STATUS.json").read_text())
        return
    prepared, e3_prepared = verify()
    if args.action == "check":
        print(
            json.dumps(
                {
                    "verified": True,
                    "E4": {p: len(v[1]) for p, v in prepared.items()},
                    "E3_initial": len(e3_prepared[1]),
                    "E3_maximum": 130,
                    "completed_stages": completed_audit(),
                }
            )
        )
        return
    if args.hwinfo_log is None:
        parser.error("--hwinfo-log required")
    check_host(host_metadata())
    preflight_log(args.hwinfo_log, LogFormat(encoding="cp1252"))
    if PAUSE.exists():
        if not args.resume:
            raise Halt("Saved user pause; explicit --resume required")
        PAUSE.unlink()
        append_json(OUTPUT / "events.jsonl", {"event": "owner_resume", "time": utc_now()})
    recover(args.hwinfo_log, prepared, e3_prepared)


if __name__ == "__main__":
    main()
