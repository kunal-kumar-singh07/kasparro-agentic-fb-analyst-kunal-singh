import sys
import os
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_loader import RESULTS_DIR
from agents.Planner_agent import PlannerAgent
from agents.data_agent import DataAgent
from agents.insight_agent import InsightAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.validator_agent import ValidatorAgent
from agents.creative_agent import CreativeImprovementAgent
from agents.report_agent import ReportAgent
from utils.gemini_client import GeminiClient


def get_user_query():
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    q = "Analyze ROAS drop and creative fatigue"
    print(f"[INFO] No CLI input detected. Using default: '{q}'")
    return q


def main():
    llm = GeminiClient()
    user_query = get_user_query()


    print(" Running Agentic Facebook Ads Analytics System")

    print("User Query:", user_query)


    planner = PlannerAgent()
    plan = planner.plan(user_query)

    print("Planned Steps:")
    for step in plan["steps"]:
        print(" -", step)
    print("\n")

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

    progress.set_description(stages[0])
    data_agent = DataAgent()
    data_agent.load_data()
    metrics = data_agent.compute_metrics()
    progress.update(1)

    progress.set_description(stages[1])
    insights = InsightAgent(llm).run(metrics)
    progress.update(1)

    progress.set_description(stages[2])
    hypotheses = HypothesisAgent(llm).run(insights)
    progress.update(1)

    progress.set_description(stages[3])
    evaluated = EvaluatorAgent(llm).run(hypotheses, metrics)
    progress.update(1)

    progress.set_description(stages[4])
    validated = ValidatorAgent(llm).run(hypotheses)
    progress.update(1)

    progress.set_description(stages[5])
    creative = CreativeImprovementAgent(llm).run(metrics, insights)
    progress.update(1)

    progress.set_description(stages[6])
    report_markdown = ReportAgent(llm).run(
        metrics,
        insights,
        hypotheses,
        validated
    )
    progress.update(1)

    progress.close()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    output_report = os.path.join(RESULTS_DIR, "final_report.md")

    with open(output_report, "w", encoding="utf-8") as f:
        f.write(report_markdown)

    print("\n")
    print(" FINAL REPORT GENERATED SUCCESSFULLY")
    print(" Saved at:", output_report)



if __name__ == "__main__":
    main()
