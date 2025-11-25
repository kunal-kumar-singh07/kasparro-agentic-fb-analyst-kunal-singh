import json
from pathlib import Path
from utils.json_extractor import extract_json

class InsightAgent:
    def __init__(self, llm, prompt_path=None):
        if prompt_path is None:
            root = Path(__file__).resolve().parent.parent.parent
            prompt_path = str(root / "prompts" / "insight_prompt.md")

        self.llm = llm
        self.prompt_template = Path(prompt_path).read_text()

    def run(self, data_dict):
        metrics_json = json.dumps(data_dict)

        prompt = self.prompt_template.replace("{{data_json}}", metrics_json)

        # retry 3 times until DeepSeek returns JSON
        for attempt in range(3):
            response = self.llm.generate(prompt)

            # debug print
            print("\nRAW MODEL RESPONSE (first 500 chars):")
            print(response[:500])

            try:
                parsed = extract_json(response)
                return parsed
            except:
                print("JSON parsing failed, retrying... (attempt " + str(attempt+1) + ")")

        # total failure
        raise ValueError("InsightAgent could not produce JSON after 3 attempts")
