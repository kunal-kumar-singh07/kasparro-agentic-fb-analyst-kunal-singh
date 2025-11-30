import json
from src.agents.hypothesis_agent import HypothesisAgent


class HypLLM:
    def generate(self, prompt):
        return json.dumps({
            "hypotheses": [
                {
                    "issue": "creative fatigue",
                    "hypothesis": "High impressions with low CTR indicate fatigue",
                    "supporting_signals": ["ctr down", "impressions up"],
                    "confidence": 0.8
                }
            ]
        })


class HypLLMFailOnce:
    def __init__(self):
        self.failed = False

    def generate(self, prompt):
        if not self.failed:
            self.failed = True
            return "INVALID JSON"
        return json.dumps({
            "hypotheses": [
                {
                    "issue": "recovered",
                    "hypothesis": "Recovered after bad json",
                    "supporting_signals": [],
                    "confidence": 0.7
                }
            ]
        })


class HypLLMAlwaysFail:
    def generate(self, prompt):
        return "NOT JSON"


def test_hypothesis_agent_generates_json():
    agent = HypothesisAgent(llm=HypLLM())
    insights = {"insights": ["ROAS dropping", "CTR stable"]}

    result = agent.run(insights, "Why did ROAS drop?")

    assert isinstance(result, dict)
    assert "hypotheses" in result
    assert isinstance(result["hypotheses"], list)
    assert len(result["hypotheses"]) > 0


def test_hypothesis_agent_retry_on_failure():
    agent = HypothesisAgent(llm=HypLLMFailOnce())
    insights = {"insights": ["ROAS dropping"]}

    result = agent.run(insights, "Why did ROAS drop?", max_attempts=2)

    assert isinstance(result, dict)
    assert "hypotheses" in result
    assert len(result["hypotheses"]) > 0


def test_hypothesis_agent_fallback():
    agent = HypothesisAgent(llm=HypLLMAlwaysFail())
    insights = {"insights": ["ROAS dropping"]}

    result = agent.run(insights, "Why did ROAS drop?", max_attempts=2)

    assert "error" in result.get("meta", {}) or result.get("hypotheses") == []
