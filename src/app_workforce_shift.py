"""
app_workforce_shift.py
======================
Streamlit dashboard — Project 2: Australian Workforce Shift 2025-2030

Chạy: streamlit run src/app_workforce_shift.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Australian Workforce Shift 2025–2030",
    page_icon="📊",
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
    base = os.path.expanduser("~/portfolio")
    db   = os.path.join(base, "data", "portfolio.db")

    if os.path.exists(db):
        conn   = sqlite3.connect(db)
        abs_df = pd.read_sql("SELECT * FROM abs_labour_force", conn, parse_dates=["date"])
        jsa    = pd.read_sql("SELECT * FROM jsa_projections",  conn)
        conn.close()
    else:
        abs_df = pd.read_csv(os.path.join(base, "data", "raw", "abs_labour_force.csv"), parse_dates=["date"])
        jsa    = pd.read_csv(os.path.join(base, "data", "raw", "jsa_projections.csv"))

    # Latest quarter
    latest   = abs_df["date"].max()
    prev_yr  = latest - pd.DateOffset(years=1)

    emp_now  = abs_df[abs_df["date"] == latest].set_index("industry")["employed_000s"]
    emp_prev = abs_df[abs_df["date"] == prev_yr].set_index("industry")["employed_000s"]

    growth = pd.DataFrame({
        "employed_000s":  emp_now,
        "yoy_growth_pct": ((emp_now / emp_prev) - 1) * 100,
        "yoy_change_000s": emp_now - emp_prev,
    }).reset_index()

    growth = growth[growth["industry"] != "Employed total ;"]

    # Join JSA
    jsa["industry_key"] = jsa["industry"].str.lower().str.strip()
    growth["industry_key"] = growth["industry"].str.lower().str.strip()

    bubble = growth.merge(
        jsa[["industry_key", "annual_growth_pct", "projected_new_jobs_000s"]],
        on="industry_key", how="left"
    ).dropna(subset=["annual_growth_pct"])

    # Quadrant
    med_growth = bubble["yoy_growth_pct"].median()
    med_proj   = bubble["annual_growth_pct"].median()

    def quadrant(row):
        g = row["yoy_growth_pct"] >= med_growth
        p = row["annual_growth_pct"] >= med_proj
        if g and p:     return "High Now + High Projected"
        if g and not p: return "High Now + Lower Projected"
        if not g and p: return "Lower Now + High Projected"
        return "Lower Now + Lower Projected"

    bubble["quadrant"] = bubble.apply(quadrant, axis=1)

    return abs_df, jsa, growth, bubble

abs_df, jsa, growth, bubble = load_data()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 📊 Australian Workforce Shift 2025–2030")
st.markdown("*Which industries are genuinely growing — and where are the data skills gaps?*")
st.divider()

# ── KPI Cards ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

fastest = growth.nlargest(1, "yoy_growth_pct")["industry"].values[0]
fastest_short = fastest.replace("Professional, Scientific and Technical Services", "Prof & Tech") \
                        .replace("Health Care and Social Assistance", "Healthcare") \
                        .replace("Electricity, Gas, Water and Waste Services", "Utilities")

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="font-size:22px;">{fastest_short}</div>
        <div class="metric-label">Fastest Growing Industry (YoY)</div>
    </div>""", unsafe_allow_html=True)

with c2:
    total_proj = jsa["projected_new_jobs_000s"].sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_proj:.0f}K</div>
        <div class="metric-label">Projected New Jobs by 2030 (000s)</div>
    </div>""", unsafe_allow_html=True)

with c3:
    growing = (growth["yoy_growth_pct"] > 0).sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{growing}</div>
        <div class="metric-label">Industries Growing Now</div>
    </div>""", unsafe_allow_html=True)

with c4:
    high_high = (bubble["quadrant"] == "High Now + High Projected").sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{high_high}</div>
        <div class="metric-label">Industries: High Now + High Projected</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Bubble Chart ─────────────────────────────────────────────────────────────
st.markdown("## Actual vs Projected Industry Growth")

color_map = {
    "High Now + High Projected":   "#27AE60",
    "High Now + Lower Projected":  "#F39C12",
    "Lower Now + High Projected":  "#2980B9",
    "Lower Now + Lower Projected": "#E74C3C",
}

# Short labels
bubble["label"] = bubble["industry"].str.replace(
    "Professional, Scientific and Technical Services", "Prof & Tech"
).str.replace("Health Care and Social Assistance", "Healthcare") \
 .str.replace("Electricity, Gas, Water and Waste Services", "Utilities") \
 .str.replace("Information Media and Telecommunications", "Info & Telecom") \
 .str.replace("Public Administration and Safety", "Public Admin") \
 .str.replace("Financial and Insurance Services", "Finance") \
 .str.replace("Administrative and Support Services", "Admin Services") \
 .str.replace("Accommodation and Food Services", "Hospitality") \
 .str.replace("Transport, Postal and Warehousing", "Transport") \
 .str.replace("Rental, Hiring and Real Estate Services", "Real Estate") \
 .str.replace("Agriculture, Forestry and Fishing", "Agriculture") \
 .str.replace("Arts and Recreation Services", "Arts & Rec") \
 .str.replace("Education and Training", "Education") \
 .str.replace("Retail Trade", "Retail") \
 .str.replace("Wholesale Trade", "Wholesale") \
 .str.replace("Other Services", "Other") \
 .str.replace("Construction", "Construction") \
 .str.replace("Manufacturing", "Manufacturing") \
 .str.replace("Mining", "Mining")

fig = px.scatter(
    bubble,
    x="yoy_growth_pct",
    y="annual_growth_pct",
    size="employed_000s",
    color="quadrant",
    text="label",
    hover_name="industry",
    hover_data={
        "yoy_growth_pct": ":.2f",
        "annual_growth_pct": ":.2f",
        "employed_000s": ":,.0f",
        "label": False,
        "quadrant": False,
    },
    color_discrete_map=color_map,
    labels={
        "yoy_growth_pct":    "Actual YoY Growth % (ABS)",
        "annual_growth_pct": "Projected Annual Growth % (JSA 2025–2030)",
        "employed_000s":     "Employed (000s)",
    },
)

fig.update_traces(
    textposition="top center",
    textfont=dict(size=10),
    marker=dict(opacity=0.85)
)

# Quadrant lines
fig.add_vline(x=bubble["yoy_growth_pct"].median(),
              line_dash="dash", line_color="gray", opacity=0.5)
fig.add_hline(y=bubble["annual_growth_pct"].median(),
              line_dash="dash", line_color="gray", opacity=0.5)

fig.update_layout(
    height=520,
    plot_bgcolor="#EEF2FF",
    paper_bgcolor="#F8F9FA",
    xaxis=dict(showgrid=True, gridcolor="#D0D8E8", zeroline=True, zerolinecolor="#888"),
    yaxis=dict(showgrid=True, gridcolor="#D0D8E8"),
    legend=dict(orientation="h", yanchor="bottom", y=-0.2),
    margin=dict(l=0, r=0, t=10, b=0)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="insight-box">
Top-right quadrant = growing now AND projected to keep growing to 2030.
Notable: Professional & Technical Services is growing at 12.36% YoY —
6× faster than JSA's projection of 1.94%, suggesting government forecasts
are significantly underestimating tech sector demand.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Bar Charts ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("## Actual Employment Growth by Industry")
    growth_sorted = growth.sort_values("yoy_growth_pct", ascending=True)
    growth_sorted = growth_sorted[growth_sorted["industry"] != "Employed total ;"]

    fig2 = go.Figure(go.Bar(
        x=growth_sorted["yoy_growth_pct"],
        y=growth_sorted["industry"],
        orientation="h",
        marker_color=[
            "#27AE60" if v >= 0 else "#E74C3C"
            for v in growth_sorted["yoy_growth_pct"]
        ],
        text=growth_sorted["yoy_growth_pct"].round(1).astype(str) + "%",
        textposition="outside"
    ))

    fig2.update_layout(
        height=500,
        plot_bgcolor="#EEF2FF",
        paper_bgcolor="#F8F9FA",
        xaxis=dict(title="YoY Growth (%)", showgrid=True, gridcolor="#D0D8E8"),
        yaxis=dict(title=""),
        margin=dict(l=0, r=40, t=10, b=0)
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("## Projected New Jobs by Industry (2025–2030)")
    jsa_sorted = jsa.sort_values("projected_new_jobs_000s", ascending=True)

    fig3 = go.Figure(go.Bar(
        x=jsa_sorted["projected_new_jobs_000s"],
        y=jsa_sorted["industry"],
        orientation="h",
        marker_color="#1E3A5F",
        text=jsa_sorted["projected_new_jobs_000s"].round(0).astype(int).astype(str) + "K",
        textposition="outside"
    ))

    fig3.update_layout(
        height=500,
        plot_bgcolor="#EEF2FF",
        paper_bgcolor="#F8F9FA",
        xaxis=dict(title="New Jobs by 2030 (000s)", showgrid=True, gridcolor="#D0D8E8"),
        yaxis=dict(title=""),
        margin=dict(l=0, r=60, t=10, b=0)
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<small>
**Data sources:** ABS Labour Force Survey Cat. 6291 (abs.gov.au) |
Jobs and Skills Australia Employment Projections May 2025–2035 (jobsandskills.gov.au)<br>
**Analysis:** Python (pandas, SQLite) | **Visualisation:** Streamlit + Plotly
</small>
""", unsafe_allow_html=True)
