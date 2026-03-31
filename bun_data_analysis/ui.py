from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st

from bun_data_analysis import charts
from bun_data_analysis.data import (
    DEFAULT_DATASET_PATH,
    build_column_report,
    build_numeric_summary,
    build_overview,
    clean_dataset,
    get_categorical_columns,
    get_filterable_columns,
    get_numeric_columns,
    load_data,
    load_default_data,
)
from bun_data_analysis.modeling import MODEL_REGISTRY, train_model

AGGREGATION_LABELS = {
    "Tong": "sum",
    "Trung binh": "mean",
    "Trung vi": "median",
    "Lon nhat": "max",
    "Nho nhat": "min",
    "Dem": "count",
}

MODEL_LABELS = {
    "Hoi quy tuyen tinh": "Linear Regression",
    "Rung ngau nhien": "Random Forest",
    "Cay quyet dinh": "Decision Tree",
}

BAO_CAO_COT_DOI_TEN = {
    "dtype": "Kieu du lieu",
    "missing_values": "So gia tri thieu",
    "missing_pct": "Ty le thieu (%)",
    "unique_values": "So gia tri khac nhau",
    "sample_values": "Vi du gia tri",
}

TOM_TAT_SO_DOI_TEN = {
    "count": "So luong",
    "mean": "Trung binh",
    "std": "Do lech chuan",
    "min": "Nho nhat",
    "25%": "Phan vi 25%",
    "50%": "Trung vi",
    "75%": "Phan vi 75%",
    "max": "Lon nhat",
}

TEN_COT_HIEN_THI = {
    "Retailer": "Nha ban le",
    "RetailerID": "Ma nha ban le",
    "Region": "Khu vuc",
    "State": "Tinh/Bang",
    "City": "Thanh pho",
    "Product": "San pham",
    "PriceperUnit": "Don gia",
    "UnitsSold": "So luong ban",
    "TotalSales": "Tong doanh thu",
    "OperatingProfit": "Loi nhuan hoat dong",
    "OperatingMargin": "Bien loi nhuan",
    "SalesMethod": "Phuong thuc ban hang",
    "InvoiceDate": "Ngay hoa don",
    "InvoiceDate_year": "Nam hoa don",
    "InvoiceDate_month": "Thang hoa don",
    "InvoiceDate_day": "Ngay trong thang",
    "InvoiceDate_weekday": "Thu trong tuan",
    "actual": "Gia tri thuc te",
    "predicted": "Gia tri du doan",
    "abs_error": "Sai so tuyet doi",
}


@st.cache_data(show_spinner=False)
def _load_sample_dataset() -> pd.DataFrame:
    return load_default_data()


@st.cache_data(show_spinner=False)
def _load_uploaded_dataset(file_bytes: bytes) -> pd.DataFrame:
    return load_data(BytesIO(file_bytes))


def run_app() -> None:
    st.set_page_config(page_title="BunDataAnalysis", layout="wide")
    st.title("BunDataAnalysis")
    st.caption("Phan tich tep CSV cho nhieu nganh voi tong quan du lieu, bieu do va mo hinh du doan co ban.")

    raw_df = _select_data_source()
    if raw_df is None:
        st.info("Tai len tep CSV hoac dung bo du lieu mau de bat dau phan tich.")
        return

    cleaned_df = clean_dataset(raw_df)
    filtered_df = _apply_filters(cleaned_df)

    tabs = st.tabs(["Tong quan", "Phan tich", "Truc quan", "Mo hinh", "Huong dan"])
    with tabs[0]:
        _render_overview(filtered_df)
    with tabs[1]:
        _render_analysis(filtered_df)
    with tabs[2]:
        _render_visuals(filtered_df)
    with tabs[3]:
        _render_modeling(filtered_df)
    with tabs[4]:
        _render_learning_path()


def _select_data_source() -> pd.DataFrame | None:
    st.sidebar.header("Nguon du lieu")
    source = st.sidebar.radio("Chon nguon du lieu", ("Du lieu mau", "Tai len CSV"))
    if source == "Du lieu mau":
        st.sidebar.caption(f"Tep du lieu mau: {DEFAULT_DATASET_PATH.name}")
        return _load_sample_dataset()

    uploaded_file = st.sidebar.file_uploader("Tai len tep CSV", type=["csv"])
    if uploaded_file is None:
        return None
    return _load_uploaded_dataset(uploaded_file.getvalue())


def _apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    st.sidebar.header("Bo loc")

    filtered = _ap_dung_bo_loc_dia_ly(filtered)

    filter_candidates = [
        cot
        for cot in get_filterable_columns(filtered)
        if cot not in {"Region", "State", "City"}
    ]
    if not filter_candidates:
        st.sidebar.caption("Khong tim thay cot van ban phu hop de tao bo loc bo sung.")
        return filtered

    default_filters = filter_candidates[: min(4, len(filter_candidates))]
    active_filters = st.sidebar.multiselect(
        "Cot dung de loc",
        options=filter_candidates,
        default=default_filters,
        format_func=_ten_cot_hien_thi,
    )

    for column in active_filters:
        values = sorted(filtered[column].dropna().astype(str).unique().tolist())
        selected_values = st.sidebar.multiselect(_ten_cot_hien_thi(column), options=values, default=values)
        if selected_values:
            filtered = filtered[filtered[column].astype(str).isin(selected_values)]

    st.sidebar.caption(f"So dong sau khi loc: {len(filtered):,}")
    return filtered


def _render_overview(df: pd.DataFrame) -> None:
    overview = build_overview(df)
    metric_columns = st.columns(5)
    metric_columns[0].metric("So dong", f"{overview['rows']:,}")
    metric_columns[1].metric("So cot", f"{overview['columns']:,}")
    metric_columns[2].metric("Cot so", f"{overview['numeric_columns']:,}")
    metric_columns[3].metric("Cot phan loai", f"{overview['categorical_columns']:,}")
    metric_columns[4].metric("O thieu du lieu", f"{overview['missing_cells']:,}")

    if overview["datetime_columns"]:
        st.caption(f"Da phat hien {overview['datetime_columns']} cot ngay gio. He thong da tu dong bo sung cac thanh phan ngay thang nam.")

    left, right = st.columns((3, 2))
    with left:
        st.subheader("Xem nhanh du lieu")
        st.dataframe(_doi_ten_cot_hien_thi(df.head(25)), width="stretch")
    with right:
        st.subheader("Bao cao cot du lieu")
        report = build_column_report(df).rename(columns=BAO_CAO_COT_DOI_TEN)
        report.index = [_ten_cot_hien_thi(index) for index in report.index]
        st.dataframe(report, width="stretch")

    numeric_summary = build_numeric_summary(df)
    if not numeric_summary.empty:
        st.subheader("Thong ke cot so")
        numeric_summary = numeric_summary.rename(columns=TOM_TAT_SO_DOI_TEN)
        numeric_summary.index = [_ten_cot_hien_thi(index) for index in numeric_summary.index]
        st.dataframe(numeric_summary, width="stretch")


def _render_analysis(df: pd.DataFrame) -> None:
    st.subheader("Suc khoe bo du lieu")
    report = build_column_report(df).sort_values("missing_values", ascending=False)
    report_hien_thi = report[["missing_values", "missing_pct", "unique_values"]].rename(columns=BAO_CAO_COT_DOI_TEN)
    report_hien_thi.index = [_ten_cot_hien_thi(index) for index in report_hien_thi.index]
    st.dataframe(report_hien_thi, width="stretch")

    numeric_columns = get_numeric_columns(df)
    categorical_columns = get_categorical_columns(df)

    st.subheader("Phan tich theo nhom")
    if numeric_columns and categorical_columns:
        group_column = st.selectbox(
            "Nhom theo cot",
            options=categorical_columns,
            key="analysis_group",
            format_func=_ten_cot_hien_thi,
        )
        value_column = st.selectbox(
            "Chi so",
            options=numeric_columns,
            key="analysis_value",
            format_func=_ten_cot_hien_thi,
        )
        agg_func = st.selectbox(
            "Cach tinh",
            options=list(AGGREGATION_LABELS.keys()),
            key="analysis_agg",
        )
        grouped = charts.aggregate_data(
            df,
            group_column=group_column,
            value_column=value_column,
            agg_func=AGGREGATION_LABELS[agg_func],
        )
        grouped = grouped.rename(columns={group_column: _ten_cot_hien_thi(group_column), "value": "Gia tri"})
        st.dataframe(grouped.head(100), width="stretch")
    else:
        st.info("Can it nhat mot cot so va mot cot phan loai de phan tich theo nhom.")

    st.subheader("Tai du lieu")
    st.download_button(
        label="Tai file CSV da lam sach",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="bun_data_analysis_cleaned.csv",
        mime="text/csv",
    )


def _render_visuals(df: pd.DataFrame) -> None:
    st.subheader("Tao bieu do")
    numeric_columns = get_numeric_columns(df)
    categorical_columns = get_categorical_columns(df)
    color_candidates = ["Khong"] + get_filterable_columns(df, max_unique=20)

    chart_type = st.selectbox(
        "Loai bieu do",
        options=["Cot", "Duong", "Tron", "Phan tan", "Tan suat", "Hop"],
    )

    if chart_type in {"Cot", "Duong", "Tron"}:
        if not numeric_columns or not categorical_columns:
            st.info("Loai bieu do nay can it nhat mot cot so va mot cot phan loai.")
            return

        group_column = st.selectbox(
            "Cot nhom",
            options=categorical_columns,
            key="chart_group",
            format_func=_ten_cot_hien_thi,
        )
        value_column = st.selectbox(
            "Cot gia tri",
            options=numeric_columns,
            key="chart_value",
            format_func=_ten_cot_hien_thi,
        )
        agg_func = st.selectbox(
            "Cach tinh",
            options=list(AGGREGATION_LABELS.keys()),
            key="chart_agg",
        )
        grouped = charts.aggregate_data(
            df,
            group_column=group_column,
            value_column=value_column,
            agg_func=AGGREGATION_LABELS[agg_func],
        )
        ten_cot_nhom = _ten_cot_hien_thi(group_column)
        ten_cot_gia_tri = _ten_cot_hien_thi(value_column)
        grouped_hien_thi = grouped.rename(columns={group_column: ten_cot_nhom, "value": "Gia tri"})
        title = f"{agg_func} cua {ten_cot_gia_tri} theo {ten_cot_nhom}"
        if chart_type == "Cot":
            fig = charts.bar_chart(grouped_hien_thi, x=ten_cot_nhom, y="Gia tri", title=title)
        elif chart_type == "Duong":
            fig = charts.line_chart(grouped_hien_thi, x=ten_cot_nhom, y="Gia tri", title=title)
        else:
            fig = charts.pie_chart(grouped_hien_thi, names=ten_cot_nhom, values="Gia tri", title=title)
        st.plotly_chart(fig, width="stretch")
        st.dataframe(grouped_hien_thi.head(100), width="stretch")
        return

    if chart_type == "Phan tan":
        if len(numeric_columns) < 2:
            st.info("Bieu do phan tan can it nhat hai cot so.")
            return

        x_column = st.selectbox("Truc X", options=numeric_columns, key="scatter_x", format_func=_ten_cot_hien_thi)
        y_options = [column for column in numeric_columns if column != x_column] or numeric_columns
        y_column = st.selectbox("Truc Y", options=y_options, key="scatter_y", format_func=_ten_cot_hien_thi)
        color_column = st.selectbox("Mau sac", options=color_candidates, key="scatter_color", format_func=_ten_cot_hien_thi)
        doi_ten = {x_column: _ten_cot_hien_thi(x_column), y_column: _ten_cot_hien_thi(y_column)}
        if color_column != "Khong":
            doi_ten[color_column] = _ten_cot_hien_thi(color_column)
        df_hien_thi = df.rename(columns=doi_ten)
        fig = charts.scatter_chart(
            df_hien_thi,
            x=_ten_cot_hien_thi(x_column),
            y=_ten_cot_hien_thi(y_column),
            color=None if color_column == "Khong" else _ten_cot_hien_thi(color_column),
        )
        st.plotly_chart(fig, width="stretch")
        return

    if chart_type == "Tan suat":
        if not numeric_columns:
            st.info("Bieu do tan suat can it nhat mot cot so.")
            return

        x_column = st.selectbox("Cot du lieu", options=numeric_columns, key="hist_x", format_func=_ten_cot_hien_thi)
        color_column = st.selectbox("Mau sac", options=color_candidates, key="hist_color", format_func=_ten_cot_hien_thi)
        doi_ten = {x_column: _ten_cot_hien_thi(x_column)}
        if color_column != "Khong":
            doi_ten[color_column] = _ten_cot_hien_thi(color_column)
        df_hien_thi = df.rename(columns=doi_ten)
        fig = charts.histogram_chart(
            df_hien_thi,
            x=_ten_cot_hien_thi(x_column),
            color=None if color_column == "Khong" else _ten_cot_hien_thi(color_column),
        )
        st.plotly_chart(fig, width="stretch")
        return

    if not numeric_columns:
        st.info("Bieu do hop can it nhat mot cot so.")
        return

    x_options = ["Khong"] + get_filterable_columns(df, max_unique=20)
    y_column = st.selectbox("Cot gia tri", options=numeric_columns, key="box_y", format_func=_ten_cot_hien_thi)
    x_column = st.selectbox("Cot nhom", options=x_options, key="box_x", format_func=_ten_cot_hien_thi)
    color_options = ["Khong"] + [column for column in get_filterable_columns(df, max_unique=20) if column != x_column]
    color_column = st.selectbox("Mau sac", options=color_options, key="box_color", format_func=_ten_cot_hien_thi)
    doi_ten = {y_column: _ten_cot_hien_thi(y_column)}
    if x_column != "Khong":
        doi_ten[x_column] = _ten_cot_hien_thi(x_column)
    if color_column != "Khong":
        doi_ten[color_column] = _ten_cot_hien_thi(color_column)
    df_hien_thi = df.rename(columns=doi_ten)
    fig = charts.box_chart(
        df_hien_thi,
        x=None if x_column == "Khong" else _ten_cot_hien_thi(x_column),
        y=_ten_cot_hien_thi(y_column),
        color=None if color_column == "Khong" else _ten_cot_hien_thi(color_column),
    )
    st.plotly_chart(fig, width="stretch")


def _render_modeling(df: pd.DataFrame) -> None:
    st.subheader("Mo hinh hoi quy co ban")
    numeric_columns = get_numeric_columns(df)
    if len(numeric_columns) < 2:
        st.warning("Can it nhat hai cot so de huan luyen mo hinh hoi quy.")
        return

    model_label = st.selectbox("Mo hinh", options=list(MODEL_LABELS.keys()))
    model_name = MODEL_LABELS[model_label]
    preferred_targets = [column for column in numeric_columns if not column.lower().endswith("id")]
    target_options = preferred_targets or numeric_columns
    default_target = "TotalSales" if "TotalSales" in target_options else target_options[0]
    target_column = st.selectbox(
        "Cot muc tieu",
        options=target_options,
        index=target_options.index(default_target),
        format_func=_ten_cot_hien_thi,
    )

    if st.button("Huan luyen mo hinh", type="primary"):
        try:
            with st.spinner("Dang huan luyen mo hinh..."):
                result = train_model(df, model_name=model_name, target_column=target_column)
        except ValueError as exc:
            st.error(str(exc))
            return

        metric_columns = st.columns(3)
        metric_columns[0].metric("Do phu hop (R2)", f"{result.metrics['R2']:.3f}")
        metric_columns[1].metric("Sai so tuyet doi TB (MAE)", _format_number(result.metrics["MAE"]))
        metric_columns[2].metric("Can hai sai so TB (RMSE)", _format_number(result.metrics["RMSE"]))

        st.caption("Cac cot dau vao duoc dung: " + ", ".join(_ten_cot_hien_thi(cot) for cot in result.feature_columns))
        if result.ignored_columns:
            st.caption("Cac cot bi bo qua: " + ", ".join(_ten_cot_hien_thi(cot) for cot in result.ignored_columns))
        st.dataframe(_doi_ten_cot_hien_thi(result.predictions.head(25)), width="stretch")


def _render_learning_path() -> None:
    st.subheader("Cach hoc project nay")
    st.markdown(
        """
        1. Bat dau voi `bun_data_analysis/data.py` de hieu cach lam sach CSV tong quat.
        2. Chuyen sang `bun_data_analysis/charts.py` de hieu cach tao bang trung gian cho bieu do.
        3. Doc `bun_data_analysis/modeling.py` de hieu pipeline hoi quy tong quat.
        4. Doc `bun_data_analysis/ui.py` sau cung de thay Streamlit ghep moi phan lai voi nhau.
        """
    )

    st.subheader("Bai tap goi y")
    st.markdown(
        """
        - Them bo loc khoang ngay cho cac cot ngay gio duoc phat hien.
        - Them heatmap tuong quan cho cac cot so.
        - Cho phep luu tuy chon bieu do vao `st.session_state`.
        - Them bai toan phan loai cho cot muc tieu dang phan loai.
        """
    )


def _format_number(value: float) -> str:
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    if abs(value) >= 1:
        return f"{value:,.2f}"
    return f"{value:,.4f}"


def _ap_dung_bo_loc_dia_ly(df: pd.DataFrame) -> pd.DataFrame:
    if not {"Region", "State", "City"} & set(df.columns):
        return df

    st.sidebar.subheader("Bo loc dia ly")
    da_loc = df.copy()

    region_options, state_options, city_options = _xay_dung_tuy_chon_dia_ly(da_loc)

    if "Region" in da_loc.columns:
        selected_regions = st.sidebar.multiselect(
            "Khu vuc",
            options=region_options,
            default=region_options,
        )
        da_loc = _loc_theo_gia_tri(da_loc, "Region", selected_regions)
    else:
        selected_regions = []

    if "State" in da_loc.columns:
        _, state_options, _ = _xay_dung_tuy_chon_dia_ly(df, selected_regions=selected_regions)
        selected_states = st.sidebar.multiselect(
            "Tinh/Bang",
            options=state_options,
            default=state_options,
        )
        da_loc = _loc_theo_gia_tri(da_loc, "State", selected_states)
    else:
        selected_states = []

    if "City" in da_loc.columns:
        _, _, city_options = _xay_dung_tuy_chon_dia_ly(
            df,
            selected_regions=selected_regions,
            selected_states=selected_states,
        )
        selected_cities = st.sidebar.multiselect(
            "Thanh pho",
            options=city_options,
            default=city_options,
        )
        da_loc = _loc_theo_gia_tri(da_loc, "City", selected_cities)

    return da_loc


def _xay_dung_tuy_chon_dia_ly(
    df: pd.DataFrame,
    *,
    selected_regions: list[str] | None = None,
    selected_states: list[str] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    region_options = _lay_gia_tri_loc(df, "Region")

    theo_khu_vuc = _loc_theo_gia_tri(df, "Region", selected_regions or [])
    state_options = _lay_gia_tri_loc(theo_khu_vuc, "State")

    theo_bang = _loc_theo_gia_tri(theo_khu_vuc, "State", selected_states or [])
    city_options = _lay_gia_tri_loc(theo_bang, "City")

    return region_options, state_options, city_options


def _lay_gia_tri_loc(df: pd.DataFrame, ten_cot: str) -> list[str]:
    if ten_cot not in df.columns:
        return []
    return sorted(df[ten_cot].dropna().astype(str).unique().tolist())


def _loc_theo_gia_tri(df: pd.DataFrame, ten_cot: str, gia_tri_duoc_chon: list[str]) -> pd.DataFrame:
    if ten_cot not in df.columns or not gia_tri_duoc_chon:
        return df
    return df[df[ten_cot].astype(str).isin(gia_tri_duoc_chon)]


def _ten_cot_hien_thi(ten_cot: str) -> str:
    return TEN_COT_HIEN_THI.get(ten_cot, ten_cot)


def _doi_ten_cot_hien_thi(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=_ten_cot_hien_thi)
