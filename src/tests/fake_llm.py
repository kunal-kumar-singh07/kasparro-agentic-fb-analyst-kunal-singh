class FakeLLM:
    def generate(self, prompt):
        if "hypotheses" in prompt.lower() or "generate hypotheses" in prompt.lower():
            return """
            {
                "hypotheses": [
                    {"issue": "low CTR", "hypothesis": "Creative fatigue"},
                    {"issue": "low ROAS", "hypothesis": "Audience saturation"}
                ]
            }
            """

        return """
        {
            "insights": ["CTR is stable", "ROAS is declining"],
            "summary_text": "Basic summary"
        }
        """

class FakeLLMFailOnce:
    def __init__(self):
        self.called = False

    def generate(self, prompt):
        if not self.called:
            self.called = True
            return "INVALID JSON"
        return '{"insights": ["Recovered after failure"]}'


class FakeLLMAlwaysFail:
    def generate(self, prompt):
        return "NOT JSON AT ALL"

class EvalLLM:
    def generate(self, prompt):
        return """
        {
            "evaluated_hypotheses": [
                {"issue": "creative fatigue", "confidence": 0.8}
            ]
        }
        """
