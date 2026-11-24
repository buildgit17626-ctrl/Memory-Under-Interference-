"""Compile with licensed, locally installed Times New Roman; no font redistribution.

Requires Python 3.13 and Tectonic 0.17.0 on PATH. On Windows, the default
font directory is the system Fonts directory. Else supply --font-directory.
"""

import argparse
import os
import shutil
import struct
import subprocess
from pathlib import Path

FILES = ("times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf")


def family_names(path: Path) -> set[str]:
    """Read the TrueType name table without adding a font-analysis dependency."""
    data = path.read_bytes()
    count = struct.unpack_from(">H", data, 4)[0]
    offset = None
    for i in range(count):
        tag, _, start, _ = struct.unpack_from(">4sIII", data, 12 + 16 * i)
        if tag == b"name":
            offset = start
            break
    if offset is None:
        raise ValueError("Missing TrueType name table: " + path.name)
    _, count, strings = struct.unpack_from(">HHH", data, offset)
    names = set()
    for i in range(count):
        platform, _, _, name_id, size, start = struct.unpack_from(
            ">HHHHHH", data, offset + 6 + 12 * i
        )
        if name_id not in {1, 4, 6, 16}:
            continue
        value = data[offset + strings + start : offset + strings + start + size]
        names.add(value.decode("utf-16-be" if platform in {0, 3} else "mac_roman"))
    return names


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-directory", type=Path)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    source = args.font_directory
    if source is None:
        if os.name != "nt":
            parser.error("Supply --font-directory with licensed Times New Roman .ttf files")
        source = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    base = Path(__file__).resolve().parent
    target = base / "manuscript/local-fonts"
    target.mkdir(exist_ok=True)
    for name in FILES:
        font = source / name
        if "Times New Roman" not in family_names(font):
            raise ValueError("Expected actual Times New Roman: " + name)
        shutil.copyfile(font, target / name)
    print("Verified four Times New Roman faces; build-only copies are not release assets.")
    if not args.prepare_only:
        subprocess.run(
            ["tectonic", "--keep-logs", "--keep-intermediates", "--outdir", ".", "main.tex"],
            cwd=base / "manuscript",
            check=True,
        )


if __name__ == "__main__":
    main()
