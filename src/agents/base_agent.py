import os
import json
import time
import re
from utils.logging_utils import log_event
from config.config_loader import RESULTS_DIR


class BaseAgent:
    def __init__(self, llm, save_path=None, max_attempts=2):
        self.llm = llm
        self.save_path = save_path
        self.max_attempts = max_attempts

    def _build_prompt(self, *args, **kwargs):
        raise NotImplementedError

    def _call_llm(self, prompt):
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)

        if hasattr(self.llm, "generate_content"):
            return self.llm.generate_content(prompt)

        raise RuntimeError("LLM client missing generate method")

    def _clean(self, text):
        text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"</?[^>]+>", "", text)
        text = text.replace("```json", "").replace("```", "")
        return text.strip()

    def _extract_json(self, raw):
        cleaned = self._clean(raw)

        try:
            return json.loads(cleaned)
        except Exception:
            pass

        m = re.search(r"({[\s\S]*})|(\[[\s\S]*\])", cleaned)
        if not m:
            raise ValueError("No JSON found")

        json_str = re.sub(r",\s*([}\]])", r"\1", m.group(0))
        return json.loads(json_str)

    def _postprocess(self, data):
        return data

    def _save(self, data):
        if not self.save_path:
            return

        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def run(self, *args, **kwargs):
        agent_name = self.__class__.__name__
        log_event(agent_name, "start", {"message": "agent started"})

        prompt = self._build_prompt(*args, **kwargs)
        last_error = None

        for attempt in range(1, self.max_attempts + 1):

            try:
                raw = self._call_llm(prompt)
            except Exception as e:
                last_error = e
                log_event(agent_name, "api_error", {"attempt": attempt, "error": str(e)})
                time.sleep(attempt)
                continue

            try:
                parsed = self._extract_json(raw)
                final = self._postprocess(parsed)
                self._save(final)

                log_event(agent_name, "success", {"attempt": attempt})
                return final

            except Exception as e:
                last_error = e
                log_event(agent_name, "parse_error", {
                    "attempt": attempt,
                    "error": str(e),
                    "raw_preview": raw[:500]
                })

                if attempt < self.max_attempts:
                    prompt = (
                        "Your previous response was invalid JSON. "
                        "Return ONLY valid JSON.\n\n"
                        f"Previous output:\n{raw}\n\n"
                        + self._build_prompt(*args, **kwargs)
                    )
                    continue

        fallback = {
            "error": str(last_error),
            "agent": agent_name,
            "data": {}
        }

        self._save(fallback)
        log_event(agent_name, "fallback", {"error": str(last_error)})
        return fallback
