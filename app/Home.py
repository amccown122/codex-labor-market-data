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

# Professional Executive Dashboard Styling
st.markdown("""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global overrides */
    .main .block-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        padding-top: 1rem;
    }
    
    /* Executive header with subtle branding */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 40px rgba(30, 58, 138, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Professional metric cards with status-based colors */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        color: #1f2937;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12);
    }
    
    /* Status indicators with semantic colors */
    .status-positive { border-left: 4px solid #10b981; }
    .status-warning { border-left: 4px solid #f59e0b; }
    .status-negative { border-left: 4px solid #ef4444; }
    .status-neutral { border-left: 4px solid #6b7280; }
    
    /* Typography hierarchy */
    .metric-title {
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6b7280;
        margin: 0;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #111827;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .metric-subtitle {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0;
        font-weight: 400;
    }
    
    /* Professional feature cards */
    .feature-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card:hover {
        border-color: #3730a3;
        box-shadow: 0 4px 12px rgba(55, 48, 163, 0.1);
    }
    
    /* CTA buttons with consistent branding */
    .cta-button {
        background: linear-gradient(135deg, #3730a3 0%, #1e40af 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem 0.25rem;
        transition: all 0.2s ease;
    }
    
    .cta-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(55, 48, 163, 0.3);
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
    # Determine status class based on market state
    state = summary['market_state']
    status_class = 'status-positive' if 'EMPLOYER' in state else 'status-negative' if 'EMPLOYEE' in state else 'status-warning'
    st.markdown(f"""
    <div class="metric-card {status_class}">
        <h3 class="metric-title">Market State</h3>
        <h2 class="metric-value">{state}</h2>
        <p class="metric-subtitle">{summary['date']}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    outlook = summary['hiring_outlook']
    status_class = 'status-positive' if outlook == 'FAVORABLE' else 'status-negative' if outlook == 'CHALLENGING' else 'status-warning'
    st.markdown(f"""
    <div class="metric-card {status_class}">
        <h3 class="metric-title">Hiring Outlook</h3>
        <h2 class="metric-value">{outlook}</h2>
        <p class="metric-subtitle">EPI: {summary['metrics']['employer_power_index']['value']}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Lower unemployment is generally good (status-positive), higher is concerning
    unemp_rate = float(summary['metrics']['unemployment_rate']['value'].replace('%', ''))
    status_class = 'status-positive' if unemp_rate < 4.5 else 'status-warning' if unemp_rate < 6.0 else 'status-negative'
    st.markdown(f"""
    <div class="metric-card {status_class}">
        <h3 class="metric-title">Unemployment Rate</h3>
        <h2 class="metric-value">{summary['metrics']['unemployment_rate']['value']}</h2>
        <p class="metric-subtitle">{summary['metrics']['unemployment_rate']['mom_change']} MoM</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    risk = summary['retention_risk']
    status_class = 'status-negative' if risk == 'ELEVATED' else 'status-positive' if risk == 'LOW' else 'status-warning'
    st.markdown(f"""
    <div class="metric-card {status_class}">
        <h3 class="metric-title">Retention Risk</h3>
        <h2 class="metric-value">{risk}</h2>
        <p class="metric-subtitle">Velocity: {summary['metrics']['talent_velocity']['value']}</p>
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
    
    # Professional color palette for executive dashboards
    colors = {
        'primary': '#3730a3',      # Professional blue
        'success': '#10b981',      # Green for positive metrics
        'warning': '#f59e0b',      # Amber for caution
        'danger': '#ef4444',       # Red for negative metrics
        'neutral': '#6b7280'       # Gray for neutral
    }
    
    # Unemployment (lower is better, so use inverted color logic)
    fig.add_trace(
        go.Scatter(x=recent_data['date'], y=recent_data['unemp_rate'], 
                  mode='lines+markers', name='Unemployment', 
                  line=dict(color=colors['danger'], width=3),
                  marker=dict(size=6)),
        row=1, col=1
    )
    
    # EPI (balanced market at 1.0)
    fig.add_trace(
        go.Scatter(x=recent_data['date'], y=recent_data['employer_power_index'], 
                  mode='lines+markers', name='EPI',
                  line=dict(color=colors['primary'], width=3),
                  marker=dict(size=6)),
        row=1, col=2
    )
    
    # Job Openings
    if 'job_openings_index' in recent_data.columns:
        fig.add_trace(
            go.Scatter(x=recent_data['date'], y=recent_data['job_openings_index'], 
                      mode='lines+markers', name='Job Openings',
                      line=dict(color=colors['success'], width=3),
                      marker=dict(size=6)),
            row=2, col=1
        )
    
    # Quits (higher usually means employee confidence)
    if 'quits_index' in recent_data.columns:
        fig.add_trace(
            go.Scatter(x=recent_data['date'], y=recent_data['quits_index'], 
                      mode='lines+markers', name='Quits',
                      line=dict(color=colors['warning'], width=3),
                      marker=dict(size=6)),
            row=2, col=2
        )
    
    fig.update_layout(
        height=500, 
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif', size=12, color='#374151'),
        title_font=dict(size=16, color='#111827')
    )
    
    # Clean grid styling
    fig.update_xaxes(gridcolor='#f3f4f6', gridwidth=1, zeroline=False)
    fig.update_yaxes(gridcolor='#f3f4f6', gridwidth=1, zeroline=False)
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