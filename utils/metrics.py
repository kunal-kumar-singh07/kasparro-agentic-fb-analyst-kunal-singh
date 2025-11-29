import time
import json
import os
from config.config_loader import RESULTS_DIR


class MetricsTracker:
    def __init__(self, run_id):
        self.run_id = run_id
        self.start_time = time.time()
        self.stages = {}
        self.counters = {}

    def mark(self, name):
        self.stages[name] = time.time()

    def inc(self, key, amount=1):
        self.counters[key] = self.counters.get(key, 0) + amount

    def save(self):
        # compute durations
        ordered = list(self.stages.items())
        durations = {}

        for i in range(1, len(ordered)):
            prev_name, prev_time = ordered[i - 1]
            curr_name, curr_time = ordered[i]
            durations[f"{prev_name}_to_{curr_name}"] = round(curr_time - prev_time, 3)

        total_runtime = round(time.time() - self.start_time, 3)

        data = {
            "run_id": self.run_id,
            "counters": self.counters,
            "stages": self.stages,
            "durations": durations,
            "times": {"total_runtime": total_runtime}
        }

        os.makedirs(RESULTS_DIR, exist_ok=True)
        path = os.path.join(RESULTS_DIR, "pipeline_metrics.json")

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        return data
