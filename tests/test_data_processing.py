import pandas as pd

from bun_data_analysis.data import build_overview, clean_dataset
from bun_data_analysis.modeling import train_model
from bun_data_analysis.ui import _xay_dung_tuy_chon_dia_ly


def test_clean_dataset_converts_money_percent_and_dates():
    raw = pd.DataFrame(
        {
            "InvoiceDate": ["3/2/2020"],
            "PriceperUnit": ["$45.00 "],
            "UnitsSold": ["1,220"],
            "TotalSales": ["$371,250 "],
            "OperatingProfit": ["$129,938 "],
            "OperatingMargin": ["35%"],
        }
    )

    cleaned = clean_dataset(raw)

    assert cleaned.loc[0, "PriceperUnit"] == 45.0
    assert cleaned.loc[0, "UnitsSold"] == 1220
    assert cleaned.loc[0, "TotalSales"] == 371250.0
    assert cleaned.loc[0, "OperatingProfit"] == 129938.0
    assert cleaned.loc[0, "OperatingMargin"] == 0.35
    assert str(cleaned.loc[0, "InvoiceDate"].date()) == "2020-02-03"
    assert cleaned.loc[0, "InvoiceDate_year"] == 2020
    assert cleaned.loc[0, "InvoiceDate_month"] == 2


def test_build_overview_aggregates_core_metrics():
    df = pd.DataFrame(
        {
            "TotalSales": [100.0, 200.0],
            "OperatingProfit": [40.0, 60.0],
            "UnitsSold": [2, 3],
        }
    )

    overview = build_overview(df)

    assert overview == {
        "rows": 2,
        "columns": 3,
        "numeric_columns": 3,
        "categorical_columns": 0,
        "datetime_columns": 0,
        "missing_cells": 0,
    }


def test_train_model_returns_metrics_and_predictions():
    df = pd.DataFrame(
        {
            "feature_num": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "feature_cat": ["a", "a", "b", "b", "c", "c", "a", "b", "c", "a"],
            "target": [2, 4, 5, 8, 10, 12, 14, 16, 18, 20],
        }
    )

    result = train_model(df, model_name="Linear Regression", target_column="target")

    assert set(result.metrics) == {"R2", "MAE", "RMSE"}
    assert not result.predictions.empty
    assert "feature_num" in result.feature_columns


def test_location_options_follow_region_and_state():
    df = pd.DataFrame(
        {
            "Region": ["East", "East", "West"],
            "State": ["New York", "New Jersey", "California"],
            "City": ["New York City", "Newark", "Los Angeles"],
        }
    )

    region_options, state_options, city_options = _xay_dung_tuy_chon_dia_ly(
        df,
        selected_regions=["East"],
        selected_states=["New York"],
    )

    assert region_options == ["East", "West"]
    assert state_options == ["New Jersey", "New York"]
    assert city_options == ["New York City"]
