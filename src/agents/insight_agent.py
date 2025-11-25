import json
import re
import time
import os
from tqdm import tqdm

RESULTS_DIR = r"E:\Kasparo\kasparro-agentic-fb-analyst-kunal-singh\results"
DEFAULT_DATASET_PATH = "/mnt/data/synthetic_fb_ads_undergarments.csv"

JSON_EXTRACTOR_REGEX = re.compile(r'({[\s\S]*})|(\[[\s\S]*\])', re.MULTILINE)

def _clean_thinking_tags(text: str) -> str:
    text = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?[^>]+>', '', text)
    text = text.replace("```json", "").replace("```", "")
    return text.strip()

def _extract_json(text: str):
    cleaned = _clean_thinking_tags(text)
    try:
        return json.loads(cleaned)
    except:
        pass
    m = JSON_EXTRACTOR_REGEX.search(cleaned)
    if not m:
        raise ValueError("No JSON block found")
    json_str = re.sub(r',\s*([}\]])', r'\1', m.group(0))
    return json.loads(json_str)

class InsightAgent:
    def __init__(self, llm, dataset_path: str = DEFAULT_DATASET_PATH, save_path: str = None):
        self.llm = llm
        self.dataset_path = dataset_path
        self.save_path = save_path or os.path.join(RESULTS_DIR, "insights.json")

    def _build_prompt(self, metrics: dict) -> str:
        schema = {
            "summary_text": "short summary",
            "insights": [
                {
                    "title": "string",
                    "description": "string",
                    "evidence": {
                        "kpi_changes": [],
                        "creative_issues": [],
                        "audience_issues": []
                    },
                    "severity": "Low|Medium|High",
                    "confidence": 0.0
                }
            ],
            "meta": {"agent": "InsightAgent", "dataset_path": self.dataset_path}
        }

        try:
            metrics_small = json.dumps(metrics, indent=2, ensure_ascii=False)
        except:
            metrics_small = json.dumps({k: "<omitted>" for k in metrics.keys()})

        return f"""
You are an analytics agent. Return one JSON object only.

Schema:
{json.dumps(schema, indent=2)}

Rules:
- JSON only
- 3–8 insights
- Evidence must include numeric signals when possible
- No <think> tags
- No explanations outside JSON

Metrics:
{metrics_small}

Return JSON now.
"""

    def _call_llm(self, prompt: str) -> str:
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        if hasattr(self.llm, "generate_content"):
            return self.llm.generate_content(prompt)
        raise RuntimeError("LLM missing generate()")

    def run(self, metrics: dict, max_attempts: int = 2) -> dict:
        prompt = self._build_prompt(metrics)
        last_exc = None

        for attempt in range(1, max_attempts + 1):
            for _ in tqdm(range(3), desc="InsightAgent", leave=False):
                time.sleep(0.08)

            try:
                raw = self._call_llm(prompt)
            except Exception as e:
                last_exc = e
                time.sleep(attempt)
                continue

            try:
                parsed = _extract_json(raw)
                parsed.setdefault("meta", {})
                parsed["meta"].update({"agent": "InsightAgent", "raw_preview": raw[:800]})

                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)

                print("Saved insights ->", self.save_path)
                return parsed

            except Exception as e:
                last_exc = e
                if attempt < max_attempts:
                    prompt = (
                        "Your previous output was not valid JSON. Return JSON only.\n\n"
                        f"Previous output:\n{raw}\n\n"
                    ) + self._build_prompt(metrics)
                    time.sleep(0.5)
                    continue
                break

        fallback = {
            "summary_text": "insights failed",
            "insights": [],
            "meta": {"agent": "InsightAgent", "error": str(last_exc)}
        }

        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2, ensure_ascii=False)

        print("Saved fallback insights ->", self.save_path)
        return fallback
