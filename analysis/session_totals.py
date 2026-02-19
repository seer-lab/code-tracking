"""
Summarize session totals (minutes) across task CSV files (1_, 2_, 3_, 4_)

Usage:
    python session_totals.py <input_dir_or_file> [-t THRESHOLD_MS] [-o OUTPUT]

This script searches recursively for task CSV files named with prefixes 1_, 2_, 3_, 4_.
For each matching file it calls ActivityAnalyzer.analyze_file_to_actions() to obtain
the "Session total" entry and sums durations (in milliseconds) by task number.

It prints subtotals (minutes) for tasks 1..4 and an overall total per student and
an overall total across all students.
"""
import argparse
from pathlib import Path
import sys
from collections import defaultdict, OrderedDict
import csv
import re

# Ensure the analyzer module in the same directory can be imported when running
# the script from the repo root
repo_dir = Path(__file__).parent
sys.path.insert(0, str(repo_dir))

from activity_analyzer import ActivityAnalyzer


def ms_to_minutes(ms):
    return ms / 60000.0


def format_minutes(ms):
    return f"{ms_to_minutes(ms):.2f}"


def find_task_files(root_path):
    """Find CSV files that look like task recordings (prefix 1_/2_/3_/4_).

    Excludes ide-events files and already-analyzed files.
    Returns a sorted list of Path objects.
    """
    p = Path(root_path)
    files = []
    for f in p.rglob('*.csv'):
        name = f.name
        # skip ide-events and already analyzed files
        if 'ide-events' in name or name.endswith('_analyzed.csv'):
            continue
        # match starting with 1_,2_,3_,4_ (or a leading digit then underscore)
        if re.match(r'^[1-4]_.*\.csv$', name):
            files.append(f)
    files = sorted(set(files))
    return files


def task_prefix_from_name(name):
    # Expect filenames like '1_something.csv' -> return '1'
    if name and '_' in name:
        prefix = name.split('_', 1)[0]
        if prefix.isdigit() and prefix in {'1', '2', '3', '4'}:
            return prefix
    return None


def find_user_from_path(path: Path):
    """Find ancestor directory name that matches user_\d+

    If none found, fall back to parent.parent name when available.
    """
    for anc in path.parents:
        if re.match(r'^user_\d+$', anc.name):
            return anc.name
    # fallback: use the folder two levels up (e.g. study_data/user_x/1/file.csv)
    try:
        return path.parent.parent.name
    except Exception:
        return path.parent.name


def write_csv_output(out_path: Path, summary: dict):
    """Write CSV with columns: user, task1_min, task1_files, task2_min, ..., total_min"""
    headers = ['user']
    for t in ['1', '2', '3', '4']:
        headers.extend([f'task{t}_minutes', f'task{t}_files'])
    headers.append('total_minutes')

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for user, data in summary.items():
            row = {'user': user}
            total = 0
            for t in ['1', '2', '3', '4']:
                ms = data.get('totals_ms', {}).get(t, 0)
                cnt = data.get('counts', {}).get(t, 0)
                row[f'task{t}_minutes'] = format_minutes(ms)
                row[f'task{t}_files'] = cnt
                total += ms
            row['total_minutes'] = format_minutes(total)
            w.writerow(row)


def main():
    parser = argparse.ArgumentParser(description='Summarize session totals across task CSV files')
    parser.add_argument('input', help='Input directory (or single file) to scan for task CSVs')
    parser.add_argument('-t', '--threshold', type=int, default=60000, help='Inactivity threshold (ms) passed to analyzer (default: 60000)')
    parser.add_argument('-o', '--output', help='Optional output CSV file to write the summary')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {args.input} does not exist")
        return

    analyzer = ActivityAnalyzer(inactivity_threshold_ms=args.threshold, log_content=False)

    # Collect files
    if input_path.is_dir():
        files = find_task_files(input_path)
    else:
        # Single file: only include if it's a task file
        files = [input_path] if task_prefix_from_name(input_path.name) in {'1','2','3','4'} else []

    if not files:
        print("No task files (1_/2_/3_/4_) found in the given path.")
        return

    # summary[user] = {'totals_ms': {task: ms}, 'counts': {task: n}}
    summary = OrderedDict()
    overall_totals = defaultdict(int)

    # Process each file
    for f in files:
        prefix = task_prefix_from_name(f.name)
        if not prefix:
            continue
        user = find_user_from_path(f)
        if user not in summary:
            summary[user] = {'totals_ms': defaultdict(int), 'counts': defaultdict(int)}

        try:
            actions = analyzer.analyze_file_to_actions(str(f))
        except Exception as e:
            print(f"Warning: failed to analyze {f}: {e}")
            continue

        if not actions:
            continue

        session_action = next((a for a in actions if a.get('action') == 'Session total'), None)
        if not session_action:
            # fallback: sum durations of actions (not perfect but safe)
            dur = sum([a.get('duration', 0) for a in actions])
        else:
            dur = session_action.get('duration', 0)

        ms = int(dur)
        summary[user]['totals_ms'][prefix] += ms
        summary[user]['counts'][prefix] += 1
        overall_totals[prefix] += ms

    # Print pretty table to console
    lines = []
    header = ["User", "Task1_min", "Task1_files", "Task2_min", "Task2_files", "Task3_min", "Task3_files", "Task4_min", "Task4_files", "Total_min"]
    col_widths = [max(len(h), 12) for h in header]

    # Print header
    hdr_line = "  ".join(h.ljust(w) for h, w in zip(header, col_widths))
    lines.append(hdr_line)
    lines.append('-' * len(hdr_line))

    grand_total_ms = 0
    for user, data in summary.items():
        row_vals = [user]
        total_ms = 0
        for t in ['1', '2', '3', '4']:
            ms = data['totals_ms'].get(t, 0)
            cnt = data['counts'].get(t, 0)
            row_vals.append(format_minutes(ms))
            row_vals.append(str(cnt))
            total_ms += ms
        row_vals.append(format_minutes(total_ms))
        grand_total_ms += total_ms
        # pad/align
        row_line = "  ".join(v.ljust(w) for v, w in zip(row_vals, col_widths))
        lines.append(row_line)

    # overall totals row
    totals_row = ["ALL"]
    overall_ms = 0
    for t in ['1', '2', '3', '4']:
        ms = overall_totals.get(t, 0)
        totals_row.append(format_minutes(ms))
        totals_row.append(str(0))
        overall_ms += ms
    totals_row.append(format_minutes(overall_ms))
    lines.append('-' * len(hdr_line))
    lines.append("  ".join(v.ljust(w) for v, w in zip(totals_row, col_widths)))

    out_text = '\n'.join(lines)
    print(out_text)

    # Optional CSV output
    if args.output:
        out_path = Path(args.output)
        try:
            write_csv_output(out_path, summary)
            print(f"\nCSV summary written to {out_path}")
        except Exception as e:
            print(f"Failed to write CSV output: {e}")


if __name__ == '__main__':
    main()

