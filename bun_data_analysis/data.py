from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "sample_dataset.csv"

AUTO_CONVERT_THRESHOLD = 0.8
FILTERABLE_UNIQUE_LIMIT = 60


def load_data(source: str | Path | BinaryIO) -> pd.DataFrame:
    return pd.read_csv(source)


def load_default_data() -> pd.DataFrame:
    return load_data(DEFAULT_DATASET_PATH)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data.columns = [str(column).strip() for column in data.columns]
    data = data.dropna(how="all").reset_index(drop=True)

    for column in data.columns:
        series = data[column]
        if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
            normalized = series.astype("string").str.strip()
            normalized = normalized.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA})
            data[column] = _coerce_string_series(normalized)

    return _add_datetime_parts(data)


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def get_datetime_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> list[str]:
    datetime_columns = set(get_datetime_columns(df))
    numeric_columns = set(get_numeric_columns(df))
    return [column for column in df.columns if column not in numeric_columns and column not in datetime_columns]


def get_filterable_columns(df: pd.DataFrame, *, max_unique: int = FILTERABLE_UNIQUE_LIMIT) -> list[str]:
    return [
        column
        for column in get_categorical_columns(df)
        if 1 < df[column].nunique(dropna=True) <= max_unique
    ]


def build_overview(df: pd.DataFrame) -> dict[str, int]:
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "numeric_columns": len(get_numeric_columns(df)),
        "categorical_columns": len(get_categorical_columns(df)),
        "datetime_columns": len(get_datetime_columns(df)),
        "missing_cells": int(df.isna().sum().sum()),
    }


def build_column_report(df: pd.DataFrame) -> pd.DataFrame:
    report = pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "missing_values": df.isna().sum(),
            "missing_pct": (df.isna().mean() * 100).round(2),
            "unique_values": df.nunique(dropna=True),
            "sample_values": [_sample_values(df[column]) for column in df.columns],
        },
        index=df.columns,
    )
    return report


def build_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = get_numeric_columns(df)
    if not numeric_columns:
        return pd.DataFrame()
    return df[numeric_columns].describe().transpose().round(3)


def _coerce_string_series(series: pd.Series) -> pd.Series:
    if series.dropna().empty:
        return series

    numeric_series = _try_parse_numeric(series)
    if numeric_series is not None:
        return numeric_series

    datetime_series = _try_parse_datetime(series)
    if datetime_series is not None:
        return datetime_series

    return series


def _try_parse_numeric(series: pd.Series) -> pd.Series | None:
    non_null = series.dropna()
    cleaned = (
        series.str.replace(r"[$€£¥]", "", regex=True)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace(r"\s+", "", regex=True)
    )
    numeric = pd.to_numeric(cleaned, errors="coerce").astype(float)
    success_ratio = numeric.notna().sum() / len(non_null)
    digit_ratio = non_null.str.contains(r"\d", regex=True, na=False).mean()

    if success_ratio < AUTO_CONVERT_THRESHOLD or digit_ratio < AUTO_CONVERT_THRESHOLD:
        return None

    if non_null.str.contains("%", regex=False, na=False).any():
        numeric = numeric.where(numeric.isna() | (numeric <= 1), numeric / 100)

    if _looks_integer(numeric):
        return numeric.round().astype("Int64")

    return numeric


def _try_parse_datetime(series: pd.Series) -> pd.Series | None:
    non_null = series.dropna()
    parsed = pd.to_datetime(series, format="mixed", dayfirst=True, errors="coerce")
    success_ratio = parsed.notna().sum() / len(non_null)
    date_like_ratio = non_null.str.contains(r"[-/:]", regex=True, na=False).mean()

    if success_ratio >= AUTO_CONVERT_THRESHOLD and date_like_ratio >= 0.4:
        return parsed
    return None


def _looks_integer(series: pd.Series) -> bool:
    non_null = series.dropna()
    if non_null.empty:
        return False
    return ((non_null - non_null.round()).abs() < 1e-9).all()


def _add_datetime_parts(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    for column in get_datetime_columns(data):
        data[f"{column}_year"] = data[column].dt.year.astype("Int64")
        data[f"{column}_month"] = data[column].dt.month.astype("Int64")
        data[f"{column}_day"] = data[column].dt.day.astype("Int64")
        data[f"{column}_weekday"] = data[column].dt.day_name()
    return data


def _sample_values(series: pd.Series) -> str:
    values = series.dropna().astype(str).unique().tolist()[:3]
    return ", ".join(values)
