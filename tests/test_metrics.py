import numpy as np
import pandas as pd

from src.metrics import annualized_return, calculate_metrics, trailing_return


def test_trailing_return_uses_available_prior_date():
    index = pd.bdate_range("2025-01-01", periods=260)
    series = pd.Series(np.linspace(100, 120, len(index)), index=index)
    value = trailing_return(series, pd.DateOffset(months=1))
    assert value > 0


def test_annualized_return_requires_history():
    index = pd.bdate_range("2025-01-01", periods=100)
    series = pd.Series(np.linspace(100, 110, len(index)), index=index)
    assert np.isnan(annualized_return(series, 3))


def test_calculate_metrics_has_expected_fields():
    index = pd.bdate_range("2020-01-01", periods=1300)
    series = pd.Series(100 * np.exp(np.arange(len(index)) * 0.0002), index=index)
    result = calculate_metrics(series)
    assert result["return_1y"] > 0
    assert result["max_drawdown"] <= 0
    assert result["history_years"] > 4


