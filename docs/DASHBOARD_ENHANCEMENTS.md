# Labor Market Dashboard Enhancement Plan

## Executive Summary
Transform the current dashboard into a strategic talent intelligence platform that provides clear signals on market conditions (headwinds vs tailwinds) and enables benchmarking of internal metrics against market conditions.

## 1. Market Signal Interpretation Layer

### Headwind/Tailwind Indicators
Create composite scores that immediately show whether conditions favor employers or employees:

#### **Employer Power Index (EPI)**
- Formula: `(Unemployment Rate × Job Seekers per Opening) / (Quits Rate × Wage Growth)`
- Interpretation:
  - EPI > 1.5 = Strong employer market (headwind for talent acquisition)
  - EPI 0.8-1.5 = Balanced market
  - EPI < 0.8 = Employee market (tailwind for retention challenges)

#### **Talent Velocity Score**
- Combines: Quits rate, hiring rate, time-to-fill proxies
- Shows how fast talent is moving in the market
- Higher score = more competitive/volatile market

### Visual Signal System
```
Market Conditions Dashboard:
┌─────────────────────────────────────┐
│ 🟢 TAILWIND: Hiring Market          │
│ Score: +2.3 (Strong)                │
│ • High talent availability          │
│ • Decreasing wage pressure          │
│ • Lower quit risk                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🔴 HEADWIND: Retention Risk         │
│ Score: -1.8 (Moderate)              │
│ • Quits rate up 15% YoY            │
│ • Competitor hiring surge           │
│ • Wage growth accelerating          │
└─────────────────────────────────────┘
```

## 2. Talent Segment Framework

### Segmentation Dimensions
1. **Role Families** (using enhanced skills taxonomy)
   - Tech/Engineering
   - Sales/Marketing
   - Operations
   - Leadership/Executive
   - Support/Admin

2. **Seniority Levels**
   - Entry (0-2 years)
   - Mid (2-5 years)
   - Senior (5-10 years)
   - Leadership (10+ years)

3. **Geographic Markets**
   - Metro areas (MSA-level data)
   - States
   - Regions (Northeast, Southeast, etc.)

### Segment-Specific Metrics
```python
segment_metrics = {
    "tech_senior_sf": {
        "market_tightness": 0.3,  # Very tight
        "quit_probability": 0.18,  # High
        "wage_premium": 1.45,     # 45% above baseline
        "time_to_fill": 67,        # days
        "offer_decline_rate": 0.35
    }
}
```

## 3. Employee Lifecycle Benchmarking

### Lifecycle Stages & Market Metrics

#### **Attraction Stage**
- Market Metric: Job postings volume, application rates
- Benchmark: Your job views vs market posting volume
- Signal: Is it getting easier or harder to attract talent?

#### **Recruitment Stage**
- Market Metric: Time-to-fill, offer acceptance rates
- Benchmark: Your time-to-fill vs market velocity
- Signal: Are you competitive in closing candidates?

#### **Onboarding Stage**
- Market Metric: New hire quits (90-day rate)
- Benchmark: Your early turnover vs market
- Signal: Is job hopping increasing?

#### **Development Stage**
- Market Metric: Skills demand changes, training investments
- Benchmark: Your L&D spend vs market
- Signal: Are you keeping pace with skill evolution?

#### **Retention Stage**
- Market Metric: Quit rates, wage growth
- Benchmark: Your retention vs market quits
- Signal: Are you at risk of increased turnover?

#### **Separation Stage**
- Market Metric: Layoff rates, voluntary vs involuntary
- Benchmark: Your separation patterns vs market
- Signal: Are your exits typical for market conditions?

## 4. Enhanced Dashboard Components

### A. Executive Summary View
```
┌──────────────────────────────────────────────┐
│            TALENT MARKET MONITOR             │
├──────────────────────────────────────────────┤
│                                              │
│  Overall Market: 🟡 TRANSITIONING           │
│                                              │
│  Hiring Outlook:    ↗️ Improving (Score: +1.2)│
│  Retention Risk:    ↘️ Declining (Score: -0.8)│
│  Wage Pressure:     → Stable (2.3% annual)  │
│  Talent Velocity:   ↗️ Accelerating         │
│                                              │
│  [!] ALERTS:                                │
│  • Tech quit rate spike in West region      │
│  • Entry-level oversupply in Finance        │
│                                              │
└──────────────────────────────────────────────┘
```

### B. Segment Comparison Matrix
Interactive heatmap showing conditions across:
- Rows: Role families / segments
- Columns: Lifecycle metrics
- Colors: Red (headwind) → Yellow (neutral) → Green (tailwind)

### C. Predictive Indicators
- **Leading Indicators**: Job postings, wage momentum
- **Current Indicators**: Quit rates, unemployment
- **Lagging Indicators**: Hiring rates, separation patterns

### D. Scenario Planning Tool
```python
scenarios = {
    "recession_mild": {
        "unemployment": "+2.5%",
        "quits": "-40%",
        "wages": "-1.5%",
        "impact": "Strong hiring market, retention easier"
    },
    "tech_boom_2": {
        "unemployment": "-1.5%",
        "quits": "+35%",
        "wages": "+6.5%",
        "impact": "Extreme competition for tech talent"
    }
}
```

## 5. Implementation Roadmap

### Phase 1: Signal Framework (Week 1)
- [ ] Implement EPI and Talent Velocity calculations
- [ ] Create headwind/tailwind classification logic
- [ ] Add visual signal indicators to dashboard

### Phase 2: Segmentation (Week 2)
- [ ] Add role family classification using skills taxonomy
- [ ] Implement geographic filtering (start with state-level)
- [ ] Create segment comparison views

### Phase 3: Lifecycle Metrics (Week 3)
- [ ] Map FRED metrics to lifecycle stages
- [ ] Build benchmark comparison framework
- [ ] Add internal metric upload capability

### Phase 4: Advanced Analytics (Week 4)
- [ ] Implement predictive indicators
- [ ] Add scenario planning tool
- [ ] Create alert system for significant changes

## 6. Data Requirements

### Additional FRED Series Needed
```python
ADDITIONAL_SERIES = [
    # Regional data
    "UNRATE_{state}",  # State unemployment rates
    "JTSQUL_{region}",  # Regional quit rates
    
    # Industry specific
    "USINFO",  # Information sector employment
    "MANEMP",  # Manufacturing employment
    
    # Leading indicators
    "ICSA",    # Initial jobless claims
    "CCSA",    # Continued claims
    
    # Wage data
    "AHETPI",  # Hourly earnings
    "ECIWAG",  # Employment cost index
]
```

### External Data Sources to Add
1. **BLS JOLTS**: More granular job openings data
2. **ADP Employment**: Real-time employment trends
3. **LinkedIn Workforce Report**: Skill migration patterns
4. **Indeed/Glassdoor**: Job posting trends, salary data

## 7. User Stories

### As a CHRO, I want to:
- See at a glance whether market conditions favor hiring or retention
- Benchmark our turnover against market quit rates by segment
- Predict talent risks 3-6 months out

### As a Talent Acquisition Leader, I want to:
- Know which segments are easiest/hardest to hire
- Track if our time-to-fill is competitive
- See wage pressure by role and location

### As a Compensation Manager, I want to:
- Monitor wage inflation by segment
- See when market rates are shifting
- Benchmark our pay against market movement

### As a Workforce Planner, I want to:
- Identify future skill gaps
- Plan for market-driven turnover
- Optimize location strategy based on talent availability

## 8. Success Metrics

### Dashboard Effectiveness
- Time to insight: < 30 seconds to understand market state
- Actionability: 80% of alerts lead to strategic decisions
- Accuracy: Signals correctly predict trends 75% of time

### Business Impact
- Reduce time-to-fill by 15% through better market timing
- Improve retention by 10% through proactive interventions
- Optimize compensation spend by 5-8% through market intelligence

## 9. Technical Implementation Notes

### New Modules Structure
```
src/
  signals/
    market_conditions.py  # Calculate headwind/tailwind scores
    talent_velocity.py    # Compute movement metrics
  segments/
    classifier.py         # Categorize into segments
    benchmarks.py        # Segment-specific calculations
  lifecycle/
    stages.py            # Map metrics to lifecycle
    comparisons.py       # Internal vs external benchmarking
```

### Dashboard Pages Structure
```
app/
  pages/
    1_Executive_Summary.py
    2_Market_Signals.py
    3_Segment_Analysis.py
    4_Lifecycle_Benchmarks.py
    5_Predictive_Insights.py
    6_Scenario_Planning.py
```

## 10. Next Steps

1. **Immediate** (This Week):
   - Implement basic signal calculations
   - Add market condition indicators to current dashboard
   - Create segment filtering capability

2. **Short-term** (Next 2 Weeks):
   - Add geographic granularity
   - Build lifecycle mapping
   - Enable CSV upload for internal metrics

3. **Medium-term** (Next Month):
   - Integrate additional data sources
   - Build predictive models
   - Add scenario planning tools

This enhancement plan transforms your dashboard from a data viewer into a strategic decision support system for talent management.