import json
from pathlib import Path
from utils.json_extractor import extract_json

class HypothesisAgent:
    def __init__(self, llm, prompt_path=None):
        if prompt_path is None:
            root = Path(__file__).resolve().parent.parent.parent
            prompt_path = str(root / "prompts" / "hypothesis_prompt.md")

        self.llm = llm
        self.prompt_template = Path(prompt_path).read_text()

    def run(self, insights):
        payload = json.dumps(insights)

        prompt = (
            self.prompt_template.replace("{{insights_json}}", payload)
        )

        response = self.llm.generate(prompt)

        try:
            parsed = extract_json(response)
            return parsed
        except:
            raise ValueError("HypothesisAgent failed to produce valid JSON")
