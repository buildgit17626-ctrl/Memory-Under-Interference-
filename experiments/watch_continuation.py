"""Restart unexpected worker crashes; never restart a deliberate validity/user stop."""

import argparse
import ctypes
import json
import subprocess
import sys
import time
from pathlib import Path

from experiments.run_continuation import OUTPUT, PAUSE


def watch(sensor_log: Path) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    status_path = OUTPUT / "STATUS.json"
    log = OUTPUT / "terminal.log"
    for restart in range(6):
        if PAUSE.exists():
            return
        # A previous deliberate stop needs owner review, not an automatic loop.
        if restart and status_path.exists():
            status = json.loads(status_path.read_text())
            if status.get("reason") in {"stopped", "finished"}:
                return
        with log.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"worker_launch": restart, "time": time.time()}) + "\n")
            stream.flush()
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    "-m",
                    "experiments.run_continuation",
                    "recover",
                    "--hwinfo-log",
                    str(sensor_log),
                ],
                stdout=stream,
                stderr=subprocess.STDOUT,
            )
            (OUTPUT / "worker.pid").write_text(str(process.pid), encoding="utf-8")
            code = process.wait()
        if code == 0 or PAUSE.exists():
            return
        if status_path.exists() and json.loads(status_path.read_text()).get("reason") == "stopped":
            return
        time.sleep(30)
    (OUTPUT / "WATCHDOG_STOP.md").write_text(
        "Unexpected worker exits exhausted five automatic restarts. Inspect terminal.log.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hwinfo-log", type=Path, required=True)
    args = parser.parse_args()
    # A distinct supervising thread keeps the machine awake during evaluation
    # too; child block-level resets cannot cancel the parent's sleep inhibition.
    power = ctypes.windll.kernel32.SetThreadExecutionState
    if not power(0x80000001):
        raise RuntimeError("Could not inhibit sleep for the continuation")
    try:
        watch(args.hwinfo_log)
    finally:
        power(0x80000000)


if __name__ == "__main__":
    main()
