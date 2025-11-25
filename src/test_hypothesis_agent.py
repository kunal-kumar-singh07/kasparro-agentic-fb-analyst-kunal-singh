import json
from utils.gemini_client import GeminiClient
from agents.hypothesis_agent import HypothesisAgent

# load insights.json (created earlier)
with open("agents/insights.json", "r") as f:
    sample_insights = json.load(f)

llm = GeminiClient()
agent = HypothesisAgent(llm)

output = agent.run(sample_insights)

print("\nHYPOTHESIS AGENT OUTPUT:\n")
print(output)
