from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor

MODEL_REGISTRY = {
    "Linear Regression": LinearRegression,
    "Random Forest": lambda: RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        min_samples_leaf=2,
    ),
    "Decision Tree": lambda: DecisionTreeRegressor(
        random_state=42,
        min_samples_leaf=2,
        max_depth=8,
    ),
}


@dataclass
class ModelResult:
    metrics: dict[str, float]
    predictions: pd.DataFrame
    feature_columns: list[str]
    ignored_columns: list[str]


def train_model(
    df: pd.DataFrame,
    *,
    model_name: str,
    target_column: str,
) -> ModelResult:
    if target_column not in df.columns:
        raise ValueError(f"Khong ton tai cot muc tieu '{target_column}'.")
    if not pd.api.types.is_numeric_dtype(df[target_column]):
        raise ValueError("Cot muc tieu phai la cot so.")

    feature_columns, ignored_columns = _select_feature_columns(df, target_column)
    if not feature_columns:
        raise ValueError("Khong tim thay cot dau vao phu hop de huan luyen mo hinh.")

    model_frame = df[feature_columns + [target_column]].dropna(subset=[target_column]).copy()
    if len(model_frame) < 10:
        raise ValueError("Can it nhat 10 dong co cot muc tieu dang so de huan luyen mo hinh.")

    X = model_frame[feature_columns]
    y = model_frame[target_column]

    categorical_features = X.select_dtypes(include=["object", "string", "category", "bool"]).columns.tolist()
    numeric_features = [column for column in feature_columns if column not in categorical_features]

    transformers = []
    if numeric_features:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                    ]
                ),
                numeric_features,
            )
        )
    if categorical_features:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            )
        )

    if not transformers:
        raise ValueError("Khong tim thay nhom bien hop le de tien xu ly.")

    preprocessor = ColumnTransformer(transformers=transformers)
    model_factory = MODEL_REGISTRY[model_name]
    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model_factory()),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    metrics = {
        "R2": r2_score(y_test, predictions),
        "MAE": mean_absolute_error(y_test, predictions),
        # Avoid version-specific sklearn API changes around RMSE helpers.
        "RMSE": sqrt(mean_squared_error(y_test, predictions)),
    }
    result_frame = X_test.copy()
    result_frame["actual"] = y_test
    result_frame["predicted"] = predictions
    result_frame["abs_error"] = (result_frame["actual"] - result_frame["predicted"]).abs()
    result_frame = result_frame.sort_values("abs_error", ascending=False).reset_index(drop=True)

    return ModelResult(
        metrics=metrics,
        predictions=result_frame,
        feature_columns=feature_columns,
        ignored_columns=ignored_columns,
    )


def _select_feature_columns(df: pd.DataFrame, target_column: str) -> tuple[list[str], list[str]]:
    feature_columns: list[str] = []
    ignored_columns: list[str] = []
    max_unique_categorical = min(100, max(20, len(df) // 2))

    for column in df.columns:
        if column == target_column:
            continue

        series = df[column]
        if series.isna().all():
            ignored_columns.append(column)
            continue

        if pd.api.types.is_datetime64_any_dtype(series):
            ignored_columns.append(column)
            continue

        if pd.api.types.is_numeric_dtype(series):
            if column.lower().endswith("id"):
                ignored_columns.append(column)
                continue
            feature_columns.append(column)
            continue

        unique_values = series.nunique(dropna=True)
        if unique_values > max_unique_categorical:
            ignored_columns.append(column)
            continue

        feature_columns.append(column)

    return feature_columns, ignored_columns
