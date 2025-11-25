import os
import sys
import json

# ensure project root is importable
sys.path.append(os.path.dirname(__file__))

from utils.gemini_client import GeminiClient
from agents.validator_agent import ValidatorAgent

BASE_DIR = os.path.dirname(__file__)
HYP_PATH = os.path.join(BASE_DIR, "agents", "hypotheses.json")

print("Looking for:", HYP_PATH)

if not os.path.exists(HYP_PATH):
    raise FileNotFoundError("hypotheses.json not found at: " + HYP_PATH)

with open(HYP_PATH, "r") as f:
    hypotheses = json.load(f)

llm = GeminiClient()
validator = ValidatorAgent(llm)

print("Running validator agent...\n")

result = validator.run(hypotheses)

print("\nVALIDATOR OUTPUT:")
print(json.dumps(result, indent=2))
