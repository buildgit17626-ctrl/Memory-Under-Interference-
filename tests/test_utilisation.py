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
