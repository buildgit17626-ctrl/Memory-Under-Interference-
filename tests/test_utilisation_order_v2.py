"""Offline tests of the proposed isolated-before-loaded execution order."""

import json
from types import SimpleNamespace

import pytest

from prompt_energy.utilisation_journal import append_json, read_jsonl
from prompt_energy.utilisation_order_v2 import (
    STAGES,
    baseline_catalogue,
    execute_v2,
    ordered_workflow,
    require_review,
)


def test_registered_order_and_no_extra_stage():
    events = []
    ordered_workflow({stage: lambda stage=stage: events.append(stage) for stage in STAGES})
    assert events == [
        "E0",
        "E0_analysis_and_eligibility",
        "isolated_baselines_40",
        "M3_generation_only_100",
        "checkpoint",
    ]
    with pytest.raises(ValueError):
        ordered_workflow({stage: lambda: None for stage in STAGES} | {"score_M3": lambda: None})


def test_failure_prevents_loaded_calls():
    events = []

    def fail():
        raise RuntimeError("isolated batch halted")

    operations = {stage: lambda stage=stage: events.append(stage) for stage in STAGES}
    operations["isolated_baselines_40"] = fail
    with pytest.raises(RuntimeError):
        ordered_workflow(operations)
    assert events == ["E0", "E0_analysis_and_eligibility"]


def test_pending_drift_disposition_prevents_activation(tmp_path):
    path = tmp_path / "review.json"
    record = {
        "amendment_sha256": "hash",
        "order_approved": False,
        "drift_block": "block",
        "energy_decision": None,
    }
    path.write_text(json.dumps(record))
    with pytest.raises(RuntimeError, match="Pending"):
        require_review(path, "hash", "block")
    record["order_approved"] = True
    path.write_text(json.dumps(record))
    with pytest.raises(RuntimeError, match="Pending"):
        require_review(path, "hash", "block")


def test_no_filler_baseline_preserves_decoding():
    source = {
        "key": "loaded",
        "model": "model",
        "task_id": "HumanEval/0",
        "condition": "near/1000",
        "request": {
            "prompt": "filler",
            "system": "system",
            "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 2048, "seed": 1729},
        },
        "identity": {"context_length": 1000},
    }
    tokenizer = SimpleNamespace(encode=lambda _: SimpleNamespace(ids=[1, 2, 3]))
    jobs = baseline_catalogue(
        {"HumanEval/0": {"entry_point": "f", "prompt": "def f(x):\n    'Return x.'"}},
        [source],
        tokenizer,
    )
    assert len(jobs) == 1 and jobs[0]["key"] != "loaded"
    assert jobs[0]["request"]["options"] == source["request"]["options"]
    assert "filler" not in jobs[0]["request"]["prompt"]
    assert jobs[0]["expected_tokens"] == 3
    assert source["request"]["prompt"] == "filler"


def test_full_revised_workflow_scores_only_e0(tmp_path, monkeypatch):
    import prompt_energy.utilisation_order_v2 as module

    events = []
    e0 = [{"key": "e0", "experiment": "E0"}]
    m3 = [
        {
            "key": f"{model}/{task}/{cell}",
            "model": model,
            "task_id": f"HumanEval/{task}",
            "experiment": "M3",
            "identity": {"context_length": 1000 if cell % 2 else 4000},
        }
        for model in ["m0", "m1"]
        for task in range(20)
        for cell in range(6)
    ]
    isolated = [
        {
            "key": f"iso/{model}/{task}",
            "model": model,
            "task_id": f"HumanEval/{task}",
            "experiment": "M3",
        }
        for model in ["m0", "m1"]
        for task in range(20)
    ]
    monkeypatch.setattr(module, "load_jobs", lambda path, *_: e0 if path == "e0" else m3)
    monkeypatch.setattr(module, "load_dataset", lambda *_: {})
    monkeypatch.setattr("prompt_energy.utilisation_supervisor.validate_pipeline", lambda *_: None)

    def generate(folder, jobs, *args, limit=100, **kwargs):
        done = {r["key"] for r in read_jsonl(folder / "calls.jsonl")}
        selected = [j for j in jobs if j["key"] not in done][: min(limit, 25)]
        events.append((folder.name, "generate", len(selected)))
        for job in selected:
            append_json(
                folder / "calls.jsonl", {**job, "wall_seconds": 1, "input_valid": True, "flags": []}
            )

    def score(folder, *_):
        events.append((folder.name, "score"))

    def analysis(_, out, **kwargs):
        events.append(("analysis", "labels"))
        out.mkdir()
        labels = {
            m: {f"HumanEval/{i}": {"solvable": True} for i in range(20)} for m in ["m0", "m1"]
        }
        (out / "heldout-labels.json").write_text(json.dumps(labels))

    def stop(root, reason, details):
        from prompt_energy.utilisation_outcome_access import evaluate, inspect_outputs

        for phase in ["M3", "M3-isolated"]:
            with pytest.raises(PermissionError):
                inspect_outputs(root / phase)
            with pytest.raises(PermissionError):
                evaluate(root / phase, {}, {})
        (root / "CHECKPOINT.md").write_text(reason)
        events.append(("checkpoint", details["m3_finished"]))
        assert details["isolated_baseline_calls"] == 40
        assert details["M3_scoring"] == "deferred"

    cfg = {
        "models": [{"tag": "m0"}, {"tag": "m1"}],
        "benchmark": {"dataset_sha256": "hash"},
        "scope": {"task_orders": "studies/utilisation/task-orders.json"},
        "_session_hwinfo_log": "unused",
    }
    pipeline = {"e0_stimuli": "e0", "m3_stimuli": "m3", "dataset": "unused", "heldout_policy": {}}
    execute_v2(
        tmp_path,
        pipeline,
        cfg,
        "hash",
        None,
        isolated,
        sensor_factory=lambda *_: None,
        generator=generate,
        scorer=score,
        analysis=analysis,
        checkpoint_writer=stop,
    )
    isolated_events = [e for e in events if e[:2] == ("M3-isolated", "generate")]
    loaded_events = [e for e in events if e[:2] == ("M3", "generate")]
    assert [e[2] for e in isolated_events] == [25, 15]
    assert [e[2] for e in loaded_events] == [25, 25, 25, 25]
    assert max(events.index(e) for e in isolated_events) < events.index(loaded_events[0])
    assert events[-1] == ("checkpoint", 100)
    assert all(event[0] == "E0" for event in events if event[1] == "score")
    assert len(read_jsonl(tmp_path / "M3/calls.jsonl")) == 100


def test_outcome_embargo_blocks_both_populations_until_checkpoint(tmp_path, monkeypatch):
    from prompt_energy.utilisation_outcome_access import (
        evaluate,
        initialise_embargo,
        inspect_outputs,
        publish_checkpoint,
    )

    initialise_embargo(tmp_path)
    scored = []
    monkeypatch.setattr(
        "prompt_energy.utilisation_eval.evaluate", lambda folder, *_: scored.append(folder.name)
    )
    for phase, n in [("M3-isolated", 40), ("M3", 100)]:
        folder = tmp_path / phase
        folder.mkdir()
        for i in range(n):
            append_json(folder / "calls.jsonl", {"key": str(i), "raw_output": "DO_NOT_REVEAL"})
        with pytest.raises(PermissionError):
            inspect_outputs(folder)
        with pytest.raises(PermissionError):
            evaluate(folder, {}, {})
    assert scored == []
    (tmp_path / "CHECKPOINT.md").write_text("Baseline power drift beyond registered threshold")
    with pytest.raises(ValueError, match="not the completed"):
        publish_checkpoint(tmp_path)
    for phase in ["M3-isolated", "M3"]:
        with pytest.raises(PermissionError):
            inspect_outputs(tmp_path / phase)
    (tmp_path / "CHECKPOINT.md").write_text(
        "STOP: 40 isolated baselines and 100 M3 generations; scoring deferred"
    )
    publish_checkpoint(tmp_path)
    assert len(inspect_outputs(tmp_path / "M3-isolated")) == 40
    assert len(inspect_outputs(tmp_path / "M3")) == 100
    evaluate(tmp_path / "M3", {}, {})
    assert scored == ["M3"]
    (tmp_path / "CHECKPOINT.md").write_text("replaced checkpoint")
    with pytest.raises(PermissionError):
        inspect_outputs(tmp_path / "M3")


def test_short_blocks_do_not_change_requested_total(monkeypatch):
    from prompt_energy import utilisation_reliability as module

    seen = []
    monkeypatch.setattr(
        module, "generate_batch", lambda *args, **kwargs: seen.append(kwargs["limit"])
    )
    module.generate_short_block(None, [], None, None, 5, limit=100)
    module.generate_short_block(None, [], None, None, 5, limit=15)
    assert seen == [25, 15]


def test_idle_stability_uses_unchanged_threshold():
    from prompt_energy.utilisation_reliability import stable_pair

    assert stable_pair(10, 11) == (True, 1)
    assert stable_pair(10, 11.01) == (False, 1)
    assert stable_pair(20, 22) == (True, 2)
    assert stable_pair(20, 22.01) == (False, 2)


def test_idle_check_retries_windows_without_model_calls(tmp_path, monkeypatch):
    from prompt_energy import utilisation_reliability as module
    from prompt_energy.utilisation_journal import read_jsonl

    windows = iter([{"watts": 10}, {"watts": 13}, {"watts": 13.5}])
    monkeypatch.setattr(module, "host_metadata", lambda: {})
    monkeypatch.setattr(module, "check_host", lambda _: None)
    monkeypatch.setattr(module, "preflight_log", lambda *_: {})
    monkeypatch.setattr(module, "baseline", lambda *args, **kwargs: next(windows))
    monkeypatch.setattr(module, "snapshot", lambda: [])
    sensor = module.SettledSensor(tmp_path / "sensor.csv", tmp_path, None)
    sensor.start()
    assert sensor.opening["watts"] == 13.5
    records = read_jsonl(tmp_path / "idle-checks.jsonl")
    assert len(records) == 3
    assert [r["stable_pair"] for r in records] == [False, False, True]
    assert not (tmp_path / "calls.jsonl").exists()
