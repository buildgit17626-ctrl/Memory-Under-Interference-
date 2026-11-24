"""Run public reanalysis with Python-level file/network/subprocess access guards.

This is a validation harness for trusted analysis code, not a security sandbox
for generated code. Run in a fresh venv with python -I verify_public.py.
"""

import argparse
import json
import os
import platform
import runpy
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--deny-probe", type=Path)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    work = base / "verified-reproduction"
    work.mkdir(exist_ok=True)
    for name in ("MPLCONFIGDIR", "TEMP", "TMP"):
        path = work / name.lower()
        path.mkdir(exist_ok=True)
        os.environ[name] = str(path)
    roots = [base, Path(sys.prefix), Path(sys.base_prefix), Path(os.environ["SystemRoot"])]
    roots = [path.resolve() for path in roots]
    attempts = {"blocked_file_accesses": 0, "network_attempts": 0, "subprocess_attempts": 0}
    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "isolated_mode": bool(sys.flags.isolated),
        "system_site_packages": sys.prefix == sys.base_prefix,
    }

    def guard(event: str, values: tuple) -> None:
        if event in {"socket.connect", "socket.getaddrinfo"}:
            attempts["network_attempts"] += 1
            raise PermissionError("Network disabled during public reproduction")
        if event == "subprocess.Popen":
            attempts["subprocess_attempts"] += 1
            raise PermissionError("Subprocesses disabled during public reproduction")
        if event not in {"open", "os.listdir", "os.scandir"} or not values:
            return
        value = values[0]
        if value is None or isinstance(value, int):
            return
        path = Path(os.fsdecode(value)).resolve()
        if not any(path.is_relative_to(root) for root in roots):
            attempts["blocked_file_accesses"] += 1
            raise PermissionError("Read/write outside public release and runtime disabled")

    sys.addaudithook(guard)
    probe_blocked = None
    if args.deny_probe:
        try:
            args.deny_probe.read_bytes()
        except PermissionError:
            probe_blocked = True
        else:
            raise ValueError("Original-data isolation probe was not blocked")
    probe_count = attempts["blocked_file_accesses"]
    sys.argv = [str(base / "reproduce.py"), "--energy", "--figures", "--output", str(work)]
    if args.full:
        sys.argv.append("--full")
    runpy.run_path(str(base / "reproduce.py"), run_name="__main__")
    result = {
        **environment,
        **attempts,
        "original_data_probe_blocked": probe_blocked,
        "unexpected_blocked_file_accesses": attempts["blocked_file_accesses"] - probe_count,
        "guard_boundary": "Public tree plus venv, Python standard library and Windows runtime",
        "limitation": "Python audit hooks verify this trusted run; not an OS security sandbox",
        "reproduction": json.loads((work / "REPRODUCED.json").read_text()),
    }
    (work / "environment.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)
    if result["unexpected_blocked_file_accesses"] or result["network_attempts"]:
        raise ValueError("Portable reproduction required unexpected external access")


if __name__ == "__main__":
    main()
