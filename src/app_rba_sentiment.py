"""
app_rba_sentiment.py
====================
Streamlit dashboard — Project 1: RBA Rate Decisions & Consumer Confidence

Chạy: streamlit run src/app_rba_sentiment.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from pathlib import Path

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RBA Rate Decisions & Consumer Confidence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F8F9FA; }
    .metric-card {
        background-color: #1E3A5F;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .metric-value { font-size: 36px; font-weight: bold; color: white; }
    .metric-label { font-size: 13px; color: #B0C4DE; margin-top: 5px; }
    .insight-box {
        background-color: #EEF2FF;
        border-left: 4px solid #1E3A5F;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 13px;
        color: #1E3A5F;
        font-style: italic;
    }
    h1 { color: #1E3A5F !important; }
    h2 { color: #1E3A5F !important; font-size: 18px !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Works both locally and on Streamlit Cloud
    # On Streamlit Cloud, files are relative to repo root
    base = Path(__file__).parent.parent

    rba  = pd.read_csv(base / "data" / "raw" / "rba_decisions.csv",  parse_dates=["date"])
    sent = pd.read_csv(base / "data" / "raw" / "sentiment_index.csv", parse_dates=["date"])
    trnd = pd.read_csv(base / "data" / "raw" / "google_trends.csv",   parse_dates=["date"])

    # Align to month start
    for df in [rba, sent, trnd]:
        df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

    # Master merge
    master = sent.merge(
        rba[["month", "new_rate", "rate_change", "decision"]],
        on="month", how="left"
    )
    master["new_rate"] = master["new_rate"].ffill()
    master["decision"] = master["decision"].fillna("hold")

    return master, rba, trnd

master, rba, trnd = load_data()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 🏦 RBA Rate Decisions & Australian Consumer Confidence")
st.markdown("*How monetary policy shapes consumer psychology — 2015 to 2026*")
st.divider()

# ── Slicer ───────────────────────────────────────────────────────────────────
col_s1, col_s2, _ = st.columns([1, 1, 3])
with col_s1:
    year_min = int(master["month"].dt.year.min())
    year_max = int(master["month"].dt.year.max())
    start_year = st.selectbox("From year", range(year_min, year_max + 1), index=0)
with col_s2:
    end_year = st.selectbox("To year", range(year_min, year_max + 1), index=year_max - year_min)

filtered = master[
    (master["month"].dt.year >= start_year) &
    (master["month"].dt.year <= end_year)
]

# ── KPI Cards ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{filtered['sentiment_score'].min():.1f}</div>
        <div class="metric-label">Lowest Confidence Score</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{int(filtered['pessimism_streak'].max())}</div>
        <div class="metric-label">Longest Pessimism Streak (months)</div>
    </div>""", unsafe_allow_html=True)

with c3:
    total_hikes = len(rba[
        (rba["decision"] == "hike") &
        (rba["date"].dt.year >= start_year) &
        (rba["date"].dt.year <= end_year)
    ])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_hikes}</div>
        <div class="metric-label">Total Rate Hikes</div>
    </div>""", unsafe_allow_html=True)

with c4:
    months_below = (filtered["sentiment_score"] < 100).sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{months_below}</div>
        <div class="metric-label">Months Below Neutral (100)</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Hero Chart ───────────────────────────────────────────────────────────────
st.markdown("## ANZ Consumer Confidence vs RBA Cash Rate")

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(
    x=filtered["month"], y=filtered["sentiment_score"],
    name="Consumer Confidence",
    line=dict(color="#1E3A5F", width=2.5),
    fill="tozeroy", fillcolor="rgba(30,58,95,0.08)"
), secondary_y=False)

fig.add_trace(go.Scatter(
    x=filtered["month"], y=filtered["new_rate"],
    name="RBA Cash Rate (%)",
    line=dict(color="#E74C3C", width=2, dash="dot")
), secondary_y=True)

# Hike markers
hikes = filtered[filtered["decision"] == "hike"]
fig.add_trace(go.Scatter(
    x=hikes["month"], y=hikes["sentiment_score"],
    mode="markers", name="Rate Hike",
    marker=dict(color="red", size=8, symbol="triangle-down")
), secondary_y=False)

# Cut markers
cuts = filtered[filtered["decision"] == "cut"]
fig.add_trace(go.Scatter(
    x=cuts["month"], y=cuts["sentiment_score"],
    mode="markers", name="Rate Cut",
    marker=dict(color="green", size=8, symbol="triangle-up")
), secondary_y=False)

# Reference line at 100
fig.add_hline(y=100, line_dash="dash", line_color="gray",
              opacity=0.6, annotation_text="Neutral (100)",
              annotation_position="left")

fig.update_layout(
    height=420,
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    plot_bgcolor="#EEF2FF",
    paper_bgcolor="#F8F9FA",
    xaxis=dict(showgrid=True, gridcolor="#D0D8E8"),
    yaxis=dict(title="Consumer Confidence Index",
               showgrid=True, gridcolor="#D0D8E8"),
    yaxis2=dict(title="Cash Rate (%)", overlaying="y", side="right"),
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="insight-box">
Index below 100 = pessimists outnumber optimists in Australia.
The 2022–2026 pessimism streak is the longest in the ANZ index's recorded history.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Google Trends Chart ──────────────────────────────────────────────────────
st.markdown("## Search Anxiety: How Australians React to Rate Hikes")

keywords = ["mortgage stress", "RBA interest rate"]
trnd_filtered = trnd[
    (trnd["keyword"].isin(keywords)) &
    (trnd["month"].dt.year >= start_year) &
    (trnd["month"].dt.year <= end_year)
]

fig2 = go.Figure()

colors = {"mortgage stress": "#E74C3C", "RBA interest rate": "#8E44AD"}

for kw in keywords:
    kw_data = trnd_filtered[trnd_filtered["keyword"] == kw]
    fig2.add_trace(go.Scatter(
        x=kw_data["month"],
        y=kw_data["search_volume"],
        name=f"'{kw}'",
        line=dict(color=colors[kw], width=2)
    ))

# Add hike lines
for _, h in rba[
    (rba["decision"] == "hike") &
    (rba["date"].dt.year >= start_year) &
    (rba["date"].dt.year <= end_year)
].iterrows():
    fig2.add_vline(
        x=h["month"], line_color="red",
        line_width=1, opacity=0.25
    )

fig2.update_layout(
    height=350,
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    plot_bgcolor="#EEF2FF",
    paper_bgcolor="#F8F9FA",
    xaxis=dict(title="", showgrid=True, gridcolor="#D0D8E8"),
    yaxis=dict(title="Search Volume (0–100, relative)",
               showgrid=True, gridcolor="#D0D8E8"),
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
<div class="insight-box">
Red vertical lines = RBA rate hike months. Search anxiety for 'RBA interest rate'
spiked immediately after the first hike in May 2022, while 'mortgage stress'
searches remained elevated long after rate cuts began — suggesting
psychological impact outlasts the monetary policy cycle.
</div>
""", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<small>
**Data sources:** ANZ-Roy Morgan Consumer Confidence Index |
RBA Cash Rate (rba.gov.au) | Google Trends (AU) via pytrends<br>
**Analysis:** Python (pandas, SQLite) | **Visualisation:** Streamlit + Plotly
</small>
""", unsafe_allow_html=True)
