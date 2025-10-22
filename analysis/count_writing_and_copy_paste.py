"""
Writing and Copy/Paste Content Analyzer

Analyzes what users actually write, copy, cut, and paste by correlating IDE events with code changes.
Captures the actual content of each operation along with frequency, location, and timing.
Follows the same directory structure as states_count and actions_count.

Usage:
python count_writing_and_copy_paste.py [study_data_folder] [output_folder]
"""

import os
import sys
import glob
import csv
import pandas as pd
from collections import defaultdict
import argparse
import matplotlib.pyplot as plt

# Define event types to track
COPY_PASTE_ACTIONS = {
    "EditorCopy": "copy",
    "EditorCut": "cut", 
    "EditorPaste": "paste",
    "$Copy": "copy",
    "$Paste": "paste",
    "$Undo": "undo"
}

# Define writing actions (individual keystrokes)
WRITING_ACTIONS = {
    "EditorEnter", "EditorBackSpace", "EditorDelete", "EditorLeft", "EditorRight",
    "EditorUp", "EditorDown", "EditorCharTyped", "EditorInput", "EditorTab"
}

# Initialize dictionaries for tracking
combined_action_dict = {action: 0 for action in list(COPY_PASTE_ACTIONS.keys()) + list(WRITING_ACTIONS)}
user_action_dicts = defaultdict(lambda: {action: 0 for action in list(COPY_PASTE_ACTIONS.keys()) + list(WRITING_ACTIONS)})
task_action_dicts = defaultdict(lambda: {action: 0 for action in list(COPY_PASTE_ACTIONS.keys()) + list(WRITING_ACTIONS)})

# Store detailed events for logging
detailed_events = []

# Store content analysis results
content_operations = []
clipboard_content = {}  # Track what was copied at each timestamp
code_snapshots = {}     # Track code state at each timestamp

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Analyze writing and copy/paste actions and optionally create visuals')
    parser.add_argument('input_path', help='Path to study_data folder')
    parser.add_argument('output_folder', help='Folder to write results (per-user-task and summaries)')
    parser.add_argument('--visuals', action='store_true', help='Create PNG visualizations from the produced CSV summaries')
    args = parser.parse_args()

    count_copy_paste_actions(args.input_path, args.output_folder)
    print('Copy/Paste/Writing analysis complete!')

    if args.visuals:
        create_visuals(args.output_folder)

def count_copy_paste_actions(input_path, output_folder):
    """Main function to analyze copy/paste/writing actions and content from IDE events and code changes"""
    # Create output folder structure
    os.makedirs(output_folder, exist_ok=True)
    # Removed creation of by_user and by_task subdirectories

    # Find all data files
    print(f"DEBUG: Searching in {os.path.abspath(input_path)}")
    ide_files = glob.glob(os.path.join(input_path, '**', '*ide-events*.csv'), recursive=True)
    code_files = glob.glob(os.path.join(input_path, '**', '*.csv'), recursive=True)
    code_files = [f for f in code_files if 'ide-events' not in f]  # Exclude IDE events from code files
    
    print(f"Found {len(ide_files)} IDE event files")
    if ide_files:
        print(f"  Sample: {ide_files[0]}")
    print(f"Found {len(code_files)} code change files")
    if code_files:
        print(f"  Sample: {code_files[0]}")

    if not ide_files:
        print("No IDE event files found")
        return

    # Process each user/task combination
    print(f"DEBUG: Processing user/task combinations...")
    processed_combinations = set()
    for ide_file in ide_files:
        user_info, task_info = extract_user_task_from_path(ide_file)
        print(f"DEBUG: Extracted user={user_info}, task={task_info} from {ide_file}")
        if user_info and task_info:
            combination = (user_info, task_info)
            if combination not in processed_combinations:
                processed_combinations.add(combination)
                process_user_task_data(input_path, user_info, task_info, output_folder)

    # Write all the different summary files
    print(f"DEBUG: Writing summaries, detailed_events count = {len(detailed_events)}")
    write_all_summaries(output_folder)

def process_user_task_data(input_path, user_info, task_info, output_folder):
    """Process both IDE events and code changes for a specific user/task combination, and log keystrokes and copy/cut/paste content per user-task."""
    print(f"Processing {user_info} task {task_info.split('_')[-1]}...")
    
    # Find the corresponding files
    user_task_folder = os.path.join(input_path, user_info, task_info.split('_')[-1])
    ide_file = None
    code_file = None
    
    if os.path.exists(user_task_folder):
        for file in os.listdir(user_task_folder):
            if 'ide-events' in file:
                ide_file = os.path.join(user_task_folder, file)
            elif file.endswith('.csv') and 'ide-events' not in file:
                code_file = os.path.join(user_task_folder, file)
    
    if not ide_file or not code_file:
        print(f"  Missing files for {user_info} task {task_info.split('_')[-1]}")
        return
    
    # Load and process the data
    ide_events = load_ide_events(ide_file)
    code_changes = load_code_changes(code_file)
    
    # --- New: Prepare per-user-task event logs ---
    keystroke_events = []
    copycutpaste_events = []

    # Sort events by timestamp
    ide_events.sort(key=lambda x: x['timestamp'])
    code_changes.sort(key=lambda x: x['timestamp'])

    task_num = task_info.split('_')[-1]  # Fix: define task_num before use

    for i, event in enumerate(ide_events):
        action = event['action']
        if action in WRITING_ACTIONS:
            # Update global counter
            combined_action_dict[action] += 1

            # Find code change near this event
            content = extract_content_around_timestamp(event, code_changes, action)
            keystroke_event = {
                'timestamp': event['timestamp'],
                'user': user_info.replace('user_', '') if user_info else '',
                'task': task_info.split('_')[-1] if task_info else '',
                'action': action,
                'filename': event['filename'],
                'line': event['line'],
                'char': event['char'],
                'content': content[:200] if content else '',
                'content_length': len(content) if content else 0
            }
            keystroke_events.append(keystroke_event)

            # Also add to global detailed_events for summary
            detailed_event = keystroke_event.copy()
            detailed_event['event_type'] = 'writing'
            detailed_event['context'] = event['context']
            detailed_events.append(detailed_event)

        elif action in COPY_PASTE_ACTIONS:
            # Update global counter
            combined_action_dict[action] += 1

            content = extract_content_around_timestamp(event, code_changes, action)
            copycutpaste_event = {
                'timestamp': event['timestamp'],
                'user': user_info.replace('user_', '') if user_info else '',
                'task': task_info.split('_')[-1] if task_info else '',
                'event_type': COPY_PASTE_ACTIONS[action],
                'action': action,
                'filename': event['filename'],
                'line': event['line'],
                'char': event['char'],
                'content': content[:200] if content else '',
                'content_length': len(content) if content else 0
            }
            copycutpaste_events.append(copycutpaste_event)

            # Also add to global detailed_events for summary
            detailed_event = copycutpaste_event.copy()
            detailed_event['context'] = event['context']
            detailed_events.append(detailed_event)

    # Write per-user-task output files
    # Use the output_folder provided by the user for all outputs
    output_dir = os.path.join(output_folder, user_info, task_num)
    os.makedirs(output_dir, exist_ok=True)
    keystroke_file = os.path.join(output_dir, 'keystrokes.csv')
    copycutpaste_file = os.path.join(output_dir, 'copycutpaste.csv')
    pd.DataFrame(keystroke_events).to_csv(keystroke_file, index=False)
    pd.DataFrame(copycutpaste_events).to_csv(copycutpaste_file, index=False)
    print(f"  Keystrokes saved to {keystroke_file}")
    print(f"  Copy/Cut/Paste saved to {copycutpaste_file}")

def load_ide_events(ide_file):
    """Load IDE events from CSV file"""
    events = []
    try:
        with open(ide_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                # Accept both "Action" type events and direct action names starting with $
                if len(row) >= 3:
                    if row[1] == "Action" or row[2].startswith('$'):
                        events.append({
                            'timestamp': row[0],
                            'action': row[2],
                            'context': row[3] if len(row) > 3 else "",
                            'filename': row[4] if len(row) > 4 else "",
                            'line': int(row[5]) if len(row) > 5 and row[5].isdigit() else -1,
                            'char': int(row[6]) if len(row) > 6 and row[6].isdigit() else -1
                        })
    except Exception as e:
        print(f"Error loading IDE events from {ide_file}: {e}")
    return events

def load_code_changes(code_file):
    """Load code changes from CSV file"""
    changes = []
    try:
        with open(code_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 6:
                    changes.append({
                        'timestamp': row[0],
                        'filename': row[2],
                        'fragment': row[5] if len(row) > 5 else ""
                    })
    except Exception as e:
        print(f"Error loading code changes from {code_file}: {e}")
    return changes

def analyze_content_operations(ide_events, code_changes, user_info, task_info):
    """Analyze what content was copied, pasted, and written"""
    # Sort events by timestamp
    ide_events.sort(key=lambda x: x['timestamp'])
    code_changes.sort(key=lambda x: x['timestamp'])
    
    clipboard_history = []
    
    for i, event in enumerate(ide_events):
        action = event['action']
        
        if action in COPY_PASTE_ACTIONS or action in WRITING_ACTIONS:
            # Count the action
            combined_action_dict[action] += 1
            user_action_dicts[user_info][action] += 1
            task_action_dicts[task_info][action] += 1
            
            # Find corresponding code changes around this time
            content = extract_content_around_timestamp(event, code_changes, action)
            
            # Log detailed event with content
            event_category = COPY_PASTE_ACTIONS.get(action, "writing")
            detailed_event = {
                'timestamp': event['timestamp'],
                'user': user_info.replace('user_', '') if user_info else '',
                'task': task_info.split('_')[-1] if task_info else '',
                'event_type': event_category,
                'action': action,
                'context': event['context'],
                'filename': event['filename'],
                'line': event['line'],
                'char': event['char'],
                'content': content[:200] if content else "",  # Limit content length
                'content_length': len(content) if content else 0
            }
            detailed_events.append(detailed_event)

            # --- Per-user-per-task output ---
            # Collect per-user-task events in a dictionary
            user_task_key = (user_info, task_info)
            if not hasattr(analyze_content_operations, 'per_user_task_events'):
                analyze_content_operations.per_user_task_events = {}
            if user_task_key not in analyze_content_operations.per_user_task_events:
                analyze_content_operations.per_user_task_events[user_task_key] = []
            analyze_content_operations.per_user_task_events[user_task_key].append(detailed_event)
            
            # Track clipboard operations
            if action == 'EditorCopy':
                clipboard_history.append({
                    'timestamp': event['timestamp'],
                    'content': content,
                    'location': f"{event['filename']}:{event['line']}:{event['char']}"
                })

def extract_content_around_timestamp(event, code_changes, action):
    """Extract the relevant content based on the event type and timestamp"""
    event_time = event['timestamp']
    
    # Find code changes close to this timestamp
    relevant_changes = []
    for change in code_changes:
        if abs_time_diff(change['timestamp'], event_time) <= 2:  # Within 2 seconds
            relevant_changes.append(change)
    
    if not relevant_changes:
        return ""
    
    # For copy operations, try to extract what was likely copied
    if action in ['EditorCopy', '$Copy']:
        return extract_copied_content(event, relevant_changes)
    
    # For paste operations, show what was pasted
    elif action in ['EditorPaste', '$Paste']:
        return extract_pasted_content(event, relevant_changes)
    
    # For writing actions, show nearby text changes
    elif action in WRITING_ACTIONS:
        return extract_written_content(event, relevant_changes)
    
    return ""

def abs_time_diff(time1, time2):
    """Calculate absolute difference between two timestamps in seconds"""
    try:
        # Simple string comparison for now - could be improved with proper datetime parsing
        return abs(float(time1.replace('T', '').replace('-', '').replace(':', '')) - 
                  float(time2.replace('T', '').replace('-', '').replace(':', ''))) / 1000000
    except:
        return 999  # Large number if parsing fails

def extract_copied_content(event, changes):
    """Extract content that was likely copied"""
    # Look for the most recent change that matches the file and approximate location
    for change in reversed(changes):
        if change['filename'] == event['filename']:
            fragment = change['fragment']
            # Try to extract text around the cursor position
            lines = fragment.split('\n')
            if 0 <= event['line'] - 1 < len(lines):
                line_content = lines[event['line'] - 1]
                # Return a reasonable selection around the character position
                start = max(0, event['char'] - 20)
                end = min(len(line_content), event['char'] + 20)
                return line_content[start:end].strip()
    return ""

def extract_pasted_content(event, changes):
    """Extract content that was pasted"""
    # Look for changes after the paste event
    for change in changes:
        if change['filename'] == event['filename'] and change['timestamp'] >= event['timestamp']:
            return change['fragment'][:100] + "..." if len(change['fragment']) > 100 else change['fragment']
    return ""

def extract_written_content(event, changes):
    """Extract content that was written (typed)"""
    # For writing events, look at the most recent change
    for change in reversed(changes):
        if change['filename'] == event['filename']:
            # Return a small portion of the change
            fragment = change['fragment']
            if len(fragment) > 50:
                return fragment[:50] + "..."
            return fragment
    return ""

def extract_user_task_from_path(file_path):
    """Extract user and task information from file path"""
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
                if next_part.isdigit():
                    task_info = f"{user_info}_{next_part}"
                    break
    return user_info, task_info

def write_csv(output_file, action_dict):
    """Write action counts to CSV file"""
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(["Action", "Count"])
            # Sort actions by count (highest first) and only write actions that occurred
            sorted_actions = sorted(action_dict.items(), key=lambda x: x[1], reverse=True)
            for action, count in sorted_actions:
                if count > 0:
                    writer.writerow([action, count])
    except Exception as e:
        print(f"Error writing {output_file}: {e}")

def write_all_summaries(output_folder):
    """Write all summary files: combined only (no by_user or by_task)"""
    # Write combined summary
    print("Writing combined summary...")
    combined_file = os.path.join(output_folder, 'combined_copy_paste_counts.csv')
    write_csv(combined_file, combined_action_dict)
    
    # Write detailed events log with content
    if detailed_events:
        detailed_file = os.path.join(output_folder, 'detailed_copy_paste_events_with_content.csv')
        df = pd.DataFrame(detailed_events)
        df.to_csv(detailed_file, index=False)
        print(f"Detailed events with content saved to {detailed_file}")
        
        # Also create a summary of content operations
        content_summary_file = os.path.join(output_folder, 'content_operations_summary.csv')
        create_content_summary(detailed_events, content_summary_file)
    
    # Removed writing of by_user and by_task summaries
    # Print summary statistics
    actions_with_counts = sum(1 for _, count in combined_action_dict.items() if count > 0)
    total_copy = combined_action_dict.get('EditorCopy', 0)
    total_cut = combined_action_dict.get('EditorCut', 0)
    total_paste = combined_action_dict.get('EditorPaste', 0)
    total_writing = sum(combined_action_dict.get(action, 0) for action in WRITING_ACTIONS)
    
    print(f"\n📊 COPY/PASTE/WRITING SUMMARY:")
    print(f"  Total copy events: {total_copy:,}")
    print(f"  Total cut events: {total_cut:,}")
    print(f"  Total paste events: {total_paste:,}")
    print(f"  Total writing events: {total_writing:,}")
    print(f"  Total detailed events logged: {len(detailed_events):,}")
    print(f"\nSuccessfully created:")
    print(f"  - 1 combined summary with {actions_with_counts} actions")
    print(f"  - 1 detailed events log with {len(detailed_events)} events and content analysis")

    # --- Per-user-per-task output ---
    if hasattr(analyze_content_operations, 'per_user_task_events'):
        per_user_task_dir = os.path.join(output_folder, 'by_user_task')
        os.makedirs(per_user_task_dir, exist_ok=True)
        for (user_info, task_info), events in analyze_content_operations.per_user_task_events.items():
            user_folder = os.path.join(per_user_task_dir, user_info)
            os.makedirs(user_folder, exist_ok=True)
            task_num = task_info.split('_')[-1]
            detailed_file = os.path.join(user_folder, f'{task_info}_copy_paste_events.csv')
            df = pd.DataFrame(events)
            df.to_csv(detailed_file, index=False)
            # Also write a summary for this user-task
            summary_file = os.path.join(user_folder, f'{task_info}_content_summary.csv')
            create_content_summary(events, summary_file)

def create_content_summary(detailed_events, output_file):
    """Create a summary of content operations"""
    try:
        summary_data = []
        
        copy_events = [e for e in detailed_events if e['event_type'] == 'copy']
        paste_events = [e for e in detailed_events if e['event_type'] == 'paste']
        writing_events = [e for e in detailed_events if e['event_type'] == 'writing']
        
        # Summarize copy operations
        for event in copy_events:
            summary_data.append({
                'operation_type': 'copy',
                'user': event['user'],
                'task': event['task'],
                'timestamp': event['timestamp'],
                'filename': event['filename'],
                'location': f"line {event['line']}, char {event['char']}",
                'content_preview': event['content'][:100] if event['content'] else "",
                'content_length': event['content_length']
            })
        
        # Summarize paste operations  
        for event in paste_events:
            summary_data.append({
                'operation_type': 'paste',
                'user': event['user'],
                'task': event['task'],
                'timestamp': event['timestamp'],
                'filename': event['filename'],
                'location': f"line {event['line']}, char {event['char']}",
                'content_preview': event['content'][:100] if event['content'] else "",
                'content_length': event['content_length']
            })
        
        # Sample some writing events (since there are many)
        writing_sample = writing_events[::max(1, len(writing_events)//50)]  # Sample up to 50 events
        for event in writing_sample:
            summary_data.append({
                'operation_type': 'writing',
                'user': event['user'],
                'task': event['task'],
                'timestamp': event['timestamp'],
                'filename': event['filename'],
                'location': f"line {event['line']}, char {event['char']}",
                'content_preview': event['content'][:100] if event['content'] else "",
                'content_length': event['content_length']
            })
        
        # Write to CSV
        if summary_data:
            df = pd.DataFrame(summary_data)
            df.to_csv(output_file, index=False)
            print(f"Content operations summary saved to {output_file}")
        
    except Exception as e:
        print(f"Error creating content summary: {e}")

def create_visuals(output_folder):
    """Create simple visualizations from the summary CSVs in output_folder."""
    try:
        combined_file = os.path.join(output_folder, 'combined_copy_paste_counts.csv')

        # Combined action counts bar chart
        if os.path.exists(combined_file):
            df_comb = pd.read_csv(combined_file)
            if not df_comb.empty:
                plt.figure(figsize=(10,6))
                plt.bar(df_comb['Action'].astype(str), df_comb['Count'].astype(int), color='steelblue')
                plt.xticks(rotation=45, ha='right')
                plt.ylabel('Count')
                plt.title('Combined Copy/Cut/Paste and Writing Counts')
                out_comb = os.path.join(output_folder, 'combined_action_counts.png')
                plt.tight_layout()
                plt.savefig(out_comb)
                plt.close()
                print(f"Saved combined action visualization to {out_comb}")

    except Exception as e:
        print(f"Error creating visuals: {e}")

if __name__ == '__main__':
    main()