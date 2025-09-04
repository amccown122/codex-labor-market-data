from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.express as px

from src.utils.storage import read_csv


st.set_page_config(page_title="Labor Market Pulse (PoC)", layout="wide")

st.title("Labor Market Pulse (PoC)")
st.caption("Free signals via FRED + Lightcast Open Skills (US-only)")


@st.cache_data(show_spinner=False)
def load_long_fred() -> pd.DataFrame | None:
    df = read_csv("fred_series_values.csv")
    if df is None or df.empty:
        return None
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    return df


@st.cache_data(show_spinner=False)
def pivot_series(long_df: pd.DataFrame) -> pd.DataFrame:
    wide = long_df.pivot_table(index="date", columns="series_id", values="value", aggfunc="last").sort_index()
    wide = wide.reset_index()
    return wide


def normalize_index(series: pd.Series, baseline_ts: pd.Timestamp) -> pd.Series:
    s = series.copy()
    s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    # Prefer at/before baseline; fallback to first available after
    before = s.loc[s.index <= baseline_ts]
    if not before.empty:
        base_val = before.iloc[-1]
    else:
        after = s.loc[s.index >= baseline_ts]
        base_val = after.iloc[0] if not after.empty else s.dropna().iloc[0]
    if pd.isna(base_val) or base_val == 0:
        return s * 0.0
    return (s / base_val) * 100.0


@st.cache_data(show_spinner=False)
def compute_metrics(wide: pd.DataFrame, baseline_ts: pd.Timestamp) -> pd.DataFrame:
    df = wide.copy()
    # Rename helpful columns if present
    colmap = {
        "UNRATE": "unemp_rate",
        "JTSJOL": "job_openings",
        "JTSHIL": "hires",
        "JTSQUL": "quits",
        "CPIAUCSL": "cpi",
    }
    for src, dst in colmap.items():
        if src in df.columns:
            df[dst] = df[src]

    out = pd.DataFrame({"date": df["date"]})
    df = df.set_index("date")

    if "cpi" in df.columns:
        out["cpi_index"] = normalize_index(df["cpi"], baseline_ts).reindex(out["date"]).values

    for col in ["job_openings", "hires", "quits"]:
        if col in df.columns:
            out[f"{col}_index"] = normalize_index(df[col], baseline_ts).reindex(out["date"]).values

    if "unemp_rate" in df.columns:
        out["unemp_rate"] = df["unemp_rate"].reindex(out["date"]).values

    if "job_openings_index" in out.columns and "cpi_index" in out.columns:
        out["real_openings_index"] = out["job_openings_index"] / (out["cpi_index"] / 100.0)

    return out


@st.cache_data(show_spinner=False)
def load_skills() -> pd.DataFrame | None:
    df = read_csv("skills_taxonomy.csv")
    return df


long_fred = load_long_fred()
skills = load_skills()

if long_fred is None:
    st.warning("No FRED data found. Run `make refresh` first.")
    st.stop()

wide = pivot_series(long_fred)

# Sidebar controls
st.sidebar.header("Controls")
min_date = pd.to_datetime(wide["date"].min()).to_pydatetime()
max_date = pd.to_datetime(wide["date"].max()).to_pydatetime()

default_start = max(min_date, pd.to_datetime(max_date) - pd.DateOffset(years=5))
if isinstance(default_start, pd.Timestamp):
    default_start = default_start.to_pydatetime()
start, end = st.sidebar.slider(
    "Date range",
    value=(default_start, max_date),
    min_value=min_date,
    max_value=max_date,
)

month_options = list(pd.to_datetime(sorted(wide["date"].dt.to_period("M").dt.to_timestamp().unique())))
default_base = pd.Timestamp("2019-12-01")
default_idx = month_options.index(default_base) if default_base in month_options else len(month_options) - 1
baseline_month = st.sidebar.selectbox(
    "Baseline month (index = 100)",
    options=month_options,
    index=default_idx,
    format_func=lambda d: pd.Timestamp(d).strftime("%Y-%m"),
)

smooth = st.sidebar.checkbox("Apply 3-month moving average", value=True)
show_yoy = st.sidebar.checkbox("Show YoY change lines", value=False)

metrics = compute_metrics(wide, pd.Timestamp(baseline_month))
metrics["date"] = pd.to_datetime(metrics["date"])  # ensure TS for filtering

mask = (metrics["date"] >= pd.Timestamp(start)) & (metrics["date"] <= pd.Timestamp(end))
view = metrics.loc[mask].copy()

def smooth_ma(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if not smooth:
        return df
    out = df.copy()
    out = out.set_index("date")
    out[cols] = out[cols].rolling(3, min_periods=1).mean()
    return out.reset_index()


st.subheader("Market Tightness")
cols = [c for c in ["job_openings_index", "unemp_rate"] if c in view.columns]
view_t = smooth_ma(view[["date"] + cols], cols)
fig1 = px.line(view_t, x="date", y=cols, labels={"value": "Index / Rate"}, title="Openings Index vs Unemployment Rate")
st.plotly_chart(fig1, use_container_width=True)

if show_yoy and "unemp_rate" in view.columns and "job_openings_index" in view.columns:
    yoy = view.set_index("date")
    yoy_df = pd.DataFrame({
        "yoy_unemp_rate": yoy["unemp_rate"].pct_change(12) * 100.0,
        "yoy_job_openings_index": yoy["job_openings_index"].pct_change(12) * 100.0,
    }).reset_index()
    fig1b = px.line(yoy_df, x="date", y=["yoy_unemp_rate", "yoy_job_openings_index"], labels={"value": "YoY %"}, title="YoY: Unemployment vs Openings Index")
    st.plotly_chart(fig1b, use_container_width=True)

st.subheader("Churn Pressure")
cols2 = [c for c in ["hires_index", "quits_index"] if c in view.columns]
if cols2:
    view_c = smooth_ma(view[["date"] + cols2], cols2)
    fig2 = px.line(view_c, x="date", y=cols2, labels={"value": "Index"}, title="Hires vs Quits Indices")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Hires/Quits indices not available yet.")

st.subheader("Real Trend")
if "real_openings_index" in view.columns:
    view_r = smooth_ma(view[["date", "real_openings_index"]], ["real_openings_index"])
    fig3 = px.line(view_r, x="date", y="real_openings_index", labels={"real_openings_index": "Index"}, title="CPI-Deflated Openings Index")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Real openings index not available yet.")

st.subheader("Skills (Lightcast Open Skills)")
if skills is None or skills.empty:
    st.info("Skills taxonomy not loaded. Run `make refresh` to fetch.")
else:
    top_cats = skills["category"].value_counts().head(8).index.tolist()
    tab_titles = [str(c) for c in top_cats]
    tabs = st.tabs(tab_titles)
    for i, cat in enumerate(top_cats):
        with tabs[i]:
            subset = skills[skills["category"] == cat].head(50)
            st.write(subset[["skill_id", "name", "category"]])
