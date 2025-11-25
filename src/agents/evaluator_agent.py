import json, re, os, time
from tqdm import tqdm
from config import RESULTS_DIR
from logging_utils import log_event

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

class EvaluatorAgent:
    def __init__(self, llm, save_path=None):
        self.llm = llm
        self.save_path = save_path or os.path.join(RESULTS_DIR, "evaluated_hypotheses.json")

    def _build_prompt(self, hypotheses: dict, metrics: dict) -> str:
        schema = {"evaluated_hypotheses":[{"issue":"string","hypothesis":"string","quantitative_support":"string","strength_score":0.0,"confidence":0.0}],"meta":{"agent":"EvaluatorAgent"}}
        return f"""You are the Evaluator Agent.

Return ONLY one valid JSON object.
Use this schema:
{json.dumps(schema, indent=2)}

METRICS:
{json.dumps(metrics, indent=2, ensure_ascii=False)}

HYPOTHESES:
{json.dumps(hypotheses, indent=2, ensure_ascii=False)}

Return ONLY JSON.
"""

    def _call_llm(self, prompt: str):
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        if hasattr(self.llm, "generate_content"):
            return self.llm.generate_content(prompt)
        raise RuntimeError("LLM client missing generate or generate_content")

    def run(self, hypotheses: dict, metrics: dict, max_attempts=2):
        log_event("EvaluatorAgent", "start", {"message":"start evaluation"})
        prompt = self._build_prompt(hypotheses, metrics)
        last_err = None
        raw = ""
        for attempt in range(1, max_attempts + 1):
            for _ in tqdm(range(3), desc="EvaluatorAgent", leave=False):
                time.sleep(0.08)
            try:
                raw = self._call_llm(prompt)
            except Exception as e:
                last_err = e
                log_event("EvaluatorAgent", "api_error", {"attempt": attempt, "error": str(e)})
                time.sleep(attempt)
                continue
            try:
                parsed = extract_json(raw)
                parsed.setdefault("meta", {})
                parsed["meta"].update({"agent":"EvaluatorAgent","raw_preview": raw[:800]})
                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)
                log_event("EvaluatorAgent", "success", {"path": self.save_path})
                return parsed
            except Exception as e:
                last_err = e
                log_event("EvaluatorAgent", "parse_error", {"attempt": attempt, "error": str(e), "raw_preview": raw[:500]})
                if attempt < max_attempts:
                    prompt = "Your previous response was invalid JSON. Return ONLY JSON.\nPrevious output:\n" + raw + "\n" + self._build_prompt(hypotheses, metrics)
                    continue
                break
        fallback = {"evaluated_hypotheses":[],"meta":{"error":str(last_err),"agent":"EvaluatorAgent"}}
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2, ensure_ascii=False)
        log_event("EvaluatorAgent", "fallback", {"error": str(last_err)})
        return fallback
