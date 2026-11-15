"""
Experiment Persistence Store
Manages training runs, metrics, and benchmark logs in a structured JSON database.
Persists across server and page refreshes.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
EXP_FILE = os.path.join(DATA_DIR, "experiments.json")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_experiments() -> List[Dict[str, Any]]:
    _ensure_dir()
    if not os.path.exists(EXP_FILE):
        return []
    try:
        with open(EXP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading experiments: {e}")
        return []


def save_experiments(experiments: List[Dict[str, Any]]):
    _ensure_dir()
    with open(EXP_FILE, "w", encoding="utf-8") as f:
        json.dump(experiments, f, indent=2)


def add_experiment(exp_data: Dict[str, Any]) -> Dict[str, Any]:
    experiments = load_experiments()
    # Check if ID already exists
    exp_id = exp_data.get("id") or f"exp_{int(time.time()*1000)}"
    exp_data["id"] = exp_id
    if "timestamp" not in exp_data:
        exp_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    # Prepend newest
    experiments.insert(0, exp_data)
    save_experiments(experiments)
    return exp_data


def get_experiment_by_id(exp_id: str) -> Optional[Dict[str, Any]]:
    experiments = load_experiments()
    for exp in experiments:
        if exp.get("id") == exp_id:
            return exp
    return None


def delete_experiment_by_id(exp_id: str) -> bool:
    experiments = load_experiments()
    initial_len = len(experiments)
    experiments = [e for e in experiments if e.get("id") != exp_id]
    if len(experiments) < initial_len:
        save_experiments(experiments)
        return True
    return False


def clear_all_experiments():
    save_experiments([])
