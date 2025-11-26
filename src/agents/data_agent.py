import pandas as pd
import os
from config.config_loader import DATA_CSV_PATH
from utils.logging_utils import log_event


class DataAgent:
    def __init__(self, csv_path=None):
        self.csv_path = csv_path or DATA_CSV_PATH
        self.df = None

    def load_data(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError("CSV file not found: " + self.csv_path)
        self.df = pd.read_csv(self.csv_path)

    def compute_metrics(self):
        df = self.df.copy()
        df['impressions'] = df['impressions'].replace(0, 1)
        df['clicks'] = df['clicks'].replace(0, 0)
        df['ctr'] = df['clicks'] / df['impressions']
        df['roas'] = df['revenue'] / df['spend'].replace(0, 1)
        df['cpc'] = df['spend'] / df['clicks'].replace(0, 1)
        df['cpm'] = (df['spend'] / df['impressions']) * 1000

        kpi_summary = {
            "total_spend": float(df["spend"].sum()),
            "total_revenue": float(df["revenue"].sum()),
            "total_purchases": int(df["purchases"].sum()) if "purchases" in df.columns else int(df.shape[0]),
            "overall_roas": float(df["revenue"].sum() / df["spend"].sum()) if df["spend"].sum() else 0.0,
            "overall_ctr": float(df["ctr"].mean()),
            "overall_cpc": float(df["cpc"].mean()),
            "overall_cpm": float(df["cpm"].mean()),
        }

        daily = df.groupby("date").agg({
            "roas": "mean",
            "ctr": "mean",
            "spend": "sum",
            "revenue": "sum"
        }).reset_index().to_dict(orient="records")

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
            .reset_index()
            .sort_values("roas", ascending=False)
        )

        top_creatives = creative_perf.head(10).to_dict(orient='records')
        worst_creatives = creative_perf.tail(10).to_dict(orient='records')

        fatigue = []
        for _, row in creative_perf.iterrows():
            try:
                if row.get("impressions", 0) > 300000 and row.get("ctr", 1) < 0.012:
                    fatigue.append({
                        "creative_message": row["creative_message"],
                        "ctr": float(row["ctr"]),
                        "impressions": int(row["impressions"]),
                        "roas": float(row["roas"])
                    })
            except Exception:
                continue

        audience_perf = df.groupby("audience_type").agg({
            "roas":"mean","ctr":"mean","cpm":"mean","cpc":"mean","spend":"sum","revenue":"sum"
        }).reset_index().to_dict(orient='records') if "audience_type" in df.columns else []

        country_perf = df.groupby("country").agg({
            "roas":"mean","ctr":"mean","cpm":"mean","spend":"sum","revenue":"sum"
        }).reset_index().to_dict(orient='records') if "country" in df.columns else []

        platform_perf = df.groupby("platform").agg({
            "roas":"mean","ctr":"mean","cpm":"mean","spend":"sum","revenue":"sum"
        }).reset_index().to_dict(orient='records') if "platform" in df.columns else []

        return {
            "kpi_summary": kpi_summary,
            "daily_metrics": daily,
            "top_creatives": top_creatives,
            "worst_creatives": worst_creatives,
            "creative_fatigue_signals": fatigue,
            "audience_performance": audience_perf,
            "country_performance": country_perf,
            "platform_performance": platform_perf
        }
