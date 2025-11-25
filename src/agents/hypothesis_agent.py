import json
import re
import os
import time
from tqdm import tqdm

JSON_REGEX = re.compile(r'({[\s\S]*})|(\[[\s\S]*\])', re.MULTILINE)

def clean_llm_output(text: str) -> str:
    """Remove <think> tags, HTML tags, backticks, code fences."""
    text = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?[^>]+>', '', text)
    text = text.replace("```json", "").replace("```", "")
    return text.strip()

def extract_json(text: str):
    text = clean_llm_output(text)

    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try regex extraction
    m = JSON_REGEX.search(text)
    if not m:
        raise ValueError("No JSON object found")

    json_str = m.group(0)
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)

    return json.loads(json_str)


class HypothesisAgent:

    def __init__(self, llm, save_path=None):
        from config import RESULTS_DIR
        self.llm = llm
        self.save_path = save_path or os.path.join(RESULTS_DIR, "hypotheses.json")

    def _build_prompt(self, insights: dict) -> str:
        schema = {
            "hypotheses": [
                {
                    "issue": "string",
                    "hypothesis": "string",
                    "supporting_signals": ["list of signals"],
                    "confidence": 0.0
                }
            ],
            "meta": {"agent": "HypothesisAgent"}
        }

        return f"""
You are a hypothesis-generating agent. Convert insights into strong, testable marketing hypotheses.

OUTPUT RULES:
- Output ONLY one clean JSON object.
- MUST follow this schema exactly:

{json.dumps(schema, indent=2)}

INSIGHTS:
{json.dumps(insights, indent=2, ensure_ascii=False)}
"""

    def _call_llm(self, prompt: str) -> str:
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        if hasattr(self.llm, "generate_content"):
            return self.llm.generate_content(prompt)
        raise RuntimeError("LLM client missing generate() or generate_content()")

    def run(self, insights: dict, max_attempts=2):
        prompt = self._build_prompt(insights)
        last_err = None

        for attempt in range(1, max_attempts + 1):
            for _ in tqdm(range(3), desc="HypothesisAgent processing", leave=False):
                time.sleep(0.08)

            try:
                raw = self._call_llm(prompt)
                parsed = extract_json(raw)

                parsed.setdefault("meta", {})
                parsed["meta"].update({
                    "raw_preview": raw[:800],
                    "agent": "HypothesisAgent"
                })

                # Save final output
                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)

                print("Saved hypotheses ->", self.save_path)
                return parsed

            except Exception as e:
                last_err = e
                if attempt < max_attempts:
                    prompt = (
                        "Your previous response was NOT valid JSON. Fix it.\n"
                        "Return ONLY clean JSON. Previous output:\n\n"
                        f"{raw}\n\n"
                    ) + self._build_prompt(insights)
                    time.sleep(0.5)
                    continue
                break

        # ---- FALLBACK ----
        fallback = {
            "hypotheses": [],
            "meta": {"error": str(last_err), "agent": "HypothesisAgent"}
        }

        # Save fallback in results folder
        from config import RESULTS_DIR
        path = os.path.join(RESULTS_DIR, "hypotheses.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2)

        print("Saved fallback hypotheses ->", path)
        return fallback
