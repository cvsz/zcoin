from __future__ import annotations

import math
import random


def bh_fdr(pvalues: list[float], alpha: float = 0.05) -> dict:
    indexed = [(i, float(p)) for i, p in enumerate(pvalues) if p is not None]
    m = len(indexed)
    if not m:
        return {"adjusted_pvalues": [], "discoveries": [], "alpha": alpha}
    ranked = sorted(indexed, key=lambda x: x[1])
    adjusted = [None] * len(pvalues)
    min_adj = 1.0
    for rank_rev, (idx, p) in enumerate(reversed(ranked), start=1):
        rank = m - rank_rev + 1
        adj = min(1.0, p * m / rank)
        min_adj = min(min_adj, adj)
        adjusted[idx] = min_adj
    return {"adjusted_pvalues": adjusted,
            "discoveries": [i for i, p in enumerate(adjusted)
                            if p is not None and p <= alpha], "alpha": alpha}


def autocorrelation_binary(values: list[int], max_lag: int = 20) -> list[dict]:
    n = len(values)
    if n < 3:
        return []
    mu = sum(values) / n
    var = sum((x - mu) ** 2 for x in values)
    out = []
    for lag in range(1, min(max_lag, n - 1) + 1):
        num = sum((values[i]-mu)*(values[i-lag]-mu) for i in range(lag, n))
        ac = num / var if var else 0.0
        z = ac * math.sqrt(n)
        out.append({"lag": lag, "autocorrelation": ac, "z": z,
                    "p_value": math.erfc(abs(z)/math.sqrt(2))})
    return out


def transition_matrix(values: list[int]) -> dict:
    counts = {"00": 0, "01": 0, "10": 0, "11": 0}
    for a, b in zip(values, values[1:]):
        counts[f"{a}{b}"] += 1
    conditional = {}
    for prev in (0, 1):
        zero, one = counts[f"{prev}0"], counts[f"{prev}1"]
        total = zero + one
        conditional[str(prev)] = {
            "p_next_0": zero/total if total else None,
            "p_next_1": one/total if total else None,
            "n": total,
        }
    return {"counts": counts, "conditional": conditional}


def bootstrap_rate(values: list[int], iterations: int = 2000, seed: int = 1337) -> dict:
    if not values:
        return {"iterations": 0, "mean": None, "ci99": [None, None]}
    rng = random.Random(seed)
    n = len(values)
    stats = [sum(values[rng.randrange(n)] for _ in range(n))/n
             for _ in range(iterations)]
    stats.sort()
    return {"iterations": iterations, "mean": sum(stats)/len(stats),
            "ci99": [stats[int(.005*(iterations-1))], stats[int(.995*(iterations-1))]]}


def beta_posterior(values: list[int], alpha0: float = 1.0, beta0: float = 1.0,
                   break_even: float = 0.5050505050505051,
                   draws: int = 20000, seed: int = 1337) -> dict:
    n, successes = len(values), sum(values)
    a, b = alpha0 + successes, beta0 + n - successes
    rng = random.Random(seed)
    above = below_inverse = 0
    samples = []
    for i in range(draws):
        x = rng.betavariate(a, b)
        above += x > break_even
        below_inverse += x < (1.0 - break_even)
        if i < min(draws, 10000):
            samples.append(x)
    samples.sort()
    def q(p: float):
        return samples[min(len(samples)-1, max(0, int(p*(len(samples)-1))))] if samples else None
    return {
        "alpha": a, "beta": b, "posterior_mean": a/(a+b),
        "probability_above_break_even": above/draws if draws else None,
        "probability_result_1_above_break_even": above/draws if draws else None,
        "probability_result_0_above_break_even": below_inverse/draws if draws else None,
        "credible_interval_99": [q(.005), q(.995)], "draws": draws,
    }


def simple_change_points(values: list[int], min_segment: int = 200,
                         threshold: float = 0.08) -> list[dict]:
    n = len(values)
    if n < min_segment * 2:
        return []
    out = []
    for cut in range(min_segment, n-min_segment+1, max(50, min_segment//2)):
        left = values[cut-min_segment:cut]
        right = values[cut:cut+min_segment]
        pl, pr = sum(left)/len(left), sum(right)/len(right)
        if abs(pr-pl) >= threshold:
            out.append({"index": cut, "left_rate": pl, "right_rate": pr,
                        "delta": pr-pl})
    return out


def holdout_split(values: list[int], train_fraction: float = 0.7) -> dict:
    n = len(values)
    if n == 0:
        return {"train": [], "holdout": []}
    cut = max(1, min(n-1, int(n*train_fraction))) if n > 1 else 1
    return {"train": values[:cut], "holdout": values[cut:]}


def epoch_segments(rows: list[dict]) -> list[dict]:
    segments, current, current_key = [], None, None
    for index, row in enumerate(rows):
        key = row.get("server_seed_hash") or row.get("server_seed") or "unknown"
        if key != current_key:
            if current:
                segments.append(current)
            current_key = key
            current = {"epoch_key": key, "start_index": index, "rows": []}
        current["rows"].append(row)
    if current:
        segments.append(current)
    for segment in segments:
        vals = [int(row["reported_result"]) for row in segment["rows"]]
        segment["end_index"] = segment["start_index"] + len(vals) - 1
        segment["n"] = len(vals)
        segment["rate_1"] = sum(vals)/len(vals) if vals else None
    return segments
