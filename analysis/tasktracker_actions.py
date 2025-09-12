"""
TaskTracker Actions Count Script

This script processes CSV files containing IDE event data and counts occurrences of specific
actions defined in the tasktracker_actions module. It can process single files or batch
process entire directory structures, generating multiple summary reports.

Usage:
python tasktracker_actions.py [input_file_or_folder] [output_folder]
"""

import csv
import glob
import os
import sys
from collections import defaultdict

# Import the actions list from external module
import tasktracker

# Initialize dictionaries with all actions set to count of 0
combined_action_dict = {action: 0 for action in tasktracker.actions}
user_action_dicts = defaultdict(lambda: {action: 0 for action in tasktracker.actions})
task_action_dicts = defaultdict(lambda: {action: 0 for action in tasktracker.actions})

def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python tasktracker_actions.py [input_file_or_folder] [output_folder]")
        print("Example: python tasktracker_actions.py data/user_24/ide-events.csv output/")
        print("Example: python tasktracker_actions.py study_data/ output/")
        sys.exit(1)

    input_path = sys.argv[1]
    output_folder = sys.argv[2]

    count_actions(input_path, output_folder)
    print('TaskTracker action list complete!')

def count_actions(input_path, output_folder):
    """
    Main function to count actions from IDE event files
    Args:
        input_path: Path to single file or folder containing CSV files
        output_folder: Where to save the results CSV
    """
    # Create output folder structure
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'by_user'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'by_task'), exist_ok=True)

    # Check if input is a single file or folder
    if os.path.isfile(input_path):
        # Single file processing
        print(f"Processing single file: {input_path}")
        read_csv(input_path)
        # For single file, create combined summary only
        write_csv(os.path.join(output_folder, 'combined_action_counts.csv'), combined_action_dict)
    else:
        # Batch processing - look for user folders
        user_folders = glob.glob(os.path.join(input_path, 'user_*'))
        print(f"Found {len(user_folders)} user folders")

        # Exit if no user folders found (for batch processing)
        if not user_folders:
            print("No user folders found")
            return

        # Find all CSV files that contain "ide-events" in their name
        # Uses recursive search to find files in nested subdirectories
        ide_files = glob.glob(os.path.join(input_path, '**', '*ide-events*.csv'), recursive=True)
        print(f"Found {len(ide_files)} IDE event files")

        # Exit if no IDE files found
        if not ide_files:
            print("No IDE event files found")
            return

        # Process each IDE file found
        for ide_file in ide_files:
            read_csv(ide_file)

        # Write all the different summary files
        write_all_summaries(output_folder)


def read_csv(ide_file):
    """
    Read a single CSV file and count actions
    Args:
        ide_file: Path to the CSV file to process
    """
    try:
        print(f"Processing file: {ide_file}")

        # Extract user and task info from file path
        user_info, task_info = extract_user_task_from_path(ide_file)

        with open(ide_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)

            # Process each row in the CSV
            for row in reader:
                # Make sure row has at least 3 columns (index 2 exists)
                if len(row) > 2:
                    action_value = row[2]  # Get action from column 2 (0-indexed)

                    # If this action matches one in our dictionary, increment counts
                    if action_value in combined_action_dict:
                        # Increment combined total
                        combined_action_dict[action_value] += 1

                        # Increment user-specific count
                        if user_info:
                            user_action_dicts[user_info][action_value] += 1

                        # Increment task-specific count
                        if task_info:
                            task_action_dicts[task_info][action_value] += 1

    except Exception as e:
        print(f"Error parsing {ide_file}: {e}")


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


def write_csv(output_file, action_dict):
    """
    Write the action counts to a CSV file
    Args:
        output_file: Path where to save the results CSV
        action_dict: Dictionary with action counts
    """
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header row
            writer.writerow(["Action", "Count"])

            # Sort actions by count (highest first)
            sorted_actions = sorted(action_dict.items(), key=lambda x: x[1], reverse=True)

            # Only write actions that actually occurred (count > 0)
            for action, count in sorted_actions:
                if count > 0:
                    writer.writerow([action, count])

    except Exception as e:
        print(f"Error writing {output_file}: {e}")


def write_all_summaries(output_folder):
    """
    Write all summary files: combined, by user, and by task
    Args:
        output_folder: Base output folder
    """
    # Write combined summary
    print("Writing combined summary...")
    combined_file = os.path.join(output_folder, 'combined_action_counts.csv')
    write_csv(combined_file, combined_action_dict)

    # Write user summaries
    print(f"Writing {len(user_action_dicts)} user summaries...")
    for user, user_dict in user_action_dicts.items():
        user_file = os.path.join(output_folder, 'by_user', f'{user}_action_counts.csv')
        write_csv(user_file, user_dict)

    # Write task summaries with user subdirectories
    print(f"Writing {len(task_action_dicts)} task summaries...")
    for task, task_dict in task_action_dicts.items():
        # Extract user from task name (e.g., "user_25_1" -> "user_25")
        user_part = '_'.join(task.split('_')[:2])  # Gets "user_25" from "user_25_1"

        # Create user subdirectory in by_task folder
        user_task_folder = os.path.join(output_folder, 'by_task', user_part)
        os.makedirs(user_task_folder, exist_ok=True)

        # Write task file in the user subdirectory
        task_file = os.path.join(user_task_folder, f'{task}_action_counts.csv')
        write_csv(task_file, task_dict)

    # Print summary of what was created
    actions_with_counts = sum(1 for _, count in combined_action_dict.items() if count > 0)
    print(f"Successfully created:")
    print(f"  - 1 combined summary with {actions_with_counts} actions")
    print(f"  - {len(user_action_dicts)} user summaries")
    print(f"  - {len(task_action_dicts)} task summaries organized by user")

if __name__ == '__main__':
    main()