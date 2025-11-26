from utils.logging_utils import log_event

class PlannerAgent:
    def plan(self, user_query: str):
        plan_dict = {
            "original_query": user_query,
            "steps": [
                {"step":"Load dataset","agent":"DataAgent","description":"Load CSV and structure advertising metrics."},
                {"step":"Compute metrics","agent":"DataAgent","description":"Compute ROAS, CTR, CPC, CPM, creative performance."},
                {"step":"Generate insights","agent":"InsightAgent","description":"Analyze patterns and anomalies in performance data."},
                {"step":"Generate hypotheses","agent":"HypothesisAgent","description":"Transform insights into testable marketing hypotheses."},
                {"step":"Validate hypotheses","agent":"ValidatorAgent","description":"Strengthen reasoning and classify hypotheses."},
                {"step":"Evaluate hypotheses quantitatively","agent":"EvaluatorAgent","description":"Check numerical evidence supporting each hypothesis."},
                {"step":"Generate improved creatives","agent":"CreativeImprovementAgent","description":"Produce better headlines, hooks, messaging for low CTR ads."},
                {"step":"Generate final report","agent":"ReportAgent","description":"Synthesize everything into a final markdown report."},
            ]
        }

        log_event("PlannerAgent", "plan_generated", {"query": user_query})
        return plan_dict
