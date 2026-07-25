from __future__ import annotations

import numpy as np
import pandas as pd

PERIODS = {
    "return_1w": pd.DateOffset(weeks=1),
    "return_1m": pd.DateOffset(months=1),
    "return_3m": pd.DateOffset(months=3),
    "return_6m": pd.DateOffset(months=6),
    "return_1y": pd.DateOffset(years=1),
}


def trailing_return(series: pd.Series, offset: pd.DateOffset) -> float:
    clean = series.dropna()
    if clean.empty:
        return np.nan
    target = clean.index[-1] - offset
    prior = clean.loc[:target]
    if prior.empty:
        return np.nan
    return (clean.iloc[-1] / prior.iloc[-1] - 1) * 100


def annualized_return(series: pd.Series, years: int) -> float:
    clean = series.dropna()
    target = clean.index[-1] - pd.DateOffset(years=years) if not clean.empty else None
    prior = clean.loc[:target] if target is not None else clean
    if prior.empty or (clean.index[-1] - clean.index[0]).days < years * 365 * 0.9:
        return np.nan
    return ((clean.iloc[-1] / prior.iloc[-1]) ** (1 / years) - 1) * 100


def calculate_metrics(series: pd.Series) -> dict[str, float | str]:
    clean = series.dropna()
    daily = clean.pct_change().dropna()
    monthly = clean.resample("ME").last().pct_change().dropna()
    peak = clean.cummax()
    drawdown = clean / peak - 1
    annual_return = daily.mean() * 252
    volatility = daily.std(ddof=1) * np.sqrt(252)
    downside = daily[daily < 0].std(ddof=1) * np.sqrt(252)
    result: dict[str, float | str] = {
        "latest_nav": clean.iloc[-1],
        "as_of": clean.index[-1].date().isoformat(),
        "volatility": volatility * 100,
        "max_drawdown": drawdown.min() * 100,
        "current_drawdown": drawdown.iloc[-1] * 100,
        "sharpe": annual_return / volatility if volatility > 0 else np.nan,
        "sortino": annual_return / downside if downside > 0 else np.nan,
        "positive_months": (monthly > 0).mean() * 100 if len(monthly) else np.nan,
        "history_years": (clean.index[-1] - clean.index[0]).days / 365.25,
    }
    result.update({name: trailing_return(clean, offset) for name, offset in PERIODS.items()})
    result["return_ytd"] = (clean.iloc[-1] / clean.loc[str(clean.index[-1].year)].iloc[0] - 1) * 100
    for years in (3, 5, 10):
        result[f"return_{years}y_annualized"] = annualized_return(clean, years)
    return result


def metrics_table(prices: pd.DataFrame) -> pd.DataFrame:
    rows = [{"ticker": ticker, **calculate_metrics(prices[ticker])} for ticker in prices]
    return pd.DataFrame(rows)


