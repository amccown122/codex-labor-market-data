from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.express as px

from src.utils.storage import read_csv


st.set_page_config(page_title="Labor Market Pulse (PoC)", layout="wide")

st.title("Labor Market Pulse (PoC)")
st.caption("Free signals via FRED + Lightcast Open Skills (US-only)")

metrics = read_csv("market_metrics_daily.csv")
skills = read_csv("skills_taxonomy.csv")

if metrics is None or metrics.empty:
    st.warning("No metrics found. Run `make refresh` first.")
    st.stop()

metrics["date"] = pd.to_datetime(metrics["date"])  # type: ignore

# Sidebar controls
st.sidebar.header("Controls")
min_date = metrics["date"].min()
max_date = metrics["date"].max()
start, end = st.sidebar.slider(
    "Date range",
    value=(max(pd.Timestamp(min_date), pd.Timestamp(max_date) - pd.DateOffset(years=5)), pd.Timestamp(max_date)),
    min_value=pd.Timestamp(min_date),
    max_value=pd.Timestamp(max_date),
)

smooth = st.sidebar.checkbox("Apply 3-month moving average", value=True)

def smooth_ma(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if not smooth:
        return df
    out = df.copy()
    out = out.set_index("date")
    out[cols] = out[cols].rolling(3, min_periods=1).mean()
    return out.reset_index()

mask = (metrics["date"] >= pd.Timestamp(start)) & (metrics["date"] <= pd.Timestamp(end))
view = metrics.loc[mask].copy()

st.subheader("Market Tightness")
cols = [c for c in ["job_openings_index", "unemp_rate"] if c in view.columns]
view_t = smooth_ma(view[["date"] + cols], cols)
fig1 = px.line(view_t, x="date", y=cols, labels={"value": "Index / Rate"}, title="Openings Index vs Unemployment Rate")
st.plotly_chart(fig1, use_container_width=True)

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
    # Simple peek: show top categories and a sample
    top_cats = skills["category"].value_counts().head(8).index.tolist()
    tab_titles = [str(c) for c in top_cats]
    tabs = st.tabs(tab_titles)
    for i, cat in enumerate(top_cats):
        with tabs[i]:
            subset = skills[skills["category"] == cat].head(50)
            st.write(subset[["skill_id", "name", "category"]])

