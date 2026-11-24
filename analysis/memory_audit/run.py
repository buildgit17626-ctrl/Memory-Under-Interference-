"""Versioned read-only scientific audit. Never contacts Ollama for generation."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from analysis.memory_audit.design import DESTINATION, ROOT
from analysis.memory_audit.effects import run_effects, summaries
from analysis.memory_audit.mechanisms import (
    audit_prompts,
    bundle_audit,
    cross_audit,
    partial_cache_audit,
    secondary_scoring,
)
from analysis.memory_audit.records import load_evidence, save_json
from analysis.memory_audit.report import write_report
from analysis.memory_audit.robustness import (
    energy_sensitivities,
    ratio_effects,
    scoring_sensitivities,
)
from analysis.memory_audit.sensors import audit_sensors, freeze_inputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "step",
        choices=[
            "freeze",
            "records",
            "secondary",
            "sensors",
            "effects",
            "summaries",
            "schedules",
            "examples",
            "supplement",
            "environment",
            "robustness",
            "report",
            "all",
        ],
    )
    args = parser.parse_args()
    if not (ROOT / "results/utilisation/continuation-v3/PAUSE").exists():
        raise RuntimeError("Generation must remain paused throughout this audit")
    DESTINATION.mkdir(parents=True, exist_ok=True)
    if args.step in {"freeze", "all"}:
        from experiments.run_e4_schema import verify
        from experiments.run_m1_r1_chain import verify as verify_r1

        verify()
        subprocess.run([sys.executable, "-m", "experiments.run_full_m1", "check"], check=True)
        verify_r1()
        manifest = freeze_inputs(DESTINATION)
        save_json(
            DESTINATION / "freeze-status.json",
            {
                "files": len(manifest),
                "bytes": sum(r["bytes"] for r in manifest.values()),
                "generation_paused": True,
            },
        )
    if args.step in {"records", "effects", "robustness", "all"}:
        frame, functions, inventory, issues = load_evidence(DESTINATION)
        print(
            json.dumps({"inventory": inventory, "integrity_issue_count": len(issues)}), flush=True
        )
    if args.step in {"secondary", "all"}:
        secondary_scoring(DESTINATION)
    if args.step in {"sensors", "all"}:
        audit_sensors(DESTINATION)
    if args.step in {"schedules", "all"}:
        from analysis.memory_audit.provenance import check_schedules

        check_schedules(DESTINATION)
    if args.step in {"effects", "all"}:
        frame = audit_prompts(frame, DESTINATION)
        # Split synthetic cache states by prefix; do not pool different probes as one condition.
        for i in frame.index[frame.stage.str.startswith("E4")]:
            identity = json.loads(frame.at[i, "identity"])
            frame.at[i, "condition"] += "/prefix" + str(identity.get("prefix_tokens"))
        frame.to_csv(DESTINATION / "calls-with-adherence.csv", index=False)
        condition_rows = summaries(frame)
        save_json(DESTINATION / "conditions.json", condition_rows)
        import pandas as pd

        pd.json_normalize(condition_rows, sep=".").to_csv(
            DESTINATION / "conditions.csv", index=False
        )
        run_effects(frame, DESTINATION)
        bundle_audit(frame, functions, DESTINATION)
        partial_cache_audit(frame, DESTINATION)
        if (DESTINATION / "secondary-scores.jsonl").exists():
            cross_audit(frame, DESTINATION)
    if args.step in {"robustness", "all"}:
        frame = audit_prompts(frame, DESTINATION)
        for i in frame.index[frame.stage.str.startswith("E4")]:
            if "/prefix" not in frame.at[i, "condition"]:
                frame.at[i, "condition"] += "/prefix" + str(
                    json.loads(frame.at[i, "identity"]).get("prefix_tokens")
                )
        energy_sensitivities(frame, DESTINATION)
        scoring_sensitivities(frame, functions, DESTINATION)
        ratio_effects(frame, DESTINATION)
        partial_cache_audit(frame, DESTINATION)
    if args.step in {"summaries"}:
        import pandas as pd

        frame = pd.read_csv(DESTINATION / "calls-with-adherence.csv")
        condition_rows = summaries(frame)
        save_json(DESTINATION / "conditions.json", condition_rows)
        pd.json_normalize(condition_rows, sep=".").to_csv(
            DESTINATION / "conditions.csv", index=False
        )
    if args.step in {"examples", "all"}:
        from analysis.memory_audit.examples import audit_examples

        audit_examples(DESTINATION)
    if args.step in {"supplement", "all"}:
        from analysis.memory_audit.supplement import supplemental_controls

        supplemental_controls(DESTINATION)
    if args.step in {"environment", "all"}:
        from analysis.memory_audit.environment import environment_audit

        environment_audit(DESTINATION)
    if args.step in {"report", "all"}:
        write_report(DESTINATION)
        from analysis.memory_audit.review import write_review

        write_review(DESTINATION)
    print(json.dumps({"finished_step": args.step, "output": str(DESTINATION)}), flush=True)


if __name__ == "__main__":
    main()
