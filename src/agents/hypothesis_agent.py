import json
import os
from src.agents.base_agent import BaseAgent
from config.config_loader import RESULTS_DIR

class HypothesisAgent(BaseAgent):
    def __init__(self, llm, save_path=None):
        save_path = save_path or os.path.join(RESULTS_DIR, "hypotheses.json")
        super().__init__(llm=llm, save_path=save_path)

    # build prompt
    def _build_prompt(self, insights: dict, query: str) -> str:
        schema = {
            "hypotheses": [
                {
                    "issue": "string",
                    "hypothesis": "string",
                    "supporting_signals": ["list of signals"],
                    "confidence": 0.0
                }
            ],
            "meta": {"agent": "HypothesisAgent"}
        }

        return f"""
You are HypothesisAgent. Convert insights into hypotheses.
Return ONLY JSON.

User Question:
{query}

Schema:
{json.dumps(schema, indent=2)}

Insights:
{json.dumps(insights, indent=2, ensure_ascii=False)}
"""

    # postprocess
    def _postprocess(self, parsed: dict) -> dict:
        parsed.setdefault("meta", {})
        parsed["meta"]["agent"] = "HypothesisAgent"
        return parsed
