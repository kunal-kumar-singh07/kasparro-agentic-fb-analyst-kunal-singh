import json
import os
from src.agents.base_agent import BaseAgent
from config.config_loader import RESULTS_DIR

class CreativeImprovementAgent(BaseAgent):
    def __init__(self, llm, save_path=None):
        save_path = save_path or os.path.join(RESULTS_DIR, "creative_recommendations.json")
        super().__init__(llm=llm, save_path=save_path)

    # build prompt
    def _build_prompt(self, metrics: dict, insights: dict, query: str) -> str:
        schema = {
            "creative_recommendations": [
                {
                    "issue": "string",
                    "old_message": "string",
                    "new_creative": "string",
                    "reasoning": "string",
                    "expected_ctr_lift": "string"
                }
            ],
            "meta": {"agent": "CreativeImprovementAgent"}
        }

        return f"""
You are CreativeImprovementAgent. Improve weak creatives using metrics and insights.
Return ONLY JSON.

User Question:
{query}

Schema:
{json.dumps(schema, indent=2)}

Metrics:
{json.dumps(metrics, indent=2)}

Insights:
{json.dumps(insights, indent=2)}
"""

    # postprocess
    def _postprocess(self, parsed: dict) -> dict:
        parsed.setdefault("meta", {})
        parsed["meta"]["agent"] = "CreativeImprovementAgent"
        return parsed
