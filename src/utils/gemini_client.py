import google.generativeai as genai
import os

class GeminiClient:
    def __init__(self, model="gemini-2.0-flash-thinking-exp"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_name = model
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt):
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 4096
            }
        )
        return response.text
