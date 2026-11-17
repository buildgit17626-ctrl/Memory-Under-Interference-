import base64
import json

import pytest

from prompt_energy.hwinfo import Sample
from prompt_energy.records import read_jsonl
from prompt_energy.utilisation_eval import score_function
from prompt_energy.utilisation_plan import SECTIONS, load_config, render, schedule
from prompt_energy.utilisation_run import Sensor, monitor, outcome, run


def fixture():
    cfg, checksum = load_config()
    model = cfg["models"][0]["tag"]
    item = {
        "task_id": "Example/0",
        "experiment": "E0",
        "condition": "P1",
        "entries": ["f"],
        "task": 'def f(x):\n    """Return x."""',
        "models": [model],
        "prompt_tokens": {model: 30},
    }
    return item, cfg, checksum


class Mock:
    calls = 0

    def exchange(self, path, payload, *, timeout):
        self.calls += 1
        r = dict(
            done=True,
            response="def f(x):\n    return x",
            prompt_eval_count=30,
            eval_count=7,
            prompt_eval_duration=100,
            eval_duration=100,
            load_duration=0,
            total_duration=200,
        )
        return dict(
            error=None,
            http_status=200,
            body_base64=base64.b64encode(json.dumps(r).encode()).decode(),
            started_at="2026-01-01T00:00:00+00:00",
            ended_at="2026-01-01T00:00:01+00:00",
            wall_seconds=1.0,
        )


class MockSensor:
    block = "test"

    def start(self):
        pass

    def before_request(self):
        pass

    def close(self):
        pass

    def measure(self, *args):
        return {"flags": [], "windows": {}}


def test_manifest_and_resume(tmp_path):
    item, cfg, h = fixture()
    items = [item, item | {"condition": "P3_1"}]
    jobs = schedule(items, cfg, h)
    assert jobs == schedule(list(reversed(items)), cfg, h)
    assert len(jobs) == 6
    client = Mock()
    for _ in range(2):
        run(tmp_path, jobs, client, MockSensor(), 0)
    assert client.calls == 6
    assert monitor(tmp_path, 0)["remaining"] == 0
    rows = read_jsonl(tmp_path / "calls.jsonl")
    assert all(r["input_valid"] and r["extracted"]["f"] for r in rows)
    with pytest.raises(ValueError, match="Schedule changed"):
        run(tmp_path, jobs[:1], client, MockSensor(), 0)


def test_duplicate_and_context():
    item, cfg, h = fixture()
    with pytest.raises(ValueError, match="Duplicate"):
        schedule([item, item], cfg, h)
    item["prompt_tokens"][item["models"][0]] = 8000
    with pytest.raises(ValueError, match="reservation"):
        schedule([item], cfg, h)


@pytest.mark.parametrize("exp", SECTIONS)
def test_layout(exp):
    keys = sorted(SECTIONS[exp])
    item = {"experiment": exp, "layout": keys, "sections": {k: [k] for k in keys}}
    assert render(item) == "".join(keys)
    with pytest.raises(ValueError, match="Unused"):
        render(item | {"layout": keys[:-1]})


def test_validity():
    item, cfg, h = fixture()
    j = schedule([item], cfg, h)[0]
    j["expected_tokens"] += 1
    j["request"]["options"]["num_predict"] = 7
    row, _ = outcome(j, Mock().exchange("", {}, timeout=10))
    assert not row["input_valid"] and row["flags"] == ["input_count_mismatch", "output_cap"]


def test_plus_inputs_sandboxed():
    row = {
        "task_id": "fixture",
        "entry_point": "f",
        "prompt": "def f(x):\n    'Return x.'\n",
        "canonical_solution": "    return x",
        "atol": 0,
        "base_input": [[0]],
        "plus_input": [[2]],
    }
    limits = {"per_candidate_wall_timeout_s": 10, "candidate_memory_mb": 256}
    results = score_function(row, "def f(x):\n    return 0", limits, 1729)
    assert [r["status"] for r in results.values()] == ["passed", "failed"]


def test_missing_sensor_coverage(tmp_path, monkeypatch):
    sensor = Sensor(tmp_path / "log", tmp_path, None)
    sensor.opening = {"watts": 2}
    monkeypatch.setattr(
        "prompt_energy.utilisation_run.capture_log",
        lambda *args: ([Sample(0, 5), Sample(1, 5)], {}),
    )
    raw = Mock().exchange("", {}, timeout=1)
    _, cfg, h = fixture()
    result = sensor.measure(raw, {"load_duration": 0, "total_duration": 1000000000})
    assert "post_load:missing_sensor_coverage" in result["flags"]
    assert result["windows"]["post_load"]["adjusted_wh"] is None


def test_torn_journal_keeps_original_bytes(tmp_path):
    from prompt_energy.utilisation_journal import append_json, read_jsonl

    log = tmp_path / "test.jsonl"
    log.write_bytes(b'{"key": "a"}\n{"key"')
    append_json(log, {"key": "b"})
    assert log.read_bytes().endswith(b'{"key"')
    assert read_jsonl(log) == [{"key": "a"}, {"key": "b"}]


def test_recover_saved_response_without_call(tmp_path):
    from prompt_energy.records import append_json

    item, cfg, h = fixture()
    jobs = schedule([item], cfg, h)[:1]
    raw = Mock().exchange("", {}, timeout=1)
    append_json(
        tmp_path / "responses.jsonl",
        {"key": jobs[0]["key"], "attempt": "original", "block": "interrupted", "raw": raw},
    )
    client = Mock()
    with pytest.raises(RuntimeError, match="energy"):
        run(tmp_path, jobs, client, MockSensor(), 0)
    run(tmp_path, jobs, client, MockSensor(), 0)
    assert client.calls == 0
    assert read_jsonl(tmp_path / "calls.jsonl")[0]["energy"]["flags"] == ["missing_energy"]


def test_type_predicate_scope():
    from prompt_energy.policy import check_source

    check_source("type(x) != int", exact_types=True)
    for source in ["f = type", "type(x).__bases__", "type(x) == y", "type('z', (), {})"]:
        with pytest.raises(ValueError):
            check_source(source, exact_types=True)


def test_e4_counter_required():
    item, cfg, h = fixture()
    item.update(
        experiment="E4",
        condition="warm",
        layout=["prefix", "task"],
        sections={"prefix": ["prefix"], "task": ["target"]},
    )
    jobs = schedule([item], cfg, h)
    assert len(jobs) == 20
    result, _ = outcome(jobs[0], Mock().exchange("", {}, timeout=10))
    assert {"cache_state_unverified", "short_fixed_workload"} <= set(result["flags"])


def test_pilot_counts_and_context():
    from experiments.utilisation_pilot import make_jobs

    jobs, registration = make_jobs()
    assert registration["requests"] == len(jobs) == 22
    assert sum(j["experiment"] == "E0" for j in jobs) == 20
    assert sum(j["expected_tokens"] == 4000 for j in jobs) == 2
    assert all(j["request"]["raw"] for j in jobs)
    assert all(
        j["expected_tokens"] + j["request"]["options"]["num_predict"]
        <= j["request"]["options"]["num_ctx"]
        for j in jobs
    )


def test_m3_review_stops_before_101_and_survives_resume(tmp_path):
    import json

    from prompt_energy.utilisation_checkpoint import checkpoint
    from prompt_energy.utilisation_plan import digest

    jobs = [{"key": str(i), "experiment": "M3", "model": "model"} for i in range(101)]
    rows = {j["key"]: j | {"wall_seconds": 10, "input_valid": True} for j in jobs[:99]}
    assert not checkpoint(tmp_path, jobs, rows, 5)
    rows["99"] = jobs[99] | {"wall_seconds": 10, "input_valid": False}
    assert checkpoint(tmp_path, jobs, rows, 5)
    assert checkpoint(tmp_path, jobs, rows, 5)
    report = json.loads((tmp_path / "m3-checkpoint.json").read_text())
    assert report["by_model"][0]["remaining_service_seconds"] == 15
    assert report["by_model"][0]["invalid_inputs"] == 1
    (tmp_path / "m3-review.json").write_text(
        json.dumps({"schedule_hash": digest(jobs), "checkpoint_calls": 100, "owner_approved": True})
    )
    assert not checkpoint(tmp_path, jobs, rows, 5)


def test_sweep_orders_are_fixed_complete_prefixes():
    import json

    from prompt_energy.utilisation_plan import ROOT

    orders = json.loads((ROOT / "studies/utilisation/task-orders.json").read_text())
    for sweep in orders["sweeps"].values():
        ids = sweep["task_order"]
        assert len(ids) == len(set(ids)) == 164
        assert set(ids) == {f"HumanEval/{i}" for i in range(164)}
        # Filtering a fixed independent eligibility mask preserves nesting.
        eligible = [tid for tid in ids if int(tid.split("/")[1]) % 2]
        assert eligible[:20] == eligible[:40][:20]


def test_extension_budget_is_a_hard_gate():
    from datetime import datetime, timedelta

    from prompt_energy.utilisation_extension import FREEZE, extension_gate

    now = FREEZE - timedelta(hours=10)
    assert extension_gate(now, 6 * 3600, 3600, [0.21])["timing_gate_passed"]
    rejected = extension_gate(now, 6 * 3600, 3601, [0.9])
    assert rejected["precision_trigger"] and not rejected["timing_gate_passed"]
    assert not extension_gate(now, 1, 1, [0.20])["precision_trigger"]
    assert not extension_gate(FREEZE, 0, 0, [0.9])["timing_gate_passed"]
    with pytest.raises(ValueError):
        extension_gate(datetime(2026, 11, 20), 0, 0, [])


def test_supervisor_hard_stops():
    from prompt_energy.utilisation_supervisor import hard_stop

    ok = {"flags": [], "call_failed": False, "energy_valid": True}
    assert hard_stop([ok] * 20, 6 * 1024**3) is None
    assert "disk" in hard_stop([], 4 * 1024**3)
    assert "90%" in hard_stop([ok] * 17 + [ok | {"energy_valid": False}] * 3, 6 * 1024**3)
    assert "3%" in hard_stop([ok] * 19 + [ok | {"call_failed": True}], 6 * 1024**3)
    assert "prompt" in hard_stop([ok | {"flags": ["input_count_mismatch"]}], 6 * 1024**3)


def test_exact_e0_swap_p():
    from prompt_energy.utilisation_e0_analysis import exact_swap_p

    assert exact_swap_p([0, 0]) == 1
    assert exact_swap_p([1, 1, 1]) == 0.25
    assert exact_swap_p([1, -1]) == 1


def test_supervisor_retry_budget_and_raw_preservation(tmp_path):
    import base64
    from types import SimpleNamespace

    from prompt_energy.utilisation_journal import read_jsonl
    from prompt_energy.utilisation_supervisor import Halt, generate_batch

    item, cfg, h = fixture()
    job = schedule([item], cfg, h)[:1]

    class Broken(Mock):
        def exchange(self, *args, **kwargs):
            envelope = super().exchange(*args, **kwargs)
            envelope["body_base64"] = base64.b64encode(b'{"error":"offline"}').decode()
            return envelope

    client = Broken()
    with pytest.raises(Halt, match="3%"):
        generate_batch(
            tmp_path,
            job,
            client,
            MockSensor(),
            5,
            sleep=lambda _: None,
            disk=lambda _: SimpleNamespace(free=10 * 1024**3),
        )
    assert client.calls == 6
    assert len(read_jsonl(tmp_path / "responses.jsonl")) == 6
    assert len(read_jsonl(tmp_path / "calls.jsonl")) == 1
    assert read_jsonl(tmp_path / "calls.jsonl")[0]["call_failed"]


def test_e0_analysis_keeps_task_pairing(tmp_path):
    from prompt_energy.utilisation_e0_analysis import analyse
    from prompt_energy.utilisation_journal import append_json

    for arm, passes in [("P1", [True, False, False]), ("P3_1", [True, True, False])]:
        for sample, passed in enumerate(passes):
            key = f"{arm}/{sample}"
            append_json(
                tmp_path / "calls.jsonl",
                {
                    "key": key,
                    "model": "model",
                    "task_id": "HumanEval/0",
                    "condition": arm,
                    "sample_idx": sample,
                    "input_valid": True,
                    "output_tokens": 10 if arm == "P1" else 20,
                    "energy": {"windows": {"post_load": {"adjusted_wh": 0.01}}},
                },
            )
            append_json(
                tmp_path / "scores.jsonl",
                {"key": key, "status": "passed" if passed else "failed", "functions": {}},
            )
    result = analyse(
        tmp_path, tmp_path / "analysis", heldout_policy={"name": "approved_E0_P1_sample0_holdout"}
    )["models"]["model"]
    assert result["complete_paired_tasks"] == 1
    assert result["mean_pass_difference"] == pytest.approx(1 / 3)
    assert result["output_tokens_difference"]["mean"] == 10
    assert result["table"]["both_pass"]["task_ids"] == ["HumanEval/0"]


def test_reference_sensitivity_keeps_primary_rows():
    from prompt_energy.utilisation_e0_analysis import reference_sensitivity

    rows = [
        {"task_id": "HumanEval/32", "pass_count_difference": 3},
        {"task_id": "HumanEval/0", "pass_count_difference": 0},
    ]
    result = reference_sensitivity(rows)
    assert len(rows) == 2
    assert result["retained_paired_tasks"] == 1
    assert result["excluded_from_paired"] == 1
    assert result["mean_pass_difference"] == 0
    assert result["ci95"] == [0, 0]


def test_frozen_m3_counts_and_midpoints():
    import json

    from prompt_energy.utilisation_plan import ROOT, load_config, schedule

    items = json.loads((ROOT / "studies/utilisation/stimuli/M3.json").read_text())
    assert len(items) == 164 * 2 * 3
    assert {i["condition"] for i in items} == {
        f"{f}/{n}" for f in ["irrelevant", "other_tasks", "near_duplicate"] for n in [1000, 4000]
    }
    for item in items:
        length = item["identity"]["context_length"]
        audit = item["identity"]["audit"]
        assert abs(audit["target_midpoint_token_approx"] - length / 2) <= 0.5
        assert all(v == length for v in item["prompt_tokens"].values())
    cfg, sha = load_config()
    jobs = schedule(items, cfg, sha)
    chosen = {f"HumanEval/{n}" for n in range(20)}
    assert len([j for j in jobs if j["task_id"] in chosen]) == 240


def test_explicit_repeat_abort_is_not_retried(tmp_path):
    import base64
    from types import SimpleNamespace

    from prompt_energy.utilisation_journal import read_jsonl
    from prompt_energy.utilisation_supervisor import Halt, generate_batch

    item, cfg, h = fixture()
    jobs = schedule([item], cfg, h)[:1]

    class Aborted(Mock):
        def exchange(self, *args, **kwargs):
            r = super().exchange(*args, **kwargs)
            r["http_status"] = 500
            r["body_base64"] = base64.b64encode(
                b'{"error":"prediction aborted, token repeat limit reached"}'
            ).decode()
            return r

    client = Aborted()
    with pytest.raises(Halt, match="3%"):
        generate_batch(
            tmp_path,
            jobs,
            client,
            MockSensor(),
            5,
            sleep=lambda _: None,
            disk=lambda _: SimpleNamespace(free=10 * 1024**3),
        )
    assert client.calls == 1
    row = read_jsonl(tmp_path / "calls.jsonl")[0]
    assert row["flags"] == ["generation_repeat_abort"] and row["input_valid"] is False
    assert len(read_jsonl(tmp_path / "responses.jsonl")) == 1


def test_drift_does_not_hide_original_hard_stop(tmp_path):
    from types import SimpleNamespace

    from prompt_energy.utilisation_journal import append_json
    from prompt_energy.utilisation_supervisor import Halt, generate_batch

    item, cfg, h = fixture()
    jobs = schedule([item], cfg, h)[:1]
    jobs[0]["expected_tokens"] = 31

    class DriftSensor(MockSensor):
        def start(self):
            append_json(
                tmp_path / "blocks.jsonl",
                {"event": "start", "block": self.block, "baseline": {"watts": 10}},
            )

        def close(self):
            append_json(
                tmp_path / "blocks.jsonl",
                {
                    "event": "end",
                    "block": self.block,
                    "baseline": {"watts": 12},
                    "drift_w": 2,
                    "flags": ["baseline_drift"],
                },
            )

    with pytest.raises(Halt, match="input-count mismatch") as result:
        generate_batch(
            tmp_path,
            jobs,
            Mock(),
            DriftSensor(),
            5,
            sleep=lambda _: None,
            disk=lambda _: SimpleNamespace(free=10 * 1024**3),
        )
    assert result.value.details["threshold_w"] == 1
    assert result.value.details["signed_drift_w"] == 2
    assert "input-count mismatch" in result.value.details["primary_error"]
