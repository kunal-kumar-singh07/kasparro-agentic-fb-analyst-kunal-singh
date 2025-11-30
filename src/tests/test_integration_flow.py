from src.agents.insight_agent import InsightAgent
from src.agents.hypothesis_agent import HypothesisAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.tests.fake_llm import FakeLLM


def test_full_integration_flow():
    metrics = {"kpi_summary": {"overall_roas": 3.5, "cpa": 12}}

    insight_agent = InsightAgent(llm=FakeLLM())
    insights = insight_agent.run(metrics)

    assert "insights" in insights

    hypothesis_agent = HypothesisAgent(llm=FakeLLM())
    hypotheses = hypothesis_agent.run(insights, "Generate hypotheses")

    assert "hypotheses" in hypotheses

    evaluator = EvaluatorAgent(llm=FakeLLM())
    evaluation = evaluator.run(hypotheses, metrics, "Evaluate")

    assert "evaluated_hypotheses" in evaluation
    assert isinstance(evaluation["evaluated_hypotheses"], list)
