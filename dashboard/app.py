from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import load_yaml  # noqa: E402
from src.portfolio import analyze_portfolio  # noqa: E402

st.set_page_config(page_title="ETF Tracker", page_icon="ðŸ“ˆ", layout="wide")


@st.cache_data(ttl=900)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    report = ROOT / "reports/latest.csv"
    prices_file = ROOT / "data/prices/adjusted_close.csv"
    if not report.exists():
        raise FileNotFoundError("Run `python -m src.pipeline` or `python -m src.pipeline --demo` first.")
    rankings = pd.read_csv(report)
    prices = pd.read_csv(prices_file, index_col="date", parse_dates=True) if prices_file.exists() else pd.DataFrame()
    return rankings, prices


st.title("ETF Tracker")
st.caption("Canadian ETF performance, risk, cost, and category-relative rankings. Educational use only.")

try:
    df, prices = load_data()
except FileNotFoundError as error:
    st.error(str(error))
    st.code("python -m src.pipeline --demo\nstreamlit run dashboard/app.py")
    st.stop()

if df["data_source"].astype(str).str.startswith("DEMO").any():
    st.warning("This download contains synthetic demo results. Run `python -m src.pipeline` to replace them with current market data.")

with st.sidebar:
    st.header("Filters")
    categories = st.multiselect("Categories", sorted(df["category"].unique()), default=[])
    maximum_mer = st.slider("Maximum MER (%)", 0.0, float(max(3, df["mer"].max())), 1.0, 0.05)
    minimum_history = st.slider("Minimum history (years)", 0, 10, 1)
    search = st.text_input("Ticker or name")
    st.info("Scores compare ETFs within their category. They are not buy recommendations.")

filtered = df[(df["mer"] <= maximum_mer) & (df["history_years"] >= minimum_history)].copy()
if categories:
    filtered = filtered[filtered["category"].isin(categories)]
if search:
    match = filtered["ticker"].str.contains(search, case=False) | filtered["name"].str.contains(search, case=False)
    filtered = filtered[match]

tab_rankings, tab_compare, tab_portfolio, tab_method = st.tabs(
    ["Rankings", "ETF comparison", "My portfolio", "Methodology"]
)

with tab_rankings:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ETFs shown", len(filtered))
    c2.metric("Latest data", filtered["as_of"].max() if len(filtered) else "â€”")
    c3.metric("Best 1-year return", f"{filtered['return_1y'].max():.1f}%" if len(filtered) else "â€”")
    c4.metric("Lowest MER", f"{filtered['mer'].min():.2f}%" if len(filtered) else "â€”")
    columns = [
        "category_rank", "ticker", "name", "category", "return_1m", "return_3m",
        "return_6m", "return_1y", "return_3y_annualized", "volatility",
        "max_drawdown", "mer", "overall_score", "signal",
    ]
    st.dataframe(
        filtered[columns].sort_values(["category", "category_rank"]),
        hide_index=True,
        width="stretch",
        column_config={
            name: st.column_config.NumberColumn(format="%.2f%%")
            for name in ["return_1m", "return_3m", "return_6m", "return_1y", "return_3y_annualized", "volatility", "max_drawdown", "mer"]
        },
    )
    if len(filtered):
        figure = px.scatter(
            filtered, x="volatility", y="return_1y", color="category", size="overall_score",
            hover_name="ticker", hover_data=["name", "mer", "max_drawdown"],
            labels={"volatility": "Annualized volatility (%)", "return_1y": "One-year return (%)"},
            title="Risk versus one-year return",
        )
        st.plotly_chart(figure, width="stretch")

with tab_compare:
    choices = st.multiselect("Select ETFs", sorted(df["ticker"]), default=[ticker for ticker in ["VEQT.TO", "XEQT.TO", "VFV.TO"] if ticker in df["ticker"].values])
    if choices and not prices.empty:
        selected = prices[choices].dropna(how="all")
        normalized = selected.div(selected.apply(lambda column: column.dropna().iloc[0])) * 10_000
        chart_data = normalized.reset_index().melt("date", var_name="ETF", value_name="Value")
        st.plotly_chart(px.line(chart_data, x="date", y="Value", color="ETF", title="Growth of $10,000"), width="stretch")
        st.dataframe(df[df["ticker"].isin(choices)], hide_index=True, width="stretch")

with tab_portfolio:
    portfolio = load_yaml("config/portfolio.yaml")["holdings"]
    st.write("Edit `config/portfolio.yaml` to enter your own holdings and target weights.")
    st.dataframe(pd.DataFrame(portfolio), hide_index=True)
    if not prices.empty:
        summary, correlation, warnings = analyze_portfolio(prices, portfolio)
        st.dataframe(summary, hide_index=True)
        if not correlation.empty:
            st.plotly_chart(px.imshow(correlation, text_auto=".2f", title="Return-correlation proxy for overlap"), width="stretch")
        for warning in warnings:
            st.warning(warning)

with tab_method:
    st.markdown("""
    ### How rankings work

    The overall score combines **40% momentum**, **35% risk-adjusted performance**,
    **15% cost**, and **10% quality**. Percentile scores are calculated within each
    ETF category, preventing bond ETFs from being judged directly against technology ETFs.

    Prices are adjusted for splits and cash distributions. Maximum drawdown measures the
    largest historical peak-to-trough decline. Correlation indicates similar return behaviour,
    but it is not a holdings-level overlap calculation.

    ### Important limitations

    Historical performance does not predict future results. MER values are maintained in the
    watchlist and should be checked against issuer documents. Yahoo Finance is convenient but
    is not an official  data feed. Confirm that an ETF is currently tradable in
     before placing an order.
    """)

