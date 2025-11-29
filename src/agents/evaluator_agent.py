import json
import os
from agents.base_agent import BaseAgent
from config.config_loader import RESULTS_DIR

class EvaluatorAgent(BaseAgent):
    def __init__(self, llm, save_path=None):
        save_path = save_path or os.path.join(RESULTS_DIR, "evaluated_hypotheses.json")
        super().__init__(llm=llm, save_path=save_path)

    # build prompt
    def _build_prompt(self, hypotheses: dict, metrics: dict, query: str) -> str:
        schema = {
            "evaluated_hypotheses": [
                {
                    "issue": "string",
                    "hypothesis": "string",
                    "quantitative_support": "string",
                    "strength_score": 0.0,
                    "confidence": 0.0
                }
            ],
            "meta": {"agent": "EvaluatorAgent"}
        }

        return f"""
You are EvaluatorAgent. Evaluate hypotheses using FB Ads metrics.
Return ONLY valid JSON.

User Question:
{query}

Schema:
{json.dumps(schema, indent=2)}

Metrics:
{json.dumps(metrics, indent=2)}

Hypotheses:
{json.dumps(hypotheses, indent=2)}
"""

    # postprocess
    def _postprocess(self, parsed: dict) -> dict:
        parsed.setdefault("meta", {})
        parsed["meta"]["agent"] = "EvaluatorAgent"
        return parsed
