"""Deduplicate captured log prefixes and export only numerical power/time samples."""

import hashlib
import json
from collections import defaultdict

import pandas as pd

from analysis.memory_audit.records import indexed, save_json
from analysis.memory_audit.sensors import integrate_many, prefix_hashes, samples
from analysis.memory_release.common import AUDIT, RELEASE, ROOT, directories


def main():
    directories()
    (RELEASE / "data/energy").mkdir(parents=True, exist_ok=True)
    original = json.loads((AUDIT / "input-manifest.json").read_text())
    groups = defaultdict(list)
    for name, meta in original.items():
        if "/sensors/" not in name or not name.endswith(".csv"):
            continue
        path = ROOT / name
        with path.open("rb") as stream:
            signature = hashlib.sha256(stream.read(65536)).hexdigest()
        groups[signature].append((name, meta))
    mapping, group_records, cached = {}, [], {}
    for index, (_, members) in enumerate(sorted(groups.items())):
        name, meta = max(members, key=lambda pair: pair[1]["bytes"])
        path = ROOT / name
        checks = prefix_hashes(
            path, [{"prefix_bytes": m["bytes"], "sha256": m["sha256"]} for _, m in members]
        )
        if not all(r["match"] for r in checks):
            raise ValueError("Log prefixes do not share their claimed source: " + name)
        times, power, notes = samples(path)
        group = f"power-{index:03d}"
        relative = "data/energy/" + group + ".csv.gz"
        pd.DataFrame({"timestamp_utc_epoch_s": times, "cpu_package_w": power}).to_csv(
            RELEASE / relative, index=False, compression="gzip", float_format="%.17g"
        )
        cached[group] = times, power
        for source, _ in members:
            mapping[source] = group
        group_records.append(
            {
                "id": group,
                "file": relative,
                "samples": len(times),
                "original_mirrors": [s for s, _ in members],
                "parser_notes": notes,
                "columns": "UTC epoch seconds; CPU Package Power watts",
            }
        )
        print(
            json.dumps(
                {
                    "sensor_groups_exported": index + 1,
                    "mirrors": len(members),
                    "samples": len(times),
                }
            ),
            flush=True,
        )
    windows = []
    for folder in sorted((ROOT / "results/utilisation").rglob("calls.jsonl")):
        stage = folder.parent.relative_to(ROOT).as_posix()
        sensor_paths = {
            p.stem: p.relative_to(ROOT).as_posix()
            for p in (folder.parent / "sensors").glob("*.csv")
        }
        for call in indexed(folder).values():
            group = mapping.get(sensor_paths.get(call.get("block")))
            if group is None:
                continue
            for kind, window in call.get("energy", {}).get("windows", {}).items():
                if window.get("start") is not None:
                    windows.append(
                        {
                            "source_folder": stage,
                            "key": call["key"],
                            "kind": kind,
                            "sensor_group": group,
                            **{
                                k: window.get(k)
                                for k in (
                                    "start",
                                    "end",
                                    "seconds",
                                    "raw_wh",
                                    "adjusted_wh",
                                    "flags",
                                )
                            },
                        }
                    )
        # Reproduce idle baselines from exported sensor samples, as well as generation windows.
        for line in (folder.parent / "blocks.jsonl").read_text().splitlines():
            event = json.loads(line)
            baseline = event.get("baseline") or {}
            group = mapping.get(sensor_paths.get(event.get("block")))
            if group and baseline.get("start") is not None:
                windows.append(
                    {
                        "source_folder": stage,
                        "key": event["block"],
                        "kind": "idle_" + event["event"],
                        "sensor_group": group,
                        **{
                            k: baseline.get(k)
                            for k in ("start", "end", "seconds", "raw_wh", "adjusted_wh", "flags")
                        },
                    }
                )
    checks = []
    for group, (times, power) in cached.items():
        chosen = [w for w in windows if w["sensor_group"] == group]
        for result in integrate_many(times, power, chosen):
            result.pop("source_folder", None)
            checks.append(result)
    available = [r for r in checks if r.get("raw_wh") is not None]
    disagree = [r for r in available if not r.get("agrees_within_1e_8_wh")]
    save_json(RELEASE / "data/energy/groups.json", group_records)
    save_json(RELEASE / "data/energy/windows.json", windows)
    save_json(
        RELEASE / "checks/public-energy-integration.json",
        {
            "original_mirrors": len(mapping),
            "deduplicated_groups": len(cached),
            "windows": len(windows),
            "available_recorded_windows": len(available),
            "disagreements": disagree,
            "unavailable_windows": [r for r in checks if r.get("unavailable_reason")],
            "max_abs_error_wh": max(
                (abs(r["difference_wh"]) for r in available if r.get("difference_wh") is not None),
                default=None,
            ),
            "note": "Numeric integration reproducibility, not sensor calibration.",
        },
    )
    if disagree:
        raise ValueError("Exported numerical power samples do not reproduce recorded windows")
    print(
        json.dumps(
            {"energy_groups": len(cached), "windows": len(windows), "disagreements": len(disagree)}
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
