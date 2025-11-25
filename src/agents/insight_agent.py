import json
import re
import time
import os
from tqdm import tqdm

# NOTE: this InsightAgent expects your llm client to implement a simple:
#   response_text = llm.generate(prompt: str)
# If your LLM client uses a different API (e.g. generate_content(...)), adapt the call in `self._call_llm`.

DEFAULT_DATASET_PATH = "/mnt/data/synthetic_fb_ads_undergarments.csv"  # path you uploaded (developer/user provided)

JSON_EXTRACTOR_REGEX = re.compile(r'({[\s\S]*})|(\[[\s\S]*\])', re.MULTILINE)

def _clean_thinking_tags(text: str) -> str:
    # remove <think>...</think> blocks
    text = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)
    # remove XML/HTML-like tags often used by some LLMs
    text = re.sub(r'</?[^>]+>', '', text)
    # remove common wrappers/backticks/code fences
    text = text.strip()
    text = re.sub(r'```json', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```', '', text)
    text = text.strip()
    return text

def _extract_json(text: str):
    """
    Try to find the first JSON object/array in `text`.
    Returns Python object or raises ValueError.
    """
    # quick clean
    cleaned = _clean_thinking_tags(text)

    # try to parse as-is
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # regex extract first {...} or [...]
    m = JSON_EXTRACTOR_REGEX.search(cleaned)
    if not m:
        raise ValueError("No JSON block found in model response")

    json_str = m.group(0)
    # sometimes model returns trailing commas — attempt to fix common issues
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)

    try:
        return json.loads(json_str)
    except Exception as e:
        # still failed
        raise ValueError(f"Failed to decode JSON extracted from model response: {e}\nExtracted text:\n{json_str}")

class InsightAgent:
    def __init__(self, llm, dataset_path: str = DEFAULT_DATASET_PATH, save_path: str = None):
        """
        llm: object with method generate(prompt: str) -> str
        dataset_path: local path to the CSV (will be included in the prompt)
        save_path: where to write the resulting insights.json (defaults to src/agents/insights.json)
        """
        self.llm = llm
        self.dataset_path = dataset_path
        if save_path:
            self.save_path = save_path
        else:
            base = os.path.dirname(__file__)
            self.save_path = os.path.join(base, "insights.json")

    def _build_prompt(self, metrics: dict) -> str:
        """
        Build a clear instruction prompt that requests JSON only.
        We include a small JSON schema to encourage strict JSON output.
        """
        schema = {
            "summary_text": "short summary (1-2 sentences)",
            "insights": [
                {
                    "title": "short title",
                    "description": "explain evidence and why it matters",
                    "evidence": {
                        "kpi_changes": [{"kpi": "ROAS", "trend": "decreasing", "dates": "2025-03-24 to 2025-03-31", "values": []}],
                        "creative_issues": [],
                        "audience_issues": []
                    },
                    "severity": "Low|Medium|High",
                    "confidence": 0.0
                }
            ],
            "meta": {"agent": "InsightAgent", "dataset_path": self.dataset_path}
        }

        # safe-serialize metrics (truncate heavy arrays if needed)
        try:
            metrics_small = json.dumps(metrics, indent=2, ensure_ascii=False)
        except Exception:
            # fallback: keep only keys
            metrics_small = json.dumps({k: "<omitted-for-prompt>" for k in metrics.keys()})

        prompt = f"""
You are an analytics assistant. Using the metrics and signals provided, produce a single JSON object (no extra text, no explanation) following this schema:

{json.dumps(schema, indent=2)}

REQUIREMENTS:
1) RETURN strictly one valid JSON object that follows the schema above.
2) Keep "summary_text" to 1-2 sentences.
3) Create 3-8 insight objects in "insights", each with actionable, evidence-backed findings.
4) In "evidence", include numeric signals where possible (kpi_changes, creative_issues, audience_issues).
5) Include in "meta" the dataset path: {self.dataset_path}.

DATA (use this to derive insights):
{metrics_small}

Important: If you are going to "think", do NOT emit any <think> tags. Output must be JSON only. If you cannot produce valid JSON, include a field "error" with a short explanation, but still return valid JSON.

Now produce the JSON object only.
"""
        return prompt

    def _call_llm(self, prompt: str) -> str:
        """
        Single point to call LLM. Adapt this if your llm client signature differs.
        """
        # If your llm client requires a method name other than `generate`, change here.
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        # support other clients like google/gemini wrappers
        if hasattr(self.llm, "generate_content"):
            # many wrappers accept a simple string; adjust if your wrapper uses a dict
            return self.llm.generate_content(prompt)
        raise RuntimeError("LLM client does not implement expected generate(...) method")

    def run(self, metrics: dict, max_attempts: int = 2) -> dict:
        """
        Run the insight agent: call LLM, ensure JSON output, save to self.save_path, and return parsed dict.
        """
        prompt = self._build_prompt(metrics)

        last_exc = None
        for attempt in range(1, max_attempts + 1):
            # show small progress steps
            for _ in tqdm(range(3), desc="InsightAgent: processing", leave=False):
                time.sleep(0.08)

            try:
                raw = self._call_llm(prompt)
            except Exception as e:
                last_exc = e
                # short backoff then retry
                time.sleep(1.0 * attempt)
                continue

            # try to extract JSON
            try:
                parsed = _extract_json(raw)
                # Attach metadata about raw response and timestamp
                if isinstance(parsed, dict):
                    parsed.setdefault("meta", {})
                    parsed["meta"].update({
                        "agent": "InsightAgent",
                        "raw_length": len(raw),
                        "raw_preview": raw[:1000]
                    })
                # save
                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)
                print("Saved insights ->", self.save_path)
                return parsed
            except Exception as e:
                last_exc = e
                # prepare a stricter retry: ask model to return JSON only and include prior response for context
                if attempt < max_attempts:
                    retry_prompt = (
                        "The previous output could not be parsed as JSON. "
                        "You must return a single valid JSON object only (no extra commentary). "
                        "Here is the previous output:\n\n"
                        f"{raw}\n\n"
                        "Now, produce only the JSON object that matches the schema and requirements."
                    )
                    prompt = retry_prompt + "\n\n" + self._build_prompt(metrics)
                    time.sleep(0.5 * attempt)
                    continue
                else:
                    break

        # if we reach here, we failed
        err_msg = f"InsightAgent failed to produce JSON after {max_attempts} attempts. Last error: {last_exc}"
        # return a safe JSON with error details
        fallback = {
            "summary_text": "insights generation failed",
            "insights": [],
            "meta": {
                "agent": "InsightAgent",
                "error": str(last_exc)
            }
        }
        # ensure saved so downstream agents have something
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2, ensure_ascii=False)
        print("Saved fallback insights ->", self.save_path)
        return fallback
