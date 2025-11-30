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

    def _fallback(self, error):
        return {"meta": {"error": str(error), "agent": self.__class__.__name__}}

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
            raise ValueError("json_parse_error")
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
        agent = self.__class__.__name__
        log_event(agent, "start", {})

        max_attempts = kwargs.pop("max_attempts", self.max_attempts)
        args_list = list(args)
        data = args_list[0] if len(args_list) > 0 else None
        extra = args_list[1] if len(args_list) > 1 and not isinstance(args_list[1], str) else None

        if len(args_list) > 1 and isinstance(args_list[1], str):
            query = args_list[1]
        elif "query" in kwargs:
            query = kwargs.pop("query")
        else:
            query = getattr(self, "default_query", "Provide analysis")

        if extra is not None:
            prompt = self._build_prompt(data, extra, query)
        else:
            prompt = self._build_prompt(data, query)

        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                raw = self._call_llm(prompt)
            except Exception as e:
                last_error = e
                log_event(agent, "error", {"error_type": "llm_api_failure", "attempt": attempt, "error": str(e)})
                time.sleep(attempt)
                continue

            try:
                parsed = self._extract_json(raw)
                final = self._postprocess(parsed)
                self._save(final)
                log_event(agent, "success", {"attempt": attempt})
                return final

            except Exception as e:
                last_error = e
                log_event(agent, "error", {"error_type": "json_parse_error", "attempt": attempt, "error": str(e)})
                if attempt < max_attempts:
                    if extra is not None:
                        prompt = "Return ONLY JSON.\n\nPrevious:\n" + raw + "\n\n" + self._build_prompt(data, extra, query)
                    else:
                        prompt = "Return ONLY JSON.\n\nPrevious:\n" + raw + "\n\n" + self._build_prompt(data, query)
                    continue

        fallback = self._fallback(last_error)
        self._save(fallback)
        log_event(agent, "fallback", {"error": str(last_error), "error_type": "agent_fallback"})
        return fallback
