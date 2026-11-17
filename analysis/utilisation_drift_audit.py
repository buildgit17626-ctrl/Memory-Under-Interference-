"""Read-only drift audit; no model requests and no correctness inspection."""

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/utilisation/supervised"
OUT = ROOT / "artifacts/utilisation/drift-audit-2026-11-17"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    blocks = [json.loads(line) for line in (RUN / "E0/blocks.jsonl").read_text().splitlines()]
    calls = [json.loads(line) for line in (RUN / "E0/calls.jsonl").read_text().splitlines()]
    raw = [json.loads(line) for line in (RUN / "E0/responses.jsonl").read_text().splitlines()]
    envelopes = {r["attempt"]: r["raw"] for r in raw}
    flagged = []
    affected = []

    def iso(timestamp):
        return datetime.fromtimestamp(timestamp, ZoneInfo("Asia/Kolkata")).isoformat()

    for event in blocks:
        if event["event"] != "end" or "baseline_drift" not in event.get("flags", []):
            continue
        opening = next(b for b in blocks if b["event"] == "start" and b["block"] == event["block"])
        start, end = opening["baseline"], event["baseline"]
        threshold = max(1.0, 0.1 * start["watts"])
        group = [r for r in calls if r["block"] == event["block"]]
        flagged.append(
            {
                "block": event["block"],
                "start_W": start["watts"],
                "end_W": end["watts"],
                "signed_drift_W": end["watts"] - start["watts"],
                "registered_threshold_W": threshold,
                "start_baseline_interval_IST": [iso(start["start"]), iso(start["end"])],
                "end_baseline_interval_IST": [iso(end["start"]), iso(end["end"])],
                "call_count": len(group),
                "finite_post_load_energy": sum(
                    r["energy"]["windows"].get("post_load", {}).get("raw_wh") is not None
                    for r in group
                ),
            }
        )
        for sequence, r in enumerate(group, 1):
            envelope = envelopes[r["attempt"]]
            post = r["energy"]["windows"].get("post_load", {})
            affected.append(
                {
                    "sequence_in_block": sequence,
                    "key": r["key"],
                    "attempt": r["attempt"],
                    "block": r["block"],
                    "task_id": r["task_id"],
                    "model": r["model"],
                    "condition": r["condition"],
                    "sample_idx": r["sample_idx"],
                    "request_start_UTC": envelope["started_at"],
                    "request_end_UTC": envelope["ended_at"],
                    "post_load_start_IST": iso(post["start"]) if "start" in post else None,
                    "post_load_end_IST": iso(post["end"]) if "end" in post else None,
                    "stored_energy_valid": r["energy_valid"],
                    "joined_baseline_drift": True,
                    "energy_flags": "|".join(r["energy"]["flags"]),
                }
            )
    if affected:
        with (OUT / "affected-calls.csv").open("w", newline="", encoding="utf8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(affected[0]))
            writer.writeheader()
            writer.writerows(affected)
    result = {
        "checkpoint_text": (RUN / "CHECKPOINT.md").read_text(),
        "completed_E0": len(calls),
        "drift_affected_calls": len(affected),
        "blocks": flagged,
        "request_range_UTC": [affected[0]["request_start_UTC"], affected[-1]["request_end_UTC"]]
        if affected
        else None,
        "sources": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [
                RUN / "CHECKPOINT.md",
                RUN / "E0/blocks.jsonl",
                RUN / "E0/calls.jsonl",
                RUN / "E0/responses.jsonl",
            ]
        },
    }
    (OUT / "evidence.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
