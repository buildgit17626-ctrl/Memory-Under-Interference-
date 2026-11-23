"""Approved queue gates, controlled caches and feedback provenance, with mock models."""

import base64
import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from experiments.prepare_remaining import BASE, configuration, jobs_for
from experiments.run_remaining import sequential_steps
from experiments.utilisation_pilot import template
from prompt_energy import remaining_cache_worker
from prompt_energy.remaining_cache import CacheClient, gate, hard_stop, outcome
from prompt_energy.remaining_materials import (
    common_prefix,
    fixtures,
    heldout_row,
    keyed,
    m2_text,
    repair_text,
    retry_feedback,
)
from prompt_energy.remaining_repair import derived_job, save_derived
from prompt_energy.utilisation_journal import read_jsonl
from prompt_energy.utilisation_plan import digest
from prompt_energy.utilisation_supervisor import Halt


def envelope(value, request=None):
    return {
        "error": None,
        "http_status": 200,
        "wall_seconds": 1,
        "body_base64": base64.b64encode(json.dumps(value).encode()).decode(),
        "request": request,
    }


def cache_job(state="warm"):
    return {
        "key": "k",
        "experiment": "E4",
        "condition": state,
        "model": "m",
        "model_digest": "digest",
        "entries": ["probe"],
        "expected_tokens": 100,
        "shared_prefix_tokens": 80,
        "prime_prompt": "prime",
        "timeout": 900,
        "request": {
            "model": "m",
            "prompt": "probe",
            "raw": True,
            "keep_alive": -1,
            "options": {"num_predict": 64},
        },
    }


def cache_response(cached=64, output=64):
    return {
        "done": True,
        "response": "1 2 3",
        "done_reason": "length",
        "prompt_eval_count": 100,
        "prompt_eval_cached_count": cached,
        "eval_count": output,
        "prompt_eval_duration": 10,
        "eval_duration": 10,
        "load_duration": 1,
        "total_duration": 21,
    }


def test_queue_order_and_no_full_e3():
    order = []
    sequential_steps(
        *[
            lambda name=name: order.append(name)
            for name in ("R2", "M2pilot", "M2full", "E4pilot", "E4full", "E3pilot")
        ]
    )
    assert order == ["R2", "M2pilot", "M2full", "E4pilot", "E4full", "E3pilot"]


def test_failed_pilot_stops_every_later_stage():
    calls = []

    def bad():
        calls.append("pilot")
        raise Halt("invalid gate")

    with pytest.raises(Halt):
        sequential_steps(lambda: calls.append("R2"), bad, *[lambda: calls.append("forbidden")] * 4)
    assert calls == ["R2", "pilot"]


def test_e4_budget_cap_is_intentional_and_native_counter_required():
    job = cache_job()
    raw = envelope(cache_response()) | {"cache_setup": {"resident_verified": True}}
    result, _ = outcome(job, raw)
    assert result["input_valid"] and result["cached_tokens"] == 64
    assert "output_cap" not in result["flags"]
    for field, replacement in (
        ("prompt_eval_cached_count", None),
        ("eval_count", 63),
        ("prompt_eval_count", 99),
    ):
        bad = cache_response()
        if replacement is None:
            del bad[field]
        else:
            bad[field] = replacement
        parsed, _ = outcome(job, envelope(bad) | {"cache_setup": {"resident_verified": True}})
        assert not parsed["input_valid"]


@pytest.mark.parametrize(
    "state,cached,valid",
    [("cold", 0, True), ("cold", 1, False), ("warm", 0, False), ("warm", 81, False)],
)
def test_e4_cache_states_and_overlap_boundary(state, cached, valid):
    parsed, _ = outcome(
        cache_job(state),
        envelope(cache_response(cached)) | {"cache_setup": {"resident_verified": True}},
    )
    assert parsed["input_valid"] == valid


def test_residency_required_and_gate_ignores_effects():
    parsed, _ = outcome(cache_job(), envelope(cache_response()))
    assert "residency_unverified" in parsed["flags"]
    calls = [
        {"key": str(i), "input_valid": True, "energy_valid": True, "flags": []} for i in range(20)
    ]
    assert gate(calls, 20)["pass"]
    calls[0]["input_valid"] = False
    assert not gate(calls, 20)["pass"]
    assert "validity failed" in hard_stop(calls, 10 * 1024**3)


def test_cache_setup_orders_unloads_residency_and_prime_and_preserves_inputs(tmp_path):
    recorded = []

    def exchange(endpoint, payload=None, **kwargs):
        recorded.append((endpoint, deepcopy(payload)))
        result = {"models": [{"digest": "digest", "size_vram": 0}]} if endpoint == "/api/ps" else {}
        return envelope(result, payload)

    proxy = CacheClient(
        SimpleNamespace(exchange=exchange),
        tmp_path,
        ["m", "other"],
        tmp_path / "PAUSE",
        sleep=lambda _: None,
    )
    original = cache_job()
    job = deepcopy(original)
    proxy.prepare(job)
    assert job == original
    assert [r[1].get("keep_alive") if r[1] else None for r in recorded] == [0, 0, -1, -1, None]
    assert recorded[3][1]["prompt"] == "prime" and recorded[3][1]["options"]["num_predict"] == 1
    assert len(read_jsonl(tmp_path / "controls.jsonl")) == 5
    recorded.clear()
    proxy.prepare(cache_job("cold"))
    assert len(recorded) == 4 and all(r[1].get("prompt") != "prime" for r in recorded if r[1])


def test_cache_setup_obeys_pause_before_any_http(tmp_path):
    pause = tmp_path / "PAUSE"
    pause.touch()
    proxy = CacheClient(
        SimpleNamespace(exchange=lambda *a, **k: pytest.fail("HTTP after pause")),
        tmp_path,
        ["m"],
        pause,
        sleep=lambda _: None,
    )
    with pytest.raises(Halt, match="User pause"):
        proxy.prepare(cache_job())


def test_cache_worker_journals_saved_response_without_repeating_measurement(tmp_path, monkeypatch):
    from prompt_energy.utilisation_journal import append_json

    job = cache_job()
    raw = envelope(cache_response()) | {"cache_setup": {"resident_verified": True}}
    append_json(tmp_path / "starts.jsonl", {"key": "k", "attempt": "a", "block": "old"})
    append_json(
        tmp_path / "responses.jsonl", {"key": "k", "attempt": "a", "block": "old", "raw": raw}
    )
    client = SimpleNamespace(
        prepare=lambda j: pytest.fail("Repeated setup"),
        exchange=lambda *a, **k: pytest.fail("Repeated generation"),
        unload=lambda: None,
    )
    sensor = SimpleNamespace(block="new", start=lambda: None, close=lambda: None)
    count = remaining_cache_worker.cache_batch(
        tmp_path, [job], client, sensor, 0, sleep=lambda _: None
    )
    assert count == 1
    call = read_jsonl(tmp_path / "calls.jsonl")[0]
    assert call["input_valid"] and not call["energy_valid"]
    assert call["energy"]["reason"] == "Recovered response; sensor block changed"


def test_feedback_is_removed_from_both_partitions_and_other_rows_preserved():
    row = {"base_input": [[1], [2]], "plus_input": [[1], [3]], "prompt": "unchanged"}
    heldout, counts = heldout_row(row, [{"args": [1], "expected": "0"}])
    assert heldout["base_input"] == [[2]] and heldout["plus_input"] == [[3]]
    assert row["base_input"] == [[1], [2]] and heldout["prompt"] == "unchanged"
    assert counts["plus_input"] == {"before": 2, "after": 1}


def test_repair_only_uses_frozen_feedback_and_explicit_memory_history():
    histories = [
        {"key": "a", "output": "attempt_a", "feedback": "feedback_a"},
        {"key": "b", "output": "attempt_b", "feedback": "feedback_b"},
    ]
    assert "attempt_a" not in repair_text("task", "f", histories, "last")
    full = repair_text("task", "f", histories, "full")
    assert full.index("attempt_a") < full.index("attempt_b")
    assert "expected return value" in retry_feedback("example", fixtures()["HumanEval/53"][0])
    assert "arguments" not in retry_feedback("retry", fixtures()["HumanEval/53"][0])
    assert "actual" not in retry_feedback("example", fixtures()["HumanEval/53"][0])


def test_dynamic_schedule_cannot_change_on_resume(tmp_path):
    save_derived(tmp_path, [{"key": "a"}])
    save_derived(tmp_path, [{"key": "a"}])
    with pytest.raises(Halt, match="changed"):
        save_derived(tmp_path, [{"key": "b"}])


def test_derived_job_binds_parent_and_frozen_round_seed():
    initial = {
        "key": "initial",
        "identity": {"pilot": True},
        "request": {"options": {"num_predict": 2048, "num_ctx": 32768}},
    }
    token = SimpleNamespace(encode=lambda text: SimpleNamespace(ids=list(range(len(text)))))
    histories = [{"key": "initial", "output": "bad", "feedback": "retry"}]
    row = {"prompt": "task", "entry_point": "f"}
    job = derived_job(
        initial, row, histories, "retry", "full", 2, token, lambda x: x, [1729, 2718, 3141]
    )
    assert job["seed"] == 2718 and job["identity"]["parent_keys"] == ["initial"]
    assert job["identity"]["feedback_history_hash"] == digest(histories)
    assert initial["request"]["options"] == {"num_predict": 2048, "num_ctx": 32768}
    assert job == keyed(job)


def test_static_transcript_has_identical_final_instruction():
    loaded = m2_text("target", "f", ["neutral", "other", "neutral"])
    isolated = m2_text("target", "f", [])
    assert (
        loaded.split("[RETURN TO ORIGINAL TARGET]")[1]
        == isolated.split("[RETURN TO ORIGINAL TARGET]")[1]
    )
    assert loaded.count("Description noted.") == 3 and "return " not in loaded


def test_prepared_materials_have_exact_counts_matching_and_no_feedback_leakage():
    from experiments.prepare_continuation import source

    _, _, tokenizer = source()
    expected = {
        ("M2", "pilot"): 50,
        ("M2", "full"): 400,
        ("E4", "pilot"): 20,
        ("E4", "full"): 400,
        ("E3", "pilot"): 10,
    }
    for (stage, phase), n in expected.items():
        cfg, checksum = configuration(stage, phase)
        jobs = jobs_for(stage, phase, cfg, checksum, tokenizer)
        assert len(jobs) == len({j["key"] for j in jobs}) == n
        for j in jobs:
            assert (
                j["expected_tokens"] + j["request"]["options"]["num_predict"]
                <= j["request"]["options"]["num_ctx"]
            )
        if stage == "M2":
            for tid in {j["task_id"] for j in jobs}:
                assert (
                    len(
                        {
                            j["expected_tokens"]
                            for j in jobs
                            if j["task_id"] == tid and j["condition"] != "isolated"
                        }
                    )
                    == 1
                )
        if stage == "E4":
            for j in jobs:
                assert j["request"]["raw"] and "system" not in j["request"]
                assert len(tokenizer.encode(j["request"]["prompt"]).ids) == j["expected_tokens"]
                assert j["shared_prefix_tokens"] == common_prefix(
                    tokenizer.encode(j["request"]["prompt"]).ids,
                    tokenizer.encode(j["prime_prompt"]).ids,
                )
    examples = json.loads((BASE / "E3/feedback-examples.json").read_text())
    heldout = json.loads((BASE / "E3/heldout-tasks.json").read_text())
    for tid, row in heldout.items():
        for case in examples[tid]:
            assert case["args"] not in row["base_input"] + row["plus_input"]


def test_full_and_pilot_keys_never_overlap():
    for stage in ("M2", "E4"):
        keys = []
        for phase in ("pilot", "full"):
            cfg, checksum = configuration(stage, phase)
            keys.append({j["key"] for j in jobs_for(stage, phase, cfg, checksum)})
        assert not keys[0] & keys[1]


def test_pause_file_is_not_removed_by_queue_modules():
    for filename in ("remaining_cache.py", "remaining_cache_worker.py", "remaining_repair.py"):
        text = (Path("src/prompt_energy") / filename).read_text()
        assert ".unlink(" not in text


def test_e3_mock_pipeline_defers_hidden_scoring_and_recovery_sends_no_duplicates(
    tmp_path, monkeypatch
):
    from experiments.prepare_continuation import source
    from prompt_energy import remaining_repair
    from prompt_energy.utilisation_journal import append_json
    from prompt_energy.utilisation_run import by_key

    cfg, checksum = configuration("E3", "pilot")
    jobs = jobs_for("E3", "pilot", cfg, checksum)
    _, tasks, tokenizer = source()
    examples = fixtures()
    heldout = {t: heldout_row(tasks[t], examples[t])[0] for t in examples}
    events = []

    def generate(folder, scheduled, *args):
        folder.mkdir(parents=True, exist_ok=True)
        saved = by_key(folder / "calls.jsonl")
        for job in scheduled:
            if job["key"] not in saved:
                events.append("generation")
                append_json(
                    folder / "calls.jsonl",
                    {
                        **job,
                        "raw_output": "def f(): pass",
                        "extracted": {},
                        "input_valid": True,
                        "flags": [],
                        "wall_seconds": 1,
                        "energy_valid": False,
                        "energy": {"windows": {}},
                        "prompt_tokens": 100,
                        "output_tokens": 4,
                    },
                )
        return {"remaining": 0}

    def feedback(folder, *args):
        saved = by_key(folder / "feedback.jsonl")
        for key, call in by_key(folder / "calls.jsonl").items():
            if key not in saved:
                passed = folder.name == "round-2"
                append_json(
                    folder / "feedback.jsonl",
                    {
                        "key": key,
                        "passed": passed,
                        "first_failure": None if passed else examples[call["task_id"]][0],
                    },
                )
        return True

    def score(folder, *args):
        events.append("heldout")
        saved = by_key(folder / "scores.jsonl")
        for key in by_key(folder / "calls.jsonl"):
            if key not in saved:
                append_json(folder / "scores.jsonl", {"key": key, "status": "failed"})
        return True

    monkeypatch.setattr(remaining_repair, "continuation_queue", generate)
    monkeypatch.setattr(remaining_repair, "feedback_batch", feedback)
    monkeypatch.setattr(remaining_repair, "evaluate_stage", score)
    args = (
        tmp_path,
        jobs,
        cfg,
        tasks,
        examples,
        heldout,
        None,
        tmp_path / "log",
        tmp_path / "PAUSE",
        tokenizer,
        template,
    )
    remaining_repair.run_pilot(*args)
    assert events.count("generation") == 90  # 10 initial + 40 + 40; round3 never launched.
    assert events[:90] == ["generation"] * 90
    result = json.loads((tmp_path / "PILOT_REVIEW.json").read_text())
    assert result["physical_calls"] == 90 and len(result["branches"]) == 40
    assert not result["full_E3_authorized"]
    assert all(b["net_post_load_wh_total_available"] is None for b in result["branches"])
    assert all(
        b["feedback_pass"] and b["final_heldout_status"] == "failed" for b in result["branches"]
    )
    events.clear()
    remaining_repair.run_pilot(*args)
    assert "generation" not in events
