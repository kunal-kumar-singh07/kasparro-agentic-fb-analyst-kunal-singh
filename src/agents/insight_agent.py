import json, re, os, time
from tqdm import tqdm
from config.config_loader import RESULTS_DIR
from utils.logging_utils import log_event

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
    except Exception:
        pass

    m = JSON_EXTRACTOR_REGEX.search(cleaned)
    if not m:
        raise ValueError("No JSON block found")

    json_str = re.sub(r',\s*([}\]])', r'\1', m.group(0))
    return json.loads(json_str)


class InsightAgent:
    def __init__(self, llm, dataset_path=None, save_path=None):
        self.llm = llm
        self.dataset_path = dataset_path
        self.save_path = save_path or os.path.join(RESULTS_DIR, "insights.json")

    def _build_prompt(self, metrics: dict, query: str) -> str:
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
            "meta": {
                "agent": "InsightAgent",
                "dataset_path": self.dataset_path
            }
        }


        try:
            metrics_block = json.dumps(metrics, indent=2, ensure_ascii=False)
        except:
            metrics_block = json.dumps({k: "<unserializable>" for k in metrics.keys()})

        return f"""
You are InsightAgent. You analyze metrics and produce insights strictly in JSON.

User Question:
{query}

Schema:
{json.dumps(schema, indent=2)}

Instructions:
- Insights must directly answer the user question.
- Use numeric, data-backed evidence.
- No explanations, no extra text, no markdown.

Metrics:
{metrics_block}

Return ONLY valid JSON.
"""

    def _call_llm(self, prompt: str) -> str:
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        if hasattr(self.llm, "generate_content"):
            return self.llm.generate_content(prompt)
        raise RuntimeError("LLM missing generate() or generate_content()")

    def run(self, metrics: dict, query: str, max_attempts=2):

        log_event("InsightAgent", "start", {"message": "start generating insights"})

        prompt = self._build_prompt(metrics, query)
        last_exc = None
        raw = ""

        for attempt in range(1, max_attempts + 1):

            for _ in tqdm(range(3), desc="InsightAgent", leave=False):
                time.sleep(0.08)


            try:
                raw = self._call_llm(prompt)

            except Exception as e:
                last_exc = e
                log_event("InsightAgent", "api_error", {
                    "attempt": attempt,
                    "error": str(e)
                })
                time.sleep(attempt)
                continue


            try:
                parsed = _extract_json(raw)

                parsed.setdefault("meta", {})
                parsed["meta"].update({
                    "agent": "InsightAgent",
                    "raw_preview": raw[:800]
                })

                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)

                log_event("InsightAgent", "success", {
                    "path": self.save_path
                })
                return parsed

            except Exception as e:
                last_exc = e
                log_event("InsightAgent", "parse_error", {
                    "attempt": attempt,
                    "error": str(e),
                    "raw_preview": raw[:500]
                })

                if attempt < max_attempts:
                    prompt = (
                        "Your previous output was INVALID JSON. "
                        "Return ONLY JSON.\n\n"
                        f"Previous output:\n{raw}\n\n"
                        + self._build_prompt(metrics, query)
                    )
                    time.sleep(0.5)
                    continue

                break


        fallback = {
            "summary_text": "insights failed",
            "insights": [],
            "meta": {
                "agent": "InsightAgent",
                "error": str(last_exc)
            }
        }

        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2, ensure_ascii=False)

        log_event("InsightAgent", "fallback", {"error": str(last_exc)})

        return fallback
