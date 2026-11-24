"""New constrained scope must not weaken the original fixed-workload/cache gates."""

import ast
import base64
import hashlib
import inspect
import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from experiments.prepare_e4_schema import BASE, configuration, jobs_for
from experiments.run_e4_schema import sequential_steps
from prompt_energy import e4_schema_worker, remaining_cache_worker
from prompt_energy.e4_schema import (
    SCHEMA,
    SchemaCacheClient,
    array_prefix_valid,
    outcome,
    pilot_gate,
)
from prompt_energy.utilisation_journal import read_jsonl
from prompt_energy.utilisation_plan import ROOT


def envelope(value, payload=None):
    return {
        "error": None,
        "http_status": 200,
        "wall_seconds": 1,
        "request": payload,
        "body_base64": base64.b64encode(json.dumps(value).encode()).decode(),
    }


def job(state="warm"):
    return {
        "experiment": "E4",
        "key": "k",
        "condition": state,
        "model": "m",
        "model_digest": "d",
        "entries": ["probe"],
        "expected_tokens": 100,
        "shared_prefix_tokens": 80,
        "prime_prompt": "prime",
        "schema_setup_prompt": "setup",
        "request": {
            "model": "m",
            "prompt": "probe",
            "raw": True,
            "stream": False,
            "keep_alive": -1,
            "format": deepcopy(SCHEMA),
            "options": {"num_predict": 64},
        },
    }


def response(tokens=64):
    return {
        "done": True,
        "response": "[1,2,3,",
        "done_reason": "length",
        "eval_count": tokens,
        "prompt_eval_count": 100,
        "prompt_eval_cached_count": 64,
        "prompt_eval_duration": 10,
        "eval_duration": 10,
        "load_duration": 1,
        "total_duration": 21,
    }


@pytest.mark.parametrize("text", ["[", "[\n", "[1,2,", "[ -12, 0, -", "[1,2,3", " "])
def test_partial_array_prefixes_are_compatible_with_long_array(text):
    assert array_prefix_valid(text)


@pytest.mark.parametrize(
    "text", ["[]", "[1]", "[01,", "[1.2,", "[true,", "```python", "{}", "[1,,"]
)
def test_non_array_or_completed_short_prefix_is_rejected(text):
    assert not array_prefix_valid(text)


def test_worker_uses_same_retry_and_measurement_code_as_frozen_v4():
    a = ast.parse(inspect.getsource(e4_schema_worker.cache_batch))
    b = ast.parse(inspect.getsource(remaining_cache_worker.cache_batch))
    assert ast.dump(a) == ast.dump(b)


def test_schema_requires_native_64_tokens_setup_and_raw_request_match():
    j = job()
    setup = {"resident_verified": True, "schema_setup_verified": True}
    raw = envelope(response(), j["request"]) | {"cache_setup": setup}
    parsed, _ = outcome(j, raw)
    assert parsed["input_valid"] and parsed["schema_request_valid"]
    assert "output_cap" not in parsed["flags"]
    short, _ = outcome(j, envelope(response(19), j["request"]) | {"cache_setup": setup})
    assert not short["input_valid"] and "short_fixed_workload" in short["flags"]
    missing, _ = outcome(
        j, envelope(response(), j["request"]) | {"cache_setup": {"resident_verified": True}}
    )
    assert "schema_setup_unverified" in missing["flags"]
    altered = deepcopy(j["request"])
    altered.pop("format")
    invalid, _ = outcome(j, envelope(response(), altered) | {"cache_setup": setup})
    assert "schema_request_mismatch" in invalid["flags"]
    bad_response = response()
    bad_response["response"] = "def f(): pass"
    invalid, _ = outcome(j, envelope(bad_response, j["request"]) | {"cache_setup": setup})
    assert "invalid_constrained_prefix" in invalid["flags"]


def test_grammar_setup_parity_and_warm_only_priming(tmp_path):
    recorded = []

    def exchange(endpoint, payload=None, **kwargs):
        recorded.append((endpoint, deepcopy(payload)))
        if endpoint == "/api/ps":
            native = {"models": [{"digest": "d", "size_vram": 0}]}
        elif payload and payload.get("prompt"):
            native = {"done": True, "eval_count": 1, "response": "["}
        else:
            native = {}
        return envelope(native, payload)

    proxy = SchemaCacheClient(
        SimpleNamespace(exchange=exchange),
        tmp_path,
        ["m", "other"],
        tmp_path / "PAUSE",
        sleep=lambda _: None,
    )
    cold = job("cold")
    saved = deepcopy(cold)
    proxy.prepare(cold)
    assert cold == saved and proxy.setup["schema_setup_verified"]
    cold_events = list(recorded)
    recorded.clear()
    proxy.prepare(job("warm"))
    warm_events = recorded
    assert cold_events[:4] == warm_events[:4]  # unload, unload, preload, grammar setup
    assert len(warm_events) == len(cold_events) + 1
    assert cold_events[3][1]["format"] == SCHEMA
    assert cold_events[3][1]["prompt"] == "setup"
    assert warm_events[4][1]["prompt"] == "prime"
    assert warm_events[4][1]["format"] == SCHEMA
    controls = read_jsonl(tmp_path / "controls.jsonl")
    assert all(c["job_key"] == "k" and not c["measured_call"] for c in controls)


def test_gate_requires_every_schema_check_and_never_uses_effect_direction():
    rows = [
        {
            "key": str(i),
            "input_valid": True,
            "energy_valid": True,
            "schema_request_valid": True,
            "schema_setup_valid": True,
            "constrained_prefix_valid": True,
        }
        for i in range(20)
    ]
    assert pilot_gate(rows, 20)["pass"]
    rows[0]["schema_setup_valid"] = False
    assert not pilot_gate(rows, 20)["pass"]
    assert not pilot_gate(rows[:10], 20)["pass"]


def test_e4_failure_blocks_full_and_e3():
    seen = []

    def failure():
        seen.append("pilot")
        raise RuntimeError("invalid")

    with pytest.raises(RuntimeError):
        sequential_steps(failure, lambda: seen.append("full"), lambda: seen.append("E3"))
    assert seen == ["pilot"]


def test_prepared_new_scope_is_disjoint_and_pairs_have_identical_requests():
    from experiments.prepare_remaining import configuration as old_configuration
    from experiments.prepare_remaining import jobs_for as old_jobs

    all_keys = []
    for phase, n in (("pilot", 20), ("full", 400)):
        cfg, checksum = configuration(phase)
        jobs = jobs_for(phase, cfg, checksum)
        assert len(jobs) == len({j["key"] for j in jobs}) == n
        all_keys.append({j["key"] for j in jobs})
        old_cfg, old_checksum = old_configuration("E4", phase)
        old = old_jobs("E4", phase, old_cfg, old_checksum)
        assert not all_keys[-1] & {j["key"] for j in old}
        pairs = {}
        for j in jobs:
            assert j["request"]["format"] == SCHEMA
            assert j["request"]["options"]["num_predict"] == 64
            key = j["model"], j["repeat"], j["identity"]["prefix_tokens"]
            pairs.setdefault(key, []).append(j)
        assert all(
            len(pair) == 2 and pair[0]["request"] == pair[1]["request"] for pair in pairs.values()
        )
    assert not all_keys[0] & all_keys[1]


def test_original_pilot_and_every_preserved_artifact_are_unchanged():
    record = json.loads((BASE / "legacy-preservation.json").read_text())
    assert record["calls"] == 10
    for name, expected in record["files"].items():
        data = (ROOT / name).read_bytes()
        assert len(data) == expected["bytes"]
        assert hashlib.sha256(data).hexdigest() == expected["sha256"]
