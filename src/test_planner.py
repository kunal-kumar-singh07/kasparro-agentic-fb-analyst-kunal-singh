from utils.ollama_client import OllamaClient
from agents.planner import PlannerAgent

# Initialize local LLM (DeepSeek-R1)
llm = OllamaClient(model="deepseek-r1")

# Initialize the planner agent
planner = PlannerAgent(llm)

# Run a test query
output = planner.run("Analyze ROAS drop in last 7 days")

print("Planner Output:")
print(output)
