from __future__ import annotations

import pandas as pd
import plotly.express as px


def aggregate_data(
    df: pd.DataFrame,
    *,
    group_column: str,
    value_column: str,
    agg_func: str,
) -> pd.DataFrame:
    if agg_func == "count":
        grouped = df.groupby(group_column, dropna=False).size().reset_index(name="value")
    else:
        grouped = (
            df.groupby(group_column, dropna=False)[value_column]
            .agg(agg_func)
            .reset_index(name="value")
        )
    return grouped.sort_values("value", ascending=False).reset_index(drop=True)


def bar_chart(grouped: pd.DataFrame, *, x: str, y: str, title: str):
    return px.bar(
        grouped,
        x=x,
        y=y,
        text_auto=".2s",
        title=title,
        labels={x: x, y: y},
    )


def line_chart(grouped: pd.DataFrame, *, x: str, y: str, title: str):
    ordered = grouped.sort_values(x)
    return px.line(
        ordered,
        x=x,
        y=y,
        markers=True,
        title=title,
        labels={x: x, y: y},
    )


def pie_chart(grouped: pd.DataFrame, *, names: str, values: str, title: str):
    return px.pie(
        grouped,
        names=names,
        values=values,
        title=title,
    )


def scatter_chart(df: pd.DataFrame, *, x: str, y: str, color: str | None):
    return px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        title=f"{y} so voi {x}",
        labels={x: x, y: y},
    )


def histogram_chart(df: pd.DataFrame, *, x: str, color: str | None):
    return px.histogram(
        df,
        x=x,
        color=color,
        title=f"Phan bo cua {x}",
        labels={x: x, "count": "Tan suat"},
    )


def box_chart(df: pd.DataFrame, *, x: str | None, y: str, color: str | None):
    return px.box(
        df,
        x=x,
        y=y,
        color=color,
        title=f"{y} theo {x or 'toan bo du lieu'}",
        labels={y: y, x or "x": x or "Toan bo du lieu"},
    )
