import pytest
from src.agents.evaluator_agent import EvaluatorAgent
from src.tests.fake_llm import EvalLLM


def test_evaluator_scores_hypotheses_correctly():
    llm = EvalLLM()
    agent = EvaluatorAgent(llm=llm)

    hypotheses = {
        "hypotheses": [
            {"issue": "creative fatigue", "hypothesis": "High impressions lowering ROAS"}
        ]
    }

    metrics = {
        "kpi_summary": {"overall_roas": 2.1}
    }

    result = agent.run(hypotheses, metrics, "Evaluate")

    assert "evaluated_hypotheses" in result
    assert isinstance(result["evaluated_hypotheses"], list)
    assert result["evaluated_hypotheses"][0]["issue"] == "creative fatigue"


def test_evaluator_handles_missing_metrics():
    llm = EvalLLM()
    agent = EvaluatorAgent(llm=llm)

    hypotheses = {"hypotheses": [{"issue": "x", "hypothesis": "y"}]}

    result = agent.run(hypotheses, {}, "Evaluate")

    assert "evaluated_hypotheses" in result
