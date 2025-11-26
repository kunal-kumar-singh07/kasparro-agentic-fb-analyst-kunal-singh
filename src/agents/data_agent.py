import pandas as pd
import os
from config.config_loader import DATA_CSV_PATH, RESULTS_DIR
from utils.logging_utils import log_event


class DataAgent:
    REQUIRED_COLUMNS = [
        "date", "impressions", "clicks", "spend", "revenue", "creative_message"
    ]

    def __init__(self, csv_path=None):
        self.csv_path = csv_path or DATA_CSV_PATH
        self.df = None

    def load_data(self):
        log_event("DataAgent", "start", {
            "message": "loading dataset",
            "path": self.csv_path
        })

        if not os.path.exists(self.csv_path):
            log_event("DataAgent", "error", {
                "error": "CSV file not found",
                "path": self.csv_path
            })
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        try:
            df = pd.read_csv(self.csv_path)

            # Normalize column names
            df.columns = df.columns.str.lower().str.strip()

            # Validate required columns
            missing = [c for c in self.REQUIRED_COLUMNS if c not in df.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")

            self.df = df

            log_event("DataAgent", "success", {
                "message": "dataset loaded",
                "rows": len(self.df),
                "columns": list(self.df.columns)
            })

        except Exception as e:
            log_event("DataAgent", "error", {"error": str(e)})
            raise e

    def compute_metrics(self):
        log_event("DataAgent", "start", {"message": "computing metrics"})

        try:
            df = self.df.copy()

            # SAFE numeric handling
            df["impressions"] = pd.to_numeric(df["impressions"], errors="coerce").fillna(0)
            df["clicks"] = pd.to_numeric(df["clicks"], errors="coerce").fillna(0)
            df["spend"] = pd.to_numeric(df["spend"], errors="coerce").fillna(0)
            df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)

            # CTR (click-through rate)
            df["ctr"] = (df["clicks"] / df["impressions"].replace(0, pd.NA))
            df["ctr"] = pd.to_numeric(df["ctr"], errors="coerce").fillna(0)

            # ROAS (Return On Ad Spend)
            df["roas"] = df["revenue"] / df["spend"].replace(0, pd.NA)
            df["roas"] = pd.to_numeric(df["roas"], errors="coerce").fillna(0)

            # CPC (Cost Per Click)
            df["cpc"] = df["spend"] / df["clicks"].replace(0, pd.NA)
            df["cpc"] = pd.to_numeric(df["cpc"], errors="coerce").fillna(0)

            # CPM (Cost Per 1000 impressions)
            df["cpm"] = (df["spend"] / df["impressions"].replace(0, pd.NA)) * 1000
            df["cpm"] = pd.to_numeric(df["cpm"], errors="coerce").fillna(0)

            # ---------- KPI SUMMARY ----------
            total_spend = float(df["spend"].sum())
            total_revenue = float(df["revenue"].sum())

            kpi_summary = {
                "total_spend": total_spend,
                "total_revenue": total_revenue,
                "total_purchases": int(df["purchases"].sum()) if "purchases" in df.columns else 0,
                "overall_roas": float(total_revenue / total_spend) if total_spend > 0 else 0.0,
                "overall_ctr": float(df["ctr"].mean()),
                "overall_cpc": float(df["cpc"].mean()),
                "overall_cpm": float(df["cpm"].mean()),
            }

            # ---------- DAILY METRICS ----------
            daily = (
                df.groupby("date")
                .agg({
                    "roas": "mean",
                    "ctr": "mean",
                    "spend": "sum",
                    "revenue": "sum"
                })
                .reset_index()
                .to_dict(orient="records")
            )

            # ---------- CREATIVE PERFORMANCE ----------
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
            ).sort_values("roas", ascending=False)

            top_creatives = creative_perf.head(10).to_dict(orient="records")
            worst_creatives = creative_perf.tail(10).to_dict(orient="records")

            # ---------- CREATIVE FATIGUE ----------
            ctr_threshold = df["ctr"].quantile(0.20)  # bottom 20% CTR
            fatigue_df = creative_perf[
                (creative_perf["impressions"] > 300000) &
                (creative_perf["ctr"] <= ctr_threshold)
            ]

            creative_fatigue = fatigue_df[[
                "creative_message", "ctr", "impressions", "roas"
            ]].to_dict(orient="records")

            # ---------- OPTIONAL GROUP PERFORMANCE ----------
            def safe_group(col):
                if col not in df.columns:
                    return []
                grouped = df.groupby(col).agg({
                    "roas": "mean",
                    "ctr": "mean",
                    "cpm": "mean",
                    "cpc": "mean",
                    "spend": "sum",
                    "revenue": "sum"
                }).reset_index()
                return grouped.to_dict(orient="records")

            result = {
                "kpi_summary": kpi_summary,
                "daily_metrics": daily,
                "top_creatives": top_creatives,
                "worst_creatives": worst_creatives,
                "creative_fatigue_signals": creative_fatigue,
                "audience_performance": safe_group("audience_type"),
                "country_performance": safe_group("country"),
                "platform_performance": safe_group("platform")
            }

            log_event("DataAgent", "success", {
                "message": "metrics computed successfully",
                "summary": kpi_summary
            })

            return result

        except Exception as e:
            log_event("DataAgent", "error", {"error": str(e)})
            raise e
