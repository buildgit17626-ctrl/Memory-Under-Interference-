"""Continuation must preserve scientific settings, retries, censoring and pause."""

import ast
import inspect
from types import SimpleNamespace

import pytest

from experiments.config import TASK_IDS
from prompt_energy import continuation_worker, utilisation_supervisor
from prompt_energy.continuation_evaluation import validity_gate
from prompt_energy.continuation_queue import continuation_queue
from prompt_energy.preference_materials import POLICIES, format_adherence, preference_prompt
from prompt_energy.semantic_alternatives import alternative_catalog
from prompt_energy.utilisation_journal import read_jsonl


def test_fork_changes_only_calendar_freeze_not_generation_semantics():
    old = ast.parse(inspect.getsource(utilisation_supervisor.generate_batch)).body[0]
    new = ast.parse(inspect.getsource(continuation_worker.continue_batch)).body[0]
    old.name = new.name
    for node in ast.walk(old):
        if isinstance(node, ast.For):
            node.body = [
                x
                for x in node.body
                if not (isinstance(x, ast.ImportFrom) and x.module == "datetime")
                and not (isinstance(x, ast.If) and "FREEZE" in ast.unparse(x.test))
            ]
    assert ast.dump(old) == ast.dump(new)
    assert utilisation_supervisor.FREEZE == "2026-11-22T23:59:00+05:30"


def test_preferences_keep_history_target_and_query_without_solution_material():
    history = [f"history_{i}" for i in range(8)]
    prompts = {p: preference_prompt("target", "final_query", history, p) for p in POLICIES}
    for text in prompts.values():
        assert text.startswith("target\n") and text.endswith("\nfinal_query")
        assert all(text.count(h) == 1 for h in history)
    assert "USER PREFERENCE" not in prompts["no_preference"]
    assert prompts["replayed"].count("[USER PREFERENCE]") == 2
    assert prompts["corrected"].index("EARLIER USER PREFERENCE") < prompts["corrected"].index(
        "USER CORRECTION"
    )


@pytest.mark.parametrize(
    "text,expected",
    [
        ("def f(x):\n    return x", True),
        ("```python\ndef f(x):\n    return x\n```", False),
        ("Here is code:\ndef f(x):\n    return x", False),
        ("def other(x):\n    return x", False),
        ("", False),
    ],
)
def test_format_adherence_is_strict_unfenced_entry_proxy(text, expected):
    assert format_adherence(text, "f")["plain_code"] == expected


def test_every_semantic_alternative_has_independent_distinguishing_expectations():
    catalog = alternative_catalog()
    assert set(catalog) == set(TASK_IDS)
    for record in catalog.values():
        assert len(record["witnesses"]) >= 2
        assert any(w["target_expected"] != w["alternative_expected"] for w in record["witnesses"])
        assert ">>>" not in record["description"] and "assert " not in record["description"]


def mock_generation(monkeypatch, pause):
    client = SimpleNamespace(count=0, success=True, pause_on_call=False)

    def exchange(*args, **kwargs):
        client.count += 1
        if client.pause_on_call:
            pause.write_text("requested")
        return {"ok": client.success, "wall_seconds": 1}

    client.exchange = exchange
    monkeypatch.setattr(
        continuation_worker,
        "outcome",
        lambda job, raw: ({"input_valid": True, "flags": [], "raw_output": "def f(): pass"}, {})
        if raw["ok"]
        else ({"flags": ["api_error"]}, None),
    )
    monkeypatch.setattr(
        continuation_worker.continue_batch,
        "__kwdefaults__",
        {**continuation_worker.continue_batch.__kwdefaults__, "sleep": lambda _: None},
    )

    class Sensor:
        block = "mock-block"
        closed = 0

        def __init__(self, *args):
            pass

        def start(self):
            pass

        def before_request(self):
            pass

        def measure(self, raw, response):
            return {"windows": {"post_load": {"raw_wh": 1, "net_wh": 0.5}}}

        def close(self):
            Sensor.closed += 1

    return client, Sensor


def test_queue_continues_across_blocks_and_skips_finished_calls(tmp_path, monkeypatch):
    pause = tmp_path / "PAUSE"
    client, sensor = mock_generation(monkeypatch, pause)
    jobs = [{"key": str(i), "timeout": 900, "request": {}} for i in range(60)]
    assert (
        continuation_queue(tmp_path, jobs, client, tmp_path / "sensor", pause, sensor=sensor)[
            "completed"
        ]
        == 60
    )
    assert client.count == 60 and sensor.closed == 3
    result = continuation_queue(tmp_path, jobs, client, tmp_path / "sensor", pause, sensor=sensor)
    assert result["elapsed_time_cutoff"] is None and client.count == 60


def test_user_pause_preserves_saved_response_and_closes_block(tmp_path, monkeypatch):
    pause = tmp_path / "PAUSE"
    client, sensor = mock_generation(monkeypatch, pause)
    client.pause_on_call = True
    jobs = [{"key": str(i), "timeout": 900, "request": {}} for i in range(3)]
    result = continuation_queue(tmp_path, jobs, client, tmp_path / "sensor", pause, sensor=sensor)
    assert result["reason"] == "user_pause" and result["completed"] == 1
    assert client.count == 1 and sensor.closed == 1
    assert len(read_jsonl(tmp_path / "responses.jsonl")) == 1


def test_pause_before_retry_keeps_attempt_without_failed_logical_row(tmp_path, monkeypatch):
    pause = tmp_path / "PAUSE"
    client, sensor = mock_generation(monkeypatch, pause)
    client.success, client.pause_on_call = False, True
    jobs = [{"key": "a", "timeout": 900, "request": {}}]
    result = continuation_queue(tmp_path, jobs, client, tmp_path / "sensor", pause, sensor=sensor)
    assert result["completed"] == 0 and len(read_jsonl(tmp_path / "starts.jsonl")) == 1
    # Explicit test-user resume; the queue itself never removes a pause.
    pause.unlink()
    client.success, client.pause_on_call = True, False
    result = continuation_queue(tmp_path, jobs, client, tmp_path / "sensor", pause, sensor=sensor)
    assert result["completed"] == 1 and client.count == 2
    assert read_jsonl(tmp_path / "calls.jsonl")[0]["attempts"] == 2


def test_archived_calendar_stop_still_prevents_model_calls(tmp_path, monkeypatch):
    client, sensor = mock_generation(monkeypatch, tmp_path / "PAUSE")
    monkeypatch.setattr(utilisation_supervisor, "FREEZE", "2000-01-01T00:00:00+05:30")
    with pytest.raises(utilisation_supervisor.Halt, match="freeze reached"):
        utilisation_supervisor.generate_batch(
            tmp_path,
            [{"key": "a", "request": {}, "timeout": 900}],
            client,
            sensor(),
            0,
            sleep=lambda _: None,
        )
    assert client.count == 0


def test_pilot_gate_ignores_success_but_blocks_caps_and_infrastructure():
    calls = [
        {"key": str(i), "input_valid": True, "flags": [], "energy_valid": True} for i in range(3)
    ]
    scores = [{"key": str(i), "status": "failed", "functions": {}} for i in range(3)]
    assert validity_gate(calls, scores, 3)["pass"]
    for s in scores:
        s["status"] = "passed"
    assert validity_gate(calls, scores, 3)["pass"]
    calls[0]["flags"] = ["output_cap"]
    assert not validity_gate(calls, scores, 3)["pass"]
    calls[0]["flags"] = []
    scores[0]["functions"] = {"task": {"base": {"status": "infrastructure_error"}}}
    assert not validity_gate(calls, scores, 3)["pass"]


@pytest.mark.parametrize("fails", [False, True])
def test_watchdog_keeps_sleep_inhibited_across_work_and_releases_on_exit(monkeypatch, fails):
    from experiments import watch_continuation as module

    states = []

    def power(state):
        states.append(state)
        return 1

    def work(_):
        assert states == [0x80000001]
        if fails:
            raise RuntimeError("mock worker failure")

    monkeypatch.setattr(
        module,
        "ctypes",
        SimpleNamespace(
            windll=SimpleNamespace(kernel32=SimpleNamespace(SetThreadExecutionState=power))
        ),
    )
    monkeypatch.setattr(module, "watch", work)
    monkeypatch.setattr("sys.argv", ["watch", "--hwinfo-log", "sensor.csv"])
    if fails:
        with pytest.raises(RuntimeError, match="mock worker failure"):
            module.main()
    else:
        module.main()
    assert states == [0x80000001, 0x80000000]
