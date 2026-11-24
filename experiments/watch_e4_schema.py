"""Owner-approved E4 amendment watcher; unexpected crashes only, not gate bypasses."""

import argparse
import ctypes
import json
import subprocess
import sys
import time
from pathlib import Path

from experiments.prepare_e4_schema import OUTPUT
from experiments.run_continuation import PAUSE
from prompt_energy.records import directory_lock


def watch(log: Path, resume: bool) -> None:
    for restart in range(6):
        if PAUSE.exists() and not (resume and restart == 0):
            return
        command = [
            sys.executable,
            "-u",
            "-m",
            "experiments.run_e4_schema",
            "recover",
            "--hwinfo-log",
            str(log),
        ]
        if resume and restart == 0:
            command.append("--resume")
        with (OUTPUT / "terminal.log").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"worker_launch": restart, "time": time.time()}) + "\n")
            stream.flush()
            process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT)
            (OUTPUT / "worker.pid").write_text(str(process.pid), encoding="utf-8")
            code = process.wait()
        status = OUTPUT / "STATUS.json"
        if code == 0 or PAUSE.exists():
            return
        if status.exists() and json.loads(status.read_text()).get("reason") in {
            "stopped",
            "finished",
        }:
            return
        time.sleep(30)
    (OUTPUT / "WATCHDOG_STOP.md").write_text(
        "Five crash restarts exhausted; inspect terminal.log.\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hwinfo-log", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with directory_lock(OUTPUT / "watch-lock"):
        power = ctypes.windll.kernel32.SetThreadExecutionState
        if not power(0x80000001):
            raise RuntimeError("Cannot inhibit idle sleep")
        try:
            watch(args.hwinfo_log, args.resume)
        finally:
            power(0x80000000)


if __name__ == "__main__":
    main()
