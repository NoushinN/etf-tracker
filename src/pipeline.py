from __future__ import annotations

import argparse

import pandas as pd

from src.config import ROOT, load_scoring, load_watchlist
from src.data import download_prices, generate_demo_prices, save_prices
from src.metrics import metrics_table
from src.report import save_reports
from src.scoring import add_scores


def run(demo: bool = False) -> pd.DataFrame:
    funds = load_watchlist()
    tickers = [fund["ticker"] for fund in funds]
    prices = generate_demo_prices(tickers) if demo else download_prices(tickers)
    save_prices(prices, ROOT / "data/prices/adjusted_close.csv")
    metadata = pd.DataFrame(funds)
    metrics = metrics_table(prices)
    combined = metadata.merge(metrics, on="ticker", how="inner")
    result = add_scores(combined, load_scoring())
    result.insert(0, "data_source", "DEMO â€” synthetic data" if demo else "Yahoo Finance")
    save_reports(result, ROOT / "reports")
    print(f"Created reports for {len(result)} ETFs through {result['as_of'].max()}.")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the ETF tracker data and reports.")
    parser.add_argument("--demo", action="store_true", help="Use deterministic offline sample data")
    args = parser.parse_args()
    run(demo=args.demo)


if __name__ == "__main__":
    main()

