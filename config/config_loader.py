import yaml
import os

# ------------------------------------------------------
# Compute absolute path to project root
# ------------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Correct absolute paths
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "config.yaml")

# Load YAML safely
with open(CONFIG_PATH, "r") as f:
    cfg = yaml.safe_load(f)

# Export values
RESULTS_DIR = os.path.join(ROOT_DIR, cfg["paths"]["results_dir"])
DATA_CSV_PATH = os.path.join(ROOT_DIR, cfg["paths"]["dataset"])
LOGS_DIR = os.path.join(ROOT_DIR, cfg["paths"]["logs_dir"])

THRESHOLDS = cfg["thresholds"]
SEED = cfg["seed"]
LLM_CONFIG = cfg["llm"]
