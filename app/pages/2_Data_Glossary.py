"""
Data Glossary - Clear explanations of all metrics, terms, and concepts
"""
import streamlit as st

st.set_page_config(page_title="Data Glossary", layout="wide", page_icon="📖")

st.title("📖 Data Glossary & Methodology")
st.caption("Clear explanations of all metrics, data sources, and calculations")

# Search functionality
search_term = st.text_input("🔍 Search glossary terms", placeholder="Type to search...")

# Create tabs for different categories
tab1, tab2, tab3, tab4 = st.tabs(["Key Metrics", "Data Sources", "Calculations", "Market Terms"])

with tab1:
    st.header("📊 Key Metrics Explained")
    
    # Main metrics with detailed explanations
    metrics = {
        "Hiring Advantage Score (EPI)": {
            "simple": "How easy it is for employers to hire and retain talent",
            "detailed": "A composite score that measures whether market conditions favor employers or employees. Higher scores (>1.2) indicate employers have the advantage - unemployment is higher relative to job openings, and employees are less likely to quit. Lower scores (<0.8) indicate employees have the advantage - low unemployment, high quit rates, and strong wage growth pressure.",
            "formula": "(Unemployment Rate × Job Seekers per Opening) ÷ (Quit Rate × Wage Growth)",
            "interpretation": {
                "Above 1.5": "Strong employer advantage - great time to hire strategically",
                "1.0-1.5": "Moderate employer advantage - balanced hiring approach",
                "0.8-1.0": "Balanced market - monitor trends closely", 
                "Below 0.8": "Employee advantage - focus on retention over hiring"
            },
            "source": "Calculated from FRED Economic Data"
        },
        
        "Talent Velocity Score": {
            "simple": "How fast people are changing jobs in the market",
            "detailed": "Measures the speed and volatility of job movements by combining quit rates and hiring rates. Higher velocity indicates a more dynamic, competitive market where talent moves frequently. Lower velocity suggests a stable market with less job hopping.",
            "formula": "3-month moving average of (Quit Rate + Hire Rate) ÷ 2, adjusted for momentum",
            "interpretation": {
                "Above 1.3": "High velocity - very competitive market, expect talent wars",
                "0.9-1.3": "Moderate velocity - normal job market activity",
                "Below 0.9": "Low velocity - stable market, less competition for talent"
            },
            "source": "Based on JOLTS (Job Openings and Labor Turnover Survey)"
        },
        
        "Talent Availability": {
            "simple": "How easy it is to find job candidates",
            "detailed": "The official unemployment rate, which measures the percentage of people actively looking for work. Higher unemployment generally means more candidates are available, making hiring easier. Lower unemployment means fewer available candidates.",
            "formula": "Number of unemployed people ÷ Total labor force × 100",
            "interpretation": {
                "Below 3.5%": "Very low unemployment - hiring will be challenging",
                "3.5-5.0%": "Normal unemployment - moderate candidate availability",
                "5.0-7.0%": "Elevated unemployment - good candidate pool",
                "Above 7.0%": "High unemployment - large candidate pool available"
            },
            "source": "U.S. Bureau of Labor Statistics (BLS) Current Population Survey"
        },
        
        "Retention Risk": {
            "simple": "How likely your employees are to quit",
            "detailed": "Assessment of voluntary turnover risk based on current quit rate trends, market conditions, and employee confidence indicators. Elevated risk means employees are more confident about finding new jobs and more likely to leave.",
            "formula": "Based on quit rate trends, talent velocity, and market conditions",
            "interpretation": {
                "LOW": "Quit rates below historical average - good time for workforce planning",
                "NORMAL": "Quit rates at expected levels - standard retention practices sufficient",
                "ELEVATED": "Quit rates above average - implement retention programs immediately"
            },
            "source": "JOLTS Survey data and trend analysis"
        },
        
        "Job Openings Index": {
            "simple": "How many job postings are available compared to baseline",
            "detailed": "Tracks the number of job openings relative to a baseline period (December 2019 = 100). Higher values indicate more job postings, suggesting strong hiring demand from employers.",
            "formula": "Current job openings ÷ Baseline job openings × 100",
            "interpretation": {
                "Above 120": "Very high job demand - competitive hiring market",
                "100-120": "Strong job demand - active hiring market",
                "80-100": "Moderate job demand - selective hiring",
                "Below 80": "Low job demand - limited hiring activity"
            },
            "source": "JOLTS Survey, seasonally adjusted"
        },
        
        "Quits Index": {
            "simple": "How many people are voluntarily leaving jobs compared to baseline",
            "detailed": "Tracks voluntary job separations (people quitting) relative to baseline. Higher values indicate employee confidence - people feel secure leaving jobs because they expect to find better ones.",
            "formula": "Current quit rate ÷ Baseline quit rate × 100",
            "interpretation": {
                "Above 110": "High quit activity - employees confident, retention risk elevated",
                "90-110": "Normal quit activity - typical job market churn",
                "80-90": "Below average quits - employees staying put",
                "Below 80": "Very low quits - job market anxiety or limited opportunities"
            },
            "source": "JOLTS Survey, voluntary separations only"
        },
        
        "Hires Index": {
            "simple": "How many people are getting hired compared to baseline",
            "detailed": "Tracks the rate of new hires relative to baseline. Higher values indicate active hiring by employers. When combined with other metrics, helps show whether hiring is driven by growth (good) or turnover (concerning).",
            "formula": "Current hire rate ÷ Baseline hire rate × 100",
            "interpretation": {
                "Above 110": "Very active hiring - growth or high turnover",
                "90-110": "Normal hiring activity - steady job market",
                "80-90": "Cautious hiring - employers being selective",
                "Below 80": "Limited hiring - economic uncertainty or cost management"
            },
            "source": "JOLTS Survey, all new hires"
        }
    }
    
    # Display metrics with search filtering
    for metric_name, details in metrics.items():
        if not search_term or search_term.lower() in metric_name.lower() or search_term.lower() in details["simple"].lower():
            with st.expander(f"**{metric_name}**", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Quick Definition:** {details['simple']}")
                    st.markdown(f"**Detailed Explanation:** {details['detailed']}")
                    
                    if 'formula' in details:
                        st.markdown(f"**How it's calculated:** `{details['formula']}`")
                    
                    st.markdown("**How to interpret the values:**")
                    for range_val, meaning in details['interpretation'].items():
                        st.markdown(f"• **{range_val}:** {meaning}")
                
                with col2:
                    st.markdown(f"**Data Source:** {details['source']}")
                    
                    # Add visual indicator for metric type
                    if "Index" in metric_name:
                        st.info("📊 **Index Metric**\nCompares current values to December 2019 baseline (100)")
                    elif "Rate" in metric_name or "Availability" in metric_name:
                        st.info("📈 **Rate Metric**\nShows percentage of total workforce")
                    else:
                        st.info("🎯 **Composite Metric**\nCombines multiple data sources")

with tab2:
    st.header("🏛️ Data Sources")
    
    sources = {
        "Federal Reserve Economic Data (FRED)": {
            "description": "The official database of U.S. economic time series data maintained by the Federal Reserve Bank of St. Louis",
            "authority": "Federal Reserve System - the central bank of the United States",
            "update_frequency": "Most series updated monthly, some weekly or quarterly",
            "reliability": "Highest - official government data with rigorous methodology",
            "website": "https://fred.stlouisfed.org",
            "what_we_use": [
                "Unemployment rates (UNRATE)",
                "Job openings (JTSJOL)", 
                "Hire rates (JTSHIL)",
                "Quit rates (JTSQUL)",
                "Consumer Price Index (CPIAUCSL)"
            ]
        },
        
        "Bureau of Labor Statistics (BLS)": {
            "description": "Primary federal agency responsible for measuring labor market activity, working conditions, and price changes",
            "authority": "U.S. Department of Labor - cabinet-level government agency",
            "update_frequency": "Monthly for most employment data, weekly for unemployment claims",
            "reliability": "Highest - gold standard for U.S. labor market data",
            "website": "https://www.bls.gov",
            "what_we_use": [
                "Current Population Survey (unemployment)",
                "Current Employment Statistics (payroll jobs)",
                "Job Openings and Labor Turnover Survey (JOLTS)"
            ]
        },
        
        "Job Openings and Labor Turnover Survey (JOLTS)": {
            "description": "Monthly survey of approximately 20,000 establishments measuring job openings, hires, and separations",
            "authority": "Bureau of Labor Statistics survey program",
            "update_frequency": "Monthly, released with about 6-week lag",
            "reliability": "High - large sample size, consistent methodology since 2000",
            "website": "https://www.bls.gov/jlt/",
            "what_we_use": [
                "Job openings by industry and region",
                "Voluntary quits (people leaving jobs)",
                "Total hires (new employees)",
                "Layoffs and discharges"
            ]
        }
    }
    
    for source_name, details in sources.items():
        if not search_term or search_term.lower() in source_name.lower():
            with st.expander(f"**{source_name}**", expanded=False):
                st.markdown(f"**What it is:** {details['description']}")
                st.markdown(f"**Authority:** {details['authority']}")
                st.markdown(f"**Update frequency:** {details['update_frequency']}")
                st.markdown(f"**Reliability:** {details['reliability']}")
                st.markdown(f"**Website:** {details['website']}")
                
                st.markdown("**What we use from this source:**")
                for item in details['what_we_use']:
                    st.markdown(f"• {item}")

with tab3:
    st.header("🧮 Calculations & Methodology")
    
    st.subheader("Index Calculations")
    st.markdown("""
    **Baseline Normalization (December 2019 = 100)**
    
    All our index metrics use December 2019 as the baseline month, set to 100. This date was chosen because:
    - It represents pre-pandemic "normal" labor market conditions
    - Unemployment was at historic lows (3.5%)  
    - Job market was stable and healthy
    - Provides a clear reference point for comparison
    
    **Formula:** `Current Value ÷ December 2019 Value × 100`
    
    **Example:** If job openings today are 1.2 times higher than December 2019, the index = 120
    """)
    
    st.subheader("Signal Generation")
    st.markdown("""
    **Market State Classification**
    
    Our system classifies the overall labor market into three states:
    
    1. **EMPLOYER'S MARKET** (Green 🟢)
       - Hiring Advantage Score > 1.2
       - High unemployment relative to job openings
       - Low quit rates
       - *Interpretation: Good time to hire, retention easier*
    
    2. **EMPLOYEE'S MARKET** (Red 🔴)  
       - Hiring Advantage Score < 0.8
       - Low unemployment, high job openings
       - High quit rates
       - *Interpretation: Hiring difficult, focus on retention*
    
    3. **TRANSITIONING MARKET** (Yellow 🟡)
       - Hiring Advantage Score 0.8 - 1.2
       - Mixed signals across metrics
       - *Interpretation: Balanced approach, monitor trends*
    """)
    
    st.subheader("Data Quality Controls")
    st.markdown("""
    **Seasonal Adjustments**
    - All data uses seasonally adjusted values when available
    - Removes predictable seasonal patterns (e.g., holiday hiring)
    - Provides clearer view of underlying trends
    
    **Outlier Detection**
    - Unusual values are flagged and investigated
    - Potential data errors are noted in calculations
    - Historical context provided for interpretation
    
    **Missing Data Handling**
    - Forward-fill used for gaps < 2 months
    - Longer gaps noted with warnings
    - Confidence intervals wider during incomplete periods
    """)

with tab4:
    st.header("💼 Market & Business Terms")
    
    business_terms = {
        "Labor Market Tightness": "How difficult it is for employers to find workers. A 'tight' market means low unemployment and high job openings - hard to hire. A 'loose' market means high unemployment - easier to hire.",
        
        "Headwinds vs Tailwinds": "Aviation metaphors for market conditions. Headwinds work against you (making hiring/retention harder), tailwinds help you (favorable conditions).",
        
        "Job Openings": "Positions that are available immediately and for which active recruitment is taking place. Excludes positions where someone has been selected but not yet started.",
        
        "Voluntary Separations (Quits)": "Employees who leave jobs on their own initiative, excluding retirements. High quit rates often signal employee confidence and job market strength.",
        
        "Labor Force Participation": "Percentage of working-age population either employed or actively looking for work. Can affect unemployment rate interpretation.",
        
        "Seasonal Adjustment": "Statistical technique to remove predictable seasonal patterns from data, revealing underlying trends. Example: removing expected December retail hiring spike.",
        
        "Year-over-Year (YoY)": "Comparison to the same month in the previous year. Helps control for seasonal effects and shows longer-term trends.",
        
        "Month-over-Month (MoM)": "Comparison to the previous month. Shows recent momentum but can be affected by seasonal patterns.",
        
        "Full Employment": "Economic condition where unemployment is at its 'natural' rate - typically 4-5% for the U.S. Includes people temporarily between jobs but excludes cyclical unemployment.",
        
        "Skills Gap": "Mismatch between skills employers need and skills job seekers have. Can create hiring difficulties even with higher unemployment.",
        
        "Talent Pipeline": "Flow of candidates from initial interest through hiring. Pipeline health affects how quickly positions can be filled.",
        
        "Employee Value Proposition (EVP)": "What you offer employees in exchange for their work - compensation, benefits, culture, growth opportunities. Affects retention risk."
    }
    
    for term, definition in business_terms.items():
        if not search_term or search_term.lower() in term.lower() or search_term.lower() in definition.lower():
            with st.expander(f"**{term}**", expanded=False):
                st.markdown(definition)

# Footer
st.markdown("---")
st.markdown("""
### 📞 Need More Information?

**For technical questions about calculations:**
- Check our methodology documentation in CLAUDE.md
- Review the source code in `src/signals/market_conditions.py`

**For data source questions:**
- Visit the official websites linked above
- FRED has extensive documentation for each data series
- BLS provides detailed methodology guides

**For business interpretation:**
- Use this glossary as a reference
- The Market Signals page provides contextual recommendations
- Executive Mode focuses on actionable insights

*Last updated: This glossary is maintained alongside dashboard updates*
""")