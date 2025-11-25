import pandas as pd
from pathlib import Path

class DataAgent:
    def __init__(self, csv_path=None):
        # set csv path
        if csv_path is None:
            root = Path(__file__).resolve().parent.parent.parent
            csv_path = str(root / "data" / "synthetic_fb_ads_undergarments.csv")
        self.csv_path = csv_path
        self.df = None

    def load_data(self):
        # load csv into dataframe
        self.df = pd.read_csv(self.csv_path)

    def compute_metrics(self):
        # work on a copy
        df = self.df.copy()

        # basic metrics
        df["ctr"] = df["clicks"] / df["impressions"]
        df["cpc"] = df["spend"] / df["clicks"].replace(0, 1)
        df["cpm"] = (df["spend"] / df["impressions"]) * 1000
        df["roas"] = df["revenue"] / df["spend"].replace(0, 1)

        # kpi summary
        summary = {
            "total_spend": float(df["spend"].sum()),
            "total_revenue": float(df["revenue"].sum()),
            "total_purchases": int(df["purchases"].sum()),
            "overall_roas": float(df["roas"].mean()),
            "overall_ctr": float(df["ctr"].mean()),
            "overall_cpc": float(df["cpc"].mean()),
            "overall_cpm": float(df["cpm"].mean())
        }

        # daily metrics
        daily_df = df.groupby("date").agg({
            "spend": "sum",
            "revenue": "sum",
            "roas": "mean",
            "ctr": "mean"
        }).reset_index()

        daily_metrics = []
        for _, row in daily_df.iterrows():
            daily_metrics.append({
                "date": row["date"],
                "roas": float(row["roas"]),
                "ctr": float(row["ctr"]),
                "spend": float(row["spend"]),
                "revenue": float(row["revenue"])
            })

        # creative-level metrics using creative_message
        creative_df = df.groupby("creative_message").agg({
            "spend": "sum",
            "revenue": "sum",
            "impressions": "sum",
            "clicks": "sum",
            "roas": "mean",
            "ctr": "mean",
            "creative_type": "first",
            "audience_type": "first"
        }).reset_index()

        # how many days each creative ran
        freq_df = df.groupby("creative_message")["date"].nunique().reset_index()
        freq_df.columns = ["creative_message", "freq_days"]
        creative_df = creative_df.merge(freq_df, on="creative_message", how="left")

        # top and worst creatives by roas
        top_creatives = creative_df.sort_values("roas", ascending=False).head(5).to_dict("records")
        worst_creatives = creative_df.sort_values("roas", ascending=True).head(5).to_dict("records")

        # simple fatigue signals: long-running creatives or very low ctr
        fatigue_df = creative_df[(creative_df["freq_days"] >= 20) | (creative_df["ctr"] < 0.008)]
        fatigue_signals = fatigue_df.to_dict("records")

        output = {
            "kpi_summary": summary,
            "daily_metrics": daily_metrics,
            "top_creatives": top_creatives,
            "worst_creatives": worst_creatives,
            "creative_fatigue_signals": fatigue_signals
        }

        return output
