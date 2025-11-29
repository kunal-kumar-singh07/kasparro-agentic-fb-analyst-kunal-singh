import json
import os
from agents.base_agent import BaseAgent
from config.config_loader import RESULTS_DIR

class ValidatorAgent(BaseAgent):
    def __init__(self, llm, save_path=None):
        save_path = save_path or os.path.join(RESULTS_DIR, "validated_hypotheses.json")
        super().__init__(llm=llm, save_path=save_path)

    # build prompt
    def _build_prompt(self, hypotheses: dict, query: str) -> str:
        schema = {
            "validated_hypotheses": [
                {
                    "issue": "string",
                    "hypothesis": "string",
                    "status": "validated | rejected | partial",
                    "strengthened_reasoning": "string",
                    "confidence": 0.0
                }
            ],
            "meta": {"agent": "ValidatorAgent"}
        }

        return f"""
You are ValidatorAgent. Validate and critique each hypothesis.
Return ONLY JSON.

User Question:
{query}

Schema:
{json.dumps(schema, indent=2)}

Hypotheses:
{json.dumps(hypotheses, indent=2)}
"""

    # postprocess
    def _postprocess(self, parsed: dict) -> dict:
        parsed.setdefault("meta", {})
        parsed["meta"]["agent"] = "ValidatorAgent"
        return parsed
