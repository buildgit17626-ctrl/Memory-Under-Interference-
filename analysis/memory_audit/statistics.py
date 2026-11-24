"""Cluster-preserving descriptive statistics with explicit ratio/missingness limits."""

from fractions import Fraction
from functools import reduce
from math import lcm

import numpy as np
from scipy.stats import binomtest

from analysis.memory_audit.design import BOOTSTRAPS, SEED
from prompt_energy.utilisation_e0_analysis import exact_swap_p


def interval(values: np.ndarray, *, total: bool = False) -> dict:
    data = np.asarray(values, dtype=float)
    data = data[np.isfinite(data)]
    if not len(data):
        return {"n_units": 0, "estimate": None, "ci95": None}
    if len(data) == 1:
        return {
            "n_units": 1,
            "estimate": float(data[0]),
            "ci95": None,
            "reason": "Only one independent resampling unit",
        }
    samples = np.random.default_rng(SEED).integers(0, len(data), (BOOTSTRAPS, len(data)))
    draws = data[samples].sum(axis=1) if total else data[samples].mean(axis=1)
    estimate = data.sum() if total else data.mean()
    return {
        "n_units": len(data),
        "estimate": float(estimate),
        "ci95": np.quantile(draws, [0.025, 0.975]).tolist(),
    }


def paired(a: np.ndarray, b: np.ndarray, *, binary_test: bool = False) -> dict:
    """Treatment minus control; missingness is paired, never independently filtered."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("Paired vectors differ in shape")
    keep = np.isfinite(a) & np.isfinite(b)
    a, b = a[keep], b[keep]
    result = interval(a - b)
    result.update(
        treatment_mean=float(a.mean()) if len(a) else None,
        control_mean=float(b.mean()) if len(b) else None,
        n_missing_pairs=int(len(keep) - keep.sum()),
    )
    if not len(a):
        result.update(p_value=None, test="unavailable")
    elif binary_test:
        losses, gains = int(((a == 0) & (b == 1)).sum()), int(((a == 1) & (b == 0)).sum())
        result.update(
            pass_to_fail=losses,
            fail_to_pass=gains,
            p_value=float(binomtest(gains, gains + losses).pvalue) if gains + losses else 1.0,
            test="exact McNemar (discordant binomial)",
        )
    else:
        fractions = [Fraction(float(x)).limit_denominator(24) for x in a - b]
        denominator = reduce(lcm, (f.denominator for f in fractions), 1)
        integers = [int(f * denominator) for f in fractions]
        result.update(p_value=exact_swap_p(integers), test="exact paired task sign swaps")
    return result


def holm(pvalues: list[float | None]) -> list[float | None]:
    # Missing tests stay in the declared family as p=1 for the multiplicity factor.
    order = sorted(range(len(pvalues)), key=lambda i: 1 if pvalues[i] is None else pvalues[i])
    result, running = [None] * len(pvalues), 0.0
    for rank, i in enumerate(order):
        p = 1.0 if pvalues[i] is None else pvalues[i]
        running = max(running, (len(order) - rank) * p)
        if pvalues[i] is not None:
            result[i] = min(1.0, running)
    return result


def ratio(energy: np.ndarray, correct: np.ndarray) -> dict:
    """Arguments contain task-cluster totals over the identical covered population."""
    energy, correct = np.asarray(energy, dtype=float), np.asarray(correct, dtype=float)
    if energy.shape != correct.shape:
        raise ValueError("Ratio numerator/denominator clusters differ")
    good = np.isfinite(energy) & np.isfinite(correct)
    energy, correct = energy[good], correct[good]
    result = {
        "n_units": len(energy),
        "energy_sum": float(energy.sum()),
        "correct": float(correct.sum()),
        "estimate": None,
        "ci95": None,
        "upper_unbounded": False,
        "zero_correct_bootstrap_draws": None,
    }
    if not len(energy) or correct.sum() == 0:
        return result
    ids = np.random.default_rng(SEED).integers(0, len(energy), (BOOTSTRAPS, len(energy)))
    numerators, denominators = energy[ids].sum(axis=1), correct[ids].sum(axis=1)
    draws = np.divide(
        numerators, denominators, out=np.full(BOOTSTRAPS, np.inf), where=denominators > 0
    )
    draws.sort()
    # Order statistics avoid interpolating finite values with infinity (which yields NaN).
    low, high = draws[np.ceil(np.array([0.025, 0.975]) * BOOTSTRAPS).astype(int) - 1]
    result.update(
        estimate=float(energy.sum() / correct.sum()),
        ci95=[float(low) if np.isfinite(low) else None, float(high) if np.isfinite(high) else None],
        upper_unbounded=not np.isfinite(high),
        zero_correct_bootstrap_draws=int((denominators == 0).sum()),
    )
    return result


def components(bundles: list[list[str]]) -> list[list[str]]:
    neighbours: dict[str, set[str]] = {}
    for members in bundles:
        for member in members:
            neighbours.setdefault(member, set()).update(members)
    unseen, groups = set(neighbours), []
    while unseen:
        pending, found = [min(unseen)], set()
        while pending:
            item = pending.pop()
            if item not in found:
                found.add(item)
                pending.extend(neighbours[item] - found)
        unseen -= found
        groups.append(sorted(found))
    return groups


def paired_ratio(ea: np.ndarray, ca: np.ndarray, eb: np.ndarray, cb: np.ndarray) -> dict:
    values = np.array([ea, ca, eb, cb], dtype=float)
    values = values[:, np.isfinite(values).all(axis=0)]
    result = {
        "n_units": values.shape[1],
        "difference": None,
        "ci95": None,
        "undefined_bootstrap_draws": None,
    }
    if values.shape[1] == 0 or values[1].sum() == 0 or values[3].sum() == 0:
        return result
    result["difference"] = float(
        values[0].sum() / values[1].sum() - values[2].sum() / values[3].sum()
    )
    if values.shape[1] < 2:
        return result
    ids = np.random.default_rng(SEED).integers(0, values.shape[1], (BOOTSTRAPS, values.shape[1]))
    sums = values[:, ids].sum(axis=2)
    defined = (sums[1] > 0) & (sums[3] > 0)
    result["undefined_bootstrap_draws"] = int((~defined).sum())
    if defined.all():
        draws = sums[0] / sums[1] - sums[2] / sums[3]
        result["ci95"] = np.quantile(draws, [0.025, 0.975]).tolist()
    else:
        result["reason"] = "Some paired ratio draws undefined; no finite interval manufactured."
    return result
