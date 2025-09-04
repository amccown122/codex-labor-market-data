"""
Market condition signals - identify headwinds vs tailwinds for talent management.
"""
from __future__ import annotations

from typing import Dict, Tuple, Optional
import pandas as pd
import numpy as np


class MarketSignals:
    """Calculate market condition signals for talent management decisions."""
    
    def __init__(self, metrics_df: pd.DataFrame):
        """
        Initialize with market metrics dataframe.
        Expected columns: date, unemp_rate, job_openings_index, 
                         quits_index, hires_index, cpi_index
        """
        self.df = metrics_df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.sort_values('date')
        
    def calculate_employer_power_index(self) -> pd.Series:
        """
        Calculate Employer Power Index (EPI).
        Higher values = employer's market (easier hiring, retention)
        Lower values = employee's market (harder hiring, retention challenges)
        
        Formula: (Unemployment Rate × Job Seekers per Opening) / (Quits Rate × Wage Growth Proxy)
        """
        # Estimate job seekers per opening (inverse of tightness)
        if 'job_openings_index' in self.df.columns:
            seekers_per_opening = self.df['unemp_rate'] / (self.df['job_openings_index'] / 100)
        else:
            seekers_per_opening = self.df['unemp_rate']  # Fallback
            
        # Use quits as proxy for employee confidence
        quits_factor = self.df.get('quits_index', 100) / 100
        
        # Use CPI change as wage growth proxy (imperfect but available)
        wage_growth_proxy = self.df['cpi_index'].pct_change(12).fillna(0.02) + 1  # YoY change
        
        # Calculate EPI
        numerator = self.df['unemp_rate'] * seekers_per_opening
        denominator = quits_factor * wage_growth_proxy
        denominator = denominator.replace(0, 1)  # Avoid division by zero
        
        epi = numerator / denominator
        
        # Normalize to intuitive scale (0-2, where 1 = balanced)
        epi = epi / epi.median()
        
        return epi
    
    def calculate_talent_velocity(self) -> pd.Series:
        """
        Calculate how fast talent is moving in the market.
        Higher values = more volatile/competitive market
        """
        # Combine quits and hires rates
        quits = self.df.get('quits_index', 100) / 100
        hires = self.df.get('hires_index', 100) / 100
        
        # 3-month moving average of combined movement
        movement = (quits + hires) / 2
        velocity = movement.rolling(window=3, min_periods=1).mean()
        
        # Add momentum component (rate of change)
        momentum = movement.pct_change(3).fillna(0)
        
        # Combined score
        talent_velocity = velocity * (1 + momentum.clip(-0.5, 0.5))
        
        return talent_velocity
    
    def classify_market_state(self, epi: float, velocity: float) -> Dict[str, any]:
        """
        Classify current market state based on EPI and velocity.
        
        Returns dict with:
        - state: Overall market classification
        - hiring_outlook: Conditions for hiring
        - retention_risk: Risk level for retention
        - recommendations: Strategic recommendations
        """
        # EPI Classification
        if epi > 1.5:
            hiring_state = "FAVORABLE"
            hiring_score = min((epi - 1) * 2, 3)  # Scale 0-3
        elif epi > 0.8:
            hiring_state = "BALANCED"
            hiring_score = 0
        else:
            hiring_state = "CHALLENGING"
            hiring_score = max((epi - 1) * 2, -3)  # Scale -3 to 0
            
        # Velocity Classification  
        if velocity > 1.3:
            volatility = "HIGH"
            retention_risk = "ELEVATED"
        elif velocity > 0.9:
            volatility = "MODERATE"
            retention_risk = "NORMAL"
        else:
            volatility = "LOW"
            retention_risk = "LOW"
            
        # Combined state
        if hiring_state == "FAVORABLE" and volatility == "LOW":
            overall = "EMPLOYER'S MARKET"
            color = "green"
        elif hiring_state == "CHALLENGING" and volatility == "HIGH":
            overall = "EMPLOYEE'S MARKET"
            color = "red"
        else:
            overall = "TRANSITIONING"
            color = "yellow"
            
        # Strategic recommendations
        recommendations = []
        
        if hiring_state == "FAVORABLE":
            recommendations.append("🎯 Accelerate strategic hiring - conditions favorable")
            recommendations.append("📊 Upgrade talent while availability is high")
        elif hiring_state == "CHALLENGING":
            recommendations.append("⚠️ Focus on retention - hiring will be difficult")
            recommendations.append("💰 Review compensation competitiveness")
            
        if retention_risk == "ELEVATED":
            recommendations.append("🔒 Implement retention programs for key talent")
            recommendations.append("📈 Monitor quit rates weekly, not monthly")
        elif retention_risk == "LOW":
            recommendations.append("✅ Opportunity to optimize workforce costs")
            recommendations.append("🔄 Good time for organizational changes")
            
        return {
            "state": overall,
            "color": color,
            "hiring_outlook": hiring_state,
            "hiring_score": round(hiring_score, 1),
            "retention_risk": retention_risk,
            "volatility": volatility,
            "epi": round(epi, 2),
            "velocity": round(velocity, 2),
            "recommendations": recommendations
        }
    
    def get_trend_signals(self, lookback_months: int = 6) -> Dict[str, str]:
        """
        Identify trends that signal upcoming changes.
        """
        if len(self.df) < lookback_months:
            return {"status": "Insufficient data for trends"}
            
        recent = self.df.tail(lookback_months)
        
        signals = []
        
        # Unemployment trend
        unemp_change = recent['unemp_rate'].iloc[-1] - recent['unemp_rate'].iloc[0]
        if abs(unemp_change) > 0.5:
            direction = "rising" if unemp_change > 0 else "falling"
            signals.append(f"Unemployment {direction} ({unemp_change:+.1f}pp)")
            
        # Quits momentum
        if 'quits_index' in recent.columns:
            quits_change = recent['quits_index'].pct_change(3).iloc[-1]
            if abs(quits_change) > 0.1:
                direction = "accelerating" if quits_change > 0 else "decelerating"
                signals.append(f"Quit rate {direction} ({quits_change:+.0%})")
                
        # Opening-to-unemployment ratio
        if 'job_openings_index' in recent.columns:
            ratio_start = recent['job_openings_index'].iloc[0] / recent['unemp_rate'].iloc[0]
            ratio_end = recent['job_openings_index'].iloc[-1] / recent['unemp_rate'].iloc[-1]
            ratio_change = (ratio_end / ratio_start - 1)
            if abs(ratio_change) > 0.15:
                direction = "tightening" if ratio_change > 0 else "loosening"
                signals.append(f"Labor market {direction} ({ratio_change:+.0%})")
                
        return {
            "signals": signals,
            "summary": " | ".join(signals) if signals else "Market conditions stable"
        }
    
    def calculate_all_signals(self) -> pd.DataFrame:
        """
        Calculate all signals and add to dataframe.
        """
        result = self.df.copy()
        
        # Calculate core signals
        result['employer_power_index'] = self.calculate_employer_power_index()
        result['talent_velocity'] = self.calculate_talent_velocity()
        
        # Classify market state for each row
        for idx, row in result.iterrows():
            if pd.notna(row['employer_power_index']) and pd.notna(row['talent_velocity']):
                state = self.classify_market_state(
                    row['employer_power_index'], 
                    row['talent_velocity']
                )
                result.at[idx, 'market_state'] = state['state']
                result.at[idx, 'hiring_outlook'] = state['hiring_outlook']
                result.at[idx, 'retention_risk'] = state['retention_risk']
                
        return result


def generate_market_summary(signals_df: pd.DataFrame) -> Dict[str, any]:
    """
    Generate executive summary of current market conditions.
    """
    if signals_df.empty:
        return {"error": "No data available"}
        
    latest = signals_df.iloc[-1]
    prev_month = signals_df.iloc[-2] if len(signals_df) > 1 else latest
    prev_year = signals_df.iloc[-12] if len(signals_df) > 12 else signals_df.iloc[0]
    
    # Calculate changes
    epi_mom = (latest['employer_power_index'] / prev_month['employer_power_index'] - 1) * 100
    epi_yoy = (latest['employer_power_index'] / prev_year['employer_power_index'] - 1) * 100
    
    velocity_mom = (latest['talent_velocity'] / prev_month['talent_velocity'] - 1) * 100
    velocity_yoy = (latest['talent_velocity'] / prev_year['talent_velocity'] - 1) * 100
    
    summary = {
        "date": latest['date'].strftime("%B %Y"),
        "market_state": latest.get('market_state', 'UNKNOWN'),
        "hiring_outlook": latest.get('hiring_outlook', 'UNKNOWN'),
        "retention_risk": latest.get('retention_risk', 'UNKNOWN'),
        "metrics": {
            "employer_power_index": {
                "value": round(latest['employer_power_index'], 2),
                "mom_change": f"{epi_mom:+.1f}%",
                "yoy_change": f"{epi_yoy:+.1f}%",
                "interpretation": "Employer advantage" if latest['employer_power_index'] > 1 else "Employee advantage"
            },
            "talent_velocity": {
                "value": round(latest['talent_velocity'], 2),
                "mom_change": f"{velocity_mom:+.1f}%",
                "yoy_change": f"{velocity_yoy:+.1f}%",
                "interpretation": "High movement" if latest['talent_velocity'] > 1.2 else "Stable market"
            },
            "unemployment_rate": {
                "value": f"{latest['unemp_rate']:.1f}%",
                "mom_change": f"{latest['unemp_rate'] - prev_month['unemp_rate']:+.1f}pp",
                "yoy_change": f"{latest['unemp_rate'] - prev_year['unemp_rate']:+.1f}pp"
            }
        }
    }
    
    return summary