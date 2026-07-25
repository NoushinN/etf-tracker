# ETF Tracker

An automated Canadian ETF screener and Streamlit dashboard for comparing ETFs
commonly available through Canadian self-directed brokerages. It measures total
return, risk, cost, trend consistency, and portfolio correlation.

> This project is an educational research tool, not financial advice or a trade
> execution system. Confirm prices, fees, eligibility, and product documents before investing.

## Features

- Curated watchlist of 40+ Canadian-listed ETFs across 13 categories
- Distribution-adjusted 1-week, 1/3/6-month, YTD, and 1/3/5/10-year returns
- Volatility, maximum drawdown, current drawdown, Sharpe and Sortino ratios
- Category-relative momentum, risk, cost, quality, and overall scores
- Trend labels without pretending to produce certain buy/sell recommendations
- Growth-of-$10,000 and risk-return comparisons
- Portfolio target weights, correlation warnings, CSV and Excel reports
- Weekly GitHub Actions refresh
- Deterministic offline demo mode

## Quick start

Python 3.11 or 3.12 is recommended.

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install, build the report, and launch Streamlit:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python -m src.pipeline
streamlit run dashboard/app.py
```

Streamlit normally opens `http://localhost:8501`.

If the market-data service is unavailable, launch a fully functional offline demo:

```bash
python -m src.pipeline --demo
streamlit run dashboard/app.py
```

## Customize it

- Edit `config/watchlist.yaml` to add or remove ETFs and update MERs.
- Edit `config/portfolio.yaml` with your holdings and target weights.
- Edit `config/scoring.yaml` to change score weights.
- Yahoo Finance uses `.TO` for Toronto-listed ETFs; for example, `VEQT.TO`.

MER values are deliberately stored in configuration because issuer fees can
change and free price APIs do not reliably maintain Canadian ETF metadata.

## Ranking methodology

The overall score is:

```text
40% momentum + 35% risk-adjusted performance + 15% cost + 10% quality
```

Momentum uses 1-, 3-, 6-, and 12-month total returns. Risk scoring uses Sharpe,
Sortino, volatility, and maximum drawdown. Quality uses positive-month frequency
and history length. All percentiles are calculated **within category**.

Scores help organize research; they do not forecast returns. Avoid selecting an
ETF solely because it recently ranked first.

## Tests and formatting

```bash
pytest -q
ruff check .
```

## GitHub and Streamlit Cloud

1. Create an empty GitHub repository.
2. Push this folder to the repository.
3. The included workflow updates reports every Friday after North American markets close.
4. On Streamlit Community Cloud, select `dashboard/app.py` as the entry point.

GitHub Actions needs `contents: write` permission. If your repository defaults to
read-only workflow permissions, enable **Settings â†’ Actions â†’ General â†’ Workflow
permissions â†’ Read and write permissions**.

## Data and limitations

- Prices come from Yahoo Finance through `yfinance`, not from .
- Adjusted prices incorporate splits and distributions when supplied correctly by the provider.
-  availability can change; search the ticker in  before ordering.
- Correlation is a behaviour-based overlap proxy, not a holdings-level comparison.
- Taxes, bid-ask spreads, currency conversion, withholding tax, and personal suitability are not modeled.
- Leveraged/inverse products are intentionally omitted from the default watchlist.

## License

MIT

