import requests
import re

class OllamaClient:
    def __init__(self, model="deepseek-r1"):
        self.model = model

    def remove_think(self, text):
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    def generate(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post("http://localhost:11434/api/generate", json=payload)
        output = response.json()["response"]

        cleaned = self.remove_think(output)
        return cleaned
