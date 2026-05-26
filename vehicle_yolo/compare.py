import csv
from pathlib import Path
from typing import Dict, List

from .config import ORIGINAL_TRAIN_RUN_NAME, RUNS_DIR, TRAIN_RUN_NAME


METRIC_KEYS = [
    "metrics/precision(B)",
    "metrics/recall(B)",
    "metrics/mAP50(B)",
    "metrics/mAP50-95(B)",
]


def _read_rows(results_csv: Path) -> List[Dict[str, str]]:
    with results_csv.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = []
        for row in reader:
            rows.append({key.strip(): value.strip() for key, value in row.items()})
        return rows


def _float_value(row: Dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value else float("nan")


def _best_row(rows: List[Dict[str, str]]) -> Dict[str, str]:
    return max(rows, key=lambda row: _float_value(row, "metrics/mAP50-95(B)"))


def print_run_summary(run_name: str) -> None:
    results_csv = RUNS_DIR / run_name / "results.csv"
    if not results_csv.exists():
        print(f"\n[{run_name}]")
        print(f"Missing results.csv: {results_csv}")
        return

    rows = _read_rows(results_csv)
    if not rows:
        print(f"\n[{run_name}]")
        print("results.csv is empty.")
        return

    row = _best_row(rows)
    print(f"\n[{run_name}] best by mAP50-95")
    print(f"epoch: {row.get('epoch', '')}")
    for key in METRIC_KEYS:
        print(f"{key}: {row.get(key, '')}")


def compare_default_runs() -> None:
    print_run_summary(TRAIN_RUN_NAME)
    print_run_summary(ORIGINAL_TRAIN_RUN_NAME)

