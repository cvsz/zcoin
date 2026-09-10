from __future__ import annotations

import math
from typing import Iterable


def normal_two_sided_p(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2))


def proportion_z_test(values: list[int], p0: float = 0.5) -> dict:
    n = len(values)
    if n == 0:
        return {"n": 0, "p_hat": None, "z": None, "p_value": None}
    successes = sum(values)
    p_hat = successes / n
    denom = math.sqrt(p0 * (1 - p0) / n)
    z = 0.0 if denom == 0 else (p_hat - p0) / denom
    return {"n": n, "successes": successes, "p_hat": p_hat,
            "z": z, "p_value": normal_two_sided_p(z)}


def wilson_interval(successes: int, n: int,
                    z: float = 2.5758293035489004) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    phat = successes / n
    denom = 1 + z*z/n
    center = (phat + z*z/(2*n)) / denom
    margin = z * math.sqrt(phat*(1-phat)/n + z*z/(4*n*n)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def runs_test(values: list[int]) -> dict:
    n = len(values)
    if n < 2:
        return {"runs": n, "z": None, "p_value": None}
    n1 = sum(values)
    n0 = n - n1
    if n0 == 0 or n1 == 0:
        return {"runs": 1, "z": None, "p_value": 0.0}
    runs = 1 + sum(values[i] != values[i-1] for i in range(1, n))
    mu = (2*n1*n0)/(n1+n0) + 1
    var = 2*n1*n0*(2*n1*n0 - n1 - n0) / (((n1+n0)**2)*(n1+n0-1))
    z = (runs - mu) / math.sqrt(var) if var > 0 else 0.0
    return {"runs": runs, "z": z, "p_value": normal_two_sided_p(z)}


def longest_streak(values: list[int]) -> dict:
    if not values:
        return {"value": None, "length": 0}
    best_v = cur_v = values[0]
    best = cur = 1
    for value in values[1:]:
        if value == cur_v:
            cur += 1
        else:
            cur_v = value
            cur = 1
        if cur > best:
            best, best_v = cur, cur_v
    return {"value": best_v, "length": best}


def nonce_audit(nonces: Iterable[int]) -> dict:
    ns = [int(x) for x in nonces]
    if not ns:
        return {"duplicates": [], "gaps": [], "monotonic_non_decreasing": True}
    seen: set[int] = set()
    dups: list[int] = []
    for nonce in ns:
        if nonce in seen:
            dups.append(nonce)
        seen.add(nonce)
    uniq = sorted(seen)
    gaps = [{"after": a, "before": b, "missing_count": b-a-1}
            for a, b in zip(uniq, uniq[1:]) if b-a > 1]
    return {
        "duplicates": sorted(set(dups)),
        "gaps": gaps[:100],
        "monotonic_non_decreasing": all(b >= a for a, b in zip(ns, ns[1:])),
    }


def edge_assessment(values: list[int], payout_multiplier: float = 1.98,
                    min_samples: int = 1000, alpha: float = 0.01,
                    min_effect: float = 0.02) -> dict:
    """Symmetric audit gate for either result; never a future prediction."""
    n = len(values)
    ones = sum(values)
    p1 = ones / n if n else None
    favored_side = None if p1 is None else (1 if p1 >= 0.5 else 0)
    favored_successes = 0 if n == 0 else max(ones, n - ones)
    favored_rate = favored_successes / n if n else None
    lo, hi = wilson_interval(favored_successes, n)
    break_even = 1.0 / payout_multiplier
    ztest = proportion_z_test(values, 0.5)
    effect = abs(p1 - 0.5) if p1 is not None else None
    evidence = bool(n >= min_samples and ztest["p_value"] is not None
                    and ztest["p_value"] < alpha and effect is not None
                    and effect >= min_effect and lo > break_even)
    return {
        "sample_size": n,
        "observed_rate_for_result_1": p1,
        "favored_side": favored_side,
        "favored_side_rate": favored_rate,
        "favored_side_ci99": [lo, hi],
        "break_even_probability": break_even,
        "two_sided_p_value_vs_50_50": ztest["p_value"],
        "absolute_effect_vs_50_50": effect,
        "positive_edge_evidence": evidence,
        "note": "Historical audit signal only; future rounds are not guaranteed or predicted.",
    }
