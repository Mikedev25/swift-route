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
def brute_force_sort(tasks: list[dict]) -> list[dict]:
    items = tasks.copy()
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
    if days == 0:  return "DUE TODAY"
    if days <= 2:  return "HIGH"
    if days <= 7:  return "MEDIUM"
    return "LOW"


def priority_color(priority: str) -> str:
    return {
        "OVERDUE":   "\033[91m",
        "DUE TODAY": "\033[93m",
        "HIGH":      "\033[33m",
        "MEDIUM":    "\033[94m",
        "LOW":       "\033[92m",
    }.get(priority, "")


# ─────────────────────────────────────────────
#  Persistence
# ─────────────────────────────────────────────
def load_tasks() -> list[dict]:
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks: list[dict]) -> None:
    with open(SAVE_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


# ─────────────────────────────────────────────
#  Display
# ─────────────────────────────────────────────
def display_tasks(tasks: list[dict]) -> None:
    active = []
    for t in tasks:
        if not t.get("done"):
            days = compute_days_remaining(t["deadline"])
            active.append({**t, "days_remaining": days})

    done_tasks = [t for t in tasks if t.get("done")]

    if not active and not done_tasks:
        print(f"\n  {DIM}No tasks yet. Add one from the menu!{RESET}\n")
        return

    sorted_tasks = brute_force_sort(active)

    print(f"\n  {BOLD}{'#':<4} {'ID':<5} {'TASK':<30} {'DEADLINE':<12} {'DAYS':>7}  {'PRIORITY':<12} CATEGORY{RESET}")
    print("  " + "─" * 88)

    for rank, task in enumerate(sorted_tasks, 1):
        days = task["days_remaining"]
        priority = get_priority(days)
        color = priority_color(priority)

        if days < 0:
            days_str = f"{abs(days)}d ago"
        elif days == 0:
            days_str = "today"
        else:
            days_str = f"{days}d left"

        print(
            f"  {DIM}{rank:<4}{RESET}"
            f"{task['id']:<5} "
            f"{task['name']:<30} "
            f"{task['deadline']:<12} "
            f"{days_str:>7}  "
            f"{color}{priority:<12}{RESET}"
            f"{task['category']}"
        )

    if done_tasks:
        print(f"\n  {DIM}─── Completed ({len(done_tasks)}) ───{RESET}")
        for t in done_tasks:
            print(f"  {DIM}{'✓':<4} {t['id']:<5} {t['name']:<30} {t['deadline']:<12} done{RESET}")

    overdue   = sum(1 for t in active if t["days_remaining"] < 0)
    due_today = sum(1 for t in active if t["days_remaining"] == 0)
    print(f"\n  {DIM}Active: {len(active)}  |  Overdue: {overdue}  |  Due today: {due_today}  |  Completed: {len(done_tasks)}{RESET}\n")


# ─────────────────────────────────────────────
#  Actions
# ─────────────────────────────────────────────
def add_task(tasks: list[dict]) -> None:
    print()

    name = input("  Task name            : ").strip()
    if not name:
        print("  Task name cannot be empty.\n")
        return

    while True:
        deadline = input("  Deadline (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
            break
        except ValueError:
            print("  Invalid format. Please use YYYY-MM-DD.")

    print("  Categories: Work, School, Personal, Health, Finance, Other")
    category = input("  Category     [Other]: ").strip() or "Other"

    new_id = max((t["id"] for t in tasks), default=0) + 1
    tasks.append({
        "id":       new_id,
        "name":     name,
        "deadline": deadline,
        "category": category,
        "done":     False,
    })
    save_tasks(tasks)
    print(f"\n  {BOLD}Task #{new_id} '{name}' added!{RESET}\n")


def mark_done(tasks: list[dict]) -> None:
    active = [t for t in tasks if not t.get("done")]
    if not active:
        print("\n  No active tasks to mark as done.\n")
        return

    display_tasks(tasks)

    try:
        rank = int(input("  Enter rank # to mark as done: "))
        sorted_active = brute_force_sort([
            {**t, "days_remaining": compute_days_remaining(t["deadline"])}
            for t in active
        ])
        if 1 <= rank <= len(sorted_active):
            task_id = sorted_active[rank - 1]["id"]
            for t in tasks:
                if t["id"] == task_id:
                    t["done"] = True
                    print(f"\n  '{t['name']}' marked as done!\n")
            save_tasks(tasks)
        else:
            print(f"\n  Rank must be between 1 and {len(sorted_active)}.\n")
    except ValueError:
        print("\n  Please enter a valid number.\n")


def remove_task(tasks: list[dict]) -> None:
    if not tasks:
        print("\n  No tasks to remove.\n")
        return

    display_tasks(tasks)

    try:
        task_id = int(input("  Enter task ID to remove: "))
        match = next((t for t in tasks if t["id"] == task_id), None)
        if match:
            tasks.remove(match)
            save_tasks(tasks)
            print(f"\n  '{match['name']}' removed.\n")
        else:
            print(f"\n  No task found with ID {task_id}.\n")
    except ValueError:
        print("\n  Please enter a valid number.\n")


def edit_task(tasks: list[dict]) -> None:
    if not tasks:
        print("\n  No tasks to edit.\n")
        return

    display_tasks(tasks)

    try:
        task_id = int(input("  Enter task ID to edit: "))
        task = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            print(f"\n  No task found with ID {task_id}.\n")
            return

        print(f"\n  Editing task #{task_id} — press Enter to keep current value.\n")

        new_name = input(f"  Name     [{task['name']}]: ").strip()
        if new_name:
            task["name"] = new_name

        while True:
            new_deadline = input(f"  Deadline [{task['deadline']}]: ").strip()
            if not new_deadline:
                break
            try:
                datetime.strptime(new_deadline, "%Y-%m-%d")
                task["deadline"] = new_deadline
                break
            except ValueError:
                print("  Invalid format. Use YYYY-MM-DD.")

        new_category = input(f"  Category [{task['category']}]: ").strip()
        if new_category:
            task["category"] = new_category

        save_tasks(tasks)
        print(f"\n  Task #{task_id} updated!\n")
    except ValueError:
        print("\n  Please enter a valid number.\n")


def show_algorithm_info() -> None:
    print(f"""
  {BOLD}Brute-Force Bubble Sort — How It Works{RESET}
  ────────────────────────────────────────
  1. For each task, compute:
       days_remaining = deadline - today

  2. Run O(n^2) bubble sort:
       for i in range(n - 1):
         for j in range(n - i - 1):
           if tasks[j].days > tasks[j+1].days:
             swap them

  3. The task with the smallest (or most negative)
     days_remaining rises to rank #1.

  Overdue tasks have negative days → always rank first.
  Complexity: O(n^2) time  |  O(1) extra space
""")


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
def main() -> None:
    tasks = load_tasks()

    print(f"\n{BOLD}  ╔══════════════════════════════════╗")
    print(f"  ║   Task Priority Manager          ║")
    print(f"  ║   Brute-Force Deadline Sorter    ║")
    print(f"  ╚══════════════════════════════════╝{RESET}")

    menu = (
        f"\n  {BOLD}[1]{RESET} View tasks    "
        f"{BOLD}[2]{RESET} Add task    "
        f"{BOLD}[3]{RESET} Mark done\n"
        f"  {BOLD}[4]{RESET} Remove task   "
        f"{BOLD}[5]{RESET} Edit task   "
        f"{BOLD}[6]{RESET} How it works    "
        f"{BOLD}[0]{RESET} Exit\n"
    )

    while True:
        print(menu)
        choice = input("  Choice: ").strip()

        if   choice == "1": display_tasks(tasks)
        elif choice == "2": add_task(tasks)
        elif choice == "3": mark_done(tasks)
        elif choice == "4": remove_task(tasks)
        elif choice == "5": edit_task(tasks)
        elif choice == "6": show_algorithm_info()
        elif choice == "0":
            print("\n  Goodbye!\n")
            break
        else:
            print("\n  Invalid choice. Please enter 0–6.\n")


if __name__ == "__main__":
    main()