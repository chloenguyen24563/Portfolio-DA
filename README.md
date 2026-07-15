# 📊 Australian Economic & Workforce Analytics Portfolio

**Data Analyst Portfolio | Python · SQL · Power BI · Streamlit**

Two data projects analysing the Australian economy from different angles —
consumer psychology under monetary policy pressure, and structural shifts
in the labour market through to 2030.

---

## 🏦 Project 1: RBA Rate Decisions & Consumer Confidence

> *When the RBA raises rates, how quickly do Australians feel it —
> and does the sentiment index tell the full story?*

### 🔴 Live Dashboard
**[View Dashboard →](https://portfolio-da-dt2mx6btl5a4kuybykikvc.streamlit.app/)**

### Key Findings

| Finding | Detail |
|---|---|
| **Longest pessimism streak on record** | 52 consecutive months below neutral (100) — started March 2022, still ongoing as of June 2026 |
| **Lowest confidence in ANZ history** | 63.6 recorded April 2026 — below the COVID crash low |
| **Search anxiety outlasts monetary policy** | Google searches for 'mortgage stress' remained elevated months after rate cuts began — behavioural anxiety persists longer than the headline index suggests |
| **16 rate hikes** | RBA delivered 16 consecutive hikes across 2022–2026 — the most aggressive tightening cycle in modern Australian history |

### Data Sources
- **ANZ-Roy Morgan Consumer Confidence Index** — monthly, 2015–2026
- **RBA Cash Rate decisions** — rba.gov.au (verified historical record)
- **Google Trends AU** — keywords: 'mortgage stress', 'RBA interest rate'

### Tech Stack
```
Python (pandas, SQLite)  →  data processing & SQL analysis
Plotly + Streamlit       →  interactive dashboard
Power BI                 →  stakeholder dashboard
GitHub                   →  version control
```

### SQL Analysis Highlights
- Event study: sentiment change 1/3/6 months after each rate hike
- Lag analysis: Google Trends spike timing relative to RBA decisions
- Pessimism streak detection using window functions
- Cross-dataset join: RBA decisions × sentiment × search behaviour

---

## 📈 Project 2: Australian Workforce Shift 2025–2030

> *Which industries are genuinely growing — and where are the
> data skills gaps that government forecasts are missing?*

### 🔴 Live Dashboard
**[View Dashboard →](https://portfolio-da-gyaaptrni7jameapcexlfp.streamlit.app/)**

### Key Findings

| Finding | Detail |
|---|---|
| **Government forecasts underestimate tech demand** | Professional & Technical Services growing at **12.36% YoY** — 6× faster than JSA's projection of 1.94%/yr |
| **Healthcare dominates job creation** | 290,000 new jobs projected by 2030 — largest of any industry |
| **Utilities surprise** | Electricity, Gas & Water growing at 13.33% YoY — fastest actual growth, not reflected in projections |
| **3 industries in "High Now + High Projected" quadrant** | Healthcare, Education, Prof & Tech — safest sectors for long-term employment |

### Data Sources
- **ABS Labour Force Survey** Cat. 6291, Table 04 — employed persons by industry division, quarterly (abs.gov.au)
- **Jobs and Skills Australia** — Employment Projections May 2025 to May 2035 (jobsandskills.gov.au)

### Tech Stack
```
Python (pandas, SQLite)  →  data processing & SQL analysis
Plotly + Streamlit       →  interactive bubble chart dashboard
Power BI                 →  stakeholder dashboard
GitHub                   →  version control
```

### SQL Analysis Highlights
- Industry growth ranking with YoY % calculation
- Projected vs actual growth gap analysis
- Quadrant classification: High/Low growth × High/Low projected
- Occupation-level data role intensity analysis

---

## 📁 Repository Structure

```
Portfolio-DA/
├── data/
│   └── raw/                    # Source data files
│       ├── rba_decisions.csv
│       ├── sentiment_index.csv
│       ├── google_trends.csv
│       ├── abs_labour_force.csv
│       └── jsa_projections.csv
├── src/
│   ├── app_rba_sentiment.py    # Streamlit app — Project 1
│   ├── app_workforce_shift.py  # Streamlit app — Project 2
│   └── process_all_real_data.py # Data processing pipeline
├── notebooks/
│   ├── 01_sql_analysis.ipynb   # SQL queries & analysis
│   └── 02_Visualization.ipynb  # Python visualisations
└── requirements.txt
```

---

## 🚀 Run Locally

```bash
# Clone repo
git clone https://github.com/chloenguyen24563/Portfolio-DA.git
cd Portfolio-DA

# Install dependencies
pip install -r requirements.txt

# Run Project 1
streamlit run src/app_rba_sentiment.py

# Run Project 2
streamlit run src/app_workforce_shift.py
```

---

## 👤 About

**Chloe Nguyen** — Business & Data Analyst based in Sydney, Australia

- Master of Business Analytics, Melbourne Institute of Technology
- Previous experience in Business Analysis and Product Operations
  across the Vietnamese market
- Seeking DA and BA roles in Australia
- Full working rights in Australia

*This portfolio uses real Australian data sources — RBA, ABS, ANZ-Roy Morgan, and Jobs and Skills Australia — to demonstrate end-to-end analytical capability: from raw data ingestion and SQL querying to interactive dashboard deployment.*
