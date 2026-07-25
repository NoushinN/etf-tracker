import pandas as pd

from src.scoring import add_scores


def test_scores_rank_within_category():
    frame = pd.DataFrame(
        {
            "ticker": ["A", "B", "C"], "category": ["Equity"] * 3,
            "return_1m": [1, 2, 3], "return_3m": [2, 3, 4],
            "return_6m": [3, 4, 5], "return_1y": [4, 5, 6],
            "sharpe": [0.5, 0.7, 1.0], "sortino": [0.6, 0.8, 1.1],
            "volatility": [10, 10, 10], "max_drawdown": [-15, -12, -10],
            "mer": [0.2, 0.2, 0.2], "positive_months": [55, 60, 65],
            "history_years": [5, 5, 5],
        }
    )
    config = {
        "momentum_weight": 0.4, "risk_adjusted_weight": 0.35,
        "cost_weight": 0.15, "quality_weight": 0.10,
        "momentum_period_weights": {"return_1m": 0.1, "return_3m": 0.2, "return_6m": 0.3, "return_1y": 0.4},
    }
    result = add_scores(frame, config)
    assert result.iloc[0]["category_rank"] == 1
    assert result.iloc[0]["ticker"] == "C"


