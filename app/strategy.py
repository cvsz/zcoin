from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable
import random


@dataclass
class Trade:
    index: int
    predicted_side: int
    actual_result: int
    stake: float
    won: bool
    pnl: float
    bankroll_after: float


def _max_drawdown(equity: list[float]) -> float:
    peak = equity[0] if equity else 0.0
    result = 0.0
    for value in equity:
        peak = max(peak, value)
        if peak > 0:
            result = max(result, (peak - value) / peak)
    return result


def _next_side(strategy: str, history: list[int], rng: random.Random) -> int:
    if strategy == "always_0": return 0
    if strategy == "always_1": return 1
    if strategy == "follow_last": return history[-1] if history else 0
    if strategy == "fade_last": return 1 - history[-1] if history else 1
    if strategy in {"majority_20", "minority_20"}:
        window = history[-20:]
        majority = 1 if window and sum(window) >= len(window)/2 else 0
        return majority if strategy == "majority_20" else 1 - majority
    if strategy == "random": return rng.randint(0, 1)
    raise ValueError(f"unknown strategy: {strategy}")


def simulate_strategy(results: Iterable[int], strategy: str,
                      starting_bankroll: float = 1000.0, base_stake: float = 1.0,
                      payout_multiplier: float = 1.98, stop_loss_pct: float = 0.20,
                      take_profit_pct: float = 0.20, max_stake_pct: float = 0.01,
                      seed: int = 1337) -> dict:
    values = [int(x) for x in results]
    bankroll = start = float(starting_bankroll)
    history: list[int] = []
    trades: list[Trade] = []
    equity = [bankroll]
    rng = random.Random(seed)
    stopped = False
    for index, actual in enumerate(values):
        if bankroll <= 0 or bankroll <= start*(1-stop_loss_pct) or bankroll >= start*(1+take_profit_pct):
            stopped = True
            break
        side = _next_side(strategy, history, rng)
        stake = min(float(base_stake), bankroll*max_stake_pct, bankroll)
        if stake <= 0: break
        won = side == actual
        pnl = stake*(payout_multiplier-1.0) if won else -stake
        bankroll += pnl
        trades.append(Trade(index, side, actual, stake, won, pnl, bankroll))
        history.append(actual)
        equity.append(bankroll)
    wagered = sum(t.stake for t in trades)
    wins = sum(t.won for t in trades)
    longest_loss = current = 0
    for trade in trades:
        current = 0 if trade.won else current + 1
        longest_loss = max(longest_loss, current)
    report = {
        "name": strategy, "trades": len(trades), "wins": wins,
        "losses": len(trades)-wins, "win_rate": wins/len(trades) if trades else 0.0,
        "total_wagered": wagered, "pnl": bankroll-start,
        "roi_on_wagered": (bankroll-start)/wagered if wagered else 0.0,
        "ending_bankroll": bankroll, "max_drawdown": _max_drawdown(equity),
        "longest_loss_streak": longest_loss, "stopped_early": stopped,
    }
    return {"report": report, "trades": [asdict(t) for t in trades], "equity": equity}


def compare_strategies(results: Iterable[int], **kwargs) -> list[dict]:
    values = list(results)
    names = ["always_0", "always_1", "follow_last", "fade_last",
             "majority_20", "minority_20", "random"]
    reports = [simulate_strategy(values, name, **kwargs)["report"] for name in names]
    return sorted(reports, key=lambda x: (x["pnl"], -x["max_drawdown"]), reverse=True)


def walk_forward_bias_strategy(results: Iterable[int], train_window: int = 500,
                               min_edge: float = 0.03, **kwargs) -> dict:
    values = [int(x) for x in results]
    bankroll = start = float(kwargs.get("starting_bankroll", 1000.0))
    payout = float(kwargs.get("payout_multiplier", 1.98))
    base_stake = float(kwargs.get("base_stake", 1.0))
    max_stake_pct = float(kwargs.get("max_stake_pct", 0.01))
    trades: list[Trade] = []
    equity = [bankroll]
    for index in range(train_window, len(values)):
        window = values[index-train_window:index]
        p1 = sum(window)/train_window
        if p1 >= 0.5 + min_edge: side = 1
        elif p1 <= 0.5 - min_edge: side = 0
        else: continue
        stake = min(base_stake, bankroll*max_stake_pct, bankroll)
        actual = values[index]
        won = side == actual
        pnl = stake*(payout-1.0) if won else -stake
        bankroll += pnl
        trades.append(Trade(index, side, actual, stake, won, pnl, bankroll))
        equity.append(bankroll)
    wagered = sum(t.stake for t in trades)
    wins = sum(t.won for t in trades)
    return {"report": {"name": f"walk_forward_bias_{train_window}", "trades": len(trades),
            "wins": wins, "losses": len(trades)-wins, "win_rate": wins/len(trades) if trades else 0.0,
            "total_wagered": wagered, "pnl": bankroll-start,
            "roi_on_wagered": (bankroll-start)/wagered if wagered else 0.0,
            "ending_bankroll": bankroll, "max_drawdown": _max_drawdown(equity)},
            "trades": [asdict(t) for t in trades], "equity": equity}


def monte_carlo_null(n_rounds: int, simulations: int = 2000,
                     payout_multiplier: float = 1.98, seed: int = 1337) -> dict:
    rng = random.Random(seed)
    pnls = []
    for _ in range(simulations):
        sample = [rng.randint(0, 1) for _ in range(n_rounds)]
        pnls.append(simulate_strategy(sample, "always_1", payout_multiplier=payout_multiplier,
                                      seed=rng.randint(0, 2**31-1))["report"]["pnl"])
    pnls.sort()
    def q(p: float):
        return pnls[min(len(pnls)-1, max(0, int(p*(len(pnls)-1))))] if pnls else None
    return {"simulations": simulations, "n_rounds": n_rounds,
            "mean_pnl": sum(pnls)/len(pnls) if pnls else 0.0,
            "median_pnl": q(.5), "p05": q(.05), "p95": q(.95),
            "profitable_fraction": sum(x > 0 for x in pnls)/len(pnls) if pnls else 0.0}
