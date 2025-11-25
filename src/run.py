import sys
import os
import json
from tqdm import tqdm

from agents.Planner_agent import PlannerAgent
from agents.data_agent import DataAgent
from agents.insight_agent import InsightAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.validator_agent import ValidatorAgent
from agents.creative_agent import CreativeImprovementAgent
from agents.report_agent import ReportAgent
from utils.gemini_client import GeminiClient

RESULTS_DIR = r"E:\Kasparo\kasparro-agentic-fb-analyst-kunal-singh\results"
os.makedirs(RESULTS_DIR, exist_ok=True)


# -------------------------------------------------------
# HANDLE USER QUERY (CLI + fallback)
# -------------------------------------------------------
def get_user_query():
    """
    Robust query handler:
    - Supports CLI input: python run.py "Analyze ROAS drop"
    - If missing, uses a default query
    """
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()

    default_query = "Analyze ROAS drop and creative fatigue"
    print(f"[INFO] No CLI input detected. Using default: '{default_query}'")
    return default_query


# -------------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------------
def main():

    # Master LLM client
    llm = GeminiClient()

    # 1) Get Query
    user_query = get_user_query()

    print("\n====================================================")
    print(" Running Agentic Facebook Ads Analytics System")
    print("====================================================")
    print("User Query:", user_query)
    print("----------------------------------------------------\n")

    # 2) Planner Agent (defines workflow)
    planner = PlannerAgent()
    plan = planner.plan(user_query)

    print("Planned Steps:")
    for step in plan["steps"]:
        print(" -", step)
    print("\n----------------------------------------------------\n")

    # Progress bar for major phases
    stages = [
        "Loading & Computing Metrics",
        "Generating Insights",
        "Generating Hypotheses",
        "Evaluator Agent (Quantitative Check)",
        "Validator Agent (Reasoning Check)",
        "Creative Improvement Agent",
        "Generating Final Report"
    ]
    progress = tqdm(total=len(stages), desc="Pipeline Progress", ncols=100)

    # -------------------------------------------------------
    # STEP 1: Data Agent
    # -------------------------------------------------------
    progress.set_description(stages[0])
    data_agent = DataAgent()
    data_agent.load_data()
    metrics = data_agent.compute_metrics()
    progress.update(1)

    # -------------------------------------------------------
    # STEP 2: Insight Agent
    # -------------------------------------------------------
    progress.set_description(stages[1])
    insight_agent = InsightAgent(llm)
    insights = insight_agent.run(metrics)
    progress.update(1)

    # -------------------------------------------------------
    # STEP 3: Hypothesis Agent
    # -------------------------------------------------------
    progress.set_description(stages[2])
    hypothesis_agent = HypothesisAgent(llm)
    hypotheses = hypothesis_agent.run(insights)
    progress.update(1)

    # -------------------------------------------------------
    # STEP 4: Evaluator Agent (quantitative validation)
    # -------------------------------------------------------
    progress.set_description(stages[3])
    evaluator_agent = EvaluatorAgent(llm)
    evaluated = evaluator_agent.run(hypotheses, metrics)
    progress.update(1)

    # -------------------------------------------------------
    # STEP 5: Validator Agent (reasoning)
    # -------------------------------------------------------
    progress.set_description(stages[4])
    validator_agent = ValidatorAgent(llm)
    validated = validator_agent.run(hypotheses)
    progress.update(1)

    # -------------------------------------------------------
    # STEP 6: Creative Improvement Agent
    # -------------------------------------------------------
    progress.set_description(stages[5])
    creative_agent = CreativeImprovementAgent(llm)
    creative_recs = creative_agent.run(metrics, insights)
    progress.update(1)

    # -------------------------------------------------------
    # STEP 7: Report Agent
    # -------------------------------------------------------
    progress.set_description(stages[6])
    report_agent = ReportAgent(llm)
    markdown_report = report_agent.run(
        metrics,
        insights,
        hypotheses,
        validated
    )
    progress.update(1)

    progress.close()

    # -------------------------------------------------------
    # SAVE FINAL REPORT
    # -------------------------------------------------------
    output_report = os.path.join(RESULTS_DIR, "final_report.md")
    with open(output_report, "w", encoding="utf-8") as f:
        f.write(markdown_report)

    print("\n====================================================")
    print(" FINAL REPORT GENERATED SUCCESSFULLY")
    print(" Saved at:", output_report)
    print("====================================================\n")


# -------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------
if __name__ == "__main__":
    main()
