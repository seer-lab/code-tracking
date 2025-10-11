"""
Execute Event Counter

Counts how often users run their code (Action,Run/RunClass/etc) in study_data IDE event logs.

Usage:
python count_execute_events.py [study_data_folder] [output_dir]
"""

import os
import sys
import glob
import csv
import pandas as pd
from collections import defaultdict
import datetime

# Event types that indicate code execution
EXECUTE_ACTIONS = {"Run", "RunClass", "RunAnything"}


def count_execute_events(study_data_folder):
    """
    Count execute events per user, per task, and overall.
    Returns: (summary_by_user_task, summary_by_user, summary_by_task, total_count)
    """
    summary_by_user_task = defaultdict(int)
    summary_by_user = defaultdict(int)
    summary_by_task = defaultdict(int)
    total_count = 0

    # Find all ide-events_filtered CSVs
    pattern = os.path.join(study_data_folder, "user_*", "*", "ide-events_filtered_*.csv")
    files = glob.glob(pattern)
    if not files:
        print("No IDE event files found!")
        return None

    print(f"Scanning {len(files)} IDE event files...")
    for file_path in files:
        # Extract user and task from path
        parts = file_path.split(os.sep)
        user = parts[-3].replace("user_", "")
        task = parts[-2]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 3:
                        continue
                    if row[1] == "Action" and row[2] in EXECUTE_ACTIONS:
                        summary_by_user_task[(user, task)] += 1
                        summary_by_user[user] += 1
                        summary_by_task[task] += 1
                        total_count += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    return summary_by_user_task, summary_by_user, summary_by_task, total_count


def save_summary_csv(summary_by_user_task, output_dir):
    """Save summary as CSV: user,task,execute_count in output_dir/summary.csv"""
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, "summary.csv")
    rows = [(user, task, count) for (user, task), count in summary_by_user_task.items()]
    df = pd.DataFrame(rows, columns=["user", "task", "execute_count"])
    df.to_csv(output_csv, index=False)
    print(f"Summary saved to {output_csv}")


def save_per_user_task_csv(summary_by_user_task, output_dir):
    """
    Save a CSV for each user-task pair in a by_user_task directory, matching study_data structure.
    Each CSV is saved as: by_user_task/user_xx/task_yy/execute_count.csv
    The CSV contains columns: user, task, execute_count
    """
    by_user_task_dir = os.path.join(output_dir, 'by_user_task')
    os.makedirs(by_user_task_dir, exist_ok=True)
    for (user, task), count in summary_by_user_task.items():
        user_dir = os.path.join(by_user_task_dir, f'user_{user}')
        task_dir = os.path.join(user_dir, str(task))
        os.makedirs(task_dir, exist_ok=True)
        file_path = os.path.join(task_dir, 'execute_count.csv')
        # Always write user and task columns for clarity
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user', 'task', 'execute_count'])
            writer.writerow([user, task, count])
    print(f"Per-user-per-task execute event counts written to {by_user_task_dir}")


def log_execution(study_data_folder, output_dir, total_count):
    """Append a log entry to output_dir/execution_log.csv with timestamp, input, output, and event count."""
    log_path = os.path.join(output_dir, 'execution_log.csv')
    log_exists = os.path.exists(log_path)
    with open(log_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not log_exists:
            writer.writerow(['timestamp', 'input_folder', 'output_dir', 'total_execute_events'])
        writer.writerow([
            datetime.datetime.now().isoformat(timespec='seconds'),
            study_data_folder,
            output_dir,
            total_count
        ])


def main():
    if len(sys.argv) < 3:
        print("Usage: python count_execute_events.py [study_data_folder] [output_dir]")
        sys.exit(1)
    study_data_folder = sys.argv[1]
    output_dir = sys.argv[2]
    result = count_execute_events(study_data_folder)
    if result:
        summary_by_user_task, summary_by_user, summary_by_task, total_count = result
        save_summary_csv(summary_by_user_task, output_dir)
        save_per_user_task_csv(summary_by_user_task, output_dir)
        log_execution(study_data_folder, output_dir, total_count)
        print("\n📊 EXECUTE EVENT SUMMARY:")
        print(f"  Total execute events: {total_count:,}")
        print(f"  Users: {len(summary_by_user)}")
        print(f"  Tasks: {len(summary_by_task)}")
        print("\n  By user:")
        for user, count in sorted(summary_by_user.items()):
            print(f"    User {user}: {count}")
        print("\n  By task:")
        for task, count in sorted(summary_by_task.items()):
            print(f"    Task {task}: {count}")

if __name__ == "__main__":
    main()
