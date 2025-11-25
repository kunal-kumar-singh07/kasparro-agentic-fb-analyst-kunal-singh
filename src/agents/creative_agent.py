import json
import os
import re
import time
from tqdm import tqdm

RESULTS_DIR = r"E:\Kasparo\kasparro-agentic-fb-analyst-kunal-singh\results"

JSON_REGEX = re.compile(r'({[\s\S]*})|(\[[\s\S]*\])')

def clean_llm_output(text: str) -> str:
    text = re.sub(r'<think>[\s\S]*?</think>', '', text)
    text = re.sub(r'```json|```', '', text)
    return text.strip()

def extract_json(text: str):
    text = clean_llm_output(text)

    try:
        return json.loads(text)
    except:
        pass

    m = JSON_REGEX.search(text)
    if not m:
        raise ValueError("No JSON found")

    json_str = m.group(0)
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)

    return json.loads(json_str)


class CreativeImprovementAgent:
    """
    Generates improved creative ideas for low-CTR ads.
    Output saved to results/creative_recommendations.json
    """

    def __init__(self, llm, save_path=None):
        self.llm = llm
        self.save_path = save_path or os.path.join(
            RESULTS_DIR, "creative_recommendations.json"
        )

    def _build_prompt(self, metrics, insights):
        schema = {
            "creatives": [
                {
                    "problem_creative": "string",
                    "issue_detected": "string",
                    "new_headline": "string",
                    "new_primary_text": "string",
                    "new_hooks": ["string"],
                    "confidence": 0.0
                }
            ],
            "meta": {"agent": "CreativeImprovementAgent"}
        }

        return f"""
You are a Creative Improvement Agent.
Your job: analyze low CTR creatives and generate improved messaging.

RULES:
- Output ONLY valid JSON.
- Follow EXACT schema:

{json.dumps(schema, indent=2)}

Input data:

METRICS:
{json.dumps(metrics, indent=2)}

INSIGHTS:
{json.dumps(insights, indent=2)}

Return only JSON.
"""

    def _call_llm(self, prompt):
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        if hasattr(self.llm, "generate_content"):
            return self.llm.generate_content(prompt)
        raise RuntimeError("LLM client missing generate/generate_content")

    def run(self, metrics, insights, max_attempts=2):
        prompt = self._build_prompt(metrics, insights)
        last_err = None

        for attempt in range(1, max_attempts + 1):
            for _ in tqdm(range(3), desc="CreativeAgent", leave=False):
                time.sleep(0.08)

            try:
                raw = self._call_llm(prompt)
                parsed = extract_json(raw)

                parsed.setdefault("meta", {})
                parsed["meta"].update({"agent": "CreativeImprovementAgent"})

                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2)

                print("Saved creative recommendations ->", self.save_path)
                return parsed

            except Exception as e:
                last_err = e
                if attempt < max_attempts:
                    prompt = (
                        "Invalid JSON detected. Return ONLY valid JSON.\n"
                        f"Previous output:\n{raw}\n\n"
                    ) + self._build_prompt(metrics, insights)
                    continue
                break

        # fallback
        fallback = {
            "creatives": [],
            "meta": {"error": str(last_err), "agent": "CreativeImprovementAgent"}
        }
        with open(self.save_path, "w") as f:
            json.dump(fallback, f, indent=2)

        print("Saved fallback creative recommendations ->", self.save_path)
        return fallback
