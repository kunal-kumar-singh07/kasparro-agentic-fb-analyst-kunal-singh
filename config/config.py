import yaml
import os

CONFIG_PATH = os.path.join("config", "config.yaml")

with open(CONFIG_PATH, "r") as f:
    cfg = yaml.safe_load(f)

RESULTS_DIR = cfg["paths"]["results_dir"]
DATA_CSV_PATH = cfg["paths"]["dataset"]
LOGS_DIR = cfg["paths"]["logs_dir"]

LLM_CONFIG = cfg["llm"]
THRESHOLDS = cfg["thresholds"]
SEED = cfg["seed"]
