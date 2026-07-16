-- ============================================================
-- SQL ANALYSIS SHOWCASE
-- Portfolio: Australian Economic & Workforce Analytics
-- Author: Chloe Nguyen
-- Database: SQLite | Tables: 5 | Period: 2015-2026
-- ============================================================
-- Run order: queries are independent, can be run in any order
-- Engine: SQLite (compatible with PostgreSQL with minor changes)
-- ============================================================


-- ============================================================
-- PROJECT 1: RBA RATE DECISIONS & CONSUMER CONFIDENCE
-- ============================================================


-- ------------------------------------------------------------
-- Q1. How did consumer confidence change before, during,
--     and after the 2022-2026 rate hiking cycle?
-- ------------------------------------------------------------
SELECT
    CASE
        WHEN date < '2022-05-01'                        THEN '1. Pre-hike (before May 2022)'
        WHEN date >= '2022-05-01' AND date < '2024-01-01' THEN '2. During hiking cycle (2022-2023)'
        ELSE                                                  '3. Post-hike / rate cuts (2024+)'
    END AS period,
    COUNT(*)                                AS months,
    ROUND(AVG(sentiment_score), 1)          AS avg_confidence,
    MIN(sentiment_score)                    AS lowest,
    MAX(sentiment_score)                    AS highest,
    SUM(CASE WHEN is_pessimistic = 1
             THEN 1 ELSE 0 END)             AS pessimistic_months
FROM sentiment_index
GROUP BY 1
ORDER BY 1;

-- Key finding: avg dropped 30.1 pts from pre-hike (110.6)
-- to during hiking cycle (80.5), then recovered only 1.6 pts
-- after cuts began (82.1) — rate cuts had near-zero effect


-- ------------------------------------------------------------
-- Q2. Pessimism streaks — which period caused the longest
--     sustained loss of consumer confidence?
-- ------------------------------------------------------------
WITH streak_groups AS (
    SELECT
        date,
        sentiment_score,
        is_pessimistic,
        -- Create group number: increments each time streak resets
        SUM(CASE WHEN is_pessimistic = 0 THEN 1 ELSE 0 END)
            OVER (ORDER BY date) AS streak_group
    FROM sentiment_index
),
streak_summary AS (
    SELECT
        streak_group,
        MIN(date)                       AS streak_start,
        MAX(date)                       AS streak_end,
        COUNT(*)                        AS streak_length_months,
        ROUND(MIN(sentiment_score), 1)  AS lowest_during_streak
    FROM streak_groups
    WHERE is_pessimistic = 1
    GROUP BY streak_group
)
SELECT
    streak_start,
    streak_end,
    streak_length_months,
    lowest_during_streak,
    CASE
        WHEN streak_start < '2020-01-01' THEN 'Pre-COVID'
        WHEN streak_start < '2022-01-01' THEN 'COVID era'
        ELSE '2022-present hiking cycle'
    END AS era
FROM streak_summary
WHERE streak_length_months >= 3
ORDER BY streak_length_months DESC;


-- ------------------------------------------------------------
-- Q3. Event study — how did sentiment change in the months
--     following each individual rate hike?
-- ------------------------------------------------------------
SELECT
    r.date                                          AS hike_date,
    r.new_rate,
    r.rate_change,
    s0.sentiment_score                              AS sentiment_at_hike,
    s1.sentiment_score                              AS sentiment_1m_after,
    s3.sentiment_score                              AS sentiment_3m_after,
    s6.sentiment_score                              AS sentiment_6m_after,
    ROUND(s1.sentiment_score - s0.sentiment_score, 1) AS change_1m,
    ROUND(s3.sentiment_score - s0.sentiment_score, 1) AS change_3m,
    ROUND(s6.sentiment_score - s0.sentiment_score, 1) AS change_6m
FROM rba_decisions r
LEFT JOIN sentiment_index s0
    ON strftime('%Y-%m', s0.date) = strftime('%Y-%m', r.date)
LEFT JOIN sentiment_index s1
    ON s1.date = date(r.date, '+1 month')
LEFT JOIN sentiment_index s3
    ON s3.date = date(r.date, '+3 months')
LEFT JOIN sentiment_index s6
    ON s6.date = date(r.date, '+6 months')
WHERE r.decision = 'hike'
ORDER BY r.date;


-- ------------------------------------------------------------
-- Q4. Average sentiment change after hikes vs cuts —
--     which direction has stronger psychological impact?
-- ------------------------------------------------------------
WITH event_windows AS (
    SELECT
        r.decision,
        ROUND(s1.sentiment_score - s0.sentiment_score, 1) AS change_1m,
        ROUND(s3.sentiment_score - s0.sentiment_score, 1) AS change_3m
    FROM rba_decisions r
    LEFT JOIN sentiment_index s0
        ON strftime('%Y-%m', s0.date) = strftime('%Y-%m', r.date)
    LEFT JOIN sentiment_index s1
        ON s1.date = date(r.date, '+1 month')
    LEFT JOIN sentiment_index s3
        ON s3.date = date(r.date, '+3 months')
    WHERE r.decision IN ('hike', 'cut')
)
SELECT
    decision,
    COUNT(*)                            AS total_events,
    ROUND(AVG(change_1m), 1)            AS avg_change_1m,
    ROUND(AVG(change_3m), 1)            AS avg_change_3m,
    ROUND(MIN(change_1m), 1)            AS worst_single_month
FROM event_windows
GROUP BY decision;


-- ------------------------------------------------------------
-- Q5. Google Trends — which keywords spiked most during
--     the rate hiking cycle vs normal periods?
-- ------------------------------------------------------------
SELECT
    keyword,
    keyword_group,
    ROUND(AVG(CASE WHEN strftime('%Y', date) < '2022'
                   THEN search_volume END), 1)  AS avg_pre_hike,
    ROUND(AVG(CASE WHEN strftime('%Y', date) >= '2022'
                   AND strftime('%Y', date) <= '2023'
                   THEN search_volume END), 1)  AS avg_during_hike,
    ROUND(AVG(CASE WHEN strftime('%Y', date) > '2023'
                   THEN search_volume END), 1)  AS avg_post_hike,
    MAX(search_volume)                          AS peak_volume,
    SUM(CASE WHEN is_spike = 1 THEN 1 ELSE 0 END) AS spike_months
FROM google_trends
GROUP BY keyword, keyword_group
ORDER BY avg_during_hike DESC;


-- ============================================================
-- PROJECT 2: AUSTRALIAN WORKFORCE SHIFT 2025-2030
-- ============================================================


-- ------------------------------------------------------------
-- Q6. Which industries are growing fastest right now,
--     and how does this compare to JSA projections?
-- ------------------------------------------------------------
WITH latest_quarter AS (
    SELECT
        industry,
        employed_000s,
        yoy_growth_pct
    FROM abs_labour_force
    WHERE date = (SELECT MAX(date) FROM abs_labour_force)
      AND industry != 'Employed total ;'
),
gap_analysis AS (
    SELECT
        l.industry,
        ROUND(l.employed_000s, 1)           AS current_employed_000s,
        ROUND(l.yoy_growth_pct, 2)          AS actual_yoy_growth_pct,
        ROUND(j.annual_growth_pct, 2)       AS jsa_projected_pct,
        ROUND(l.yoy_growth_pct
              - j.annual_growth_pct, 2)     AS gap_actual_vs_projected,
        j.projected_new_jobs_000s
    FROM latest_quarter l
    LEFT JOIN jsa_projections j
        ON LOWER(TRIM(l.industry)) LIKE '%' || LOWER(TRIM(j.industry)) || '%'
        OR LOWER(TRIM(j.industry)) LIKE '%' || LOWER(TRIM(l.industry)) || '%'
)
SELECT *
FROM gap_analysis
WHERE jsa_projected_pct IS NOT NULL
ORDER BY actual_yoy_growth_pct DESC;

-- Key finding: Professional & Technical Services shows
-- largest gap: actual 12.36% vs projected 1.94% (+10.4 pts)


-- ------------------------------------------------------------
-- Q7. Quadrant classification — which industries are
--     growing NOW and projected to keep growing?
-- ------------------------------------------------------------
WITH latest AS (
    SELECT industry, yoy_growth_pct, employed_000s
    FROM abs_labour_force
    WHERE date = (SELECT MAX(date) FROM abs_labour_force)
      AND industry != 'Employed total ;'
),
joined AS (
    SELECT
        l.industry,
        ROUND(l.yoy_growth_pct, 2)      AS actual_growth,
        ROUND(j.annual_growth_pct, 2)   AS projected_growth,
        ROUND(l.employed_000s, 1)       AS employed_000s
    FROM latest l
    LEFT JOIN jsa_projections j
        ON LOWER(TRIM(l.industry)) LIKE '%' || LOWER(TRIM(j.industry)) || '%'
        OR LOWER(TRIM(j.industry)) LIKE '%' || LOWER(TRIM(l.industry)) || '%'
    WHERE j.annual_growth_pct IS NOT NULL
),
medians AS (
    SELECT
        AVG(actual_growth)    AS med_actual,
        AVG(projected_growth) AS med_projected
    FROM joined
)
SELECT
    j.industry,
    j.actual_growth,
    j.projected_growth,
    j.employed_000s,
    CASE
        WHEN j.actual_growth >= m.med_actual
         AND j.projected_growth >= m.med_projected
            THEN 'HIGH NOW + HIGH PROJECTED'
        WHEN j.actual_growth >= m.med_actual
         AND j.projected_growth < m.med_projected
            THEN 'HIGH NOW + LOWER PROJECTED'
        WHEN j.actual_growth < m.med_actual
         AND j.projected_growth >= m.med_projected
            THEN 'LOWER NOW + HIGH PROJECTED'
        ELSE 'LOWER NOW + LOWER PROJECTED'
    END AS quadrant
FROM joined j
CROSS JOIN medians m
ORDER BY quadrant, j.actual_growth DESC;

-- ============================================================
-- End of SQL Showcase — 7 queries covering both projects
-- ============================================================
