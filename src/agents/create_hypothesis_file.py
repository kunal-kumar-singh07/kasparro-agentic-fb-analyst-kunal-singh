import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.gemini_client import GeminiClient
from agents.hypothesis_agent import HypothesisAgent
from agents.data_agent import DataAgent
from agents.insight_agent import InsightAgent
import json

llm = GeminiClient()

data = DataAgent()
data.load_data()
metrics = data.compute_metrics()

insight_agent = InsightAgent(llm)
insights = insight_agent.run(metrics)

h_agent = HypothesisAgent(llm)
hypotheses = h_agent.run(insights)

with open("hypotheses.json", "w") as f:
    json.dump(hypotheses, f, indent=2)

print("hypotheses.json created!")
