import json
import re
import os
import time
from tqdm import tqdm

RESULTS_DIR = r"E:\Kasparo\kasparro-agentic-fb-analyst-kunal-singh\results"


class ReportAgent:
    def __init__(self, llm):
        self.llm = llm

    def clean_markdown(self, text):
        """Extract clean markdown from LLM output."""

        # Remove <think> tags
        text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)

        # Remove HTML-like tags
        text = re.sub(r"</?[^>]+>", "", text)

        # Remove stray JSON at bottom of output
        text = re.sub(r"\{[\s\S]*?\}$", "", text).strip()

        # Extract markdown from code block if provided
        code_block = re.search(r"```(?:markdown)?\s*([\s\S]*?)\s*```", text)
        if code_block:
            return code_block.group(1).strip()

        # No code block → return cleaned text
        return text.strip()

    def build_prompt(self, metrics, insights, hypotheses, validations):
        return f"""
You are the ReportAgent.

Write a complete, professional FINAL REPORT in pure MARKDOWN.

Rules:
- Output ONLY markdown (no JSON, no XML, no commentary).
- Use sections, headers, lists, tables.
- Synthesize insights, hypotheses, validation, recommendations.

DATA BELOW:

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
        prompt = self.build_prompt(metrics, insights, hypotheses, validations)

        last_raw = None

        for attempt in range(retries + 1):

            for _ in tqdm(range(3), desc="ReportAgent", leave=False):
                time.sleep(0.08)

            raw = self.llm.generate(prompt)
            last_raw = raw

            debug_path = os.path.join(RESULTS_DIR, "report_raw_debug.txt")
            os.makedirs(RESULTS_DIR, exist_ok=True)
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(raw)

            try:
                markdown = self.clean_markdown(raw)

                if len(markdown) < 50:
                    raise ValueError("Markdown too short — invalid response")

                report_path = os.path.join(RESULTS_DIR, "final_report.md")
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(markdown)

                print("Report saved ->", report_path)
                return markdown

            except Exception as e:
                print(f"ReportAgent error (Attempt {attempt+1}/{retries+1}): {e}")

        raise ValueError(
            f"ReportAgent failed after retries. Debug saved at: {debug_path}"
        )
