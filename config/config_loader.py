import os
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "config.yaml")

with open(CONFIG_PATH, "r") as f:
    cfg = yaml.safe_load(f)

def _env_or_cfg(env_name, cfg_value, cast=str):
    val = os.getenv(env_name)
    if val is None:
        return cfg_value
    try:
        return cast(val)
    except Exception:
        return cfg_value

DATA_CSV_PATH = _env_or_cfg("DATA_CSV_PATH", os.path.join(ROOT_DIR, cfg["paths"]["dataset"]))
RESULTS_DIR   = _env_or_cfg("RESULTS_DIR",   os.path.join(ROOT_DIR, cfg["paths"]["results_dir"]))
LOGS_DIR      = _env_or_cfg("LOGS_DIR",      os.path.join(ROOT_DIR, cfg["paths"]["logs_dir"]))

LLM_CONFIG = {
    "model":       _env_or_cfg("LLM_MODEL",   cfg["llm"]["model"]),
    "temperature": _env_or_cfg("LLM_TEMP",    cfg["llm"]["temperature"], float),
    "max_retries": _env_or_cfg("LLM_RETRIES", cfg["llm"]["max_retries"], int),
}

THRESHOLDS = {
    "low_ctr":         _env_or_cfg("LOW_CTR",          cfg["thresholds"]["low_ctr"], float),
    "high_impressions": _env_or_cfg("HIGH_IMPRESSIONS", cfg["thresholds"]["high_impressions"], int),
    "min_confidence":  _env_or_cfg("MIN_CONFIDENCE",   cfg["thresholds"]["min_confidence"], float),
}

SEED = _env_or_cfg("SEED", cfg["seed"], int)
