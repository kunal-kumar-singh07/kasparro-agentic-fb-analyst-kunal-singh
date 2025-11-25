import json
import os
from tqdm import tqdm

from agents.planner_agent import PlannerAgent
from agents.data_agent import DataAgent
from agents.insight_agent import InsightAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.validator_agent import ValidatorAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.creative_agent import CreativeImprovementAgent
from agents.report_agent import ReportAgent

from utils.gemini_client import GeminiClient

RESULTS_DIR = r"E:\Kasparo\kasparro-agentic-fb-analyst-kunal-singh\results"
os.makedirs(RESULTS_DIR, exist_ok=True)

llm = GeminiClient()


# -------------------------
# 1) PLANNER AGENT
# -------------------------
planner = PlannerAgent()
plan = planner.plan("Generate full marketing analysis report")

print("\n=== PLAN ===")
for step in plan["steps"]:
    print("•", step)

print("\nStarting pipeline...\n")


# Setup progress bar
stages = [
    "Load dataset & compute metrics",
    "Generate insights",
    "Generate hypotheses",
    "Validate hypotheses",
    "Evaluate hypotheses quantitatively",
    "Generate creative improvements",
    "Generate final report"
]

progress = tqdm(total=len(stages), desc="Pipeline", ncols=100)


# -------------------------
# 2) DATA AGENT
# -------------------------
progress.set_description(stages[0])
data_agent = DataAgent()
data_agent.load_data()
metrics = data_agent.compute_metrics()
progress.update(1)


# -------------------------
# 3) INSIGHT AGENT
# -------------------------
progress.set_description(stages[1])
insight_agent = InsightAgent(llm)
insights = insight_agent.run(metrics)
progress.update(1)


# -------------------------
# 4) HYPOTHESIS AGENT
# -------------------------
progress.set_description(stages[2])
hyp_agent = HypothesisAgent(llm)
hypotheses = hyp_agent.run(insights)
progress.update(1)


# -------------------------
# 5) VALIDATOR AGENT
# -------------------------
progress.set_description(stages[3])
validator = ValidatorAgent(llm)
validations = validator.run(hypotheses)
progress.update(1)


# -------------------------
# 6) EVALUATOR AGENT (quantitative validation)
# -------------------------
progress.set_description(stages[4])
evaluator = EvaluatorAgent(llm)
evaluation = evaluator.run(hypotheses, metrics)
progress.update(1)


# -------------------------
# 7) CREATIVE IMPROVEMENT AGENT
# -------------------------
progress.set_description(stages[5])
creative_agent = CreativeImprovementAgent(llm)
creative_recos = creative_agent.run(metrics, insights)
progress.update(1)


# -------------------------
# 8) REPORT AGENT
# -------------------------
progress.set_description(stages[6])
report_agent = ReportAgent(llm)
markdown = report_agent.run(metrics, insights, hypotheses, validations)
progress.update(1)

progress.close()


# -------------------------
# SAVE FINAL REPORT
# -------------------------
report_path = os.path.join(RESULTS_DIR, "final_report.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write(markdown)

print("\nFINAL REPORT GENERATED AND SAVED TO:")
print(report_path)
