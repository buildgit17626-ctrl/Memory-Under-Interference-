"""Secondary code/format audits and sandboxed saved-output scoring; no inference."""

import ast
import io
import json
import re
import tokenize
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.memory_audit.design import ROOT, STAGES, stage_path
from analysis.memory_audit.records import indexed, save_json
from analysis.memory_audit.statistics import components, interval, paired
from experiments.prepare_continuation import source
from prompt_energy.preference_materials import format_adherence
from prompt_energy.utilisation_eval import score_function
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import digest


def complete_blocks(text: str) -> tuple[list[str], str]:
    pattern = r"(?ms)^\s*```(?:python|py)?\s*\n(.*?)^\s*```\s*$"
    blocks = re.findall(pattern, text)
    return blocks, re.sub(pattern, "", text).strip()


def format_features(raw: str, extracted: str, entry: str) -> dict:
    blocks, outside = complete_blocks(raw)
    try:
        tree = ast.parse(extracted)
        parseable = any(isinstance(n, ast.FunctionDef) and n.name == entry for n in tree.body)
        docstrings = sum(
            isinstance(n, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
            and ast.get_docstring(n) is not None
            for n in ast.walk(tree)
        )
        comments = sum(
            t.type == tokenize.COMMENT
            for t in tokenize.generate_tokens(io.StringIO(extracted).readline)
        )
    except (SyntaxError, ValueError, tokenize.TokenError, IndentationError, RecursionError):
        parseable, docstrings, comments = False, None, None
    fence_tolerant = parseable and (not outside if blocks else raw.strip() == extracted.strip())
    return {
        **format_adherence(raw, entry),
        "complete_fences": len(blocks),
        "outside_fence_text": bool(outside) if blocks else False,
        "comment_tokens": comments,
        "docstrings": docstrings,
        "fence_tolerant_syntax_adherence": bool(fence_tolerant),
        "comment_docstring_free_proxy": bool(fence_tolerant and comments == docstrings == 0),
        "boundary": "Mechanical features; comments/docstrings are not automatically explanations.",
    }


def score_record(task: dict, code: str, cfg: dict, seed: int) -> dict:
    parts = score_function(task, code, cfg["evaluation"], seed)
    infrastructure = any(p["status"] == "infrastructure_error" for p in parts.values())
    return {
        "partitions": parts,
        "passed": None if infrastructure else all(p["status"] == "passed" for p in parts.values()),
    }


def secondary_scoring(destination: Path) -> None:
    """Append separate keyed scores. Existing recorded outcomes never change."""
    cfg, tasks, _ = source()
    alternatives = json.loads(
        (ROOT / "studies/utilisation/continuation-v3/R2/alternatives.json").read_text()
    )
    target = destination / "secondary-scores.jsonl"
    done = indexed(target)
    for stage in STAGES:
        if stage.phase not in {"main", "partial"} or stage.name.startswith("E4"):
            continue
        calls = indexed(stage_path(stage) / "calls.jsonl")
        for call in calls.values():
            if not call["input_valid"] or call.get("call_failed"):
                continue
            operations = []
            if stage.name == "M3R2" and "output_cap" not in call["flags"]:
                tid = call["task_id"]
                operations.append(
                    (
                        "alternative_suite",
                        tid,
                        alternatives[tid]["row"],
                        call["extracted"][tasks[tid]["entry_point"]],
                    )
                )
            for tid in call["identity"].get("task_ids", [call["task_id"]]):
                entry = tasks[tid]["entry_point"]
                original = call["extracted"][entry]
                if "output_cap" in call["flags"]:
                    operations.append(
                        ("cap_salvage_original_extraction", tid, tasks[tid], original)
                    )
                blocks, _ = complete_blocks(call.get("raw_output") or "")
                if len(blocks) > 1:
                    merged = "\n\n".join(blocks)
                    try:
                        tree = ast.parse(merged)
                    except (SyntaxError, ValueError, RecursionError):
                        continue
                    if any(isinstance(n, ast.FunctionDef) and n.name == entry for n in tree.body):
                        if merged.strip() != original.strip():
                            operations.append(("merged_complete_fences", tid, tasks[tid], merged))
            for operation, tid, task, code in operations:
                key = digest([operation, call["key"], tid, task, code, cfg["evaluation"]])
                if key in done:
                    continue
                record = {
                    "key": key,
                    "operation": operation,
                    "stage": stage.name,
                    "call_key": call["key"],
                    "task": tid,
                    "code_sha256": digest(code),
                    "suite_sha256": digest(task),
                    "analysis_label": "posthoc scoring audit",
                    **score_record(task, code, cfg, call["seed"]),
                }
                append_json(target, record)
                done[key] = record
                if len(done) % 25 == 0:
                    print(
                        json.dumps({"secondary_scores_saved": len(done), "operation": operation}),
                        flush=True,
                    )


def audit_prompts(frame: pd.DataFrame, destination: Path) -> pd.DataFrame:
    _, tasks, _ = source()
    e5rows, promptrows = [], []
    for name, folder in (("E5", "continuation-v3/E5/full"), ("R1", "r1-v2/full")):
        root = ROOT / "results/utilisation" / folder
        original = indexed(root / "adherence.jsonl")
        for call in indexed(root / "calls.jsonl").values():
            tid, entry = call["task_id"], tasks[call["task_id"]]["entry_point"]
            prompt = call["request"]["prompt"]
            if name == "E5":
                features = format_features(
                    call.get("raw_output") or "", call["extracted"][entry], entry
                )
                expected = original[call["key"]]
                if features["plain_code"] != expected["plain_code"]:
                    raise ValueError("Stored E5 primary adherence mismatch")
                e5rows.append(
                    {
                        "key": call["key"],
                        "model": call["model"],
                        "task": tid,
                        "condition": call["condition"],
                        **features,
                    }
                )
            else:
                expected = "\n".join(
                    [
                        "[TARGET SPECIFICATION]\n" + tasks[tid]["prompt"],
                        "[USER PREFERENCE]\nReturn only Python code, without explanation.",
                        f"[CURRENT QUERY]\nComplete the function {entry}.",
                    ]
                )
                promptrows.append(
                    {
                        "key": call["key"],
                        "task": tid,
                        "model": call["model"],
                        "policy": call["condition"],
                        "prompt_tokens": call["prompt_tokens"],
                        "code_only_present": "Return only Python code, without explanation."
                        in prompt,
                        "target_spec_occurrences": prompt.count(tasks[tid]["prompt"]),
                        "target_preference_query_exact_equivalent": prompt == expected,
                        "prompt_sha256": digest(prompt),
                    }
                )
    e5 = pd.DataFrame(e5rows)
    e5.to_csv(destination / "e5-format-audit.csv", index=False)
    pd.DataFrame(promptrows).to_csv(destination / "r1-prompt-audit.csv", index=False)
    columns = {
        "plain_code": "adherence",
        "fence_tolerant_syntax_adherence": "adherence_fence_tolerant",
        "comment_docstring_free_proxy": "adherence_strict_proxy",
    }
    for old, new in columns.items():
        mapping = e5.set_index("key")[old].astype(float)
        frame[new] = frame["key"].map(mapping)
    joined = e5.merge(frame[["key", "passed", "capped"]], on="key", validate="one_to_one")
    joined["joint_primary_correct_and_adherent"] = (joined.passed == 1) & joined.plain_code
    joined["joint_fence_tolerant"] = (joined.passed == 1) & joined.fence_tolerant_syntax_adherence
    joined.groupby(["model", "condition"]).agg(
        attempts=("key", "size"),
        adherence=("plain_code", "sum"),
        fence_tolerant=("fence_tolerant_syntax_adherence", "sum"),
        comments=("comment_tokens", lambda s: (s.fillna(0) > 0).sum()),
        docstrings=("docstrings", lambda s: (s.fillna(0) > 0).sum()),
        joint=("joint_primary_correct_and_adherent", "sum"),
        joint_fence_tolerant=("joint_fence_tolerant", "sum"),
    ).to_csv(destination / "e5-joint-outcomes.csv")
    return frame


def bundle_audit(frame: pd.DataFrame, funcs: pd.DataFrame, destination: Path) -> None:
    m1 = frame[frame.stage == "M1"]
    isolation = funcs[(funcs.stage == "M1") & (funcs.condition == "isolated")].set_index(
        ["model", "task"]
    )
    output = []
    for (model, condition), group in m1[m1.condition.str.startswith("active/")].groupby(
        ["model", "condition"]
    ):
        observed, baseline, whole, isolated_whole, rows = [], [], [], [], []
        bundles = []
        for _, call in group.iterrows():
            members = json.loads(call.bundle_members)
            bundles.append(members)
            candidate = funcs[(funcs.stage == "M1") & (funcs["key"] == call["key"])]
            control = [float(isolation.loc[(model, t)].passed) for t in members]
            vals = candidate.passed.to_numpy(dtype=float)
            if np.isfinite(vals).all() and np.isfinite(control).all():
                observed.append(float(vals.mean()))
                baseline.append(float(np.mean(control)))
                whole.append(float(np.all(vals == 1)))
                isolated_whole.append(float(np.all(np.array(control) == 1)))
            rows.append(
                {
                    "call_key": call["key"],
                    "members": members,
                    "function_observations": len(vals),
                    "component_isolation_passes": control,
                }
            )
        graph = components(bundles)
        function_diff = paired(np.array(observed), np.array(baseline))
        whole_diff = paired(np.array(whole), np.array(isolated_whole), binary_test=True)
        output.append(
            {
                "model": model,
                "condition": condition,
                "bundles": len(group),
                "membership_components": graph,
                "component_count": len(graph),
                "function_fraction_difference_conditional": function_diff,
                "whole_bundle_difference_conditional": whole_diff,
                "robust_component_interval": None if len(graph) < 2 else "not implemented",
                "reason": "One membership component cannot identify component-level uncertainty."
                if len(graph) < 2
                else "Overlapping membership retained.",
                "sources": rows,
            }
        )
    from analysis.memory_audit.statistics import holm

    for endpoint in (
        "function_fraction_difference_conditional",
        "whole_bundle_difference_conditional",
    ):
        for row, adjusted in zip(
            output, holm([r[endpoint]["p_value"] for r in output]), strict=True
        ):
            row[endpoint]["holm_family8_p"] = adjusted
    save_json(destination / "m1-bundle-dependencies.json", output)


def partial_cache_audit(frame: pd.DataFrame, destination: Path) -> None:
    output = []
    partial = frame[frame.stage == "E4_partial"].copy()
    partial["prefix"] = partial.identity.map(lambda s: json.loads(s)["prefix_tokens"])
    partial["state"] = partial.condition.str.split("/").str[0]
    for (model, prefix), g in partial.groupby(["model", "prefix"]):
        warm, cold = (
            g[g.state == "warm"].set_index("repeat"),
            g[g.state == "cold"].set_index("repeat"),
        )
        ids = sorted(set(warm.index) & set(cold.index))
        values = {}
        for metric in ("gross_wh", "net_wh", "prefill_s", "decode_s", "wall_s"):
            values[metric] = interval((warm.loc[ids, metric] - cold.loc[ids, metric]).to_numpy())
        output.append(
            {
                "model": model,
                "prefix_tokens": int(prefix),
                "warm_calls": len(warm),
                "cold_calls": len(cold),
                "paired_repeats": ids,
                "warm_unmatched": sorted(set(warm.index) - set(cold.index)),
                "cold_unmatched": sorted(set(cold.index) - set(warm.index)),
                "warm_minus_cold": values,
                "analysis_label": "posthoc partial-run repeatability; not completed E4 inference",
                "warning": "Few paired repeats; no task population or sensor-calibration interval.",
            }
        )
    save_json(destination / "e4-partial-paired.json", output)


def cross_audit(frame: pd.DataFrame, destination: Path) -> None:
    secondary = indexed(destination / "secondary-scores.jsonl")
    alternative = {
        r["call_key"]: r for r in secondary.values() if r["operation"] == "alternative_suite"
    }
    rows = []
    for _, call in frame[frame.stage == "M3R2"].iterrows():
        extra = alternative.get(call["key"])
        alt = extra["passed"] if extra else None
        if pd.isna(call.passed) or call.capped or alt is None:
            cell = "invalid_or_censored"
        elif call.passed == 1:
            cell = "both_pass" if alt else "target_only"
        else:
            cell = "distractor_only" if alt else "both_fail"
        rows.append(
            {
                "key": call["key"],
                "model": call.model,
                "condition": call.condition,
                "task": call.task,
                "target_pass": call.passed,
                "distractor_pass": alt,
                "cell": cell,
                "distractor_only": float(cell == "distractor_only")
                if cell != "invalid_or_censored"
                else np.nan,
            }
        )
    cross = pd.DataFrame(rows)
    cross.to_csv(destination / "cross-pass-per-response.csv", index=False)
    cross.groupby(["model", "condition", "cell"]).size().rename("count").to_csv(
        destination / "cross-pass-counts.csv"
    )
    effects = []
    for model, g in cross.groupby("model"):
        a = (
            g[g.condition.str.startswith("near_duplicate_")]
            .groupby("task")
            .distractor_only.agg(["mean", "count"])
        )
        for control_name, mask in (
            ("isolation", g.condition == "isolated"),
            ("irrelevant", g.condition.str.startswith("irrelevant_")),
        ):
            b = g[mask].groupby("task").distractor_only.agg(["mean", "count"])
            ids = sorted(
                set(a[a["count"] == 4].index)
                & set(b[b["count"] == (1 if control_name == "isolation" else 4)].index)
            )
            effects.append(
                {
                    "model": model,
                    "comparison": "near-minus-" + control_name,
                    "analysis_label": "posthoc mechanism comparison",
                    **paired(a.loc[ids, "mean"].to_numpy(), b.loc[ids, "mean"].to_numpy()),
                    "task_ids": ids,
                }
            )
    from analysis.memory_audit.statistics import holm

    for row, adjusted in zip(effects, holm([r["p_value"] for r in effects]), strict=True):
        row["holm_family4_p"] = adjusted
    save_json(destination / "cross-pass-effects.json", effects)
