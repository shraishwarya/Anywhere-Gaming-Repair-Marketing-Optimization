-- Anywhere Gaming Repair: Marketing Optimization
-- SQLite-compatible SQL. The CSV can be imported into a table named ad_market_data.
-- Note: this is a synthetic practice dataset, not actual company data.

-- 1) Inspect the data
SELECT * FROM ad_market_data LIMIT 10;

-- 2) Clean channel names and filter to the target audience.
-- NULL CPM values are filled using spend / impressions * 1000.
WITH cleaned AS (
    SELECT
        TRIM(media_channel) AS cleaned_channel,
        age_group,
        CAST(monthly_spend_usd AS REAL) AS spend_usd,
        CAST(impressions AS INTEGER) AS impressions,
        CAST(engagements AS INTEGER) AS engagements,
        COALESCE(
            CAST(cost_per_thousand_impressions AS REAL),
            CAST(monthly_spend_usd AS REAL) * 1000.0 / NULLIF(CAST(impressions AS REAL), 0)
        ) AS cpm
    FROM ad_market_data
    WHERE age_group IN ('18-34', '25-34')
)
SELECT
    cleaned_channel,
    COUNT(*) AS campaign_rows,
    ROUND(SUM(spend_usd), 2) AS total_spend_usd,
    SUM(impressions) AS total_impressions,
    SUM(engagements) AS total_engagements,
    ROUND(100.0 * SUM(engagements) / NULLIF(SUM(impressions), 0), 2) AS engagement_rate_pct,
    ROUND(1000.0 * SUM(spend_usd) / NULLIF(SUM(impressions), 0), 2) AS weighted_cpm
FROM cleaned
GROUP BY cleaned_channel
ORDER BY weighted_cpm ASC;

-- 3) Budget check: show each campaign row that is within the $2,000 monthly cap.
SELECT
    TRIM(media_channel) AS cleaned_channel,
    monthly_spend_usd,
    impressions,
    engagements,
    ROUND(100.0 * engagements / NULLIF(impressions, 0), 2) AS engagement_rate_pct
FROM ad_market_data
WHERE age_group IN ('18-34', '25-34')
  AND monthly_spend_usd <= 2000
ORDER BY engagement_rate_pct DESC;
