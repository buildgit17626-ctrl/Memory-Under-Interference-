"""Sequential execution and durable recovery for a single frozen schedule."""

import ctypes
import json
import statistics
import time
import uuid
from datetime import datetime
from pathlib import Path

import psutil

from prompt_energy.extraction import extract_code
from prompt_energy.full_energy import drift, full_energy
from prompt_energy.full_run import baseline, check_host
from prompt_energy.hwinfo import LogFormat, capture_log, check_recent, parse_log, preflight_log
from prompt_energy.metadata import host_metadata
from prompt_energy.ollama import decode_response
from prompt_energy.records import directory_lock, write_once
from prompt_energy.utilisation_checkpoint import checkpoint
from prompt_energy.utilisation_journal import append_json, read_jsonl
from prompt_energy.utilisation_plan import digest


def by_key(path: Path) -> dict:
    rows = read_jsonl(path)
    indexed = {row["key"]: row for row in rows}
    if len(rows) != len(indexed):
        raise ValueError(f"Duplicate keys in {path}")
    return indexed


def snapshot() -> list[dict]:
    return [p.info for p in psutil.process_iter(["pid", "name", "cpu_times"])]


class Sensor:
    def __init__(self, log: Path, root: Path, fmt: LogFormat):
        self.log, self.fmt = log, fmt
        self.block = uuid.uuid4().hex
        self.mirror = root / "sensors" / (self.block + ".csv")
        self.events = root / "blocks.jsonl"

    def start(self) -> None:
        host = host_metadata()
        check_host(host)
        sensor = preflight_log(self.log, self.fmt)
        self.opening = baseline(self.log, self.mirror, self.fmt, sleep=time.sleep, now=time.time)
        append_json(
            self.events,
            {
                "event": "start",
                "block": self.block,
                "baseline": self.opening,
                "host": host,
                "preflight": sensor,
                "processes": snapshot(),
            },
        )

    def before_request(self) -> None:
        data = self.log.read_bytes()
        read_at = time.time()
        samples = parse_log(data, self.fmt, live=True)
        # Parsing a long history must not age the already-captured snapshot.
        check_recent(samples, read_at)

    def measure(self, raw: dict, response: dict | None) -> dict:
        end = datetime.fromisoformat(raw["ended_at"]).timestamp()
        samples, provenance = capture_log(self.log, self.mirror, self.fmt, end)
        result = full_energy(samples, raw, response, self.opening["watts"])
        for name, window in result["windows"].items():
            result["flags"].extend(f"{name}:{flag}" for flag in window["flags"])
        result["snapshot"] = provenance
        return result

    def close(self) -> None:
        ending = None
        try:
            ending = baseline(self.log, self.mirror, self.fmt, sleep=time.sleep, now=time.time)
        finally:
            delta, flags = drift(self.opening["watts"], ending and ending["watts"])
            append_json(
                self.events,
                {
                    "event": "end",
                    "block": self.block,
                    "baseline": ending,
                    "drift_w": delta,
                    "flags": flags,
                    "processes": snapshot(),
                },
            )


def outcome(job: dict, raw: dict) -> tuple[dict, dict | None]:
    result = {
        "input_valid": False,
        "flags": [],
        "extracted": {},
        "prompt_tokens": None,
        "output_tokens": None,
        "prefill_ns": None,
        "decode_ns": None,
        "raw_output": None,
    }
    try:
        r = decode_response(raw, generation=True)
    except (ValueError, TypeError, KeyError) as exc:
        result["flags"].append("api_error")
        result["reason"] = str(exc)
        return result, None
    cap = job["request"]["options"]["num_predict"]
    result.update(
        prompt_tokens=r["prompt_eval_count"],
        output_tokens=r["eval_count"],
        prefill_ns=r["prompt_eval_duration"],
        decode_ns=r["eval_duration"],
        raw_output=r["response"],
        wall_seconds=raw["wall_seconds"],
    )
    cached = r.get("prompt_eval_cached_count", 0)
    if job["experiment"] == "E4":
        # Cache experiments require an independently documented server counter.
        if "prompt_eval_cached_count" not in r:
            result["flags"].append("cache_state_unverified")
        elif bool(cached) != (job["condition"] == "warm"):
            result["flags"].append("cache_state_mismatch")
        if r["eval_count"] != cap:
            result["flags"].append("short_fixed_workload")
    elif cached:
        result["flags"].append("unexpected_cache")
    if r["prompt_eval_count"] != job["expected_tokens"]:
        result["flags"].append("input_count_mismatch")
    result["input_valid"] = not result["flags"]
    if r.get("done_reason") == "length" or r["eval_count"] >= cap:
        result["flags"].append("output_cap")
    if job["experiment"] != "U2":
        result["extracted"] = {
            entry: extract_code(r["response"], entry) for entry in job["entries"]
        }
    return result, r


def cache_controls(root: Path, client, job: dict, attempt: str) -> None:
    # Unload first to discard previous prefix state; preload in both arms.
    base = {"model": job["model"], "stream": False}
    controls = [
        base | {"keep_alive": 0},
        base | {"keep_alive": -1, "options": job["request"]["options"]},
    ]
    if job["condition"] == "warm":
        prime = job["request"] | {"prompt": job["prime_prefix"]}
        controls.append(prime | {"options": prime["options"] | {"num_predict": 1}})
    for idx, control in enumerate(controls):
        envelope = client.exchange("/api/generate", control, timeout=job["timeout"])
        append_json(root / "controls.jsonl", {"key": f"{attempt}/{idx}", "raw": envelope})
        decode_response(envelope)


def run(root: Path, jobs: list, client, sensor, gap: float, *, sleep=time.sleep) -> None:
    with directory_lock(root):
        manifest = {"schedule_hash": digest(jobs), "count": len(jobs)}
        path = root / "schedule.json"
        if path.exists():
            if json.loads(path.read_text()) != manifest:
                raise ValueError("Schedule changed on resume")
        else:
            write_once(path, manifest)
        complete = by_key(root / "calls.jsonl")
        saved = by_key(root / "responses.jsonl")
        pending = [j for j in jobs if j["key"] not in complete]
        if not pending:
            return
        if checkpoint(root, jobs, complete, gap):
            print("M3 checkpoint awaits owner review; see m3-checkpoint.json", flush=True)
            return
        # ES_SYSTEM_REQUIRED prevents idle sleep during the measured block.
        power = ctypes.windll.kernel32.SetThreadExecutionState
        if not power(0x80000001):
            raise OSError("Cannot inhibit Windows idle sleep")
        try:
            sensor.start()
        except BaseException:
            power(0x80000000)
            raise
        try:
            for j in pending:
                if checkpoint(root, jobs, complete, gap):
                    print("M3 checkpoint reached; ending baseline and awaiting review", flush=True)
                    break
                key = j["key"]
                if key in saved:
                    record = saved[key]
                else:
                    attempt = uuid.uuid4().hex
                    append_json(
                        root / "starts.jsonl",
                        {"key": key, "attempt": attempt, "block": sensor.block},
                    )
                    if j["experiment"] == "E4":
                        cache_controls(root, client, j, attempt)
                        sleep(gap)
                    sensor.before_request()
                    raw = client.exchange("/api/generate", j["request"], timeout=j["timeout"])
                    record = {"key": key, "attempt": attempt, "block": sensor.block, "raw": raw}
                    append_json(root / "responses.jsonl", record)
                raw = record["raw"]
                result, response = outcome(j, raw)
                try:
                    if record["block"] != sensor.block:
                        raise ValueError("recovered response in another sensor block")
                    energy = sensor.measure(raw, response)
                except (ValueError, OSError) as exc:
                    energy = {"windows": {}, "flags": ["missing_energy"], "reason": str(exc)}
                append_json(
                    root / "calls.jsonl",
                    {
                        **j,
                        **result,
                        "attempt": record["attempt"],
                        "block": record["block"],
                        "energy": energy,
                        "wall_seconds": raw["wall_seconds"],
                    },
                )
                if response is None or "missing_energy" in energy["flags"]:
                    raise RuntimeError("Recorded invalid request or energy; inspect before resume")
                complete[key] = by_key(root / "calls.jsonl")[key]
                sleep(gap)
        finally:
            try:
                sensor.close()
            finally:
                power(0x80000000)


def monitor(root: Path, gap: float) -> dict:
    total = json.loads((root / "schedule.json").read_text())["count"]
    rows = list(by_key(root / "calls.jsonl").values())
    remaining = total - len(rows)
    eta = (statistics.mean(r["wall_seconds"] for r in rows) + gap) * remaining if rows else None
    return {
        "planned": total,
        "finished": len(rows),
        "remaining": remaining,
        "invalid_inputs": sum(not r["input_valid"] for r in rows),
        "eta_seconds_excluding_baselines_and_sensor_wait": eta,
    }
