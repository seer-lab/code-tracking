"""
Execute Event Counter and Analyzer

Counts and analyzes how often users run their code (Action,Run/RunClass/etc) in study_data IDE event logs.
Provides comprehensive summaries, per-user/per-task breakdowns, and visualizations.

Usage:
python count_execute_events.py [study_data_folder] [output_dir] [--visuals]
"""

import os
import glob
import csv
import pandas as pd
from collections import defaultdict
import datetime
import argparse
import matplotlib.pyplot as plt
import numpy as np

# Poster-friendly save helper (transparent PNG + PDF/SVG)
def save_fig_variants(fig, out_base, dpi=600, transparent=True):
    """Save a figure to PNG (transparent) and vector formats (PDF, SVG) with tight layout.
    out_base: full path without extension (e.g. os.path.join(visuals_dir, 'name'))
    """
    try:
        fig.patch.set_alpha(0)
    except Exception:
        pass
    for ax in getattr(fig, 'axes', []):
        try:
            ax.set_facecolor('none')
        except Exception:
            pass

    png_path = out_base + '.png'
    pdf_path = out_base + '.pdf'
    svg_path = out_base + '.svg'

    # PNG: high-res transparent
    fig.savefig(png_path, dpi=dpi, transparent=transparent, bbox_inches='tight', pad_inches=0.02, facecolor='none')
    # Vector outputs (best for poster printing)
    try:
        fig.savefig(pdf_path, dpi=dpi, transparent=transparent, bbox_inches='tight', pad_inches=0.02, facecolor='none')
        fig.savefig(svg_path, dpi=dpi, transparent=transparent, bbox_inches='tight', pad_inches=0.02, facecolor='none')
    except Exception:
        pass

# Event types that indicate code execution
EXECUTE_ACTIONS = {"Run", "RunClass", "RunAnything"}

# Human-readable names for execute actions
EXECUTE_ACTION_NAMES = {
    "Run": "Run Program",
    "RunClass": "Run Class",
    "RunAnything": "Run Anything"
}

# Global tracking dictionaries
combined_execute_dict = {action: 0 for action in EXECUTE_ACTIONS}
user_execute_dicts = defaultdict(lambda: {action: 0 for action in EXECUTE_ACTIONS})
task_execute_dicts = defaultdict(lambda: {action: 0 for action in EXECUTE_ACTIONS})

# Track detailed execution events with timestamps
detailed_executions = []


def count_execute_events(study_data_folder):
    """
    Count execute events per user, per task, and overall with detailed tracking.
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
                header = next(reader, None)  # Skip header if exists

                for row in reader:
                    if len(row) < 3:
                        continue
                    if row[1] == "Action" and row[2] in EXECUTE_ACTIONS:
                        action_type = row[2]
                        timestamp = row[0] if len(row) > 0 else ""

                        # Update counters
                        summary_by_user_task[(user, task)] += 1
                        summary_by_user[user] += 1
                        summary_by_task[task] += 1
                        total_count += 1

                        # Update global action tracking
                        combined_execute_dict[action_type] += 1
                        user_execute_dicts[user][action_type] += 1
                        task_execute_dicts[task][action_type] += 1

                        # Track detailed execution
                        detailed_executions.append({
                            'timestamp': timestamp,
                            'user': user,
                            'task': task,
                            'action_type': action_type,
                            'action_name': EXECUTE_ACTION_NAMES.get(action_type, action_type)
                        })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return summary_by_user_task, summary_by_user, summary_by_task, total_count


def get_human_readable_name(action):
    """Convert action names to human-readable format"""
    return EXECUTE_ACTION_NAMES.get(action, action)

def combine_action_counts(action_dict):
    """Convert action dictionary to human-readable names"""
    readable = {}
    for action, count in action_dict.items():
        readable_name = get_human_readable_name(action)
        readable[readable_name] = count
    return readable

def write_combined_summary_csv(output_dir, total_count, summary_by_user, summary_by_task):
    """Write comprehensive combined summary with metrics and action breakdown"""
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, "combined_execute_summary.csv")

    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])

            # Overall metrics
            writer.writerow(["=== OVERALL METRICS ===", ""])
            writer.writerow(["Total Execute Events", total_count])
            writer.writerow(["Total Users", len(summary_by_user)])
            writer.writerow(["Total Tasks", len(summary_by_task)])
            writer.writerow(["Average Executions per User", total_count / len(summary_by_user) if summary_by_user else 0])
            writer.writerow(["Average Executions per Task", total_count / len(summary_by_task) if summary_by_task else 0])
            writer.writerow(["", ""])

            # Action type breakdown
            writer.writerow(["=== EXECUTE ACTION TYPES ===", ""])
            readable_actions = combine_action_counts(combined_execute_dict)
            sorted_actions = sorted(readable_actions.items(), key=lambda x: x[1], reverse=True)
            for action, count in sorted_actions:
                if count > 0:
                    writer.writerow([action, count])

        print(f"Combined summary saved to {output_csv}")
    except Exception as e:
        print(f"Error writing combined summary: {e}")

def save_summary_csv(summary_by_user_task, output_dir):
    """Save detailed summary as CSV: user,task,execute_count in output_dir/execute_events_summary.csv"""
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, "execute_events_summary.csv")
    rows = [(user, task, count) for (user, task), count in summary_by_user_task.items()]
    df = pd.DataFrame(rows, columns=["user", "task", "execute_count"])
    df = df.sort_values(['user', 'task'])
    df.to_csv(output_csv, index=False)
    print(f"Detailed summary saved to {output_csv}")


def save_per_user_summaries(summary_by_user, output_dir):
    """Save per-user summaries in summaries/by_user/ directory"""
    by_user_dir = os.path.join(output_dir, 'summaries', 'by_user')
    os.makedirs(by_user_dir, exist_ok=True)

    for user, total_count in summary_by_user.items():
        user_file = os.path.join(by_user_dir, f'user_{user}_execute_summary.csv')

        # Get action breakdown for this user
        action_breakdown = user_execute_dicts[user]
        readable_actions = combine_action_counts(action_breakdown)

        with open(user_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["User", user])
            writer.writerow(["Total Executions", total_count])
            writer.writerow(["", ""])
            writer.writerow(["=== ACTION BREAKDOWN ===", ""])
            for action, count in sorted(readable_actions.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    writer.writerow([action, count])

    print(f"Per-user summaries saved to {by_user_dir}")

def save_per_task_summaries(summary_by_task, output_dir):
    """Save per-task summaries in summaries/by_task/ directory"""
    by_task_dir = os.path.join(output_dir, 'summaries', 'by_task')
    os.makedirs(by_task_dir, exist_ok=True)

    for task, total_count in summary_by_task.items():
        task_file = os.path.join(by_task_dir, f'task_{task}_execute_summary.csv')

        # Get action breakdown for this task
        action_breakdown = task_execute_dicts[task]
        readable_actions = combine_action_counts(action_breakdown)

        with open(task_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Task", task])
            writer.writerow(["Total Executions", total_count])
            writer.writerow(["", ""])
            writer.writerow(["=== ACTION BREAKDOWN ===", ""])
            for action, count in sorted(readable_actions.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    writer.writerow([action, count])

    print(f"Per-task summaries saved to {by_task_dir}")

def save_per_user_task_csv(summary_by_user_task, output_dir):
    """
    Save a CSV for each user-task pair in a user_xx/task directory, matching study_data structure.
    Each CSV is saved as: user_xx/task/execute_count.csv
    The CSV contains columns: user, task, execute_count
    """
    for (user, task), count in summary_by_user_task.items():
        user_dir = os.path.join(output_dir, f'user_{user}')
        task_dir = os.path.join(user_dir, str(task))
        os.makedirs(task_dir, exist_ok=True)
        file_path = os.path.join(task_dir, 'execute_count.csv')
        # Always write user and task columns for clarity
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user', 'task', 'execute_count'])
            writer.writerow([user, task, count])
    print(f"Per-user-per-task execute event counts written to individual folders")


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


def save_detailed_executions(output_dir):
    """Save detailed execution events to CSV"""
    if detailed_executions:
        detailed_file = os.path.join(output_dir, 'detailed_execute_events.csv')
        df = pd.DataFrame(detailed_executions)
        df.to_csv(detailed_file, index=False)
        print(f"Detailed execution events saved to {detailed_file}")

def create_visuals(output_dir, summary_by_user, summary_by_task, summary_by_user_task, total_count):
    """Create comprehensive visualizations for execute events"""
    visuals_dir = os.path.join(output_dir, 'visuals')
    os.makedirs(visuals_dir, exist_ok=True)

    try:
        # Poster-friendly rcParams (larger fonts, cleaner look)
        import matplotlib as mpl
        mpl.rcParams.update({
            'font.size': 14,
            'axes.titlesize': 18,
            'axes.labelsize': 16,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'legend.fontsize': 12,
            'figure.dpi': 300
        })

        # 1. Combined execute action types bar chart
        combined_file = os.path.join(output_dir, 'combined_execute_summary.csv')
        if os.path.exists(combined_file):
            df_comb = pd.read_csv(combined_file)
            if not df_comb.empty:
                # Find action types section
                action_start_idx = None
                for idx, row in df_comb.iterrows():
                    if row['Metric'] == '=== EXECUTE ACTION TYPES ===':
                        action_start_idx = idx + 1
                        break

                if action_start_idx is not None:
                    action_data = df_comb.iloc[action_start_idx:].copy()
                    action_data = action_data[action_data['Metric'].notna() & (action_data['Metric'] != '')]

                    if not action_data.empty:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        colors = ['#e74c3c', '#3498db', '#2ecc71']
                        bars = ax.bar(action_data['Metric'].astype(str), action_data['Value'].astype(int),
                                     color=colors[:len(action_data)], edgecolor='black', linewidth=1.2, alpha=0.8)
                        ax.set_xlabel('Execute Action Type', fontsize=12, fontweight='bold')
                        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
                        ax.set_title('Execute Action Type Distribution',
                                    fontsize=14, fontweight='bold', pad=20)
                        plt.xticks(rotation=45, ha='right')
                        ax.grid(axis='y', alpha=0.3)

                        # Add value labels on bars
                        for bar in bars:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height,
                                   f'{int(height):,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

                        plt.tight_layout()
                        out_actions_base = os.path.join(visuals_dir, 'execute_action_types')
                        save_fig_variants(fig, out_actions_base, dpi=600)
                        plt.close()
                        print(f"Saved action types visualization to {out_actions_base}.png and vector formats")

        # 2. Execute events by user (enhanced bar chart)
        if summary_by_user:
            users_sorted = sorted(summary_by_user.items(), key=lambda x: x[1], reverse=True)
            users = [f"User {u}" for u, _ in users_sorted]
            counts = [c for _, c in users_sorted]

            fig, ax = plt.subplots(figsize=(max(12, len(users) * 0.5), 7))
            bars = ax.bar(users, counts, color='#3498db', edgecolor='darkblue', linewidth=1.2, alpha=0.8)
            ax.set_xlabel('User', fontsize=12, fontweight='bold')
            ax.set_ylabel('Execute Count', fontsize=12, fontweight='bold')
            ax.set_title(f'Code Executions by User (Total: {total_count:,})',
                        fontsize=14, fontweight='bold', pad=20)
            plt.xticks(rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height):,}', ha='center', va='bottom', fontsize=9)

            plt.tight_layout()
            out_user_base = os.path.join(visuals_dir, 'execute_by_user')
            save_fig_variants(fig, out_user_base, dpi=600)
            plt.close()
            print(f"Saved user visualization to {out_user_base}.png and vector formats")

        # 3. Execute events by task (enhanced bar chart)
        if summary_by_task:
            tasks_sorted = sorted(summary_by_task.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0)
            tasks = [f"Task {t}" for t, _ in tasks_sorted]
            counts = [c for _, c in tasks_sorted]

            fig, ax = plt.subplots(figsize=(max(12, len(tasks) * 0.5), 7))
            bars = ax.bar(tasks, counts, color='#e74c3c', edgecolor='darkred', linewidth=1.2, alpha=0.8)
            ax.set_xlabel('Task', fontsize=12, fontweight='bold')
            ax.set_ylabel('Execute Count', fontsize=12, fontweight='bold')
            ax.set_title(f'Code Executions by Task (Total: {total_count:,})',
                        fontsize=14, fontweight='bold', pad=20)
            plt.xticks(rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height):,}', ha='center', va='bottom', fontsize=9)

            plt.tight_layout()
            out_task_base = os.path.join(visuals_dir, 'execute_by_task')
            save_fig_variants(fig, out_task_base, dpi=600)
            plt.close()
            print(f"Saved task visualization to {out_task_base}.png and vector formats")

        # 4. Heatmap of user x task executions
        if summary_by_user_task:
            # Create matrix for heatmap
            users = sorted(set(u for u, t in summary_by_user_task.keys()))
            tasks = sorted(set(t for u, t in summary_by_user_task.keys()), key=lambda x: int(x) if x.isdigit() else 0)

            matrix = np.zeros((len(users), len(tasks)))
            for i, user in enumerate(users):
                for j, task in enumerate(tasks):
                    matrix[i, j] = summary_by_user_task.get((user, task), 0)

            fig, ax = plt.subplots(figsize=(max(12, len(tasks) * 0.6), max(8, len(users) * 0.4)))
            im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')

            # Set ticks and labels
            ax.set_xticks(np.arange(len(tasks)))
            ax.set_yticks(np.arange(len(users)))
            ax.set_xticklabels([f"Task {t}" for t in tasks])
            ax.set_yticklabels([f"User {u}" for u in users])

            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Execute Count', rotation=270, labelpad=20, fontweight='bold')

            # Add text annotations
            for i in range(len(users)):
                for j in range(len(tasks)):
                    text_color = 'white' if matrix[i, j] > matrix.max() / 2 else 'black'
                    text = ax.text(j, i, int(matrix[i, j]),
                                 ha="center", va="center", color=text_color, fontsize=8)

            ax.set_title('Execute Events Heatmap: User × Task', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Task', fontsize=12, fontweight='bold')
            ax.set_ylabel('User', fontsize=12, fontweight='bold')

            plt.tight_layout()
            out_heatmap_base = os.path.join(visuals_dir, 'execute_heatmap')
            save_fig_variants(fig, out_heatmap_base, dpi=600)
            plt.close()
            print(f"Saved heatmap visualization to {out_heatmap_base}.png and vector formats")

        # 5. Distribution analysis - executions per user
        if summary_by_user:
            counts = list(summary_by_user.values())

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

            # Histogram
            ax1.hist(counts, bins=min(20, len(set(counts))), color='#3498db', edgecolor='black', alpha=0.7)
            ax1.set_xlabel('Execute Count', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Number of Users', fontsize=12, fontweight='bold')
            ax1.set_title('Distribution of Execute Counts per User', fontsize=13, fontweight='bold')
            ax1.grid(axis='y', alpha=0.3)
            ax1.axvline(np.mean(counts), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(counts):.1f}')
            ax1.axvline(np.median(counts), color='green', linestyle='--', linewidth=2, label=f'Median: {np.median(counts):.1f}')
            ax1.legend()

            # Box plot
            ax2.boxplot(counts, vert=True)
            ax2.set_ylabel('Execute Count', fontsize=12, fontweight='bold')
            ax2.set_title('Execute Count Distribution (Box Plot)', fontsize=13, fontweight='bold')
            ax2.grid(axis='y', alpha=0.3)

            # Add statistics text
            stats_text = f"Min: {min(counts)}\nMax: {max(counts)}\nMean: {np.mean(counts):.1f}\nMedian: {np.median(counts):.1f}\nStd: {np.std(counts):.1f}"
            ax2.text(1.15, 0.5, stats_text, transform=ax2.transAxes, fontsize=10,
                    verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            plt.tight_layout()
            out_dist_base = os.path.join(visuals_dir, 'execute_distribution_users')
            save_fig_variants(fig, out_dist_base, dpi=600)
            plt.close()
            print(f"Saved distribution visualization to {out_dist_base}.png and vector formats")

        # 6. Distribution analysis - executions per task
        if summary_by_task:
            counts = list(summary_by_task.values())

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

            # Histogram
            ax1.hist(counts, bins=min(20, len(set(counts))), color='#e74c3c', edgecolor='black', alpha=0.7)
            ax1.set_xlabel('Execute Count', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Number of Tasks', fontsize=12, fontweight='bold')
            ax1.set_title('Distribution of Execute Counts per Task', fontsize=13, fontweight='bold')
            ax1.grid(axis='y', alpha=0.3)
            ax1.axvline(np.mean(counts), color='blue', linestyle='--', linewidth=2, label=f'Mean: {np.mean(counts):.1f}')
            ax1.axvline(np.median(counts), color='green', linestyle='--', linewidth=2, label=f'Median: {np.median(counts):.1f}')
            ax1.legend()

            # Box plot
            ax2.boxplot(counts, vert=True)
            ax2.set_ylabel('Execute Count', fontsize=12, fontweight='bold')
            ax2.set_title('Execute Count Distribution (Box Plot)', fontsize=13, fontweight='bold')
            ax2.grid(axis='y', alpha=0.3)

            # Add statistics text
            stats_text = f"Min: {min(counts)}\nMax: {max(counts)}\nMean: {np.mean(counts):.1f}\nMedian: {np.median(counts):.1f}\nStd: {np.std(counts):.1f}"
            ax2.text(1.15, 0.5, stats_text, transform=ax2.transAxes, fontsize=10,
                    verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            plt.tight_layout()
            out_dist_task_base = os.path.join(visuals_dir, 'execute_distribution_tasks')
            save_fig_variants(fig, out_dist_task_base, dpi=600)
            plt.close()
            print(f"Saved task distribution visualization to {out_dist_task_base}.png and vector formats")

        print("\n✅ All visualizations created successfully!")

    except Exception as e:
        print(f"Error creating visuals: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description='Count and analyze execute events with comprehensive summaries and visualizations')
    parser.add_argument('study_data_folder', help='Path to study_data folder')
    parser.add_argument('output_dir', help='Folder to write CSV summaries and optional visuals')
    parser.add_argument('--visuals', action='store_true', help='Generate comprehensive visualization PNGs')
    args = parser.parse_args()

    result = count_execute_events(args.study_data_folder)
    if result:
        summary_by_user_task, summary_by_user, summary_by_task, total_count = result

        # Write all summaries
        write_combined_summary_csv(args.output_dir, total_count, summary_by_user, summary_by_task)
        save_summary_csv(summary_by_user_task, args.output_dir)
        save_per_user_summaries(summary_by_user, args.output_dir)
        save_per_task_summaries(summary_by_task, args.output_dir)
        save_per_user_task_csv(summary_by_user_task, args.output_dir)
        save_detailed_executions(args.output_dir)
        log_execution(args.study_data_folder, args.output_dir, total_count)

        # Print comprehensive summary
        print("\n📊 EXECUTE EVENT SUMMARY:")
        print(f"  Total execute events: {total_count:,}")
        print(f"  Total users: {len(summary_by_user)}")
        print(f"  Total tasks: {len(summary_by_task)}")
        print(f"  Average per user: {total_count / len(summary_by_user):.1f}")
        print(f"  Average per task: {total_count / len(summary_by_task):.1f}")

        # Action type breakdown
        print("\n🎯 EXECUTE ACTION TYPES:")
        readable_actions = combine_action_counts(combined_execute_dict)
        for action, count in sorted(readable_actions.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / total_count * 100) if total_count > 0 else 0
                print(f"  {action}: {count:,} ({percentage:.1f}%)")

        print("\n👥 TOP USERS BY EXECUTIONS:")
        for user, count in sorted(summary_by_user.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  User {user}: {count:,}")

        print("\n📋 TOP TASKS BY EXECUTIONS:")
        for task, count in sorted(summary_by_task.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  Task {task}: {count:,}")

        print("\n✅ Successfully created:")
        print(f"  - Combined summary in {args.output_dir}")
        print(f"  - Per-user summaries in summaries/by_user/")
        print(f"  - Per-task summaries in summaries/by_task/")
        print(f"  - Detailed events log")

        # Create visualizations if requested
        if args.visuals:
            print("\n🎨 Creating visualizations...")
            create_visuals(args.output_dir, summary_by_user, summary_by_task, summary_by_user_task, total_count)

if __name__ == "__main__":
    main()
