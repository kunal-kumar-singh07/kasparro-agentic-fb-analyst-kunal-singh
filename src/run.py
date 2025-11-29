import os
import sys
import uuid
import time
from tqdm import tqdm

# Fix import paths for your folder structure
CURRENT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT)
sys.path.append(PROJECT_ROOT)
sys.path.append(CURRENT)

from agents.Planner_agent import PlannerAgent
from agents.data_agent import DataAgent
from agents.insight_agent import InsightAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.validator_agent import ValidatorAgent
from agents.creative_agent import CreativeImprovementAgent
from agents.report_agent import ReportAgent

from utils.metrics import MetricsTracker
from utils.logging_utils import log_event
from utils.gemini_client import GeminiClient


def get_user_query():
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    return "Analyze ROAS drop and creative fatigue"


def run_pipeline(user_query):
    run_id = uuid.uuid4().hex[:10]

    log_event("Pipeline", "start", {"run_id": run_id, "query": user_query})
    print("Running pipeline...")
    print("Query:", user_query)
    print()

    metrics_tracker = MetricsTracker(run_id)

    llm = GeminiClient()

    stages = [
        "computing metrics",
        "insights",
        "hypotheses",
        "evaluation",
        "validation",
        "creative",
        "final report"
    ]

    with tqdm(total=len(stages), desc="pipeline", ncols=100) as bar:

        # Planner
        planner = PlannerAgent()
        plan = planner.plan(user_query)
        log_event("Pipeline", "planner_done", {"steps": len(plan["steps"])})

        # Data Agent
        print("Loading dataset...")
        data_agent = DataAgent()
        data_agent.load_data()

        bar.set_description(stages[0])
        print("Computing metrics...")
        metrics = data_agent.compute_metrics()
        metrics_tracker.inc("rows_processed", len(data_agent.df))
        metrics_tracker.mark("metrics_ready")
        bar.update(1)

        # Insight Agent
        bar.set_description(stages[1])
        print("Generating insights...")
        insight_agent = InsightAgent(llm)
        insights = insight_agent.run(metrics, user_query)
        metrics_tracker.mark("insights_ready")
        bar.update(1)

        # Hypothesis Agent
        bar.set_description(stages[2])
        print("Generating hypotheses...")
        hypothesis_agent = HypothesisAgent(llm)
        hypotheses = hypothesis_agent.run(insights, user_query)
        metrics_tracker.mark("hypotheses_ready")
        bar.update(1)

        # Evaluator Agent
        bar.set_description(stages[3])
        print("Evaluating hypotheses...")
        evaluator_agent = EvaluatorAgent(llm)
        evaluated = evaluator_agent.run(hypotheses, metrics, user_query)
        metrics_tracker.mark("evaluation_ready")
        bar.update(1)

        # Validator Agent
        bar.set_description(stages[4])
        print("Validating hypotheses...")
        validator_agent = ValidatorAgent(llm)
        validated = validator_agent.run(hypotheses, user_query)
        metrics_tracker.mark("validated_ready")
        bar.update(1)

        # Creative Agent
        bar.set_description(stages[5])
        print("Generating creative recommendations...")
        creative_agent = CreativeImprovementAgent(llm)
        creatives = creative_agent.run(metrics, insights, user_query)
        metrics_tracker.mark("creatives_ready")
        bar.update(1)

        # Report Agent
        bar.set_description(stages[6])
        print("Generating final report...")
        report_agent = ReportAgent(llm)
        report_resp = report_agent.run(
            metrics,
            insights,
            hypotheses,
            evaluated,
            creatives,
            user_query
        )
        metrics_tracker.mark("report_ready")
        bar.update(1)

    # Save pipeline metrics
    pipeline_metrics = metrics_tracker.save()
    log_event("Pipeline", "complete", {
        "run_id": run_id,
        "total_time": pipeline_metrics["times"]["total_runtime"]
    })

    print("\nPipeline completed.")
    return report_resp


if __name__ == "__main__":
    query = get_user_query()
    run_pipeline(query)
