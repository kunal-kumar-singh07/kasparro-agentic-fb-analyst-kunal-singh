import json
import os
import re
import time
from tqdm import tqdm

JSON_REGEX = re.compile(r'({[\s\S]*})|(\[[\s\S]*\])', re.MULTILINE)

def clean_llm_output(text: str) -> str:
    """Remove <think> tags and junk wrappers."""
    text = re.sub(r'<think>[\s\S]*?</think>', '', text)
    text = re.sub(r'```json|```', '', text)
    return text.strip()

def extract_json(text: str):
    text = clean_llm_output(text)

    try:
        return json.loads(text)
    except Exception:
        pass

    m = JSON_REGEX.search(text)
    if not m:
        raise ValueError("No JSON found in LLM output")

    json_str = m.group(0)
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)

    return json.loads(json_str)


class ValidatorAgent:
    """
    Validates hypotheses and strengthens reasoning.
    Saves output to validated_hypotheses.json
    """

    def __init__(self, llm, save_path=None):
        self.llm = llm
        base = os.path.dirname(__file__)
        self.save_path = save_path or os.path.join(base, "validated_hypotheses.json")

    def _build_prompt(self, hypotheses: dict) -> str:
        schema = {
            "validated_hypotheses": [
                {
                    "issue": "string",
                    "hypothesis": "string",
                    "status": "validated | rejected | partial",
                    "strengthened_reasoning": "string",
                    "confidence": 0.0
                }
            ],
            "meta": {"agent": "ValidatorAgent"}
        }

        return f"""
You are a Validator Agent. Your job is to evaluate hypotheses based on available insights.

FOLLOW STRICT RULES:
1. Output ONE valid JSON object ONLY.
2. Use EXACT schema:

{json.dumps(schema, indent=2)}

3. Strengthen each hypothesis with deeper logic.
4. Use marketing science, causal reasoning, and signals.
5. Confidence = 0.0–1.0

HYPOHESES TO VALIDATE:
{json.dumps(hypotheses, indent=2, ensure_ascii=False)}

Return ONLY JSON.
"""

    def _call_llm(self, prompt: str) -> str:
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        if hasattr(self.llm, "generate_content"):
            return self.llm.generate_content(prompt)
        raise RuntimeError("LLM client missing generate method")

    def run(self, hypotheses: dict, max_attempts=2):
        prompt = self._build_prompt(hypotheses)
        last_err = None

        for attempt in range(1, max_attempts + 1):

            for _ in tqdm(range(3), desc="ValidatorAgent processing", leave=False):
                time.sleep(0.08)

            try:
                raw = self._call_llm(prompt)
                parsed = extract_json(raw)

                parsed.setdefault("meta", {})
                parsed["meta"].update({
                    "raw_preview": raw[:800],
                    "agent": "ValidatorAgent"
                })

                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)

                print("Saved validated hypotheses ->", self.save_path)
                return parsed

            except Exception as e:
                last_err = e
                if attempt < max_attempts:
                    prompt = (
                        "Your last response was invalid JSON. "
                        "Return ONLY JSON.\nPrevious output:\n"
                        f"{raw}\n"
                    ) + self._build_prompt(hypotheses)
                    continue
                break

        fallback = {
            "validated_hypotheses": [],
            "meta": {"error": str(last_err), "agent": "ValidatorAgent"}
        }

        with open(self.save_path, "w") as f:
            json.dump(fallback, f, indent=2)

        return fallback
