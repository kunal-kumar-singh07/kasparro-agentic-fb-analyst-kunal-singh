import json, re, os, time
from tqdm import tqdm
from config.config_loader import RESULTS_DIR
from utils.logging_utils import log_event


def clean_markdown(text: str) -> str:
    """Extract clean markdown from LLM output."""
    # Remove hidden thinking tags
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)

    # Remove HTML tags
    text = re.sub(r"</?[^>]+>", "", text)

    # Extract markdown code block if present
    block = re.search(r"```(?:markdown)?\s*([\s\S]*?)```", text)
    if block:
        return block.group(1).strip()

    return text.strip()


class ReportAgent:
    def __init__(self, llm, retries=2):
        self.llm = llm
        self.retries = retries
        self.save_path = os.path.join(RESULTS_DIR, "final_report.md")

    def build_prompt(self, metrics, insights, hypotheses, evaluated, creatives, query):
        return f"""
You are the ReportAgent. You will write a complete, clean, structured final report in pure markdown.
The report must directly answer the user's question.

User Question:
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

Instructions:
- Return ONLY markdown (no JSON).
- Use headings, tables, bullets.
- Include a summary, insights, hypothesis evaluation, and final recommendations.
- Be concise and actionable.
"""

    def _call_llm(self, prompt: str) -> str:
        """Support both .generate() and .generate_content()"""
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        if hasattr(self.llm, "generate_content"):
            return self.llm.generate_content(prompt)
        raise RuntimeError("LLM object missing generate() / generate_content()")

    def run(self, metrics, insights, hypotheses, evaluated, creatives, query):

        log_event("ReportAgent", "start", {"message": "start report generation"})

        prompt = self.build_prompt(metrics, insights, hypotheses, evaluated, creatives, query)

        last_raw = ""

        for attempt in range(self.retries + 1):

            for _ in tqdm(range(3), desc="ReportAgent", leave=False):
                time.sleep(0.08)

            raw = self._call_llm(prompt)
            last_raw = raw

            # Save debug always
            debug_path = os.path.join(RESULTS_DIR, "report_raw_debug.txt")
            os.makedirs(os.path.dirname(debug_path), exist_ok=True)
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(raw)

            try:
                markdown = clean_markdown(raw)

                if len(markdown) < 50:
                    raise ValueError("Markdown output too short; likely malformed.")

                # Save final report
                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                with open(self.save_path, "w", encoding="utf-8") as f:
                    f.write(markdown)

                log_event("ReportAgent", "success", {"path": self.save_path})
                return markdown

            except Exception as e:
                log_event("ReportAgent", "error", {
                    "attempt": attempt,
                    "error": str(e),
                    "raw_preview": last_raw[:500],
                })
                time.sleep(1)

        raise ValueError(
            f"ReportAgent failed after {self.retries} retries. See debug file: {debug_path}"
        )
