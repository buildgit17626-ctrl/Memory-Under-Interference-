"""Reproduce competing CPU activity and aborted-call diagnosis without generation."""

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/utilisation/supervised/E0"
OUT = ROOT / "artifacts/utilisation/reliability-2026-11-17"


def main() -> None:
    blocks = [json.loads(line) for line in (RUN / "blocks.jsonl").read_text().splitlines()]
    end = [b for b in blocks if b["event"] == "end"][-1]
    start = next(b for b in blocks if b["event"] == "start" and b["block"] == end["block"])
    before = {p["pid"]: p for p in start["processes"]}
    deltas = []
    for p in end["processes"]:
        a = before.get(p["pid"])
        if (
            a
            and a["name"] == p["name"]
            and p["pid"] != 0
            and p.get("cpu_times")
            and a.get("cpu_times")
        ):
            used = sum(p["cpu_times"][:2]) - sum(a["cpu_times"][:2])
            if used >= 0:
                deltas.append({"process": p["name"], "pid": p["pid"], "cpu_seconds": used})
    calls = [json.loads(line) for line in (RUN / "calls.jsonl").read_text().splitlines()]
    failed = [r for r in calls if not r["input_valid"]]
    keys = {r["key"] for r in failed}
    errors = []
    for r in map(json.loads, (RUN / "responses.jsonl").read_text().splitlines()):
        if r["key"] in keys:
            envelope = r["raw"]
            body = json.loads(base64.b64decode(envelope["body_base64"]))
            errors.append(
                {
                    "key": r["key"],
                    "attempt": r["attempt"],
                    "http_status": envelope["http_status"],
                    "error": body.get("error"),
                    "seconds": envelope["wall_seconds"],
                }
            )
    result = {
        "logical_calls": len(calls),
        "invalid_calls": len(failed),
        "block": end["block"],
        "start_W": start["baseline"]["watts"],
        "end_W": end["baseline"]["watts"],
        "signed_drift_W": end["drift_w"],
        "process_cpu_deltas": sorted(deltas, key=lambda d: d["cpu_seconds"], reverse=True)[:12],
        "failed_attempts": errors,
        "limits": (
            "CPU deltas use surviving same-name PIDs; they identify competing work, "
            "not a sole cause."
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "diagnosis.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
