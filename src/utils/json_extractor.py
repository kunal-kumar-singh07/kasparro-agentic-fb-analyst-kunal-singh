import json
import re

def extract_json(text):
    """
    Extract JSON from Gemini output:
    - Strips ```json blocks
    - Removes <thinking> sections
    - Finds deepest {...} block
    """
    # remove <thinking></thinking>
    cleaned = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL)

    # remove fenced code blocks
    cleaned = re.sub(r"```json|```", "", cleaned)

    # find JSON object using greedy match
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise ValueError("No JSON found in model response")

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decode failed: {e}")
