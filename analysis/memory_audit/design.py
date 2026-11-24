"""Explicit evidence populations and audit paths; no inference configuration changes."""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / "artifacts/memory-audit/2026-11-24-v1"
BOOTSTRAPS = 2000
SEED = 1732
ENERGY_MODE = "HWiNFO CPU Package Power; trapezoidal; approximate post-load; block-start net"


@dataclass(frozen=True)
class Stage:
    name: str
    folder: str
    phase: str
    expected: int


STAGES = (
    Stage("E0", "supervised/E0", "main", 1968),
    Stage("M3_isolated", "supervised/M3-isolated", "main", 40),
    Stage("M3_initial", "supervised/M3", "main", 240),
    Stage("M1", "m1-full", "main", 1040),
    Stage("M1_pilot", "m1-pilot", "pilot", 70),
    Stage("R1", "r1-v2/full", "main", 400),
    Stage("R1_pilot", "r1-v2/pilot", "pilot", 50),
    Stage("M3R2", "continuation-v3/R2/full", "main", 1040),
    Stage("M3R2_pilot", "continuation-v3/R2/pilot", "pilot", 130),
    Stage("M2", "remaining-v4/M2/full", "main", 400),
    Stage("M2_pilot", "remaining-v4/M2/pilot", "pilot", 50),
    Stage("E5", "continuation-v3/E5/full", "main", 400),
    Stage("E5_pilot", "continuation-v3/E5/pilot", "pilot", 50),
    Stage("E4_original_pilot", "remaining-v4/E4/pilot", "failed_feasibility", 20),
    Stage("E4_schema_pilot", "e4-schema-v5/pilot", "pilot", 20),
    Stage("E4_partial", "e4-schema-v5/full", "partial", 400),
    Stage("harness_pilot", "pilot", "harness_validation", 22),
)


def stage_path(stage: Stage) -> Path:
    return ROOT / "results/utilisation" / stage.folder
