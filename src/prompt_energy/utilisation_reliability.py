"""Approved shorter measurement blocks and stable idle-window preflight."""

import json
import time

from experiments.config import P4
from prompt_energy.full_run import baseline, check_host
from prompt_energy.hwinfo import preflight_log
from prompt_energy.metadata import host_metadata
from prompt_energy.utilisation_journal import append_json
from prompt_energy.utilisation_run import Sensor, snapshot
from prompt_energy.utilisation_supervisor import Halt, generate_batch

BLOCK_LIMIT = 25
MAX_IDLE_WINDOWS = 6


def stable_pair(previous: float, current: float) -> tuple[bool, float]:
    threshold = max(P4["drift_absolute_w"], P4["drift_fraction"] * previous)
    return abs(current - previous) <= threshold, threshold


class SettledSensor(Sensor):
    """Accept a starting baseline only after two adjacent stable 60s windows."""

    def start(self) -> None:
        host = host_metadata()
        check_host(host)
        live = preflight_log(self.log, self.fmt)
        previous = None
        for index in range(MAX_IDLE_WINDOWS):
            current = baseline(self.log, self.mirror, self.fmt, sleep=time.sleep, now=time.time)
            stable, threshold = (
                (False, None)
                if previous is None
                else stable_pair(previous["watts"], current["watts"])
            )
            append_json(
                self.events.parent / "idle-checks.jsonl",
                {
                    "block": self.block,
                    "window": index + 1,
                    "baseline": current,
                    "previous_w": previous["watts"] if previous else None,
                    "stable_pair": stable,
                    "threshold_w": threshold,
                },
            )
            print(
                json.dumps(
                    {
                        "phase": "idle_stability",
                        "window": index + 1,
                        "watts": current["watts"],
                        "stable_pair": stable,
                    }
                ),
                flush=True,
            )
            if stable:
                self.opening = current
                append_json(
                    self.events,
                    {
                        "event": "start",
                        "block": self.block,
                        "baseline": current,
                        "host": host,
                        "preflight": live,
                        "processes": snapshot(),
                        "idle_pair": {"previous_baseline": previous, "threshold_w": threshold},
                    },
                )
                return
            previous = current
        raise Halt(
            "Idle baseline did not settle after six 60-second windows",
            {"windows": MAX_IDLE_WINDOWS, "no_generation_in_block": True},
        )


def generate_short_block(root, jobs, client, sensor, gap, limit=100, **kwargs):
    return generate_batch(root, jobs, client, sensor, gap, limit=min(limit, BLOCK_LIMIT), **kwargs)
