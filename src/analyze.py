"""
Run from the project root:
    python -m pip install -r requirements.txt
    python src/analyze.py

This analyzes a synthetic practice dataset, not actual company performance.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ad_market_data.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA)
df["media_channel"] = df["media_channel"].astype("string").str.strip()
df["age_group"] = df["age_group"].astype("string").str.strip()

# Keep target audience records; the 25-34 subset is part of the 18-34 target.
df = df[df["age_group"].isin(["18-34", "25-34"])].copy()
df["monthly_spend_usd"] = pd.to_numeric(df["monthly_spend_usd"], errors="coerce")
df["impressions"] = pd.to_numeric(df["impressions"], errors="coerce")
df["engagements"] = pd.to_numeric(df["engagements"], errors="coerce")
df["cost_per_thousand_impressions"] = pd.to_numeric(
    df["cost_per_thousand_impressions"], errors="coerce"
)
calculated_cpm = df["monthly_spend_usd"] * 1000 / df["impressions"].replace(0, pd.NA)
df["cpm_clean"] = df["cost_per_thousand_impressions"].fillna(calculated_cpm)
df["engagement_rate_pct"] = 100 * df["engagements"] / df["impressions"].replace(0, pd.NA)

summary = (
    df.groupby("media_channel", dropna=False)
    .agg(
        campaign_rows=("media_channel", "size"),
        total_spend_usd=("monthly_spend_usd", "sum"),
        total_impressions=("impressions", "sum"),
        total_engagements=("engagements", "sum"),
    )
    .reset_index()
)
summary["engagement_rate_pct"] = 100 * summary["total_engagements"] / summary["total_impressions"]
summary["weighted_cpm"] = 1000 * summary["total_spend_usd"] / summary["total_impressions"]
summary = summary.sort_values("weighted_cpm")
summary.to_csv(OUT / "channel_summary.csv", index=False)
df.to_csv(OUT / "cleaned_campaign_data.csv", index=False)

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(summary["media_channel"], summary["weighted_cpm"])
ax.set_title("Weighted Cost per 1,000 Impressions by Channel")
ax.set_ylabel("Weighted CPM (USD)")
ax.set_xlabel("Advertising channel")
ax.tick_params(axis="x", rotation=15)
fig.tight_layout()
fig.savefig(OUT / "weighted_cpm.png", dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(summary["media_channel"], summary["engagement_rate_pct"])
ax.set_title("Engagement Rate by Advertising Channel")
ax.set_ylabel("Engagement rate (%)")
ax.set_xlabel("Advertising channel")
ax.tick_params(axis="x", rotation=15)
fig.tight_layout()
fig.savefig(OUT / "engagement_rate.png", dpi=160)
plt.close(fig)

print("\nChannel summary (synthetic practice data):")
print(summary.round(2).to_string(index=False))
print(f"\nSaved results in: {OUT}")
