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

        self.json_system = (
            "You are a strict JSON generator. "
            "Output ONLY valid JSON. "
            "No explanations. No markdown. No lists. No text before or after. "
            "If unsure, output an empty JSON object {}."
        )

        self.json_fix_prompt = (
            "Fix the following text into valid JSON. "
            "If missing JSON, generate {}. "
            "Output ONLY JSON:\n\n"
        )

    def run(self, data_dict):
        metrics = json.dumps(data_dict)
        prompt = self.prompt_template.replace("{{data_json}}", metrics)
        final_prompt = self.json_system + "\n\n" + prompt

        for attempt in range(3):
            response = self.llm.generate(final_prompt)

            print("\nRAW MODEL RESPONSE:")
            print(response[:500])

            try:
                return extract_json(response)
            except:
                print(f"Parse failed, attempting JSON repair ({attempt+1})...")

            # second pass: force JSON repair
            repair_prompt = self.json_system + "\n" + self.json_fix_prompt + response
            repaired = self.llm.generate(repair_prompt)

            try:
                return extract_json(repaired)
            except:
                print(f"JSON repair failed ({attempt+1})")

        raise ValueError("Gemini failed to generate JSON after 3 attempts.")
