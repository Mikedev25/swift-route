"""
Task Listing System with Brute-Force Deadline Prioritization
============================================================
Uses a brute-force O(n^2) bubble sort to rank tasks by nearest deadline.
All tasks are entered by the user — no pre-loaded data.
"""

import json
import os
from datetime import datetime, date

SAVE_FILE = "tasks.json"

RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"


# ─────────────────────────────────────────────
#  Brute-force O(n^2) bubble sort
#  Sorts tasks by days_remaining ascending.
#  Overdue tasks (negative days) always rank first.
# ─────────────────────────────────────────────
def brute_force_sort(shipments: list) -> list:
    items = shipments.copy()
    n = len(items)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if items[j]["days_remaining"] > items[j + 1]["days_remaining"]:
                items[j], items[j + 1] = items[j + 1], items[j]
    return items


def compute_days_remaining(deadline_str: str) -> int:
    deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    return (deadline - date.today()).days


def get_priority(days: int) -> str:
    if days < 0:   return "OVERDUE"
    if days == 0:  return "CRITICAL"
    if days <= 2:  return "HIGH"
    if days <= 7:  return "MEDIUM"
    return "LOW"


PRIORITY_COLORS = {
    "OVERDUE":  "#c0392b",   # deep red
    "CRITICAL": "#e67e22",   # orange
    "HIGH":     "#f1c40f",   # yellow
    "MEDIUM":   "#2980b9",   # blue
    "LOW":      "#27ae60",   # green
}
 
PRIORITY_TEXT_COLORS = {
    "OVERDUE":  "white",
    "CRITICAL": "white",
    "HIGH":     "#1a1a1a",
    "MEDIUM":   "white",
    "LOW":      "white",
}
 
PRIORITY_ORDER = ["OVERDUE", "CRITICAL", "HIGH", "MEDIUM", "LOW"]

# Binary Search

def binary_search_history(sorted_history: list, query: str) -> list:
    """
    Returns all history entries whose item_code starts with `query`.
    The list must be sorted alphabetically by item_code.
    Falls back gracefully for partial matches.
    """
    query = query.lower()
    lo, hi = 0, len(sorted_history) - 1
    # find left boundary
    first = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if sorted_history[mid]["item_code"].lower() >= query:
            if sorted_history[mid]["item_code"].lower().startswith(query):
                first = mid
            hi = mid - 1
        else:
            lo = mid + 1
 
    if first == -1:
        return []
 
    # collect all matches rightward
    results = []
    idx = first
    while idx < len(sorted_history) and \
            sorted_history[idx]["item_code"].lower().startswith(query):
        results.append(sorted_history[idx])
        idx += 1
    return results
 
# ─────────────────────────────────────────────
#  Persistence
# ─────────────────────────────────────────────
SHIPMENTS_FILE = "shipments.json"
HISTORY_FILE   = "history.json"
 
 
def load_json(path: str, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default
 
 
def save_json(path: str, data) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

