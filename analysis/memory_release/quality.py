"""Verify original immutability, numeric exports and meaningful release invariants."""

import json
import subprocess

import numpy as np

from analysis.memory_audit.records import indexed, save_json
from analysis.memory_audit.sensors import freeze_inputs
from analysis.memory_release.common import AUDIT, RELEASE, ROOT, directories


def main():
    directories()
    original = freeze_inputs(AUDIT)
    calls, changed = 0, []
    for path in sorted((ROOT / "results/utilisation").rglob("calls.jsonl")):
        public = RELEASE / "data/raw" / path.relative_to(ROOT)
        left, right = indexed(path), indexed(public)
        if left.keys() != right.keys():
            raise ValueError("Exported logical keys changed")
        for key, a in left.items():
            b = right[key]
            for field in (
                "raw_output",
                "extracted",
                "prompt_tokens",
                "output_tokens",
                "prefill_ns",
                "decode_ns",
                "input_valid",
                "flags",
            ):
                if a.get(field) != b.get(field):
                    changed.append({"key": key, "field": field})
            if a["request"]["prompt"] != b["request"]["prompt"]:
                changed.append({"key": key, "field": "prompt"})
            calls += 1
    if changed:
        raise ValueError("Public transformation changed scientific generation fields")
    reproduced = json.loads((ROOT / "tmp/mui-reproduction-check/REPRODUCED.json").read_text())
    energy = json.loads((ROOT / "tmp/mui-reproduction-check/energy-check.json").read_text())
    ratios = json.loads((ROOT / "tmp/mui-reproduction-check/r1-paired-ratios.json").read_text())
    expected = json.loads((AUDIT / "energy-per-correct-differences.json").read_text())
    for r in ratios:
        e = next(
            e
            for e in expected
            if e["stage"] == "R1"
            and e["model"] == r["model"]
            and e["comparison"] == "oracle_selective minus full_history"
            and e["field"] == "net_wh"
            and e["variant"] == "primary"
        )
        if not np.allclose(r["ci95"], e["ci95"], rtol=0, atol=1e-12) or not np.isclose(
            r["difference"], e["difference"], rtol=0, atol=1e-12
        ):
            raise ValueError("Portable paired ratio did not reproduce")
    pdf = json.loads((RELEASE / "checks/pdf-quality.json").read_text())
    licence = json.loads((RELEASE / "checks/permission-audit.json").read_text())
    status = {
        "original_files_verified_unchanged": len(original),
        "original_bytes_verified_unchanged": sum(r["bytes"] for r in original.values()),
        "public_generation_records_verified": calls,
        "changed_scientific_generation_fields": changed,
        "portable_reproduction": reproduced,
        "portable_energy": energy,
        "paired_ratio_ci_reproduced": len(ratios),
        "pdf": pdf,
        "verified_licence_notices": len(licence),
        "model_or_embedding_generations": 0,
        "external_publication": False,
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
    }
    portable = RELEASE / "checks/portable-environment.json"
    if portable.exists():
        fresh = json.loads(portable.read_text())
        if (
            not fresh["isolated_mode"]
            or fresh["system_site_packages"]
            or not fresh["original_data_probe_blocked"]
            or fresh["network_attempts"]
            or fresh["unexpected_blocked_file_accesses"]
        ):
            raise ValueError("Clean-environment public reproduction failed its isolation checks")
        status["fresh_environment_public_reproduction"] = fresh
    save_json(RELEASE / "checks/scientific-quality.json", status)
    print(
        json.dumps({k: v for k, v in status.items() if k not in {"pdf", "source_commit"}}),
        flush=True,
    )


if __name__ == "__main__":
    main()
