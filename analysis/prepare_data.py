"""
Data Preparation Script

This script prepares the IDE events and code changes data for analysis.
It works with nested directory structure where each user folder contains task folders.

Updated 2025-07-09 to compress consecutive identical lines in IDE events data.

Usage:
python prepare_data.py [study_data_folder] [output_folder] [--compress-ide-events]
"""

import os
import sys
import csv
import json
import glob
import pandas as pd
from datetime import datetime

def compress_consecutive_lines(rows, min_consecutive=3):
    """
    Compress consecutive identical lines in IDE events data.
    When 3+ identical lines are found (ignoring timestamp), keep only first and last.
    """
    if not rows:
        return rows
    
    compressed_rows = []
    i = 0
    
    while i < len(rows):
        current_row = rows[i]
        
        # Count consecutive identical rows (ignoring timestamp - column 0)
        consecutive_count = 1
        j = i + 1
        
        # Compare all columns except timestamp (index 0)
        current_pattern = current_row[1:] if len(current_row) > 1 else []
        
        while j < len(rows):
            next_pattern = rows[j][1:] if len(rows[j]) > 1 else []
            if current_pattern == next_pattern and len(current_pattern) > 0:
                consecutive_count += 1
                j += 1
            else:
                break
        
        # If we have enough consecutive identical lines, compress them
        if consecutive_count >= min_consecutive:
            # Add first line
            compressed_rows.append(current_row)
            
            # Skip the middle lines (j-1 is the last identical line)
            # Add last line only if there are more than min_consecutive lines
            if consecutive_count > min_consecutive:
                compressed_rows.append(rows[j-1])
            
            print(f"    Compressed {consecutive_count} consecutive identical lines to 2 lines")
            i = j
        else:
            # Add all lines if less than threshold
            for k in range(i, j):
                compressed_rows.append(rows[k])
            i = j
    
    return compressed_rows

def process_data(study_data_folder, output_folder, compress_ide=False):
    """Process all data files and save standardized versions."""
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Find all user folders
    user_folders = glob.glob(os.path.join(study_data_folder, "user_*"))
    if not user_folders:
        print("No user folders found")
        return
    
    print(f"Found {len(user_folders)} user folders")
    if compress_ide:
        print("IDE events compression enabled")
    
    # Initialize data containers
    all_ide_events = []
    code_changes_by_task = {}
    
    # Process each user
    for user_folder in user_folders:
        user_id = os.path.basename(user_folder)
        print(f"Processing {user_id}...")
        
        # Create user output folder
        user_output_folder = os.path.join(output_folder, user_id)
        os.makedirs(user_output_folder, exist_ok=True)
        
        # Find task folders (1, 2, 3, 4) or process files directly in user folder
        task_folders = []
        for i in range(1, 5):  # Tasks 1-4
            task_folder = os.path.join(user_folder, str(i))
            if os.path.isdir(task_folder):
                task_folders.append((str(i), task_folder))
        
        # If no task folders, look for files directly in user folder
        if not task_folders:
            process_user_files_direct(user_id, user_folder, user_output_folder, all_ide_events, code_changes_by_task, compress_ide)
        else:
            # Process each task folder
            for task_id, task_folder in task_folders:
                process_task_folder(user_id, task_id, task_folder, user_output_folder, all_ide_events, code_changes_by_task, compress_ide)
    
    # Save combined data
    if all_ide_events:
        combined_ide_df = pd.DataFrame(all_ide_events)
        combined_ide_path = os.path.join(output_folder, "all_users_combined_ide_events.csv")
        combined_ide_df.to_csv(combined_ide_path, index=False)
        print(f"Combined IDE events saved to {combined_ide_path}")
    
    # Save combined code changes by task
    for task_id, changes in code_changes_by_task.items():
        if changes:
            df = pd.DataFrame(changes)
            path = os.path.join(output_folder, f"all_users_task{task_id}_code_changes.csv")
            df.to_csv(path, index=False)
            print(f"Combined code changes for task {task_id} saved to {path}")

def process_user_files_direct(user_id, user_folder, output_folder, all_ide_events, code_changes_by_task, compress_ide=False):
    """Process files directly in the user folder."""
    # Find IDE events files
    ide_files = glob.glob(os.path.join(user_folder, "*ide-events*.csv"))
    
    # Process IDE events
    user_ide_events = []
    for file_path in ide_files:
        events = parse_ide_events(file_path, user_id, compress_ide)
        user_ide_events.extend(events)
        all_ide_events.extend(events)
    
    # Save user's IDE events
    if user_ide_events:
        ide_df = pd.DataFrame(user_ide_events)
        suffix = "_compressed" if compress_ide else ""
        ide_path = os.path.join(output_folder, f"{user_id}_combined_ide_events{suffix}.csv")
        ide_df.to_csv(ide_path, index=False)
    
    # Process code changes for each task
    for task_id in range(1, 5):
        task_id_str = str(task_id)
        code_files = glob.glob(os.path.join(user_folder, f"{task_id_str}_*.csv"))
        code_files = [f for f in code_files if "ide-events" not in os.path.basename(f).lower()]
        
        task_changes = []
        for file_path in code_files:
            changes = parse_code_changes(file_path, user_id, task_id_str)
            task_changes.extend(changes)
            if task_id_str not in code_changes_by_task:
                code_changes_by_task[task_id_str] = []
            code_changes_by_task[task_id_str].extend(changes)
        
        # Save user's code changes for this task
        if task_changes:
            changes_df = pd.DataFrame(task_changes)
            changes_path = os.path.join(output_folder, f"{user_id}_task{task_id_str}_code_changes.csv")
            changes_df.to_csv(changes_path, index=False)

def process_task_folder(user_id, task_id, task_folder, output_folder, all_ide_events, code_changes_by_task, compress_ide=False):
    """Process files in a task subfolder."""
    # Find IDE events files
    ide_files = glob.glob(os.path.join(task_folder, "*ide-events*.csv"))
    
    # Process IDE events
    user_ide_events = []
    for file_path in ide_files:
        events = parse_ide_events(file_path, user_id, compress_ide)
        # Add task_id to events
        for event in events:
            event['task_id'] = task_id
        user_ide_events.extend(events)
        all_ide_events.extend(events)
    
    # Save user's IDE events for this task
    if user_ide_events:
        ide_df = pd.DataFrame(user_ide_events)
        suffix = "_compressed" if compress_ide else ""
        ide_path = os.path.join(output_folder, f"{user_id}_task{task_id}_ide_events{suffix}.csv")
        ide_df.to_csv(ide_path, index=False)
    
    # Find code changes files
    code_files = glob.glob(os.path.join(task_folder, "*.csv"))
    code_files = [f for f in code_files if "ide-events" not in os.path.basename(f).lower()]
    
    # Process code changes
    task_changes = []
    for file_path in code_files:
        changes = parse_code_changes(file_path, user_id, task_id)
        task_changes.extend(changes)
        if task_id not in code_changes_by_task:
            code_changes_by_task[task_id] = []
        code_changes_by_task[task_id].extend(changes)
    
    # Save user's code changes for this task
    if task_changes:
        changes_df = pd.DataFrame(task_changes)
        changes_path = os.path.join(output_folder, f"{user_id}_task{task_id}_code_changes.csv")
        changes_df.to_csv(changes_path, index=False)

def parse_ide_events(file_path, user_id, compress_ide=False):
    """Parse IDE events from CSV file."""
    events = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Apply compression if requested
            if compress_ide and rows:
                # Separate header if exists
                header_row = None
                data_rows = rows
                
                if rows and not rows[0][0].startswith('2025-'):
                    header_row = rows[0]
                    data_rows = rows[1:]
                
                # Compress the data rows
                if data_rows:
                    original_count = len(data_rows)
                    compressed_data = compress_consecutive_lines(data_rows, min_consecutive=3)
                    print(f"  Compressed {original_count} rows to {len(compressed_data)} rows")
                    
                    # Rebuild rows
                    if header_row:
                        rows = [header_row] + compressed_data
                    else:
                        rows = compressed_data
            
            for row in rows:
                if len(row) >= 5:  # Ensure enough columns for basic IDE event structure
                    # Create event dictionary
                    event = {
                        'timestamp': row[0],
                        'eventType': row[1],
                        'actionType': row[2],
                        'context': row[3] if len(row) > 3 else '',
                        'asterisk': row[4] if len(row) > 4 else '',
                        'userId': user_id.replace('user_', '')
                    }
                    events.append(event)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return events

def parse_code_changes(file_path, user_id, task_id):
    """Parse code changes from CSV file."""
    changes = []
    try:
        # Try to determine if file has headers
        with open(file_path, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            f.seek(0)
            
            # Check if first row looks like headers
            has_header = csv.Sniffer().has_header(sample)
            
            if has_header:
                reader = csv.DictReader(f)
                for row in reader:
                    # Add userId and task_id if not present
                    if 'userId' not in row or not row['userId']:
                        row['userId'] = user_id.replace('user_', '')
                    row['task_id'] = task_id
                    changes.append(row)
            else:
                # Parse without headers
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 6:  # Ensure enough columns
                        change = {
                            'date': row[0],
                            'timestamp': row[1] if len(row) > 1 else None,
                            'fileName': row[2] if len(row) > 2 else None,
                            'fragment': row[5] if len(row) > 5 else None,
                            'userId': user_id.replace('user_', ''),
                            'task_id': task_id
                        }
                        changes.append(change)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return changes

def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python prepare_data.py [study_data_folder] [output_folder] [--compress-ide-events]")
        sys.exit(1)
    
    study_data_folder = sys.argv[1]
    output_folder = sys.argv[2]
    compress_ide = "--compress-ide-events" in sys.argv
    
    process_data(study_data_folder, output_folder, compress_ide)
    print("Data preparation complete!")

if __name__ == "__main__":
    main()