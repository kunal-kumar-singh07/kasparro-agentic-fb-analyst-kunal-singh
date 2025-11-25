import google.generativeai as genai

class GeminiClient:
    def __init__(self, model="gemini-2.0-flash"):
        # setting api key directly
        genai.configure(api_key="AIzaSyA2Uc7IuEv149dmqPti3RCd5csPnCrmEaw")
        self.model_name = model
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text
