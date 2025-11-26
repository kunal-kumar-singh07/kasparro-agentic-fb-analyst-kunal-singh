from utils.logging_utils import log_event

class PlannerAgent:
    def plan(self, user_query: str):
        plan_dict = {
            "original_query": user_query,
            "steps": [
                {
                    "id": 1,
                    "step": "Load dataset",
                    "agent": "DataAgent",
                    "description": "Load CSV and structure advertising metrics."
                },
                {
                    "id": 2,
                    "step": "Compute metrics",
                    "agent": "DataAgent",
                    "description": "Compute ROAS, CTR, CPC, CPM, creative performance."
                },
                {
                    "id": 3,
                    "step": "Generate insights",
                    "agent": "InsightAgent",
                    "description": "Analyze patterns, anomalies, and key performance movements."
                },
                {
                    "id": 4,
                    "step": "Generate hypotheses",
                    "agent": "HypothesisAgent",
                    "description": "Convert insights into testable marketing hypotheses."
                },
                {
                    "id": 5,
                    "step": "Evaluate hypotheses",
                    "agent": "EvaluatorAgent",
                    "description": "Quantitatively validate each hypothesis using metrics data."
                },
                {
                    "id": 6,
                    "step": "Improve creatives",
                    "agent": "CreativeImprovementAgent",
                    "description": "Generate better hooks, angles, messaging for underperforming creatives."
                },
                {
                    "id": 7,
                    "step": "Generate final report",
                    "agent": "ReportAgent",
                    "description": "Synthesize conclusions into a final markdown report."
                }
            ]
        }

        log_event("PlannerAgent", "plan_generated", {"query": user_query})
        return plan_dict
