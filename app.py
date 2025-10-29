import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Goal Rush Pro", page_icon="⚽")
st.title("GOAL RUSH PRO")
st.write("xG + Goals Model | Over 1.5, BTTS & Correct Score Predictions")

# Mock data with home/away split (fixed keys)
stats = {
    'Bradford City': {'home_xg': 1.6, 'home_gf': 1.8, 'home_xga': 0.7, 'away_xga': 1.0},
    'Lincoln City': {'away_xg': 0.7, 'away_gf': 0.9, 'home_xga': 0.8, 'away_xga': 1.0},
    'Genoa': {'home_xg': 0.6, 'home_gf': 0.0, 'home_xga': 1.4, 'away_xga': 1.0},
    'Cremonese': {'away_xg': 1.1, 'away_gf': 1.0, 'home_xga': 1.0, 'away_xga': 1.0},
    'Leeds United': {'home_xg': 1.1, 'home_gf': 1.0, 'home_xga': 1.2, 'away_xga': 1.5},
    'West Ham': {'away_xg': 0.7, 'away_gf': 0.75, 'home_xga': 1.8, 'away_xga': 2.0}
}
league_avg_xg = 1.3
league_avg_gf = 1.15

def predict_match(home, away, odds=1.33):
    home_xg = stats[home]['home_xg']
    home_gf = stats[home]['home_gf']
    away_xga = stats[away]['away_xga']
    away_ga = stats[away]['away_xga']  # Using xga as proxy for ga
    
    lambda_home_xg = (home_xg / league_avg_xg) * away_xga * league_avg_xg
    lambda_home_gf = (home_gf / league_avg_gf) * away_ga * league_avg_gf
    lambda_home = 0.7 * lambda_home_xg + 0.3 * lambda_home_gf
    
    away_xg = stats[away]['away_xg']
    away_gf = stats[away]['away_gf']
    home_xga = stats[home]['home_xga']
    home_ga = stats[home]['home_xga']  # Proxy
    
    lambda_away_xg = (away_xg / league_avg_xg) * home_xga * league_avg_xg
    lambda_away_gf = (away_gf / league_avg_gf) * home_ga * league_avg_gf
    lambda_away = 0.7 * lambda_away_xg + 0.3 * lambda_away_gf
    
    total_lambda = lambda_home + lambda_away
    prob_over_1_5 = 1 - poisson.cdf(1, total_lambda)
    
    # BTTS
    p_btts = 0
    for i in range(1, 5):
        for j in range(1, 5):
            p_btts += poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)
    
    # Top 3 Scores
    scores = {}
    for i in range(0, 5):
        for j in range(0, 5):
            prob = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)
            if prob > 0.02:
                scores[f"{i}-{j}"] = prob
    top3 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    implied = 1 / odds
    ev = prob_over_1_5 * odds - 1
    
    return {
        'lambda': round(total_lambda, 2),
        'over_1_5': round(prob_over_1_5, 3),
        'btts': round(p_btts, 3),
        'top3': [(s, round(p, 3)) for s, p in top3],
        'ev': round(ev, 3),
        'value': ev > 0
    }

# Demo Matches
st.write("### Today's Matches (Demo Data)")
matches = [
    ("Bradford City", "Lincoln City", "League One"),
    ("Genoa", "Cremonese", "Serie A"),
    ("Leeds United", "West Ham", "Premier League")
]

for home, away, league in matches:
    result = predict_match(home, away)
    
    with st.expander(f"{home} vs {away} ({league})"):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total λ", result['lambda'])
        col2.metric("Over 1.5", f"{result['over_1_5']:.1%}")
        col3.metric("BTTS", f"{result['btts']:.1%}")
        col4.metric("EV @1.33", f"{result['ev']:+.1%}", delta="VALUE!" if result['value'] else None)
        
        score_text = " | ".join([f"{s}: {p:.1%}" for s, p in result['top3']])
        st.caption(f"Top Scores: {score_text}")
        
        if result['value']:
            st.success("BET THIS OVER 1.5!")
        else:
            st.info("No value — pass.")

st.write("---")
st.caption("Built with Goal Rush Pro | Data: Mock (Add FBref scraper next)")
