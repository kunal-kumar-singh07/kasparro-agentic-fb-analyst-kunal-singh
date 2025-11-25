import os
import sys
import json

sys.path.append(os.path.dirname(__file__))

from utils.gemini_client import GeminiClient
from agents.report_agent import ReportAgent

BASE = os.path.dirname(__file__)

metrics = json.load(open(os.path.join(BASE, "agents", "metrics_cache.json")))
insights = json.load(open(os.path.join(BASE, "agents", "insights.json")))
hypotheses = json.load(open(os.path.join(BASE, "agents", "hypotheses.json")))
validations = json.load(open(os.path.join(BASE, "agents", "validated_hypotheses.json")))

llm = GeminiClient()
agent = ReportAgent(llm)

report = agent.run(metrics, insights, hypotheses, validations)

output_path = os.path.join(BASE, "report.md")
with open(output_path, "w") as f:
    f.write(report)

print("Report saved at:", output_path)
