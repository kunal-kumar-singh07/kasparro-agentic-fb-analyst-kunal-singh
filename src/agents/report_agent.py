import json, re, os, time
from tqdm import tqdm
from config.config_loader import RESULTS_DIR
from utils.logging_utils import log_event

from config.config_loader import LOGS_DIR

def clean_markdown(text):
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?[^>]+>", "", text)
    text = re.sub(r"\{[\s\S]*?\}$", "", text).strip()
    code_block = re.search(r"```(?:markdown)?\s*([\s\S]*?)\s*```", text)
    if code_block:
        return code_block.group(1).strip()
    return text.strip()

class ReportAgent:
    def __init__(self, llm):
        self.llm = llm
        self.save_path = os.path.join(RESULTS_DIR, "final_report.md")

    def build_prompt(self, metrics, insights, hypotheses, validations):
        return f"""You are the ReportAgent. Write a complete FINAL REPORT in MARKDOWN. Output only markdown.

METRICS:
{json.dumps(metrics, indent=2)}

INSIGHTS:
{json.dumps(insights, indent=2)}

HYPOTHESES:
{json.dumps(hypotheses, indent=2)}

VALIDATIONS:
{json.dumps(validations, indent=2)}
"""

    def run(self, metrics, insights, hypotheses, validations, retries=2):
        log_event("ReportAgent", "start", {"message":"start report generation"})
        prompt = self.build_prompt(metrics, insights, hypotheses, validations)
        last_raw = ""
        for attempt in range(retries + 1):
            for _ in tqdm(range(3), desc="ReportAgent", leave=False):
                time.sleep(0.08)
            raw = self.llm.generate(prompt)
            last_raw = raw
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            debug_path = os.path.join(RESULTS_DIR, "report_raw_debug.txt")
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(raw)
            try:
                markdown = clean_markdown(raw)
                if len(markdown) < 50:
                    raise ValueError("Markdown too short")
                with open(self.save_path, "w", encoding="utf-8") as f:
                    f.write(markdown)
                log_event("ReportAgent", "success", {"path": self.save_path})
                return markdown
            except Exception as e:
                log_event("ReportAgent", "error", {"attempt": attempt, "error": str(e), "raw_preview": last_raw[:500]})
                time.sleep(1)
                continue
        raise ValueError("ReportAgent failed after retries. See " + debug_path)
