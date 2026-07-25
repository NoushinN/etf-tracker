from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


def download_prices(tickers: list[str], years: int = 11) -> pd.DataFrame:
    """Download split/distribution-adjusted daily closes from Yahoo Finance."""
    start = (pd.Timestamp.today().normalize() - pd.DateOffset(years=years)).date()
    raw = yf.download(
        tickers=tickers,
        start=start.isoformat(),
        end=(date.today() + pd.Timedelta(days=1)).isoformat(),
        auto_adjust=True,
        actions=False,
        progress=False,
        group_by="column",
        threads=True,
        timeout=15,
    )
    if raw.empty:
        raise RuntimeError("The market-data provider returned no prices.")
    prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
    if len(tickers) == 1:
        prices.columns = tickers
    prices = prices.sort_index().dropna(axis=1, how="all").ffill(limit=5)
    missing = sorted(set(tickers) - set(prices.columns))
    if missing:
        print(f"Warning: no usable price history for: {', '.join(missing)}")
    return prices


def generate_demo_prices(tickers: list[str], years: int = 6) -> pd.DataFrame:
    """Create deterministic synthetic prices for offline demos and tests."""
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=252 * years)
    output: dict[str, np.ndarray] = {}
    for position, ticker in enumerate(tickers):
        rng = np.random.default_rng(10_000 + position)
        annual_return = 0.025 + (position % 9) * 0.012
        annual_volatility = 0.06 + (position % 7) * 0.025
        daily = rng.normal(annual_return / 252, annual_volatility / np.sqrt(252), len(dates))
        output[ticker] = 100 * np.exp(np.cumsum(daily))
    return pd.DataFrame(output, index=dates)


def save_prices(prices: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(path, index_label="date")

