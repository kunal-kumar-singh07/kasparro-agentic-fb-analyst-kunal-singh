import json
import os
from agents.base_agent import BaseAgent
from config.config_loader import RESULTS_DIR

class InsightAgent(BaseAgent):
    def __init__(self, llm, save_path=None, dataset_path=None):
        save_path = save_path or os.path.join(RESULTS_DIR, "insights.json")
        super().__init__(llm=llm, save_path=save_path)
        self.dataset_path = dataset_path

    # build prompt
    def _build_prompt(self, metrics: dict, query: str) -> str:
        schema = {
            "summary_text": "short summary",
            "insights": [
                {
                    "title": "string",
                    "description": "string",
                    "evidence": {
                        "kpi_changes": [],
                        "creative_issues": [],
                        "audience_issues": []
                    },
                    "severity": "Low|Medium|High",
                    "confidence": 0.0
                }
            ],
            "meta": {"agent": "InsightAgent"}
        }

        try:
            metrics_block = json.dumps(metrics, indent=2, ensure_ascii=False)
        except:
            metrics_block = json.dumps(
                {k: "<unserializable>" for k in metrics.keys()},
                indent=2
            )

        return f"""
You are InsightAgent. You analyze FB Ads metrics and generate insights.
Return ONLY JSON matching the schema.

User Question:
{query}

Schema:
{json.dumps(schema, indent=2)}

Metrics:
{metrics_block}
"""

    # postprocess
    def _postprocess(self, parsed: dict) -> dict:
        parsed.setdefault("meta", {})
        parsed["meta"]["agent"] = "InsightAgent"
        return parsed
