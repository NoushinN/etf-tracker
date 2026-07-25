from __future__ import annotations

import pandas as pd


def analyze_portfolio(prices: pd.DataFrame, holdings: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    weights = pd.Series({item["ticker"]: item["weight"] for item in holdings}, dtype=float)
    available = [ticker for ticker in weights.index if ticker in prices]
    if not available:
        return pd.DataFrame(), pd.DataFrame(), ["No portfolio tickers have price data."]
    weights = weights[available] / weights[available].sum()
    returns = prices[available].pct_change().dropna(how="all")
    correlation = returns.corr()
    portfolio_return = returns.mul(weights, axis=1).sum(axis=1)
    summary = pd.DataFrame(
        {
            "metric": ["Holdings", "Annualized return", "Annualized volatility"],
            "value": [
                str(len(available)),
                f"{portfolio_return.mean() * 252 * 100:.2f}%",
                f"{portfolio_return.std() * (252**0.5) * 100:.2f}%",
            ],
        }
    )
    warnings = []
    for left_index, left in enumerate(available):
        for right in available[left_index + 1 :]:
            value = correlation.loc[left, right]
            if pd.notna(value) and value >= 0.90:
                warnings.append(f"{left} and {right} have very high return correlation ({value:.2f}).")
    return summary, correlation, warnings

