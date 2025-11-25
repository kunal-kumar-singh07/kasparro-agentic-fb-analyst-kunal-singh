from agents.data_agent import DataAgent

csv_path = r"E:\Kasparo\kasparro-agentic-fb-analyst-kunal-singh\data\synthetic_fb_ads_undergarments.csv"

agent = DataAgent(csv_path)
agent.load_data()
output = agent.compute_metrics()

print(output)
