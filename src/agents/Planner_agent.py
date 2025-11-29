from utils.logging_utils import log_event

class PlannerAgent:
    def __init__(self):
        self.agent_name = "PlannerAgent"

    # plan
    def plan(self, user_query: str):
        plan = [
            {
                "id": 1,
                "step": "load dataset",
                "agent": "DataAgent",
                "description": "Load CSV and normalize schema."
            },
            {
                "id": 2,
                "step": "compute metrics",
                "agent": "DataAgent",
                "description": "Compute CTR, ROAS, CPC, CPM, fatigue scores."
            },
            {
                "id": 3,
                "step": "insights",
                "agent": "InsightAgent",
                "description": "Generate insights using computed metrics."
            },
            {
                "id": 4,
                "step": "hypotheses",
                "agent": "HypothesisAgent",
                "description": "Convert insights into hypotheses."
            },
            {
                "id": 5,
                "step": "evaluate",
                "agent": "EvaluatorAgent",
                "description": "Quantitatively evaluate hypotheses."
            },
            {
                "id": 6,
                "step": "validate",
                "agent": "ValidatorAgent",
                "description": "Validate and refine hypotheses."
            },
            {
                "id": 7,
                "step": "creative improvements",
                "agent": "CreativeImprovementAgent",
                "description": "Improve weak creatives."
            },
            {
                "id": 8,
                "step": "final report",
                "agent": "ReportAgent",
                "description": "Generate the final markdown report."
            }
        ]

        log_event(self.agent_name, "plan_generated", {"query": user_query})
        return {"original_query": user_query, "steps": plan}
