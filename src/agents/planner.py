import json
from pathlib import Path
from utils.json_extractor import extract_json

class PlannerAgent:
    def __init__(self, llm, prompt_path=None):
        if prompt_path is None:
            # Auto-detect project root (planner.py → agents → src → project root)
            root = Path(__file__).resolve().parent.parent.parent
            prompt_path = str(root / "prompts" / "planner_prompt.md")

        self.llm = llm
        self.prompt_template = Path(prompt_path).read_text()


    def run(self, user_query):
        # Fill prompt template
        prompt = self.prompt_template.replace("{{user_query}}", user_query)

        # Call local DeepSeek via Ollama
        response = self.llm.generate(prompt)

        # Extract ONLY JSON (DeepSeek prints reasoning first)
        plan = extract_json(response)

        # Basic validation
        if "tasks" not in plan:
            raise ValueError("'tasks' field missing in planner output")

        return plan
