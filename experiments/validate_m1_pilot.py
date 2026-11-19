"""Validate new reference bundles in restricted workers; no Ollama calls."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from prompt_energy.utilisation_eval import load_dataset, score_function
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_plan import ROOT, digest, load_config
from prompt_energy.utilisation_run import by_key


def main() -> None:
    cfg, _ = load_config()
    tasks = load_dataset(
        ROOT / "results/utilisation/validation/HumanEvalPlus.jsonl.gz",
        cfg["benchmark"]["dataset_sha256"],
    )
    stimulus = ROOT / "studies/utilisation/stimuli/M1-pilot.json"
    items = json.loads(stimulus.read_text())
    root = ROOT / "results/utilisation/m1-pilot-validation"
    root.mkdir(parents=True, exist_ok=True)
    path = root / "references.jsonl"
    done = by_key(path)
    expected = set()
    for item in items:
        if not (item["condition"] == "isolated" or item["condition"].startswith("active/")):
            continue
        ids = item["identity"]["task_ids"]
        code = "\n\n".join(tasks[tid]["prompt"] + tasks[tid]["canonical_solution"] for tid in ids)
        for tid in ids:
            key = digest([ids, tid, code, cfg["evaluation"], cfg["benchmark"]["dataset_sha256"]])
            expected.add(key)
            if key not in done:
                partitions = score_function(tasks[tid], code, cfg["evaluation"], 1729)
                row = {"key": key, "task_id": tid, "bundle_task_ids": ids, "partitions": partitions}
                append_json(path, row)
                done[key] = row
    failed = [
        key
        for key in expected
        if any(x["status"] != "passed" for x in done[key]["partitions"].values())
    ]
    result = {
        "checks": len(expected),
        "passed": len(expected) - len(failed),
        "failed_keys": failed,
        "stimuli_hash": digest(items),
        "no_model_calls": True,
    }
    (root / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
