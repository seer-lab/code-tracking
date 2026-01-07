"""
Timeline Plot Generator with Multi-User and Task Segmentation

This script visualizes coding activity logs from CSV files as horizontal timeline plots.
Each user is plotted on the y-axis, with actions rendered as colored bars along the x-axis
based on their duration. Gradients reflect code content length, and compilation-related
actions are marked with visual symbols. Inactivity appears naturally as gaps.

The script processes up to four tasks and combines all relevant CSV files from the specified
input directory. User and task information is extracted from metadata or filenames.

Usage:
python activity_plot.py [--input input_path] [--output output_path]
"""


# Group together the actions with a colour legend (each action is a different colour
# all users should appear in one plot (y-axis) and with the duration (x-axis)
# each plot should cover one task - four different plots
# gradient can be used for how much code is included in a given action
# a symbol or marker for certain activities - do this for compilations
# include gaps for inactivity

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import argparse
from pathlib import Path
import re

# ─────────────────────────────────────────────
# Parse command-line arguments
# ─────────────────────────────────────────────
parser = argparse.ArgumentParser(description='Generate timeline plots from CSV files.')
parser.add_argument('--input', type=str, required=True, help='Path to folder containing CSV files')
parser.add_argument('--output', type=str, default='./plots', help='Optional path to output folder for saving plots')
args = parser.parse_args()

input_folder = Path(args.input)
output_folder = Path(args.output)
output_folder.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# Color map from previous logic (same as before)
# ─────────────────────────────────────────────
ACTION_COLOR_MAP = {
    # [insert the full ACTION_COLOR_MAP here as before]
    'Gained Focus': '#4C72B0',
    'Lost Focus': '#4C72B0',
    'New Project': '#55A868',
    'No Project': '#55A868',
    'New Python File': '#55A868',
    'Save File': '#55A868',
    'Save All': '#55A868',
    'Run': '#DD8452',
    'Rerun': '#DD8452',
    'Run Class': '#DD8452',
    'Choose Run Configuration': '#DD8452',
    'Debug': '#C44E52',
    'Debug Class': '#C44E52',
    'Resume debug': '#C44E52',
    'Stop debug/run': '#C44E52',
    'Step into (debugging)': '#C44E52',
    'Toggle Line Breakpoint': '#C44E52',
    'Compile': '#8C564B',
    'Compilation Finished': '#8C564B',
    'Copy': '#937860',
    'Paste': '#DA8BC3',
    'Cut': '#B07AA1',
    'Undo': '#7F7F7F',
    'Redo': '#9C9C9C',
    'Duplicate Line': '#64B5CD',
    'Split Line': '#64B5CD',
    'Reformat Code': '#64B5CD',
    'Create New Element': '#64B5CD',
    'Choose Autocomplete Item': '#4D9DE0',
    'Accept Inline Completion': '#4D9DE0',
    # Make all arrow and simple-edit keys darker and grouped so they're more visible
    'Left Arrow': '#6E6E6E',
    'Right Arrow': '#6E6E6E',
    'Up Arrow': '#6E6E6E',
    'Down Arrow': '#6E6E6E',
    'Enter': '#6E6E6E',
    'Tab': '#6E6E6E',
    'Backspace': '#6E6E6E',
    'Delete': '#6E6E6E',
    'Select Left': '#C7C7C7',
    'Select Right': '#C7C7C7',
    'Search Everywhere': '#E5AE38',
    'Show Popup Menu': '#E5AE38',
    'Copy File Path': '#E5AE38',
}

MARKER_ACTIONS = ['Compile', 'Compilation Finished']
EXCLUDE_ACTIONS = ['Session started', 'Session total']

# Define a set of actions that should be more visible (darker baseline alpha)
DARK_ACTIONS = {'Left Arrow', 'Right Arrow', 'Up Arrow', 'Down Arrow', 'Enter', 'Tab', 'Backspace', 'Delete'}

ARROW_ACTIONS = {'Left Arrow', 'Right Arrow', 'Up Arrow', 'Down Arrow'}
EDIT_ACTIONS = {'Enter', 'Tab', 'Backspace', 'Delete'}

# ─────────────────────────────────────────────
# Load all CSVs in folder
# ─────────────────────────────────────────────
all_csvs = list(input_folder.glob('*.csv'))
if not all_csvs:
    print(f"No CSV files found in {input_folder}")
    exit()

df_list = []

for file in all_csvs:
    temp = pd.read_csv(file)
    temp['source_file'] = file.stem

    # Ensure required columns
    temp = temp[temp['duration_sec'] > 0]
    temp['action'] = temp['action'].fillna('Unknown')
    temp['content'] = temp['content'].fillna('')
    temp['content_length'] = temp['content'].apply(len)

    # Extract user/task from details or fallback to filename
    temp['user'] = temp['details'].str.extract(r'User: (\w+)', expand=False)
    temp['task'] = temp['details'].str.extract(r'Task: (\w+)', expand=False)

    # Use filename parts as sensible defaults for any missing values (fill per-row)
    default_user = file.stem.split('_')[0]
    default_task = file.stem.split('_')[1] if '_' in file.stem else 'Task4'

    temp['user'] = temp['user'].fillna(default_user)
    temp['task'] = temp['task'].fillna(default_task)

    df_list.append(temp)

# Combine and filter
df = pd.concat(df_list, ignore_index=True)
df = df[~df['action'].isin(EXCLUDE_ACTIONS)]

# Ensure task column is string and has no NaNs
df['task'] = df['task'].astype(str)

# ─────────────────────────────────────────────
# Normalize for alpha based on content length (robust to vmin == vmax)
# ─────────────────────────────────────────────
vmin = df['content_length'].min()
vmax = df['content_length'].max()
if pd.isna(vmin) or pd.isna(vmax):
    # no content length information; use default small range
    vmin, vmax = 0, 1
if vmax == vmin:
    vmax = max(1, vmin)
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

# Helper: natural sort key for users like 'student1', 'student2', ...
def natural_user_key(s):
    m = re.match(r'^(.*?)(\d+)$', str(s))
    if m:
        prefix, num = m.group(1).lower(), int(m.group(2))
        return (prefix, num)
    return (str(s).lower(), 0)

# Build a global user list so every plot shows the same y-axis ordering
all_users = pd.unique(df['user'])
sorted_all_users = sorted(all_users, key=natural_user_key)
global_user_map = {user: i for i, user in enumerate(sorted_all_users)}

# ─────────────────────────────────────────────
# Plot up to 4 tasks
# ─────────────────────────────────────────────
unique_tasks = [t for t in pd.unique(df['task']) if str(t).lower() != 'nan'][:4]

for task in unique_tasks:
    task_df = df[df['task'] == task].copy()
    if task_df.empty:
        # nothing to plot for this task
        continue

    # Use the global user map so all users appear on each plot
    task_df['y_pos'] = task_df['user'].map(global_user_map)

    # calculate a sensible figure height (min height to accommodate labels)
    height = max(3.0, 0.6 + 0.6 * len(sorted_all_users))
    fig, ax = plt.subplots(figsize=(14, height))

    for _, row in task_df.iterrows():
        color = ACTION_COLOR_MAP.get(row['action'], 'gray')

        # Gradient (alpha) based on content length. Use a higher baseline alpha for
        # DARK_ACTIONS so arrow/edit keys are more visible even when content_length is low.
        base = norm(row['content_length']) if row['content_length'] > 0 else 0.0
        if row['action'] in DARK_ACTIONS:
            # darker baseline (min 0.4) and scale up with content (darker overall)
            alpha = 0.4 + 0.6 * base
        else:
            # default baseline (min 0.15)
            alpha = 0.15 + 0.85 * base
        # cap
        alpha = min(1.0, max(0.05, alpha))

        ax.barh(
            y=row['y_pos'],
            left=row['start_sec'],
            width=row['duration_sec'],
            color=color,
            edgecolor='black',
            alpha=alpha
        )

        if row['action'] in MARKER_ACTIONS:
            ax.plot(
                row['start_sec'] + row['duration_sec'] / 2,
                row['y_pos'],
                marker='o',
                color='black',
                markersize=6
            )

    # Axis & legend
    ax.set_yticks(list(global_user_map.values()))
    ax.set_yticklabels(list(global_user_map.keys()))
    ax.set_xlabel('Time (seconds)')
    ax.set_title(f'Timeline of Actions – {task}')

    # Make legend only for actions actually present in this task
    present_actions = set(task_df['action'].unique())

    # Build grouped legend handles: arrows combined, edit keys combined, others individually
    legend_handles = []

    # Arrows grouped
    if present_actions & ARROW_ACTIONS:
        arrow_color = ACTION_COLOR_MAP.get('Left Arrow', '#6E6E6E')
        legend_handles.append(mpatches.Patch(color=arrow_color, label='Arrow keys'))

    # Edit keys grouped
    if present_actions & EDIT_ACTIONS:
        edit_color = ACTION_COLOR_MAP.get('Enter', '#6E6E6E')
        legend_handles.append(mpatches.Patch(color=edit_color, label='Edit keys'))

    # Add the remaining individual actions (exclude ones already grouped)
    for action, color in ACTION_COLOR_MAP.items():
        if action in ARROW_ACTIONS or action in EDIT_ACTIONS:
            continue
        if action in present_actions:
            legend_handles.append(mpatches.Patch(color=color, label=action))

    if legend_handles:
        ax.legend(handles=legend_handles, title='Action', bbox_to_anchor=(1.02, 1), loc='upper left')

    # invert y-axis so the first (student1) is at the top
    ax.invert_yaxis()

    # Improve layout: reserve right margin for legend and ensure top/bottom padding
    plot_path = output_folder / f'timeline_{task}.png'
    fig.subplots_adjust(right=0.78, top=0.95, bottom=0.08)
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"[✔] Saved plot for task '{task}' → {plot_path}")
    plt.close()
