import json
from src.agents.evaluator_agent import EvaluatorAgent


class EvalLLM:
    def generate(self, prompt):
        return json.dumps({
            "evaluated_hypotheses": [
                {
                    "issue": "creative fatigue",
                    "hypothesis": "Fatigue due to high impressions",
                    "quantitative_support": "ROAS down 20%",
                    "strength_score": 0.7,
                    "confidence": 0.85
                }
            ],
            "meta": {"agent": "EvaluatorAgent"}
        })


def test_evaluator_agent_validates_hypotheses():
    llm = EvalLLM()

    hypotheses = {
        "hypotheses": [
            {"issue": "creative fatigue", "hypothesis": "High impressions reducing ROAS"}
        ]
    }

    metrics = {
        "kpi_summary": {"overall_roas": 5.82}
    }

    agent = EvaluatorAgent(llm)
    result = agent.run(hypotheses, metrics, "Evaluate hypotheses")

    assert "evaluated_hypotheses" in result
    h = result["evaluated_hypotheses"][0]
    assert h["strength_score"] == 0.7
    assert h["confidence"] == 0.85
