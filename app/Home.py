"""
Labor Market Pulse - Enhanced Dashboard with Market Signals
Main landing page and navigation.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.utils.storage import read_csv
from src.signals.market_conditions import MarketSignals, generate_market_summary

st.set_page_config(
    page_title="Labor Market Pulse", 
    layout="wide",
    page_icon="🎯",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .feature-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
    .nav-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.5rem;">🎯 Labor Market Pulse</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
        Strategic talent intelligence platform with real-time market signals
    </p>
</div>
""", unsafe_allow_html=True)

# Load and process data for summary
@st.cache_data(show_spinner=False)
def load_market_summary():
    """Load market data and generate executive summary."""
    metrics = read_csv("market_metrics_daily.csv")
    if metrics is None or metrics.empty:
        return None
        
    metrics['date'] = pd.to_datetime(metrics['date'])
    
    # Calculate signals
    signals = MarketSignals(metrics)
    enhanced_df = signals.calculate_all_signals()
    summary = generate_market_summary(enhanced_df)
    
    return summary, enhanced_df

summary_data = load_market_summary()

if summary_data is None:
    st.error("""
    ### 🚨 No Market Data Available
    
    Please run the data refresh command to fetch the latest economic data:
    
    ```bash
    make refresh
    ```
    
    Or run individual components:
    ```bash
    make refresh-fred
    make refresh-metrics
    ```
    """)
    st.stop()

summary, full_data = summary_data

# === EXECUTIVE DASHBOARD ===
st.header("📊 Executive Dashboard")

# Key metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: white;">Market State</h3>
        <h2 style="margin: 0.5rem 0; color: white;">{summary['market_state']}</h2>
        <p style="margin: 0; opacity: 0.9;">{summary['date']}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: white;">Hiring Outlook</h3>
        <h2 style="margin: 0.5rem 0; color: white;">{summary['hiring_outlook']}</h2>
        <p style="margin: 0; opacity: 0.9;">EPI: {summary['metrics']['employer_power_index']['value']}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: white;">Unemployment</h3>
        <h2 style="margin: 0.5rem 0; color: white;">{summary['metrics']['unemployment_rate']['value']}</h2>
        <p style="margin: 0; opacity: 0.9;">{summary['metrics']['unemployment_rate']['mom_change']} MoM</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: white;">Retention Risk</h3>
        <h2 style="margin: 0.5rem 0; color: white;">{summary['retention_risk']}</h2>
        <p style="margin: 0; opacity: 0.9;">Velocity: {summary['metrics']['talent_velocity']['value']}</p>
    </div>
    """, unsafe_allow_html=True)

# Quick trends visualization
st.subheader("📈 Market Trends at a Glance")

if len(full_data) > 12:
    # Show last 12 months of key metrics
    recent_data = full_data.tail(12)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Unemployment Rate", "Employer Power Index", "Job Openings Index", "Quits Index"),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Unemployment
    fig.add_trace(
        go.Scatter(x=recent_data['date'], y=recent_data['unemp_rate'], 
                  mode='lines+markers', name='Unemployment', 
                  line=dict(color='#1f77b4', width=3)),
        row=1, col=1
    )
    
    # EPI
    fig.add_trace(
        go.Scatter(x=recent_data['date'], y=recent_data['employer_power_index'], 
                  mode='lines+markers', name='EPI',
                  line=dict(color='#ff7f0e', width=3)),
        row=1, col=2
    )
    
    # Job Openings
    if 'job_openings_index' in recent_data.columns:
        fig.add_trace(
            go.Scatter(x=recent_data['date'], y=recent_data['job_openings_index'], 
                      mode='lines+markers', name='Job Openings',
                      line=dict(color='#2ca02c', width=3)),
            row=2, col=1
        )
    
    # Quits
    if 'quits_index' in recent_data.columns:
        fig.add_trace(
            go.Scatter(x=recent_data['date'], y=recent_data['quits_index'], 
                      mode='lines+markers', name='Quits',
                      line=dict(color='#d62728', width=3)),
            row=2, col=2
        )
    
    fig.update_layout(height=500, showlegend=False)
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Index", row=1, col=2)
    fig.update_yaxes(title_text="Index", row=2, col=1)
    fig.update_yaxes(title_text="Index", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)

# === PLATFORM FEATURES ===
st.markdown("---")
st.header("🚀 Platform Features")

# Feature overview
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🎯 Market Signals
    - **Headwind/Tailwind Analysis**: Clear indicators of market conditions
    - **Employer Power Index**: Quantified hiring advantage metrics
    - **Talent Velocity Tracking**: Monitor market volatility
    - **Strategic Recommendations**: AI-driven insights for HR strategy
    
    ### 📊 Advanced Analytics  
    - **Predictive Indicators**: Early warning signals for market shifts
    - **Historical Patterns**: Year-over-year comparative analysis
    - **Momentum Tracking**: 3-month trend acceleration detection
    - **Market Intelligence Feed**: Real-time alerts on significant changes
    """)

with col2:
    st.markdown("""
    ### 🏢 Talent Benchmarking *(Coming Soon)*
    - **Segment Analysis**: Compare metrics by role, level, and location
    - **Lifecycle Metrics**: Track attraction through retention
    - **Internal vs Market**: Benchmark your people metrics
    - **Competitive Intelligence**: Understand your market position
    
    ### 📍 Geographic Intelligence *(Coming Soon)*
    - **Metro-level Analysis**: City and region-specific insights
    - **Location Strategy**: Optimize office and remote work decisions
    - **Migration Patterns**: Track talent movement between markets
    - **Cost vs Availability**: Balance compensation and talent access
    """)

# === NAVIGATION ===
st.markdown("---")
st.header("🧭 Dashboard Navigation")

st.info("""
**📱 Multi-page Dashboard**: Use the sidebar navigation to explore different analysis views:

- **🏠 Home**: Executive overview and platform introduction (this page)
- **📊 Market Signals**: Detailed headwind/tailwind analysis with strategic recommendations
- **📈 Market Tightness**: Traditional unemployment vs job openings analysis
- **🔄 Churn Pressure**: Quits vs hires indices and turnover insights
- **💰 Real Trend**: CPI-adjusted economic indicators
- **🛠️ Skills**: Role-family analysis using skills taxonomy (when available)
""")

# Quick action buttons
st.markdown("### Quick Actions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎯 View Market Signals", type="primary"):
        st.switch_page("pages/1_Market_Signals.py")

with col2:
    if st.button("📊 Market Analysis"):
        # Will redirect to original analysis once we restructure
        pass

with col3:
    if st.button("🔄 Refresh Data"):
        st.code("make refresh")
        st.caption("Run this command in your terminal")

with col4:
    if st.button("📚 View Documentation"):
        st.code("cat CLAUDE.md")
        st.caption("Implementation guide")

# === RECENT UPDATES ===
st.markdown("---")
st.header("🆕 Recent Updates")

st.success("""
**✅ Enhanced Market Signals (Latest)**
- Added Employer Power Index (EPI) calculation
- Implemented Talent Velocity Score
- Created headwind/tailwind classification system
- Built strategic recommendations engine
- Added momentum and trend detection

**✅ Core Platform (Established)**
- FRED economic data integration (5 series)
- Real-time dashboard with interactive controls
- CSV and DuckDB dual storage system
- Automated nightly refresh via GitHub Actions
""")

# === DATA FRESHNESS ===
if 'date' in full_data.columns:
    latest_date = full_data['date'].max()
    st.markdown(f"---")
    st.caption(f"📅 Data current through: **{latest_date.strftime('%B %d, %Y')}**")
    st.caption("🔄 Data refreshes automatically daily at 7:00 AM UTC via GitHub Actions")
else:
    st.caption("📅 Data freshness information unavailable")

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>Labor Market Pulse | Built with Streamlit + FRED Economic Data + Lightcast Open Skills</p>
    <p>For questions or feature requests, check the CLAUDE.md documentation</p>
</div>
""", unsafe_allow_html=True)