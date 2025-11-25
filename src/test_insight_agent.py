from tqdm import tqdm
from utils.gemini_client import GeminiClient
from agents.data_agent import DataAgent
from agents.insight_agent import InsightAgent

print("Starting pipeline...\n")

steps = ["Init LLM", "Load Data", "Compute Metrics", "Generate Insights"]
pbar = tqdm(total=len(steps), desc="Pipeline Progress")

# init LLM (Step 1)
llm = GeminiClient()
pbar.update(1)

# load & compute data (Step 2 & 3)
data_agent = DataAgent()
data_agent.load_data()
pbar.update(1)

data_output = data_agent.compute_metrics()
pbar.update(1)

# run Insight Agent (Step 4)
insight_agent = InsightAgent(llm)
insights = insight_agent.run(data_output)
pbar.update(1)

pbar.close()

print("\nINSIGHT OUTPUT:")
print(insights)
