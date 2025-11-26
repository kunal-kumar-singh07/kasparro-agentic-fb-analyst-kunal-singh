import sys
import os
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.Planner_agent import PlannerAgent
from agents.data_agent import DataAgent
from agents.insight_agent import InsightAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.validator_agent import ValidatorAgent
from agents.creative_agent import CreativeImprovementAgent
from agents.report_agent import ReportAgent
from utils.gemini_client import GeminiClient
from config.config_loader import RESULTS_DIR


def get_user_query():
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()

    default_query = "Analyze ROAS drop and creative fatigue"
    print(f"[INFO] No CLI input detected. Using default: '{default_query}'")
    return default_query


def main():


        llm = GeminiClient()
        user_query = get_user_query()

        print("Running Agentic Facebook Ads Analytics System")
        print("User Query:", user_query)


        planner = PlannerAgent()
        plan = planner.plan(user_query)

        print("\nPlanned Steps:")
        for step in plan["steps"]:
            print(" -", step)

        stages = [
            "Loading & Computing Metrics",
            "Generating Insights",
            "Generating Hypotheses",
            "Evaluator Loop",
            "Validator Agent",
            "Creative Agent",
            "Final Report"
        ]

        progress = tqdm(total=len(stages), desc="Pipeline Progress", ncols=100)


        progress.set_description(stages[0])
        data_agent = DataAgent()
        data_agent.load_data()
        metrics = data_agent.compute_metrics()
        progress.update(1)


        progress.set_description(stages[1])
        insight_agent = InsightAgent(llm)
        insights = insight_agent.run(metrics, user_query)
        progress.update(1)


        progress.set_description(stages[2])
        hypothesis_agent = HypothesisAgent(llm)
        hypotheses = hypothesis_agent.run(insights, user_query)
        progress.update(1)


        progress.set_description(stages[3])
        evaluator = EvaluatorAgent(llm)

        max_iterations = 2
        iteration = 0

        evaluated = evaluator.run(hypotheses, metrics, user_query)

        while iteration < max_iterations:
            weak = [
                h for h in evaluated["evaluated_hypotheses"]
                if h.get("strength_score", 1) < 0.4
            ]

            if not weak:
                break

            hypotheses = hypothesis_agent.run(insights, user_query)
            evaluated = evaluator.run(hypotheses, metrics, user_query)
            iteration += 1

        progress.update(1)


        progress.set_description(stages[4])
        validator_agent = ValidatorAgent(llm)
        validated = validator_agent.run(hypotheses, user_query)
        progress.update(1)


        progress.set_description(stages[5])
        creative_agent = CreativeImprovementAgent(llm)
        creative_recs = creative_agent.run(metrics, insights, user_query)
        progress.update(1)


        progress.set_description(stages[6])
        report_agent = ReportAgent(llm)

        markdown_report = report_agent.run(
            metrics,
            insights,
            hypotheses,      # FIXED
            evaluated,       # FIXED
            creative_recs,   # FIXED
            user_query
        )

        progress.update(1)
        progress.close()

        # Save final markdown
        output_report = os.path.join(RESULTS_DIR, "final_report.md")
        with open(output_report, "w", encoding="utf-8") as f:
            f.write(markdown_report)

        print("\nFINAL REPORT GENERATED")
        print("Saved at:", output_report)


if __name__ == "__main__":
    main()
