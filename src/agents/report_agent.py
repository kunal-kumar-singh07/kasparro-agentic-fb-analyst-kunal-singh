import os
import re
import json
from utils.logging_utils import log_event
from config.config_loader import RESULTS_DIR


def clean_markdown(text):
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?[^>]+>", "", text)

    block = re.search(r"```(?:markdown)?\s*([\s\S]*?)```", text)
    if block:
        return block.group(1).strip()

    return text.strip()


class ReportAgent:
    def __init__(self, llm, save_path=None, max_attempts=2):
        self.llm = llm
        self.max_attempts = max_attempts
        self.save_path = save_path or os.path.join(RESULTS_DIR, "final_report.md")

    def _build_prompt(self, metrics, insights, hypotheses, evaluated, creatives, query):
        return f"""
You are the ReportAgent. Write a clear, structured, business-facing marketing analysis report in MARKDOWN.

User Query:
{query}

Metrics:
{json.dumps(metrics, indent=2)}

Insights:
{json.dumps(insights, indent=2)}

Hypotheses:
{json.dumps(hypotheses, indent=2)}

Evaluated Hypotheses:
{json.dumps(evaluated, indent=2)}

Creative Recommendations:
{json.dumps(creatives, indent=2)}

Rules:
- Output ONLY clean markdown.
- NO JSON.
- NO HTML.
- NO code fences unless needed for tables.
"""

    def _call_llm(self, prompt):
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        if hasattr(self.llm, "generate_content"):
            return self.llm.generate_content(prompt)
        raise RuntimeError("LLM missing generate()")

    def run(self, metrics, insights, hypotheses, evaluated, creatives, query):

        log_event("ReportAgent", "start", {"message": "agent started"})
        prompt = self._build_prompt(metrics, insights, hypotheses, evaluated, creatives, query)

        last_error = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                raw = self._call_llm(prompt)
                md = clean_markdown(raw)

                if len(md.strip()) < 40:
                    raise ValueError("Report is too short, invalid output.")

                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                with open(self.save_path, "w", encoding="utf-8") as f:
                    f.write(md)

                log_event("ReportAgent", "success", {"attempt": attempt})
                return md

            except Exception as e:
                last_error = e
                log_event("ReportAgent", "parse_error", {
                    "attempt": attempt,
                    "error": str(e),
                    "raw_preview": raw[:300] if 'raw' in locals() else "NO RAW OUTPUT"
                })

        fallback = f"# Report Error\nCould not generate report.\nError: {last_error}"

        with open(self.save_path, "w", encoding="utf-8") as f:
            f.write(fallback)

        log_event("ReportAgent", "fallback", {"error": str(last_error)})
        return fallback
