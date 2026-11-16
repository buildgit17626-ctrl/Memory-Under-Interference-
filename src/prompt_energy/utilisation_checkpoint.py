"""Mandatory timing-only review at the first 100 completed M3 requests."""

import json
import statistics
from pathlib import Path

from prompt_energy.records import write_once
from prompt_energy.utilisation_plan import digest


def checkpoint(
    root: Path, jobs: list[dict], complete: dict, gap: float, threshold: int = 100
) -> bool:
    """Return True to stop until a schedule-bound owner review is recorded."""
    planned = [j for j in jobs if j["experiment"] == "M3"]
    observed = [r for r in complete.values() if r["experiment"] == "M3"]
    if len(observed) < threshold or not any(j["key"] not in complete for j in planned):
        return False
    identity = {"schedule_hash": digest(jobs), "checkpoint_calls": threshold}
    receipt = root / "m3-review.json"
    if receipt.exists():
        review = json.loads(receipt.read_text())
        if (
            not all(review.get(k) == v for k, v in identity.items())
            or review.get("owner_approved") is not True
        ):
            raise ValueError("Invalid M3 owner review receipt")
        return False
    path = root / "m3-checkpoint.json"
    if not path.exists():
        strata = []
        for model in sorted({j["model"] for j in planned}):
            rows = [r for r in observed if r["model"] == model]
            remaining = sum(j["model"] == model and j["key"] not in complete for j in planned)
            mean = statistics.mean(r["wall_seconds"] for r in rows) if rows else None
            strata.append(
                {
                    "model": model,
                    "observed": len(rows),
                    "remaining": remaining,
                    "mean_wall_seconds": mean,
                    "remaining_service_seconds": (mean + gap) * remaining
                    if mean is not None
                    else None,
                    "invalid_inputs": sum(not r["input_valid"] for r in rows),
                }
            )
        write_once(
            path,
            {
                **identity,
                "observed": len(observed),
                "by_model": strata,
                "omitted_overhead": "baselines, sensor wait, scoring, retries and downtime",
            },
        )
    return True
