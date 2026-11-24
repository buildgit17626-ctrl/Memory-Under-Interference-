"""Approved constrained E4 workload, shared setup, and explicit prefix validity."""

import re
import uuid
from pathlib import Path

from prompt_energy.ollama import decode_response
from prompt_energy.remaining_cache import CacheClient, gate
from prompt_energy.remaining_cache import hard_stop as cache_hard_stop
from prompt_energy.remaining_cache import outcome as cache_outcome
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_supervisor import Halt

SCHEMA = {
    "type": "array",
    "items": {"type": "integer"},
    "minItems": 1000,
    "maxItems": 1000,
}
SETUP = "SCHEMA_SETUP_ONLY\nOutput a JSON array of exactly 1000 integers."
INTEGER = r"-?(?:0|[1-9][0-9]*)"
ARRAY_PREFIX = re.compile(r"\s*\[\s*(?:" + INTEGER + r"\s*,\s*)*(?:" + INTEGER + r"\s*|-)?\Z")


def array_prefix_valid(text: str) -> bool:
    """A64-token response must be an unfinished array, never code or a completed short array."""
    # Whitespace alone is a possible incomplete root prefix; no semantic success claim.
    return not text.strip() or ARRAY_PREFIX.fullmatch(text) is not None


def outcome(job: dict, raw: dict) -> tuple[dict, dict | None]:
    parsed, native = cache_outcome(job, raw)
    if native is None:
        return parsed, None
    request = raw.get("request", {})
    schema_ok = request.get("format") == SCHEMA == job["request"].get("format")
    setup_ok = raw.get("cache_setup", {}).get("schema_setup_verified") is True
    prefix_ok = array_prefix_valid(native["response"])
    if not schema_ok:
        parsed["flags"].append("schema_request_mismatch")
    if not setup_ok:
        parsed["flags"].append("schema_setup_unverified")
    if not prefix_ok:
        parsed["flags"].append("invalid_constrained_prefix")
    parsed.update(
        schema_request_valid=schema_ok,
        schema_setup_valid=setup_ok,
        constrained_prefix_valid=prefix_ok,
        input_valid=not parsed["flags"],
    )
    return parsed, native


def hard_stop(rows: list[dict], free_bytes: int) -> str | None:
    return cache_hard_stop(rows, free_bytes)


class SchemaCacheClient(CacheClient):
    """Same grammar setup in both arms before warm-only prefix priming."""

    def __init__(self, client, root: Path, models: list[str], pause: Path, **kwargs):
        super().__init__(client, root, models, pause, **kwargs)
        self.current_key = None

    def control(
        self, label: str, payload: dict | None, *, endpoint="/api/generate", timeout=900
    ) -> dict:
        raw = self.client.exchange(endpoint, payload, timeout=timeout)
        append_json(
            self.root / "controls.jsonl",
            {
                "key": uuid.uuid4().hex,
                "label": label,
                "job_key": self.current_key,
                "raw": raw,
                "measured_call": False,
            },
        )
        return decode_response(raw)

    def prepare(self, job: dict) -> None:
        if self.pause.exists():
            raise Halt("User pause")
        self.current_key = job["key"]
        self.unload()
        request = job["request"]
        if request.get("format") != SCHEMA:
            raise Halt("E4 approved schema missing")
        options = request["options"]
        base = {"model": job["model"], "stream": False, "keep_alive": -1}
        self.control("preload", base | {"options": options})
        setup = self.control(
            "schema_setup",
            request
            | {
                "prompt": job["schema_setup_prompt"],
                "options": options | {"num_predict": 1},
            },
        )
        if setup.get("done") is not True or setup.get("eval_count") != 1:
            raise Halt("E4 schema setup did not produce one token")
        if not array_prefix_valid(setup.get("response", "")):
            raise Halt("E4 schema setup returned a non-array prefix")
        if job["condition"] == "warm":
            self.control(
                "prime",
                request
                | {
                    "prompt": job["prime_prompt"],
                    "options": options | {"num_predict": 1},
                },
            )
        resident = self.control("residency", None, endpoint="/api/ps")
        loaded = resident.get("models", [])
        if len(loaded) != 1 or not any(
            m.get("digest") == job["model_digest"] and m.get("size_vram") == 0 for m in loaded
        ):
            raise Halt("E4 requires exactly the selected CPU model resident")
        self.setup = {
            "resident_verified": True,
            "resident_models": loaded,
            "state": job["condition"],
            "job_key": job["key"],
            "schema_setup_verified": True,
            "schema_setup_native": setup,
        }
        self.sleep(5)
        if self.pause.exists():
            raise Halt("User pause after cache setup")


def pilot_gate(calls: list[dict], expected: int) -> dict:
    result = gate(calls, expected)
    schema_valid = sum(
        r.get("schema_request_valid") is True
        and r.get("schema_setup_valid") is True
        and r.get("constrained_prefix_valid") is True
        for r in calls
    )
    result.update(schema_verified=schema_valid, pass_schema=schema_valid == expected)
    result["pass"] = result["pass"] and schema_valid == expected
    return result
