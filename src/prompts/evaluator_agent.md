def _build_prompt(self, hypotheses: dict, metrics: dict) -> str:
    schema = {
        "evaluated_hypotheses":[
            {
                "issue":"string",
                "hypothesis":"string",
                "quantitative_support":"string",
                "strength_score":0.0,
                "confidence":0.0
            }
        ],
        "meta":{"agent":"EvaluatorAgent"}
    }

    return f"""You are the Evaluator Agent.

Return ONLY one valid JSON object.
Use this schema:
{json.dumps(schema, indent=2)}

METRICS:
{json.dumps(metrics, indent=2, ensure_ascii=False)}

HYPOTHESES:
{json.dumps(hypotheses, indent=2, ensure_ascii=False)}

Return ONLY JSON.
"""
