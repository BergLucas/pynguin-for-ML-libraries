import json
import os


def load_summary(experiment_path: str) -> dict:
    summary_path = os.path.join(experiment_path, "summary.json")

    with open(summary_path, "r") as f:
        return json.load(f)
