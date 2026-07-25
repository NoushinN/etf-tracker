from __future__ import annotations

import numpy as np
import pandas as pd


def percentile(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    ranked = series.rank(pct=True, na_option="bottom") * 100
    return ranked if higher_is_better else 100 - ranked + (100 / max(len(series), 1))


def add_scores(frame: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = frame.copy()
    scored_groups = []
    for _, group in df.groupby("category", dropna=False):
        group = group.copy()
        momentum = sum(
            percentile(group[column]).fillna(0) * weight
            for column, weight in config["momentum_period_weights"].items()
        )
        risk = (
            percentile(group["sharpe"]).fillna(0) * 0.35
            + percentile(group["sortino"]).fillna(0) * 0.20
            + percentile(group["volatility"], False).fillna(0) * 0.20
            + percentile(group["max_drawdown"]).fillna(0) * 0.25
        )
        cost = percentile(group["mer"], False).fillna(0)
        quality = (
            percentile(group["positive_months"]).fillna(0) * 0.65
            + percentile(group["history_years"]).fillna(0) * 0.35
        )
        group["momentum_score"] = momentum
        group["risk_score"] = risk
        group["cost_score"] = cost
        group["quality_score"] = quality
        group["overall_score"] = (
            momentum * config["momentum_weight"]
            + risk * config["risk_adjusted_weight"]
            + cost * config["cost_weight"]
            + quality * config["quality_weight"]
        )
        scored_groups.append(group)
    result = pd.concat(scored_groups, ignore_index=True)
    result["signal"] = result.apply(classify_signal, axis=1)
    result["category_rank"] = (
        result.groupby("category")["overall_score"].rank(ascending=False, method="min").astype(int)
    )
    return result.sort_values(["category", "category_rank"])


def classify_signal(row: pd.Series) -> str:
    if row.get("history_years", 0) < 1:
        return "Insufficient history"
    if row.get("max_drawdown", 0) < -40 or row.get("volatility", 0) > 35:
        return "High risk"
    periods = [row.get(name, np.nan) for name in ("return_3m", "return_6m", "return_1y")]
    if all(pd.notna(value) and value > 0 for value in periods):
        return "Strong trend"
    if row.get("return_1m", 0) > 0 and row.get("return_3m", 0) > 0:
        return "Improving"
    if row.get("return_3m", 0) < 0 and row.get("return_6m", 0) < 0:
        return "Weakening"
    return "Neutral"


