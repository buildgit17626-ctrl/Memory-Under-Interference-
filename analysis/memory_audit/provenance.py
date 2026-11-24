"""Compare saved calls with frozen offline schedules, never a live runtime."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from analysis.memory_audit.design import DESTINATION, ROOT, STAGES, stage_path
from analysis.memory_audit.records import indexed, save_json


def check_schedules(destination=DESTINATION):
    from experiments.prepare_full_m1 import BASE, configuration
    from experiments.run_continuation import verify as continuation
    from experiments.run_e4_schema import verify as schema
    from experiments.run_m1_r1_chain import verify as retention
    from experiments.run_remaining import verify as remaining
    from prompt_energy.utilisation_order_v2 import select_m3
    from prompt_energy.utilisation_plan import load_config, schedule

    def read(path):
        return json.loads((ROOT / path).read_text())

    cfg, checksum = load_config()
    expected = {
        "E0": schedule(read("studies/utilisation/stimuli/E0.json"), cfg, checksum),
        "M1_pilot": schedule(read("studies/utilisation/stimuli/M1-pilot.json"), cfg, checksum),
        "harness_pilot": read("results/utilisation/pilot/pilot-jobs.json"),
    }
    labels = read("results/utilisation/supervised/analysis/heldout-labels.json")
    order = read(cfg["scope"]["task_orders"])["sweeps"]["M3"]["task_order"]
    expected["M3_initial"] = select_m3(
        schedule(read("studies/utilisation/stimuli/M3.json"), cfg, checksum),
        labels,
        order,
        cfg["models"],
    )
    pairs = {(r["model"], r["task_id"]) for r in expected["M3_initial"]}
    expected["M3_isolated"] = [
        r
        for r in read("studies/utilisation/stimuli/M3-isolated-v2.json")
        if (r["model"], r["task_id"]) in pairs
    ]
    m1_cfg, m1_sha = configuration()
    expected["M1"] = schedule(json.loads((BASE / "stimuli.json").read_text()), m1_cfg, m1_sha)
    for phase, (_, jobs) in retention().items():
        expected["R1" if phase == "full" else "R1_pilot"] = jobs
    for (stage, phase), (_, jobs, _) in continuation().items():
        name = "M3R2" if stage == "R2" else stage
        expected[name if phase == "full" else name + "_pilot"] = jobs
    for (stage, phase), (_, jobs, _) in remaining().items():
        if stage == "M2":
            expected["M2" if phase == "full" else "M2_pilot"] = jobs
        elif stage == "E4" and phase == "pilot":
            expected["E4_original_pilot"] = jobs
    prepared, _ = schema()
    for phase, (_, jobs, _) in prepared.items():
        expected["E4_partial" if phase == "full" else "E4_schema_pilot"] = jobs
    rows = []
    for stage in STAGES:
        planned = {j["key"]: j for j in expected[stage.name]}
        saved = indexed(stage_path(stage) / "calls.jsonl")
        foreign = sorted(set(saved) - set(planned))
        mismatches = []
        for key in set(planned) & set(saved):
            for field, value in planned[key].items():
                if saved[key].get(field) != value:
                    mismatches.append({"key": key, "field": field})
        rows.append(
            {
                "stage": stage.name,
                "planned": len(planned),
                "saved": len(saved),
                "missing_keys": sorted(set(planned) - set(saved)),
                "foreign_keys": foreign,
                "frozen_job_field_mismatches": mismatches,
            }
        )
    save_json(destination / "schedule-audit.json", rows)
    print(
        json.dumps(
            {
                "schedule_stages": len(rows),
                "foreign_keys": sum(len(r["foreign_keys"]) for r in rows),
                "field_mismatches": sum(len(r["frozen_job_field_mismatches"]) for r in rows),
            }
        )
    )


if __name__ == "__main__":
    check_schedules()
