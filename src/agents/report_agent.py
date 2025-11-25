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
        """
        Extracts markdown from code blocks if present,
        otherwise returns the raw text stripped of whitespace.
        """
        # Look for content inside ```markdown ... ``` or ``` ... ```
        code_block_pattern = r"```(?:markdown)?\s*([\s\S]*?)\s*```"
        match = re.search(code_block_pattern, text)
        if match:
            return match.group(1).strip()

        # If no code blocks, just return the text
        return text.strip()

    def build_prompt(self, metrics, insights, hypotheses, validations):
        # CHANGED: We now ask for direct Markdown, not JSON.
        return f"""
You are the ReportAgent.

Your task is to write a comprehensive, professional Final Report in MARKDOWN format based on the data provided below.

INSTRUCTIONS:
- Do NOT output JSON.
- Output ONLY the Markdown text.
- Use headers (#, ##), bullet points, and clear sections.
- Synthesize the findings into a cohesive narrative.

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

            # Simulated thinking bar
            for _ in tqdm(range(3), desc="ReportAgent", leave=False):
                time.sleep(0.08)

            raw = self.llm.generate(prompt)
            last_raw = raw

            # Save raw output for debugging
            debug_path = os.path.join(RESULTS_DIR, "report_raw_debug.txt")
            os.makedirs(RESULTS_DIR, exist_ok=True)
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(raw)

            try:
                # CHANGED: We use clean_markdown instead of extract_json
                markdown = self.clean_markdown(raw)

                if len(markdown) < 50:  # Increased threshold slightly
                    raise ValueError("Generated report is too short or empty.")

                report_path = os.path.join(RESULTS_DIR, "final_report.md")
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(markdown)

                print("Report saved ->", report_path)
                return markdown

            except Exception as e:
                print(f"ReportAgent error (Attempt {attempt + 1}/{retries + 1}):", e)
                continue

        raise ValueError(f"ReportAgent failed after {retries} retries.\nRaw saved at: {debug_path}")