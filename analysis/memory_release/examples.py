"""Trace publication examples to saved public records without running candidate code."""

import ast
import hashlib
import json

from analysis.memory_audit.records import indexed, save_json
from analysis.memory_release.common import RELEASE, directories

EXAMPLE_KEY = "34303c8e4927afd811965083065734287a537b4b782b0c47886aa0bd8a9c6b7d"
PROMPTS = (
    ("r2-competing", "continuation-v3/R2/full", EXAMPLE_KEY),
    (
        "r1-oracle",
        "r1-v2/full",
        "dd7667ecb15441f30abeb44a35487f04e4f29303d1d67b9680d732df78984b36",
    ),
    (
        "r1-target-query",
        "r1-v2/full",
        "3fddbabc51a0fabc427777033aee91a43b1adf4e20694fc3ac86ace5ca69dbe6",
    ),
    (
        "e5-immediate",
        "continuation-v3/E5/full",
        "d8c0d20e0645dd09e79939f73159c6edea060ca12f95aed86f511d0ac6562ca6",
    ),
)


def omit_function_docstring(code: str) -> str:
    """Remove only a function's docstring lines; retain its executable text verbatim."""
    tree = ast.parse(code)
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
    if ast.get_docstring(function) is None:
        return code
    doc = function.body[0]
    lines = code.splitlines(keepends=True)
    return "".join(lines[: doc.lineno - 1] + lines[doc.end_lineno :])


def main() -> None:
    directories()
    destination = RELEASE / "examples"
    destination.mkdir(exist_ok=True)
    records = []
    for name, folder, key in PROMPTS:
        relative = "data/raw/results/utilisation/" + folder + "/calls.jsonl"
        call = indexed(RELEASE / relative)[key]
        # UTF-8 writing without a final newline preserves the exact saved prompt string.
        data = call["request"]["prompt"].encode("utf-8")
        (destination / (name + ".txt")).write_bytes(data)
        records.append(
            {
                "name": name,
                "source": relative,
                "call_key": key,
                "task": call["task_id"],
                "model": call["model"],
                "condition": call["condition"],
                "prompt_sha256": hashlib.sha256(data).hexdigest(),
                "prompt_tokens": call["prompt_tokens"],
                "system": call["request"].get("system"),
                "options": call["request"]["options"],
            }
        )
    call = indexed(RELEASE / "data/raw/results/utilisation/continuation-v3/R2/full/calls.jsonl")[
        EXAMPLE_KEY
    ]
    audit = json.loads((RELEASE / "data/audit/representative-code-audit.json").read_text())
    example = next(row for row in audit if row["call_key"] == EXAMPLE_KEY)
    code = call["extracted"]["has_close_elements"]
    if code != example["code"] or example["cell"] != "distractor_only":
        raise ValueError("Worked example does not match the audited saved response")
    (destination / "generated-code.txt").write_bytes(code.encode("utf-8"))
    (destination / "generated-code-excerpt.txt").write_bytes(
        omit_function_docstring(code).encode("utf-8")
    )
    target = (
        call["request"]["prompt"]
        .split("[TARGET SPECIFICATION]\n", 1)[1]
        .split("\n[BACKGROUND SPECIFICATIONS", 1)[0]
    )
    (destination / "target-specification.txt").write_bytes(target.encode("utf-8"))
    prompt = call["request"]["prompt"]
    alternative_start = prompt.index("from typing import List", prompt.index("[BACKGROUND"))
    first_alternative_end = prompt.index('"""', prompt.index('"""', alternative_start) + 3) + 3
    padding = prompt.index("[NEUTRAL PADDING]")
    omitted = prompt[first_alternative_end:padding]
    repetition_count = prompt.count("def has_close_elements_alternative(")
    excerpt = (
        prompt[:first_alternative_end]
        + f"\n\n[EDITORIAL OMISSION: {repetition_count - 1} further identical "
        + "alternative descriptions]"
        + "\n\n"
        + prompt[padding:]
    )
    if omitted.count("def has_close_elements_alternative(") != repetition_count - 1:
        raise ValueError("Unrecognized repeated-background layout")
    (destination / "r2-layout-excerpt.txt").write_bytes(excerpt.encode("utf-8"))
    e5 = (destination / "e5-immediate.txt").read_text()
    last_preference = e5.rindex("[USER PREFERENCE]")
    e5_excerpt = (
        e5.split("[EARLIER TASK SPECIFICATION]", 1)[0]
        + "[EDITORIAL OMISSION: fixed earlier-task descriptions]\n\n"
        + e5[last_preference:]
    )
    (destination / "e5-layout-excerpt.txt").write_bytes(e5_excerpt.encode("utf-8"))
    score = indexed(RELEASE / "data/raw/results/utilisation/continuation-v3/R2/full/scores.jsonl")[
        EXAMPLE_KEY
    ]
    cross = [
        json.loads(line)
        for line in (RELEASE / "data/audit/secondary-scores.jsonl").read_text().splitlines()
        if line
    ]
    saved_cross = [row for row in cross if row.get("call_key") == EXAMPLE_KEY]
    if not any(row["operation"] == "alternative_suite" and row["passed"] for row in saved_cross):
        raise ValueError("Saved alternative-suite evaluation missing for example")
    if score["status"] != "failed":
        raise ValueError("Worked example is no longer a recorded target failure")
    witness_scores = [
        json.loads(line)
        for line in (RELEASE / "data/audit/representative-witness-scores.jsonl")
        .read_text()
        .splitlines()
        if line
    ]
    evidence = {
        "selection": "Existing deterministic audit example; illustrative, not a frequency estimate",
        "original_audit": "data/audit/representative-code-audit.json",
        "example": example,
        "target_score": score,
        "alternative_score": saved_cross,
        "witness_scores": [row for row in witness_scores if row["call_key"] == EXAMPLE_KEY],
        "rendered_prompts": records,
        "new_inference_or_candidate_execution": False,
        "code_excerpt_transformation": "Function docstring lines omitted; other text unchanged",
        "r2_alternative_description_copies": repetition_count,
    }
    save_json(destination / "provenance.json", evidence)
    print(json.dumps({"rendered_prompts": len(records), "worked_example_key": EXAMPLE_KEY}))


if __name__ == "__main__":
    main()
