import pytest
from src.agents.insight_agent import InsightAgent


def test_insight_agent_generates_json(fake_llm):
    agent = InsightAgent(llm=fake_llm)
    metrics = {"kpi_summary": {"overall_roas": 5.8}}

    result = agent.run(metrics, "Analyze ROAS drop")

    assert isinstance(result, dict)
    assert "insights" in result
    assert isinstance(result["insights"], list)
    assert len(result["insights"]) > 0


def test_insight_agent_retry_json_failure(fake_llm_fail_once):
    agent = InsightAgent(llm=fake_llm_fail_once)
    metrics = {"kpi_summary": {"overall_roas": 5.8}}

    result = agent.run(metrics, "Analyze ROAS drop", max_attempts=2)

    assert isinstance(result, dict)
    assert "insights" in result
    assert len(result["insights"]) > 0


def test_insight_agent_fallback(fake_llm_always_fail):
    agent = InsightAgent(llm=fake_llm_always_fail)
    metrics = {"kpi_summary": {"overall_roas": 5.8}}

    result = agent.run(metrics, "Analyze ROAS drop", max_attempts=2)

    assert "error" in result.get("meta", {}) or "insights" in result or "summary_text" in result
