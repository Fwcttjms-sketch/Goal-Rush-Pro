--- (Paste this entire block into GitHub's "app.py") ---

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="Goal Rush Pro", page_icon="⚽", layout="wide")
st.title("🚀 **GOAL RUSH PRO**")
st.markdown("---")
st.write("**xG + Goals Hybrid Model | Over 1.5, BTTS & Correct Score Predictions | Value Bets Only**")
st.markdown("---")

# === 1. GET TODAY'S FIXTURES (Simplified for Demo) ===
@st.cache_data(ttl=3600)  # Refresh hourly
def get_fixtures():
    # Demo fixtures (replace with real scraper if needed)
    fixtures = [
        ("Bradford City", "Lincoln City", "League One"),
        ("Genoa", "Cremonese", "Serie A"),
        ("Leeds United", "West Ham", "Premier League")
    ]
    return fixtures

# === 2. SIMULATED TEAM STATS (For Demo - Use Real FBref in Production) ===
@st.cache_data
def get_team_stats():
    # Mock data based on recent analyses
    stats = {
        'Bradford City': {'home_xg': 1.6, 'home_gf': 1.8, 'home_xga': 0.7, 'home_ga': 0.8},
        'Lincoln City': {'away_xg': 0.7, 'away_gf': 0.9, 'away_xga': 0.8, 'away_ga': 1.0},
        'Genoa': {'home_xg': 0.6, 'home_gf': 0.0, 'home_xga': 1.4, 'home_ga': 1.0},
        'Cremonese': {'away_xg': 1.1, 'away_gf': 1.0, 'away_xga': 1.0, 'away_ga': 1.0},
        'Leeds United': {'home_xg': 1.1, 'home_gf': 1.0, 'home_xga': 1.2, 'home_ga': 1.3},
        'West Ham': {'away_xg': 0.7, 'away_gf': 0.75, 'away_xga': 1.8, 'away_ga': 2.25}
    }
    league_avg_xg = 1.3  # Serie A/PL avg
    league_avg_gf = 1.15
    return stats, league_avg_xg, league_avg_gf

# === 3. PREDICTION ENGINE ===
def predict_match(home, away, stats, league_avg_xg, league_avg_gf, odds_over_1_5=1.33):
    # Home team lambdas
    home_xg = stats[home]['home_xg']
    home_gf = stats[home]['home_gf']
    away_xga = stats[away]['away_xga']
    away_ga = stats[away]['away_ga']
    
    lambda_home_xg = (home_xg / league_avg_xg) * away_xga * league_avg_xg
    lambda_home_gf = (home_gf / league_avg_gf) * away_ga * league_avg_gf
    lambda_home = 0.7 * lambda_home_xg + 0.3 * lambda_home_gf
    
    # Away team lambdas
    away_xg = stats[away]['away_xg']
    away_gf = stats[away]['away_gf']
    home_xga = stats[home]['home_xga']
    home_ga = stats[home]['home_ga']
    
    lambda_away_xg = (away_xg / league_avg_xg) * home_xga * league_avg_xg
    lambda_away_gf = (away_gf / league_avg_gf) * home_ga * league_avg_gf
    lambda_away = 0.7 * lambda_away_xg + 0.3 * lambda_away_gf
    
    total_lambda = lambda_home + lambda_away
    prob_over_1_5 = 1 - poisson.cdf(1, total_lambda)
    
    # BTTS & Scores
    p_btts = 0
    scores = {}
    for i in range(0, 6):  # Limit for speed
        for j in range(0, 6):
            prob = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)
            if i > 0 and j > 0:
                p_btts += prob
            score = f"{i}-{j}"
            if prob > 0.02:  # Top scores >2%
                scores[score] = prob
    top3 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    implied = 1 / odds_over_1_5
    ev = prob_over_1_5 * odds_over_1_5 - 1
    
    return {
        'lambda': round(total_lambda, 2),
        'over_1_5': round(prob_over_1_5, 3),
        'btts': round(p_btts, 3),
        'top3': [(s, round(p, 3)) for s, p in top3],
        'implied': round(implied, 3),
        'ev': round(ev, 3),
        'value': ev > 0
    }

# === 4. RUN APP ===
stats, avg_xg, avg_gf = get_team_stats()
fixtures = get_fixtures()

st.write("### 🔥 **Today's Hot Matches**")
if not fixtures:
    st.info("No matches today — check back soon!")
else:
    for home, away, league in fixtures:
        if home in stats and away in stats:  # Only if data available
            result = predict_match(home, away, stats, avg_xg, avg_gf)
            
            with st.expander(f"**{home} vs {away}** ({league})"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("λ (Total Goals)", result['lambda'])
                col2.metric("Over 1.5", f"{result['over_1_5']:.1%}")
                col3.metric("BTTS Yes", f"{result['btts']:.1%}")
                col4.metric("EV @1.33", f"{result['ev']:+.1%}", 
                           delta="🎯 VALUE!" if result['value'] else None)
                
                # Top Scores
                score_text = " | ".join([f"{s}: {p:.1%}" for s, p in result['top3']])
                st.caption(f"**Top Scores**: {score_text}")
                
                if result['value']:
                    st.success(f"**🚀 GOAL RUSH ALERT: Back Over 1.5 @1.33+**")
                else:
                    st.warning("No value here — skip.")
        else:
            st.caption(f"**{home} vs {away}**: Data loading...")

st.markdown("---")
st.caption("*Built with ❤️ by Goal Rush Pro | Data: FBref | Model: 70% xG + 30% Goals*")

--- (End of code block) ---
