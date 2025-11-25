from utils.ollama_client import OllamaClient
from agents.data_agent import DataAgent
from agents.insight_agent import InsightAgent
from tqdm import tqdm
import time

print("Starting pipeline...\n")

steps = ["Loading LLM", "Loading data", "Computing metrics", "Generating insights"]

with tqdm(total=len(steps), desc="Pipeline Progress", ncols=80) as pbar:

    llm = OllamaClient(model="deepseek-r1")
    time.sleep(0.2)
    pbar.update(1)

    data_agent = DataAgent()
    data_agent.load_data()
    time.sleep(0.2)
    pbar.update(1)

    data_output = data_agent.compute_metrics()
    time.sleep(0.2)
    pbar.update(1)

    insight_agent = InsightAgent(llm)
    insights = insight_agent.run(data_output)
    time.sleep(0.2)
    pbar.update(1)

print("\nINSIGHT OUTPUT:")
print(insights)
