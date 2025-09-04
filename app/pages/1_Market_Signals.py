"""
Market Signals Dashboard - Clear indicators of labor market headwinds and tailwinds.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.storage import read_csv
from src.signals.market_conditions import MarketSignals, generate_market_summary

st.set_page_config(page_title="Market Signals", layout="wide", page_icon="📊")

# Professional styling consistent with Home.py
st.markdown("""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main .block-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Signal cards with status indicators */
    .signal-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        color: #1f2937;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid #f1f5f9;
        margin: 1rem 0;
    }
    
    .signal-positive { border-left: 4px solid #10b981; }
    .signal-warning { border-left: 4px solid #f59e0b; }
    .signal-negative { border-left: 4px solid #ef4444; }
    
    .signal-title {
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6b7280;
        margin: 0 0 0.5rem 0;
    }
    
    .signal-value {
        font-size: 1.875rem;
        font-weight: 700;
        color: #111827;
        margin: 0 0 0.5rem 0;
    }
    
    .signal-subtitle {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0;
    }
    
    /* Tab styling improvements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Alert improvements */
    .trend-alert {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
        font-weight: 500;
    }
    
    .alert-success { 
        background: #f0fdf4; 
        border-color: #10b981; 
        color: #065f46; 
    }
    
    .alert-warning { 
        background: #fffbeb; 
        border-color: #f59e0b; 
        color: #92400e; 
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Labor Market Signals Dashboard")
st.caption("Real-time intelligence on market conditions - Headwinds vs Tailwinds")

# Add help link to glossary
col_title, col_help = st.columns([4, 1])
with col_help:
    if st.button("📖 Need help with terms?", help="View comprehensive data glossary"):
        st.switch_page("pages/2_Data_Glossary.py")

# Load data
@st.cache_data(show_spinner=False)
def load_and_process_data():
    """Load market metrics and calculate signals."""
    metrics = read_csv("market_metrics_daily.csv")
    if metrics is None:
        return None, None
        
    metrics['date'] = pd.to_datetime(metrics['date'])
    
    # Calculate signals
    signals = MarketSignals(metrics)
    enhanced_df = signals.calculate_all_signals()
    
    return enhanced_df, signals

# Load data
data, signals_obj = load_and_process_data()

if data is None:
    st.error("No market data available. Please run `make refresh` first.")
    st.stop()

# Get latest signals
latest_date = data['date'].max()
latest_data = data[data['date'] == latest_date].iloc[0]

# Trend calculation for last 6 months
trends = signals_obj.get_trend_signals() if signals_obj else {}

# === EXECUTIVE SUMMARY SECTION ===
st.header("Executive Summary")

# Create 3 columns for key metrics
col1, col2, col3 = st.columns(3)

with col1:
    # Market State Card with professional styling
    market_state = latest_data.get('market_state', 'UNKNOWN')
    status_class = 'signal-positive' if 'EMPLOYER' in market_state else 'signal-negative' if 'EMPLOYEE' in market_state else 'signal-warning'
    
    st.markdown(f"""
    <div class="signal-card {status_class}">
        <h3 class="signal-title">Market State</h3>
        <h1 class="signal-value">{market_state}</h1>
        <p class="signal-subtitle">EPI: {latest_data['employer_power_index']:.2f} | 
           Velocity: {latest_data['talent_velocity']:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Hiring Outlook Card
    hiring = latest_data.get('hiring_outlook', 'UNKNOWN')
    status_class = 'signal-positive' if hiring == 'FAVORABLE' else 'signal-negative' if hiring == 'CHALLENGING' else 'signal-warning'
    
    st.markdown(f"""
    <div class="signal-card {status_class}">
        <h3 class="signal-title">Hiring Outlook</h3>
        <h1 class="signal-value">{hiring}</h1>
        <p class="signal-subtitle">Unemployment: {latest_data['unemp_rate']:.1f}% | 
           Openings Index: {latest_data.get('job_openings_index', 100):.0f}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Retention Risk Card
    retention = latest_data.get('retention_risk', 'UNKNOWN')
    status_class = 'signal-negative' if retention == 'ELEVATED' else 'signal-positive' if retention == 'LOW' else 'signal-warning'
    
    st.markdown(f"""
    <div class="signal-card {status_class}">
        <h3 class="signal-title">Retention Risk</h3>
        <h1 class="signal-value">{retention}</h1>
        <p class="signal-subtitle">Quits Index: {latest_data.get('quits_index', 100):.0f} | 
           Hires Index: {latest_data.get('hires_index', 100):.0f}</p>
    </div>
    """, unsafe_allow_html=True)

# Trend Summary with professional styling
if trends.get('signals'):
    st.markdown("---")
    st.subheader("📈 6-Month Trends")
    for signal in trends['signals']:
        if "rising" in signal or "accelerating" in signal or "tightening" in signal:
            st.markdown(f'<div class="trend-alert alert-warning">⚠️ {signal}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="trend-alert alert-success">✅ {signal}</div>', unsafe_allow_html=True)

# === STRATEGIC RECOMMENDATIONS ===
st.markdown("---")
st.header("🎯 Strategic Recommendations")

# Add explanation for first-time users
with st.expander("❓ What do these metrics mean?", expanded=False):
    st.markdown("""
    **🏆 Employer Power Index (EPI)** → **Hiring Advantage Score**
    - Measures whether conditions favor employers (easier hiring/retention) or employees (competitive market)
    - **Above 1.2**: Strong employer advantage - great time to hire strategically
    - **0.8-1.2**: Balanced market - proceed with standard approach  
    - **Below 0.8**: Employee advantage - focus on retention over hiring
    
    **⚡ Talent Velocity Score**
    - Shows how fast people are changing jobs (quit rates + hire rates)
    - **High velocity**: Competitive market with lots of job movement
    - **Low velocity**: Stable market with less job hopping
    
    **💡 For detailed explanations** of all terms and data sources, visit the **📖 Data Glossary** page.
    """)

# Calculate recommendations based on current state
market_class = signals_obj.classify_market_state(
    latest_data['employer_power_index'],
    latest_data['talent_velocity']
)

rec_col1, rec_col2 = st.columns(2)
with rec_col1:
    st.subheader("Immediate Actions")
    for rec in market_class['recommendations'][:2]:
        st.markdown(f"• {rec}")
        
with rec_col2:
    st.subheader("Planning Considerations")
    for rec in market_class['recommendations'][2:]:
        st.markdown(f"• {rec}")

# === DETAILED METRICS VISUALIZATION ===
st.markdown("---")
st.header("📊 Detailed Market Analysis")

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["Signal Trends", "Market Dynamics", "Predictive Indicators", "Historical Patterns"])

with tab1:
    # Employer Power Index and Talent Velocity over time
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Employer Power Index (EPI)", "Talent Velocity Score"),
        vertical_spacing=0.15
    )
    
    # Professional colors matching our design system
    colors = {
        'primary': '#3730a3',
        'secondary': '#1e40af',  
        'accent': '#ef4444',
        'success': '#10b981'
    }
    
    # EPI Chart with professional styling
    fig.add_trace(
        go.Scatter(
            x=data['date'], 
            y=data['employer_power_index'],
            mode='lines+markers',
            name='EPI',
            line=dict(color=colors['primary'], width=3),
            marker=dict(size=4, color=colors['primary']),
            fill='tozeroy',
            fillcolor=f"rgba({int(colors['primary'][1:3], 16)}, {int(colors['primary'][3:5], 16)}, {int(colors['primary'][5:7], 16)}, 0.1)"
        ),
        row=1, col=1
    )
    
    # Add reference line at 1 (balanced market)
    fig.add_hline(y=1, line_dash="dash", line_color="#6b7280", line_width=2,
                  annotation_text="Balanced Market", annotation_font_color="#6b7280", row=1, col=1)
    
    # Talent Velocity Chart
    fig.add_trace(
        go.Scatter(
            x=data['date'], 
            y=data['talent_velocity'],
            mode='lines+markers',
            name='Velocity',
            line=dict(color=colors['accent'], width=3),
            marker=dict(size=4, color=colors['accent']),
            fill='tozeroy',
            fillcolor=f"rgba({int(colors['accent'][1:3], 16)}, {int(colors['accent'][3:5], 16)}, {int(colors['accent'][5:7], 16)}, 0.1)"
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600, 
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif', size=12, color='#374151'),
        title_font=dict(size=14, color='#111827')
    )
    
    # Clean grid styling
    fig.update_xaxes(gridcolor='#f3f4f6', gridwidth=1, zeroline=False)
    fig.update_yaxes(gridcolor='#f3f4f6', gridwidth=1, zeroline=False)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Index Value", row=1, col=1)
    fig.update_yaxes(title_text="Velocity Score", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Scatter plot showing relationship between unemployment and quits
    if 'quits_index' in data.columns:
        fig = px.scatter(
            data.tail(36),  # Last 3 years
            x='unemp_rate',
            y='quits_index',
            size='talent_velocity',
            color='employer_power_index',
            hover_data=['date'],
            labels={
                'unemp_rate': 'Unemployment Rate (%)',
                'quits_index': 'Quits Index',
                'employer_power_index': 'EPI',
                'talent_velocity': 'Velocity'
            },
            title="Market Dynamics: Unemployment vs Quits (sized by velocity)",
            color_continuous_scale='RdYlBu_r'  # Blue to red, professional palette
        )
        
        # Professional styling
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Inter, sans-serif', size=12, color='#374151'),
            title_font=dict(size=16, color='#111827'),
            coloraxis_colorbar=dict(
                title_font=dict(size=12),
                tickfont=dict(size=10)
            )
        )
        
        fig.update_xaxes(gridcolor='#f3f4f6', gridwidth=1, zeroline=False)
        fig.update_yaxes(gridcolor='#f3f4f6', gridwidth=1, zeroline=False)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **How to read this chart:**
        - 📍 Position: Lower-left = employer's market, Upper-right = employee's market
        - 🔵 Size: Larger bubbles = higher talent velocity (more volatile market)
        - 🎨 Color: Green = employer advantage, Red = employee advantage
        """)

with tab3:
    # Leading indicators dashboard
    st.subheader("Leading Indicators")
    
    # Calculate momentum indicators
    data['epi_momentum'] = data['employer_power_index'].pct_change(3)
    data['velocity_momentum'] = data['talent_velocity'].pct_change(3)
    
    # Create gauge charts for momentum
    col1, col2 = st.columns(2)
    
    with col1:
        latest_epi_mom = data['epi_momentum'].iloc[-1] * 100
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=latest_epi_mom,
            title={'text': "EPI Momentum (3M)"},
            delta={'reference': 0},
            gauge={
                'axis': {'range': [-50, 50]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [-50, -20], 'color': "lightgray"},
                    {'range': [-20, 20], 'color': "gray"},
                    {'range': [20, 50], 'color': "lightgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        latest_vel_mom = data['velocity_momentum'].iloc[-1] * 100
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=latest_vel_mom,
            title={'text': "Velocity Momentum (3M)"},
            delta={'reference': 0},
            gauge={
                'axis': {'range': [-50, 50]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [-50, -20], 'color': "lightgray"},
                    {'range': [-20, 20], 'color': "gray"},
                    {'range': [20, 50], 'color': "lightgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.caption("Momentum > 20% suggests accelerating trends requiring attention")

with tab4:
    # Historical patterns analysis
    st.subheader("Historical Market Patterns")
    
    # Year-over-year comparison
    current_year = latest_date.year
    years_to_show = min(3, len(data['date'].dt.year.unique()))
    
    fig = go.Figure()
    
    for year_offset in range(years_to_show):
        year = current_year - year_offset
        year_data = data[data['date'].dt.year == year].copy()
        year_data['month'] = year_data['date'].dt.month
        
        opacity = 1.0 if year_offset == 0 else 0.5 - (year_offset * 0.15)
        width = 3 if year_offset == 0 else 2
        
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['employer_power_index'],
            mode='lines',
            name=str(year),
            line=dict(width=width),
            opacity=opacity
        ))
    
    fig.update_layout(
        title="Employer Power Index - Year-over-Year Comparison",
        xaxis_title="Month",
        yaxis_title="EPI Value",
        hovermode='x unified',
        height=400
    )
    
    fig.update_xaxes(
        tickmode='array',
        tickvals=list(range(1, 13)),
        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    )
    
    st.plotly_chart(fig, use_container_width=True)

# === MARKET INTELLIGENCE FEED ===
st.markdown("---")
st.header("📰 Market Intelligence Feed")

# Generate alerts based on significant changes
alerts = []

# Check for significant monthly changes
if len(data) > 1:
    prev = data.iloc[-2]
    
    # EPI change
    epi_change = (latest_data['employer_power_index'] / prev['employer_power_index'] - 1) * 100
    if abs(epi_change) > 10:
        direction = "shifted toward employers" if epi_change > 0 else "shifted toward employees"
        alerts.append(f"🔔 Market power has {direction} by {abs(epi_change):.1f}% this month")
    
    # Unemployment spike
    unemp_change = latest_data['unemp_rate'] - prev['unemp_rate']
    if abs(unemp_change) > 0.3:
        direction = "increased" if unemp_change > 0 else "decreased"
        alerts.append(f"📊 Unemployment rate {direction} by {abs(unemp_change):.1f} percentage points")
    
    # Quits momentum
    if 'quits_index' in data.columns:
        quits_change = (latest_data['quits_index'] / prev['quits_index'] - 1) * 100
        if abs(quits_change) > 5:
            direction = "surged" if quits_change > 0 else "dropped"
            alerts.append(f"🚪 Quit rates have {direction} by {abs(quits_change):.1f}%")

if alerts:
    for alert in alerts:
        st.markdown(f'<div class="trend-alert alert-warning">{alert}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="trend-alert alert-success">✅ No significant market disruptions detected</div>', unsafe_allow_html=True)

# Footer with data freshness
st.markdown("---")
st.caption(f"Last updated: {latest_date.strftime('%B %d, %Y')} | Data source: FRED Economic Data")