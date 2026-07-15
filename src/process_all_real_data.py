"""
process_all_real_data.py
========================
Xử lý tất cả data thật từ /Users/Chloe/Downloads/Project/

Input files:
    RBA Cash Rate.xlsx          → data/raw/rba_decisions.csv
    anz_confidence.xlsx         → data/raw/sentiment_index.csv
    Mortgage Stress.csv         → }
    Cost Of Living.csv          → } data/raw/google_trends.csv
    Fixed Home Loan.csv         → }
    Refinance Of HomeLoan.csv   → }
    RBA Interest Rate.csv       → }
    employment_projections...   → data/raw/jsa_projections.csv
    ABS_Labour_Force.xlsx       → data/raw/abs_labour_force.csv  (nếu có)

Chạy: python src/process_all_real_data.py
"""

from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
import os
os.chdir(PROJECT_ROOT)
os.makedirs("data/raw", exist_ok=True)

import pandas as pd
import numpy as np

PROJECT_DIR = Path("/Users/Chloe/Downloads/Project")

print("=" * 55)
print("Processing All Real Data Files")
print(f"Source: {PROJECT_DIR}")
print("=" * 55)


# ══════════════════════════════════════════════════════
# 1. RBA CASH RATE — data thật từ rba.gov.au
#    Sheet: Data, data bắt đầu từ row 11
#    Columns: date, Cash Rate Target, Change in Cash Rate
# ══════════════════════════════════════════════════════
print("\n[1/5] RBA Cash Rate...")

rba_raw = pd.read_excel(
    PROJECT_DIR / "RBA Cash Rate.xlsx",
    sheet_name="Data",
    header=None,
    skiprows=11  # data bắt đầu từ row 11
)

rba_raw.columns = ["date", "cash_rate", "rate_change"] + [f"col_{i}" for i in range(len(rba_raw.columns)-3)]
rba_raw["date"]       = pd.to_datetime(rba_raw["date"], errors="coerce")
rba_raw["cash_rate"]  = pd.to_numeric(rba_raw["cash_rate"], errors="coerce")
rba_raw["rate_change"]= pd.to_numeric(rba_raw["rate_change"], errors="coerce")
rba_raw = rba_raw.dropna(subset=["date", "cash_rate"])
rba_raw = rba_raw[rba_raw["date"] >= "2015-01-01"]

# Chỉ lấy ngày có rate change (RBA decision days)
# Lấy first day of each month để deduplicate
rba_raw["month"] = rba_raw["date"].dt.to_period("M")

# Lấy ngày đầu tiên trong tháng có rate change khác 0
decisions = rba_raw[rba_raw["rate_change"].notna() & (rba_raw["rate_change"] != 0)].copy()

# Nếu không có rate change, lấy 1 record/tháng (hold)
monthly = rba_raw.sort_values("date").drop_duplicates("month", keep="first")
monthly = monthly.merge(
    decisions[["month","rate_change"]].rename(columns={"rate_change":"actual_change"}),
    on="month", how="left"
)
monthly["rate_change"] = monthly["actual_change"].fillna(0)

monthly["decision"] = monthly["rate_change"].apply(
    lambda x: "hike" if x > 0 else "cut" if x < 0 else "hold"
)

def label_era(d):
    if d.year < 2019:   return "low-rate era"
    if d.year < 2020:   return "pre-COVID"
    if d.year <= 2021:  return "COVID"
    if d.year <= 2023:  return "hiking cycle"
    return "post-hike"

monthly["era"] = monthly["date"].apply(label_era)

rba_out = monthly[["date","cash_rate","rate_change","decision","era"]].copy()
rba_out = rba_out.rename(columns={"cash_rate":"new_rate"})
rba_out = rba_out.sort_values("date").reset_index(drop=True)

rba_out.to_csv("data/raw/rba_decisions.csv", index=False)
print(f"  Saved: data/raw/rba_decisions.csv ({len(rba_out)} rows)")
print(f"  Hikes: {(rba_out['decision']=='hike').sum()} | "
      f"Cuts: {(rba_out['decision']=='cut').sum()} | "
      f"Holds: {(rba_out['decision']=='hold').sum()}")
print(f"  Rate range: {rba_out['new_rate'].min()}% → {rba_out['new_rate'].max()}%")


# ══════════════════════════════════════════════════════
# 2. ANZ-ROY MORGAN CONSUMER CONFIDENCE
#    Sheet: Sheet1
#    Format: Wide — YEAR | JAN | FEB | ... | DEC | YEARLY AVERAGE
#    Melt sang long format, monthly
# ══════════════════════════════════════════════════════
print("\n[2/5] ANZ-Roy Morgan Consumer Confidence...")

anz_raw = pd.read_excel(PROJECT_DIR / "anz_confidence.xlsx", sheet_name="Sheet1")
anz_raw.columns = [str(c).strip() for c in anz_raw.columns]

# Melt wide → long
months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
month_map = {m: i+1 for i, m in enumerate(months)}

anz_long = anz_raw[["YEAR"] + months].melt(
    id_vars="YEAR", var_name="month_str", value_name="confidence_score"
)
anz_long["YEAR"] = pd.to_numeric(anz_long["YEAR"], errors="coerce")
anz_long = anz_long.dropna(subset=["YEAR"])
anz_long["month_num"] = anz_long["month_str"].map(month_map)
anz_long["date"] = pd.to_datetime(
    anz_long["YEAR"].astype(int).astype(str) + "-" +
    anz_long["month_num"].astype(str) + "-01"
)

# Clean score — remove footnote markers like ** #
anz_long["confidence_score"] = (
    anz_long["confidence_score"]
    .astype(str)
    .str.replace(r"[^0-9.]", "", regex=True)
)
anz_long["confidence_score"] = pd.to_numeric(anz_long["confidence_score"], errors="coerce")
anz_long = anz_long.dropna(subset=["confidence_score"])
anz_long = anz_long[anz_long["date"] >= "2015-01-01"]
anz_long = anz_long.sort_values("date").reset_index(drop=True)

# Derived columns — same structure as Westpac for compatibility
sent = anz_long[["date","confidence_score"]].copy()
sent = sent.rename(columns={"confidence_score":"sentiment_score"})

# ANZ index: pessimistic < 100
sent["is_pessimistic"]  = sent["sentiment_score"] < 100
sent["mom_change"]      = sent["sentiment_score"].diff().round(2)
sent["rolling_6m_avg"]  = sent["sentiment_score"].rolling(6, min_periods=3).mean().round(2)
sent["sentiment_gap"]   = (sent["sentiment_score"] - sent["rolling_6m_avg"]).round(2)

streak, streaks = 0, []
for v in sent["is_pessimistic"]:
    streak = streak + 1 if v else 0
    streaks.append(streak)
sent["pessimism_streak"] = streaks
sent["source"] = "ANZ-Roy Morgan Consumer Confidence Index"

sent.to_csv("data/raw/sentiment_index.csv", index=False)
print(f"  Saved: data/raw/sentiment_index.csv ({len(sent)} months)")
print(f"  Range: {sent['date'].min().date()} → {sent['date'].max().date()}")
print(f"  Score: min={sent['sentiment_score'].min():.1f} "
      f"mean={sent['sentiment_score'].mean():.1f} "
      f"max={sent['sentiment_score'].max():.1f}")
print(f"  Pessimistic months (<100): {sent['is_pessimistic'].sum()} "
      f"| Longest streak: {sent['pessimism_streak'].max()} months")


# ══════════════════════════════════════════════════════
# 3. GOOGLE TRENDS CSVs
#    5 keywords — đã download thủ công từ trends.google.com.au
#    Format: date, keyword_value (weekly)
# ══════════════════════════════════════════════════════
print("\n[3/5] Google Trends (5 CSV files)...")

TREND_FILES = {
    "mortgage stress":     "Mortgage Stress.csv",
    "cost of living":      "Cost Of Living.csv",
    "fixed rate mortgage": "Fixed Home Loan.csv",
    "refinance home loan": "Refinance Of HomeLoan.csv",
    "RBA interest rate":   "RBA Interest Rate.csv",
}

KEYWORD_GROUPS = {
    "mortgage stress":     "financial_stress",
    "cost of living":      "financial_stress",
    "fixed rate mortgage": "behaviour_change",
    "refinance home loan": "behaviour_change",
    "RBA interest rate":   "awareness",
}

all_trends = []
for keyword, filename in TREND_FILES.items():
    fpath = PROJECT_DIR / filename
    # Try _1 variant if primary doesn't exist
    if not fpath.exists():
        alt = PROJECT_DIR / filename.replace(".csv", " _1.csv")
        if alt.exists():
            fpath = alt

    if not fpath.exists():
        print(f"  WARNING: {filename} not found — skipping")
        continue

    # Google Trends CSV format:
    # Row 0: "Category: All categories"
    # Row 1: blank or column headers
    # Row 2+: date, value
    try:
        # Try reading with skiprows=1 first
        df = pd.read_csv(fpath, skiprows=1)
        # Check if first column is date-like
        if df.shape[1] >= 2:
            df.columns = ["date", "search_volume"] + [f"col_{i}" for i in range(df.shape[1]-2)]
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])
            df["search_volume"] = pd.to_numeric(df["search_volume"], errors="coerce")
            df = df.dropna(subset=["search_volume"])
            df["keyword"] = keyword
            df["keyword_group"] = KEYWORD_GROUPS[keyword]
            all_trends.append(df[["date","keyword","keyword_group","search_volume"]])
            print(f"  {keyword:<25} {len(df)} rows")
    except Exception as e:
        print(f"  ERROR reading {filename}: {e}")

if all_trends:
    trends = pd.concat(all_trends, ignore_index=True)
    trends["search_volume_raw"] = trends["search_volume"]

    # Weekly → Monthly aggregate
    trends["date"] = trends["date"].dt.to_period("M").dt.to_timestamp()
    trends = (trends.groupby(["date","keyword","keyword_group"])[["search_volume","search_volume_raw"]]
              .mean().round(1).reset_index())
    trends = trends[trends["date"] >= "2015-01-01"]
    trends = trends.sort_values(["keyword","date"]).reset_index(drop=True)

    # 3-month rolling smooth
    trends["search_volume"] = (
        trends.groupby("keyword")["search_volume"]
              .transform(lambda x: x.rolling(3, min_periods=1).mean().round(1))
    )

    # Spike flag
    trends["rolling_6m"] = (
        trends.groupby("keyword")["search_volume_raw"]
              .transform(lambda x: x.rolling(6, min_periods=3).mean())
    )
    trends["is_spike"] = trends["search_volume_raw"] > (trends["rolling_6m"] * 1.5)

    trends.to_csv("data/raw/google_trends.csv", index=False)
    print(f"\n  Saved: data/raw/google_trends.csv ({len(trends)} rows, "
          f"{trends['keyword'].nunique()} keywords)")
else:
    print("  No trend files found — will need to run fetch_google_trends.py")


# ══════════════════════════════════════════════════════
# 4. JSA EMPLOYMENT PROJECTIONS
# ══════════════════════════════════════════════════════
print("\n[4/5] JSA Employment Projections...")

jsa_raw = pd.read_excel(
    PROJECT_DIR / "employment_projections_-_may_2025_to_may_2035.xlsx",
    sheet_name="Table_1 Industry Division",
    header=None
)

data_t1 = jsa_raw.iloc[9:].copy()
data_t1.columns = (
    ["industry_level","industry_code","industry",
     "baseline_2025","projected_2030","projected_2035"]
    + [f"col_{i}" for i in range(len(jsa_raw.columns)-6)]
)
data_t1 = data_t1[["industry_level","industry_code","industry",
                    "baseline_2025","projected_2030","projected_2035"]]
data_t1 = data_t1.dropna(subset=["industry"])
data_t1 = data_t1[data_t1["industry_level"] == 1].copy()

for col in ["baseline_2025","projected_2030","projected_2035"]:
    data_t1[col] = pd.to_numeric(data_t1[col], errors="coerce")

data_t1["annual_growth_pct"]       = ((data_t1["projected_2030"]/data_t1["baseline_2025"])**(1/5)-1)*100
data_t1["projected_new_jobs_000s"] = data_t1["projected_2030"] - data_t1["baseline_2025"]
data_t1["growth_5yr_pct"]          = ((data_t1["projected_2030"]/data_t1["baseline_2025"])-1)*100

for col in ["annual_growth_pct","projected_new_jobs_000s","growth_5yr_pct"]:
    data_t1[col] = data_t1[col].round(2)

data_t1["industry"] = data_t1["industry"].astype(str).str.strip()
data_t1["projection_period"] = "2025-2030"
data_t1["source"] = "Jobs and Skills Australia — May 2025 Employment Projections"

jsa_out = data_t1[[
    "industry","industry_code","baseline_2025","projected_2030",
    "projected_new_jobs_000s","annual_growth_pct","growth_5yr_pct",
    "projection_period","source"
]].reset_index(drop=True)

jsa_out.to_csv("data/raw/jsa_projections.csv", index=False)
print(f"  Saved: data/raw/jsa_projections.csv ({len(jsa_out)} industries)")
print(f"\n  Top 5 fastest growing:")
print(jsa_out.nlargest(5,"annual_growth_pct")[["industry","annual_growth_pct","projected_new_jobs_000s"]].to_string(index=False))


# ══════════════════════════════════════════════════════
# 5. ABS LABOUR FORCE
# ══════════════════════════════════════════════════════
print("\n[5/5] ABS Labour Force...")

abs_path = PROJECT_DIR / "ABS_Labour_Force.xlsx"
if abs_path.exists():
    raw = pd.read_excel(abs_path, sheet_name="Data1", header=None)
    industry_names = raw.iloc[0, 1:].tolist()
    series_types   = raw.iloc[2, 1:].tolist()
    sa_cols = [i for i, t in enumerate(series_types) if t == "Seasonally Adjusted"]

    def clean_industry(name):
        if not isinstance(name, str): return None
        name = name.replace(";  Employed total ;","").replace("; Employed total ;","").strip()
        return None if name.lower() == "employed total" else name

    data_rows = raw.iloc[10:].copy()
    data_rows["date"] = pd.to_datetime(data_rows.iloc[:,0], errors="coerce")
    data_rows = data_rows.dropna(subset=["date"])
    data_rows = data_rows[data_rows["date"] >= "2015-01-01"]

    records = []
    for col_idx in sa_cols:
        industry = clean_industry(industry_names[col_idx])
        if not industry: continue
        for _, row in data_rows.iterrows():
            val = row.iloc[col_idx+1]
            if pd.notna(val):
                records.append({"date":row["date"],"industry":industry,"employed_000s":round(float(val),1)})

    abs_df = pd.DataFrame(records)
    abs_df = abs_df.sort_values(["industry","date"]).reset_index(drop=True)
    abs_df["yoy_change_000s"] = abs_df.groupby("industry")["employed_000s"].diff(4).round(1)
    abs_df["yoy_growth_pct"]  = abs_df.groupby("industry")["employed_000s"].pct_change(4).round(4)*100
    abs_df.to_csv("data/raw/abs_labour_force.csv", index=False)
    print(f"  Saved: data/raw/abs_labour_force.csv ({len(abs_df)} rows, {abs_df['industry'].nunique()} industries)")
    latest = abs_df[abs_df["date"]==abs_df["date"].max()]
    print(f"  Top 3 by employment:")
    print(latest.nlargest(3,"employed_000s")[["industry","employed_000s","yoy_growth_pct"]].to_string(index=False))
else:
    print("  ABS_Labour_Force.xlsx not found in Project folder")
    print("  Copy file vào /Users/Chloe/Downloads/Project/ rồi chạy lại")


# ══════════════════════════════════════════════════════
print(f"\n{'='*55}")
print("All done. Files in data/raw/:")
for f in sorted(Path("data/raw").glob("*.csv")):
    size = f.stat().st_size / 1024
    print(f"  {f.name:<35} {size:6.1f} KB")
