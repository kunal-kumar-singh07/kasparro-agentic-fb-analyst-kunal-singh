import json
import re
import os
from tqdm import tqdm

class ReportAgent:
    def __init__(self, llm):
        self.llm = llm

    def extract_json(self, text):
        matches = re.findall(r"\{[\s\S]*?\}", text)
        if not matches:
            raise ValueError("No JSON found in LLM response")
        for m in matches:
            try:
                return json.loads(m)
            except:
                continue
        raise ValueError("JSON detected but parsing failed")

    def build_prompt(self, metrics, insights, hypotheses, validations):
        return f"""
You are the ReportAgent.

Your job is to generate a clean, complete MARKDOWN report.
Return ONLY this JSON structure:

{{
  "markdown": "<THE_FULL_MARKDOWN_REPORT>"
}}

Rules:
- Do not include anything outside the JSON.
- The "markdown" field must contain full readable markdown.
- No Base64.
- No explanations.

Here is the input data:

METRICS:
{json.dumps(metrics)}

INSIGHTS:
{json.dumps(insights)}

HYPOTHESES:
{json.dumps(hypotheses)}

VALIDATIONS:
{json.dumps(validations)}
"""

    def run(self, metrics, insights, hypotheses, validations, retries=2):
        prompt = self.build_prompt(metrics, insights, hypotheses, validations)

        for attempt in range(retries + 1):
            raw = self.llm.generate(prompt)

            with open("report_raw_debug.txt", "w", encoding="utf-8") as f:
                f.write(raw)

            try:
                data = self.extract_json(raw)
                markdown = data.get("markdown", "").strip()

                if len(markdown) < 20:
                    raise ValueError("Markdown too short, invalid.")

                results_dir = os.path.join(os.path.dirname(__file__), "..", "results")
                os.makedirs(results_dir, exist_ok=True)

                report_path = os.path.join(results_dir, "final_report.md")

                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(markdown)

                return markdown

            except Exception as e:
                print("ReportAgent error, retrying:", e)

        raise ValueError("ReportAgent failed after retries.")
