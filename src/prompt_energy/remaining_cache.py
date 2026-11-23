"""Verified resident cache controls; all setup responses are retained separately."""

import time
import uuid
from pathlib import Path

from prompt_energy.ollama import decode_response
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_run import outcome as coding_outcome
from prompt_energy.utilisation_supervisor import Halt
from prompt_energy.utilisation_supervisor import hard_stop as common_hard_stop


def outcome(job: dict, raw: dict) -> tuple[dict, dict | None]:
    parsed, response = coding_outcome(job, raw)
    if response is None:
        return parsed, None
    # The intentional fixed token workload is not an incomplete coding solution.
    parsed["flags"] = [f for f in parsed["flags"] if f != "output_cap"]
    cached = response.get("prompt_eval_cached_count")
    parsed.update(
        cached_tokens=cached,
        shared_prefix_tokens=job["shared_prefix_tokens"],
        workload_endpoint="registered_64_token_budget",
        model_residency=raw.get("cache_setup", {}).get("resident_verified", False),
        cache_setup=raw.get("cache_setup"),
    )
    if not parsed["model_residency"]:
        parsed["flags"].append("residency_unverified")
    if type(cached) is not int or cached < 0 or cached > job["shared_prefix_tokens"]:
        parsed["flags"].append("invalid_cache_counter")
    parsed["input_valid"] = not parsed["flags"]
    return parsed, response


def hard_stop(rows: list[dict], free_bytes: int) -> str | None:
    reason = common_hard_stop(rows, free_bytes)
    if reason:
        return reason
    if any(not r["input_valid"] and not r.get("call_failed") for r in rows):
        return "E4 cache/residency/workload validity failed; retain output and inspect"
    return None


class CacheClient:
    """The measured exchange follows controlled setup; no second measured request on resume."""

    def __init__(self, client, root: Path, models: list[str], pause: Path, *, sleep=time.sleep):
        self.client, self.root, self.models, self.pause, self.sleep = (
            client,
            root,
            models,
            pause,
            sleep,
        )
        self.setup = None

    def control(
        self, label: str, payload: dict | None, *, endpoint="/api/generate", timeout=900
    ) -> dict:
        raw = self.client.exchange(endpoint, payload, timeout=timeout)
        append_json(
            self.root / "controls.jsonl",
            {
                "key": uuid.uuid4().hex,
                "label": label,
                "raw": raw,
                "measured_call": False,
            },
        )
        return decode_response(raw)

    def unload(self) -> None:
        for model in self.models:
            self.control("unload", {"model": model, "stream": False, "keep_alive": 0})

    def prepare(self, job: dict) -> None:
        if self.pause.exists():
            raise Halt("User pause")
        self.unload()
        base = {"model": job["model"], "stream": False, "keep_alive": -1}
        options = job["request"]["options"]
        self.control("preload", base | {"options": options})
        if job["condition"] == "warm":
            self.control(
                "prime",
                job["request"]
                | {
                    "prompt": job["prime_prompt"],
                    "options": options | {"num_predict": 1},
                },
            )
        resident = self.control("residency", None, endpoint="/api/ps")
        loaded = resident.get("models", [])
        verified = len(loaded) == 1 and any(
            m.get("digest") == job["model_digest"] and m.get("size_vram") == 0 for m in loaded
        )
        if not verified:
            raise Halt("E4 requires exactly the selected CPU model resident")
        self.setup = {
            "resident_verified": True,
            "resident_models": loaded,
            "state": job["condition"],
            "job_key": job["key"],
        }
        self.sleep(5)
        if self.pause.exists():
            raise Halt("User pause after cache setup")

    def exchange(self, *args, **kwargs) -> dict:
        raw = self.client.exchange(*args, **kwargs)
        return raw | {"cache_setup": self.setup}


def gate(calls: list[dict], expected: int) -> dict:
    valid = sum(bool(r["input_valid"]) and not r.get("call_failed", False) for r in calls)
    coverage = sum(bool(r["energy_valid"]) for r in calls)
    return {
        "expected": expected,
        "calls": len(calls),
        "valid_cache_resident_fixed_workload": valid,
        "energy_available": coverage,
        "unique": len({r["key"] for r in calls}),
        "pass": len(calls) == len({r["key"] for r in calls}) == valid == coverage == expected,
        "uses_effect_direction": False,
    }
