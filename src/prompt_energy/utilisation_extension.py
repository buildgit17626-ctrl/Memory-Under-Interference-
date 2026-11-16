"""Timing gate for the owner-approved single sweep-extension decision."""

from datetime import datetime

FREEZE = datetime.fromisoformat("2026-11-22T23:59:00+05:30")


def extension_gate(
    now: datetime, pending_seconds: float, extension_seconds: float, interval_widths: list[float]
) -> dict:
    """Check measured workload estimates without reading effects or p-values."""
    import math

    values = [pending_seconds, extension_seconds, *interval_widths]
    if now.tzinfo is None or not all(math.isfinite(v) and v >= 0 for v in values):
        raise ValueError("Require aware time and finite nonnegative estimates")
    left = max(0.0, (FREEZE - now).total_seconds())
    total = pending_seconds + extension_seconds
    return {
        "seconds_left": left,
        "maximum_projected_seconds": 0.70 * left,
        "projected_seconds": total,
        "timing_gate_passed": left > 0 and total <= 0.70 * left,
        "precision_trigger": any(w > 0.20 for w in interval_widths),
        "rule": "Timing gate applies regardless of precision; no direction or significance input",
    }
