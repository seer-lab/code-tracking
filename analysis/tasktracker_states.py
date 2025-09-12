"""
TaskTracker States Time Script

This script processes CSV files containing IDE state data and calculates the total duration of states
and individual state sessions. It groups consecutive same states into single sessions.

Usage:
python tasktracker_states.py [input_file_or_folder] [output_folder]
"""
import csv
import glob
import os
import sys
from collections import defaultdict
from datetime import datetime

import tasktracker

# Dictionaries for total time in each state (cumulative)
combined_state_dict = {state: 0 for state in tasktracker.states}
user_state_dict = defaultdict(lambda: {state: 0 for state in tasktracker.states})
task_state_dict = defaultdict(lambda: {state: 0 for state in tasktracker.states})

# Lists for individual state sessions (grouped consecutive same states)
all_state_changes = []
user_state_changes = defaultdict(list)
task_state_changes = defaultdict(list)

def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python tasktracker_states.py [input_file_or_folder] [output_folder]")
        print("Example: python tasktracker_states.py data/user_24/ide-events.csv output/")
        print("Example: python tasktracker_states.py study_data/ output/")
        sys.exit(1)

    input_path = sys.argv[1]
    output_folder = sys.argv[2]

    time_states(input_path, output_folder)
    print('TaskTracker states analysis complete!')

def time_states(input_path, output_folder):
    """
    Main function to time the states from IDE event files
    Args:
        input_path: Path to single file or folder containing CSV files
        output_folder: Where to save the results CSV
    """
    # Create output folder structure
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'by_user'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'by_task'), exist_ok=True)

    if os.path.isfile(input_path):
        print(f"Processing single file: {input_path}")
        read_csv(input_path)
        # Write both types of summaries
        write_csv(os.path.join(output_folder, 'combined_state_totals.csv'), combined_state_dict)
        write_state_changes_csv(os.path.join(output_folder, 'combined_state_sessions.csv'), all_state_changes)
    else:
        user_folders = glob.glob(os.path.join(input_path, 'user_*'))
        print(f"Found {len(user_folders)} user folders")

        if not user_folders:
            print("No user folders found")
            return

        ide_files = glob.glob(os.path.join(input_path, '**', '*ide-events*.csv'), recursive=True)
        print(f"Found {len(ide_files)} IDE event files")

        if not ide_files:
            print("No IDE event files found")
            return

        for ide_file in ide_files:
            read_csv(ide_file)

        write_all_summaries(output_folder)

def read_csv(ide_file):
    """
    Read a single CSV file and calculate state durations, grouping consecutive same states
    Args:
        ide_file: Path to the CSV file to process
    """
    try:
        print(f"Processing file: {ide_file}")

        user_info, task_info = extract_user_task_from_path(ide_file)

        with open(ide_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)

            # Variables for session tracking
            current_session_state = None
            current_session_start = None
            row_count = 0
            sessions_count = 0

            for row in reader:
                row_count += 1

                if len(row) > 2:
                    # Get current timestamp
                    timestamp_str = row[0]
                    event_type = row[1]  # "IdeState" or "Action"
                    value = row[2]       # State name or action name

                    # Determine current state
                    if event_type == "IdeState":
                        # Explicit state change
                        if value in tasktracker.states:
                            current_state = value
                        else:
                            continue  # Skip unknown states
                    elif event_type == "Action":
                        # Action implies Active state (assuming Active is in tasktracker.states)
                        current_state = "Active"  # You might need to adjust this to match your states list
                    else:
                        continue  # Skip other event types

                    # Parse timestamp
                    try:
                        # Try common timestamp formats
                        if 'T' in timestamp_str:
                            current_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        else:
                            current_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            current_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            continue  # Skip rows with unparseable timestamps

                    # Check if we need to end the current session
                    if current_session_state is not None and current_state != current_session_state:
                        # End the previous session
                        end_previous_session(current_session_state, current_session_start, current_timestamp,
                                           user_info, task_info)
                        sessions_count += 1

                    # Start new session if state changed or if this is the first state
                    if current_state != current_session_state:
                        current_session_state = current_state
                        current_session_start = current_timestamp

            # End the final session if there was one
            if current_session_state is not None and current_session_start is not None:
                # Use the last timestamp as the end (this is an approximation)
                end_previous_session(current_session_state, current_session_start, current_timestamp,
                                   user_info, task_info)
                sessions_count += 1

            print(f"  Processed {row_count} rows, found {sessions_count} state sessions")

    except Exception as e:
        print(f"Error parsing {ide_file}: {e}")

def end_previous_session(state, start_time, end_time, user_info, task_info):
    """
    End a state session and record the duration
    Args:
        state: The state that ended
        start_time: When the session started
        end_time: When the session ended
        user_info: User identifier
        task_info: Task identifier
    """
    duration_seconds = (end_time - start_time).total_seconds()

    # Only count positive durations
    if duration_seconds > 0:
        # Add to total time dictionaries
        combined_state_dict[state] += duration_seconds
        if user_info:
            user_state_dict[user_info][state] += duration_seconds
        if task_info:
            task_state_dict[task_info][state] += duration_seconds

        # Record individual state session
        state_session = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'state': state,
            'duration_seconds': duration_seconds,
            'user': user_info,
            'task': task_info
        }

        all_state_changes.append(state_session)
        if user_info:
            user_state_changes[user_info].append(state_session)
        if task_info:
            task_state_changes[task_info].append(state_session)

def extract_user_task_from_path(file_path):
    """
    Extract user and task information from file path
    Expected structure: study_data/user_25/1/.../*.csv
    Args:
        file_path: Full path to the CSV file
    Returns:
        tuple: (user_info, task_info) where task_info includes both user and task
    """
    path_parts = file_path.replace('\\', '/').split('/')

    user_info = None
    task_info = None

    # Find user folder and the task folder that follows it
    for i, part in enumerate(path_parts):
        if part.startswith('user_'):
            user_info = part

            # Look for the task number in the next directory
            if i + 1 < len(path_parts):
                next_part = path_parts[i + 1]
                # Check if next part is a number (task number)
                if next_part.isdigit():
                    task_info = f"{user_info}_{next_part}"
                    break
                # If not a digit, might be a folder name containing task info
                elif 'task' in next_part.lower() or next_part.isalnum():
                    task_info = f"{user_info}_{next_part}"
                    break

    return user_info, task_info

def write_csv(output_file, state_dict):
    """
    Write the total state times to a CSV file
    Args:
        output_file: Path where to save the results CSV
        state_dict: Dictionary with state total times
    """
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header row
            writer.writerow(["State", "Total_Seconds", "Total_Minutes", "Total_Hours"])

            # Sort states by total time (highest first)
            sorted_states = sorted(state_dict.items(), key=lambda x: x[1], reverse=True)

            # Only write states that have time > 0
            for state, total_seconds in sorted_states:
                if total_seconds > 0:
                    total_minutes = total_seconds / 60
                    total_hours = total_seconds / 3600
                    writer.writerow([state, f"{total_seconds:.2f}", f"{total_minutes:.2f}", f"{total_hours:.2f}"])

    except Exception as e:
        print(f"Error writing {output_file}: {e}")

def write_state_changes_csv(output_file, state_changes):
    """
    Write individual state sessions to a CSV file
    Args:
        output_file: Path where to save the results CSV
        state_changes: List of state session dictionaries
    """
    try:
        if not state_changes:
            return

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header row
            writer.writerow(["Start_Time", "End_Time", "State", "Duration_Seconds", "Duration_Minutes", "User", "Task"])

            # Sort by start time
            sorted_changes = sorted(state_changes, key=lambda x: x['start_time'])

            for change in sorted_changes:
                duration_minutes = change['duration_seconds'] / 60
                writer.writerow([
                    change['start_time'],
                    change['end_time'],
                    change['state'],
                    f"{change['duration_seconds']:.2f}",
                    f"{duration_minutes:.2f}",
                    change['user'],
                    change['task']
                ])

    except Exception as e:
        print(f"Error writing {output_file}: {e}")

def write_all_summaries(output_folder):
    """
    Write all summary files: combined, by user, and by task
    Args:
        output_folder: Base output folder
    """
    # Write combined summaries
    print("Writing combined summaries...")
    combined_totals_file = os.path.join(output_folder, 'combined_state_totals.csv')
    combined_sessions_file = os.path.join(output_folder, 'combined_state_sessions.csv')
    write_csv(combined_totals_file, combined_state_dict)
    write_state_changes_csv(combined_sessions_file, all_state_changes)

    # Write user summaries
    print(f"Writing {len(user_state_dict)} user summaries...")
    for user, user_dict in user_state_dict.items():
        # Total times
        user_totals_file = os.path.join(output_folder, 'by_user', f'{user}_state_totals.csv')
        write_csv(user_totals_file, user_dict)

        # Individual sessions
        user_sessions_file = os.path.join(output_folder, 'by_user', f'{user}_state_sessions.csv')
        write_state_changes_csv(user_sessions_file, user_state_changes[user])

    # Write task summaries with user subdirectories
    print(f"Writing {len(task_state_dict)} task summaries...")
    for task, task_dict in task_state_dict.items():
        # Extract user from task name
        user_part = '_'.join(task.split('_')[:2])

        # Create user subdirectory in by_task folder
        user_task_folder = os.path.join(output_folder, 'by_task', user_part)
        os.makedirs(user_task_folder, exist_ok=True)

        # Total times
        task_totals_file = os.path.join(user_task_folder, f'{task}_state_totals.csv')
        write_csv(task_totals_file, task_dict)

        # Individual sessions
        task_sessions_file = os.path.join(user_task_folder, f'{task}_state_sessions.csv')
        write_state_changes_csv(task_sessions_file, task_state_changes[task])

    # Print summary
    total_sessions = len(all_state_changes)
    total_time = sum(combined_state_dict.values())
    print(f"Successfully created:")
    print(f"  - Combined summaries ({total_sessions} state sessions, {total_time/3600:.2f} total hours)")
    print(f"  - {len(user_state_dict)} user summaries")
    print(f"  - {len(task_state_dict)} task summaries organized by user")

if __name__ == '__main__':
    main()