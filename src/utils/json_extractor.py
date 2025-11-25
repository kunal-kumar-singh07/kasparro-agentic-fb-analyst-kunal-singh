import json
import re

def remove_think(text):
    # remove <think> ... </think>
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

def extract_json(text):
    cleaned = remove_think(text)

    # find first json object
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        block = match.group(0)
        try:
            return json.loads(block)
        except:
            raise ValueError("JSON block found but parsing failed")

    raise ValueError("No JSON found in model response")
