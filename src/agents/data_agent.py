import pandas as pd
import os

class DataAgent:
    def __init__(self, csv_path="E:\Kasparo\kasparro-agentic-fb-analyst-kunal-singh\data\synthetic_fb_ads_undergarments.csv"):
        self.csv_path = csv_path
        self.df = None

    def load_data(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError("CSV file not found: " + self.csv_path)
        self.df = pd.read_csv(self.csv_path)

    def compute_metrics(self):
        df = self.df.copy()

        df["ctr"] = df["clicks"] / df["impressions"].replace(0, 1)
        df["roas"] = df["revenue"] / df["spend"].replace(0, 1)
        df["cpc"] = df["spend"] / df["clicks"].replace(0, 1)
        df["cpm"] = (df["spend"] / df["impressions"].replace(0, 1)) * 1000

        kpi_summary = {
            "total_spend": float(df["spend"].sum()),
            "total_revenue": float(df["revenue"].sum()),
            "total_purchases": int(df["purchases"].sum()),
            "overall_roas": float(df["revenue"].sum() / df["spend"].sum()),
            "overall_ctr": float(df["ctr"].mean()),
            "overall_cpc": float(df["cpc"].mean()),
            "overall_cpm": float(df["cpm"].mean()),
        }

        daily_metrics = [
            {
                "date": str(row["date"]),
                "roas": float(row["roas"]),
                "ctr": float(row["ctr"]),
                "spend": float(row["spend"]),
                "revenue": float(row["revenue"])
            }
            for _, row in df.groupby("date").agg({
                "roas": "mean",
                "ctr": "mean",
                "spend": "sum",
                "revenue": "sum"
            }).reset_index().iterrows()
        ]

        creative_perf = (
            df.groupby("creative_message")
            .agg({
                "roas": "mean",
                "ctr": "mean",
                "cpc": "mean",
                "cpm": "mean",
                "spend": "sum",
                "revenue": "sum",
                "impressions": "sum",
                "clicks": "sum"
            })
            .sort_values("roas", ascending=False)
            .reset_index()
        )

        top_creatives = creative_perf.head(10).to_dict(orient="records")
        worst_creatives = creative_perf.tail(10).to_dict(orient="records")

        fatigue = []
        for _, row in creative_perf.iterrows():
            if row["impressions"] > 300000 and row["ctr"] < 0.012:
                fatigue.append({
                    "creative_message": row["creative_message"],
                    "ctr": float(row["ctr"]),
                    "impressions": int(row["impressions"]),
                    "roas": float(row["roas"])
                })

        audience_perf = (
            df.groupby("audience_type")
            .agg({
                "roas": "mean",
                "ctr": "mean",
                "cpm": "mean",
                "cpc": "mean",
                "spend": "sum",
                "revenue": "sum"
            })
            .reset_index()
            .to_dict(orient="records")
        )

        country_perf = (
            df.groupby("country")
            .agg({
                "roas": "mean",
                "ctr": "mean",
                "cpm": "mean",
                "spend": "sum",
                "revenue": "sum"
            })
            .reset_index()
            .to_dict(orient="records")
        )

        platform_perf = (
            df.groupby("platform")
            .agg({
                "roas": "mean",
                "ctr": "mean",
                "cpm": "mean",
                "spend": "sum",
                "revenue": "sum"
            })
            .reset_index()
            .to_dict(orient="records")
        )

        return {
            "kpi_summary": kpi_summary,
            "daily_metrics": daily_metrics,
            "top_creatives": top_creatives,
            "worst_creatives": worst_creatives,
            "creative_fatigue_signals": fatigue,
            "audience_performance": audience_perf,
            "country_performance": country_perf,
            "platform_performance": platform_perf
        }
