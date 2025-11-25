import json
import os
from tqdm import tqdm

from agents.data_agent import DataAgent
from agents.insight_agent import InsightAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.validator_agent import ValidatorAgent
from agents.report_agent import ReportAgent
from utils.gemini_client import GeminiClient

llm = GeminiClient()

stages = [
    "Loading & computing metrics",
    "Generating insights",
    "Generating hypotheses",
    "Validating hypotheses",
    "Generating final report"
]

progress = tqdm(total=len(stages), desc="Pipeline Progress", ncols=100)


# 1) DATA
progress.set_description(stages[0])
data = DataAgent()
data.load_data()
metrics = data.compute_metrics()
progress.update(1)


# 2) INSIGHT AGENT
progress.set_description(stages[1])
insight_agent = InsightAgent(llm)
insights = insight_agent.run(metrics)
progress.update(1)


# 3) HYPOTHESIS AGENT
progress.set_description(stages[2])
hyp_agent = HypothesisAgent(llm)
hypotheses = hyp_agent.run(insights)
progress.update(1)


# 4) VALIDATOR AGENT
progress.set_description(stages[3])
validator = ValidatorAgent(llm)
validations = validator.run(hypotheses)
progress.update(1)


# 5) REPORT AGENT
progress.set_description(stages[4])
report_agent = ReportAgent(llm)
markdown = report_agent.run(metrics, insights, hypotheses, validations)
progress.update(1)

progress.close()


# SAVE OUTPUT
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "final_report.md")
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(markdown)

print("\nFINAL REPORT GENERATED AND SAVED TO:")
print(OUTPUT_PATH)
