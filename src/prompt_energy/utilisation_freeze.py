"""Require committed exact-byte experiment preregistrations before generation."""

import hashlib
import json
import subprocess
from pathlib import Path

from prompt_energy.utilisation_plan import ROOT, digest


def verify_registration(jobs: list, stimuli: Path, config: dict) -> dict:
    def committed(path: Path) -> bytes:
        rel = path.resolve().relative_to(ROOT).as_posix()
        blob = subprocess.check_output(["git", "show", f"HEAD:{rel}"], cwd=ROOT)
        if path.read_bytes().replace(b"\r\n", b"\n") != blob:
            raise ValueError(f"Uncommitted changes to {rel}")
        return blob

    preregs = {}
    committed(ROOT / config["paths"]["config"])
    stimulus_hash = hashlib.sha256(committed(stimuli)).hexdigest()
    for exp in {j["experiment"] for j in jobs}:
        path = ROOT / config["paths"]["preregistrations"] / f"{exp}.json"
        blob = committed(path)
        record = json.loads(blob)
        preregs[exp] = hashlib.sha256(blob).hexdigest()
        for field in (
            "date",
            "hypotheses",
            "competing_predictions",
            "conditions",
            "outcomes",
            "analysis",
            "exclusions",
        ):
            if not record.get(field):
                raise ValueError(f"Missing registration field {field}")
        subset = [j for j in jobs if j["experiment"] == exp]
        if (
            record["schedule_hash"] != digest(subset)
            or record["stimuli_hash"] != stimulus_hash
            or record["config_hash"] != subset[0]["config_hash"]
        ):
            raise ValueError(f"Registration mismatch for {exp}")
    return {
        "commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "stimuli_sha256": stimulus_hash,
        "prereg_sha256": preregs,
    }
