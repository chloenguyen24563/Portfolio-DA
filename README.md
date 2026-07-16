# 📊 Australian Economic \& Workforce Analytics Portfolio

**Chloe Nguyen | Business \& Data Analyst | Sydney, Australia**

> Two data projects analysing the Australian economy from different angles —
> consumer psychology under monetary policy pressure, and structural shifts
> in the labour market through to 2030.

**Tech Stack:** Python · SQL · Power BI · Streamlit · Plotly · pandas

\---

## 🏦 Project 1: RBA Rate Decisions \& Consumer Confidence

### 🔴 [Live Dashboard →](https://portfolio-da-dt2mx6btl5a4kuybykikvc.streamlit.app/)

### The Question

*When the RBA raises interest rates, how quickly do Australians feel it — and does the headline sentiment index tell the full story?*

Most commentary focuses on the rate decision itself. This project looks at what happens *after* — tracking consumer confidence and search behaviour over 11 years to understand the psychological lag between monetary policy and real-world anxiety.

### Key Findings

|#|Finding|Data|
|-|-|-|
|1|**Longest pessimism streak on record**|52 consecutive months below neutral (100) — started March 2022, ongoing as of June 2026|
|2|**Lowest confidence in ANZ index history**|63.6 recorded April 2026 — below the COVID crash of March 2020|
|3|**Rate cuts are not working**|Confidence averaged 110.6 pre-hike, dropped to 80.5 during hiking cycle, and recovered only to 82.1 after cuts began — a 30.1 pt crash with just 1.6 pts recovery|
|4|**Behavioural anxiety outlasts monetary policy**|Google searches for 'mortgage stress' remained elevated months after rate cuts began — psychological anxiety persists longer than the headline index suggests|

### Outcomes \& Recommendations

**What the data tells us:**

* Consumer confidence crashed **30.1 points** from pre-hike (avg 110.6) to during hiking cycle (avg 80.5).
* After rate cuts began in 2025, confidence recovered only **1.6 points** to 82.1 — statistically negligible.
* Google Trends data reveals search anxiety persists 2–3 months beyond what the headline index captures, suggesting the index overstates the pace of recovery.

**Business Implications:**

* Organisations in retail, banking, property, and FMCG that are planning revenue recovery based on the ANZ headline index may be significantly ahead of actual consumer readiness.
* The near-zero recovery in sentiment post-cut suggests structural factors (cost of living, accumulated debt stress) are dampening the usual stimulus effect of rate cuts.

**Recommendations:**

1. Businesses should supplement ANZ sentiment data with real-time Google Trends signals for a more accurate read on actual consumer mood.
2. Marketing and commercial teams should delay "recovery cycle" messaging until both the sentiment index AND search anxiety normalise simultaneously — using one signal alone is insufficient.
3. Businesses planning for a consumer recovery should factor in a 6–12 month lag after rate cuts before confidence meaningfully improves — historical data from this cycle suggests monetary easing alone is not sufficient to restore consumer sentiment quickly.

### Methodology

|Step|Detail|
|-|-|
|**Data sources**|ANZ-Roy Morgan (roymorgan.com), RBA decisions (rba.gov.au), Google Trends AU via pytrends|
|**Processing**|Aligned 3 datasets to monthly frequency; cash rate forward-filled between decisions; 3-month rolling average applied to Google Trends to smooth weekly noise|
|**SQL analysis**|Event study (sentiment at t+1/t+3/t+6 months post-hike); pre/during/post cycle segmentation; pessimism streak detection via window functions|
|**Metric definition**|"Pessimism streak" = consecutive months with ANZ index < 100 (pessimists outnumber optimists)|
|**Visualisation**|Streamlit + Plotly for public dashboard; Power BI for stakeholder format; reference line at 100 to mark neutral threshold|

### Limitations

* ANZ-Roy Morgan index is survey-based — subject to sampling bias and question framing effects.
* Google Trends data is a relative index (0–100), not absolute search volume — directional rather than precise.
* Analysis is correlational — cannot definitively isolate RBA decisions as sole driver of sentiment changes.

### Data Sources

|Dataset|Source|Coverage|
|-|-|-|
|ANZ-Roy Morgan Consumer Confidence|roymorgan.com|2015–2026, monthly|
|RBA Cash Rate decisions|rba.gov.au|2015–2026, per decision|
|Google Trends AU|trends.google.com.au via pytrends|2015–2026, monthly|

\---

## 📈 Project 2: Australian Workforce Shift 2025–2030

### 🔴 [Live Dashboard →](https://portfolio-da-gyaaptrni7jameapcexlfp.streamlit.app/)

### The Question

*Which Australian industries are genuinely growing right now — and where are the gaps between what is actually happening and what the government is projecting?*

Government employment projections shape policy, skills funding, and migration intake. This project cross-references JSA projections against actual ABS employment data to surface discrepancies with real implications for workforce planning.

### Key Findings

|#|Finding|Data|
|-|-|-|
|1|**Government significantly underestimates tech demand**|Professional \& Technical Services growing at **12.36% YoY** — 6x faster than JSA projection of 1.94%/yr|
|2|**Healthcare dominates job creation**|290,000 new jobs projected by 2030 — largest of any industry; actual growth of 3.61% YoY confirms the trend|
|3|**Utilities sector surprise**|Electricity, Gas \& Water growing at **13.33% YoY** — fastest actual growth of any industry, yet below-median in JSA projections|
|4|**Clear winners through 2030**|Healthcare, Education, and Professional \& Technical Services sit in the "High Now + High Projected" quadrant — strongest combination of current and future growth|

### Outcomes \& Recommendations

**What the data tells us:**

* The gap between actual YoY growth (12.36%) and JSA projected annual growth (1.94%) for Professional \& Technical Services is the largest discrepancy across all 19 industries analysed.
* 3 of 19 industries fall in the "High Now + High Projected" quadrant — these represent the most resilient employment sectors through 2030.
* Rental \& Real Estate shows the largest negative divergence: projected 1.39%/yr growth but actual YoY of -15.97% — a significant red flag for workforce planning in that sector.

**Business Implications:**

* Skills funding and training programs calibrated to JSA projections may be systematically underinvesting in tech roles relative to actual market demand.
* Skilled migration intake for ICT occupations may be insufficient given the gap between projected and actual growth.
* Organisations in Rental \& Real Estate should treat JSA projections with caution — actual data suggests a contraction that government figures do not reflect.

**Recommendations:**

1. Workforce planners and policy makers should incorporate quarterly ABS actuals as a validation layer on top of 5-year JSA projections — annual recalibration is insufficient given the speed of change in tech sectors.
2. Skills funding bodies (TAFE, industry training packages) should reallocate resources toward Professional \& Technical Services roles — current demand outpaces supply by a 6x margin.
3. Job seekers and career changers seeking long-term stability should prioritise Healthcare and Professional \& Technical Services — both industries demonstrate strong actual AND projected growth, making them the most resilient choice through 2030.

### Methodology

|Step|Detail|
|-|-|
|**Data sources**|ABS Labour Force Survey Cat. 6291 Table 04 (abs.gov.au); JSA Employment Projections May 2025–2035 (jobsandskills.gov.au)|
|**Processing**|YoY growth = (latest quarter / same quarter prior year) - 1, to eliminate seasonal effects; industry names harmonised via lowercase string matching across ABS and JSA|
|**SQL analysis**|Industry growth ranking; projected vs actual gap analysis; quadrant classification (High/Low actual × High/Low projected)|
|**Metric definition**|Quadrant thresholds set at median values of each axis — relative positioning ensures industries are compared against each other, not against a fixed benchmark|
|**Visualisation**|Bubble chart encodes 3 dimensions simultaneously: actual growth (x), projected growth (y), employment size (bubble size); quadrant lines at median to avoid clustering|

### Limitations

* ABS data available at industry Division level only (19 industries) — sub-industry breakdowns not in public dataset.
* JSA projections based on May 2025 baseline — may not reflect structural shifts from AI adoption or post-pandemic normalisation.
* YoY growth calculated from a single quarter comparison — does not smooth seasonal variation.

### Data Sources

|Dataset|Source|Coverage|
|-|-|-|
|ABS Labour Force Survey Cat. 6291, Table 04|abs.gov.au|2015–2026, quarterly|
|JSA Employment Projections May 2025–2035|jobsandskills.gov.au|19 industry divisions|

\---

## 📁 Repository Structure

```
Portfolio-DA/
├── README.md
├── requirements.txt
├── data/
│   └── raw/
│       ├── rba\\\_decisions.csv
│       ├── sentiment\\\_index.csv
│       ├── google\\\_trends.csv
│       ├── abs\\\_labour\\\_force.csv
│       └── jsa\\\_projections.csv
├── src/
│   ├── app\\\_rba\\\_sentiment.py       # Streamlit app — Project 1
│   ├── app\\\_workforce\\\_shift.py     # Streamlit app — Project 2
│   └── process\\\_all\\\_real\\\_data.py   # Data processing pipeline
└── notebooks/
    ├── 01\\\_sql\\\_analysis.ipynb      # SQL queries \\\& analysis
    └── 02\\\_Visualization.ipynb     # Python visualisations
```

\---

## 🚀 Run Locally

```bash
# Clone repo
git clone https://github.com/chloenguyen24563/Portfolio-DA.git
cd Portfolio-DA

# Install dependencies
pip install -r requirements.txt

# Run Project 1
streamlit run src/app\\\_rba\\\_sentiment.py

# Run Project 2 
streamlit run src/app\\\_workforce\\\_shift.py --server.port 8502
```

\---

## 👤 About

**Chloe Nguyen** — Business \& Data Analyst based in Sydney, Australia

* Master of Business Analytics, Melbourne Institute of Technology
* Previous experience in Business Analysis and Product Operations
across the Vietnamese market
* Seeking DA and BA roles in Australia
* Full working rights in Australia

*This portfolio uses real Australian data sources — RBA, ABS, ANZ-Roy Morgan, and Jobs and Skills Australia — to demonstrate end-to-end analytical capability: from raw data ingestion and SQL querying to interactive dashboard deployment.*

