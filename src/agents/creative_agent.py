import json, re, os, time
from tqdm import tqdm
from config.config_loader import RESULTS_DIR

from config.config_loader import LOGS_DIR

from utils.logging_utils import log_event


JSON_REGEX = re.compile(r'({[\s\S]*})|(\[[\s\S]*\])', re.MULTILINE)

def clean_llm_output(text: str) -> str:
    text = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?[^>]+>', '', text)
    text = text.replace("```json", "").replace("```", "")
    return text.strip()

def extract_json(text: str):
    text = clean_llm_output(text)
    try:
        return json.loads(text)
    except Exception:
        pass
    m = JSON_REGEX.search(text)
    if not m:
        raise ValueError("No JSON found")
    json_str = m.group(0)
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    return json.loads(json_str)

class CreativeImprovementAgent:
    def __init__(self, llm, save_path=None):
        self.llm = llm
        self.save_path = save_path or os.path.join(RESULTS_DIR, "creative_recommendations.json")

    def _build_prompt(self, metrics, insights):
        schema = {"creative_recommendations":[{"issue":"string","old_message":"string","new_creative":"string","reasoning":"string","expected_ctr_lift":"string"}],"meta":{"agent":"CreativeImprovementAgent"}}
        return f"""You are a Creative Improvement Agent. Return ONLY JSON following schema.

Metrics:
{json.dumps(metrics, indent=2, ensure_ascii=False)}

Insights:
{json.dumps(insights, indent=2, ensure_ascii=False)}
"""

    def _call_llm(self, prompt: str):
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        if hasattr(self.llm, "generate_content"):
            return self.llm.generate_content(prompt)
        raise RuntimeError("LLM client missing generate method")

    def run(self, metrics, insights, max_attempts=2):
        log_event("CreativeImprovementAgent", "start", {"message":"start creative improvements"})
        prompt = self._build_prompt(metrics, insights)
        last_err = None
        raw = ""
        for attempt in range(1, max_attempts + 1):
            for _ in tqdm(range(3), desc="CreativeImprovementAgent", leave=False):
                time.sleep(0.08)
            try:
                raw = self._call_llm(prompt)
            except Exception as e:
                last_err = e
                log_event("CreativeImprovementAgent", "api_error", {"attempt": attempt, "error": str(e)})
                time.sleep(attempt)
                continue
            try:
                parsed = extract_json(raw)
                parsed.setdefault("meta", {})
                parsed["meta"].update({"agent":"CreativeImprovementAgent","raw_preview": raw[:800]})
                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)
                log_event("CreativeImprovementAgent", "success", {"path": self.save_path})
                return parsed
            except Exception as e:
                last_err = e
                log_event("CreativeImprovementAgent", "parse_error", {"attempt": attempt, "error": str(e), "raw_preview": raw[:500]})
                if attempt < max_attempts:
                    prompt = "Your last output was invalid JSON. Return ONLY JSON.\nPrevious output:\n" + raw + "\n" + self._build_prompt(metrics, insights)
                    continue
                break
        fallback = {"creative_recommendations":[],"meta":{"error":str(last_err),"agent":"CreativeImprovementAgent"}}
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2, ensure_ascii=False)
        log_event("CreativeImprovementAgent", "fallback", {"error": str(last_err)})
        return fallback
