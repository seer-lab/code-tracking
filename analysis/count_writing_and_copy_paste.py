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

# Track volume metrics globally
combined_volume_stats = {
    'chars_written': 0,
    'chars_deleted': 0,
    'chars_copied': 0,
    'chars_pasted': 0,
    'chars_cut': 0,
    'total_keystrokes': 0,
    'total_copy_paste_ops': 0
}

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
    
    # --- Prepare per-user-task event logs ---
    keystroke_events = []
    copycutpaste_events = []

    # Track actual code volume changes
    writing_stats = {'chars_written': 0, 'lines_added': 0, 'chars_deleted': 0}
    copy_paste_stats = {'chars_copied': 0, 'chars_pasted': 0, 'chars_cut': 0}

    # Sort events by timestamp
    ide_events.sort(key=lambda x: x['timestamp'])
    code_changes.sort(key=lambda x: x['timestamp'])

    # Create a map of code states over time to calculate deltas
    previous_code_state = {}  # filename -> previous fragment

    task_num = task_info.split('_')[-1]

    for i, event in enumerate(ide_events):
        action = event['action']

        # Find the nearest code change to understand what actually changed
        nearest_change = None
        min_time_diff = float('inf')
        for change in code_changes:
            time_diff = abs_time_diff(change['timestamp'], event['timestamp'])
            if time_diff < min_time_diff and time_diff <= 3:  # Within 3 seconds
                min_time_diff = time_diff
                nearest_change = change

        if action in WRITING_ACTIONS:
            # Update global counter
            combined_action_dict[action] += 1

            # Calculate actual content change if we have a code change
            content = ""
            chars_changed = 0
            if nearest_change:
                content = nearest_change['fragment']
                filename = nearest_change['filename']

                # Calculate delta from previous state
                if filename in previous_code_state:
                    prev_content = previous_code_state[filename]
                    curr_content = content

                    # Simple delta calculation
                    if len(curr_content) > len(prev_content):
                        chars_changed = len(curr_content) - len(prev_content)
                        writing_stats['chars_written'] += chars_changed
                    elif len(curr_content) < len(prev_content):
                        chars_changed = len(prev_content) - len(curr_content)
                        writing_stats['chars_deleted'] += chars_changed

                previous_code_state[filename] = content

            keystroke_event = {
                'timestamp': event['timestamp'],
                'user': user_info.replace('user_', '') if user_info else '',
                'task': task_info.split('_')[-1] if task_info else '',
                'action': action,
                'filename': event['filename'],
                'line': event['line'],
                'char': event['char'],
                'content': content[:200] if content else '',
                'content_length': len(content) if content else 0,
                'chars_changed': chars_changed
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

            # Get the actual content for copy/paste operations
            content = ""
            content_size = 0
            if nearest_change:
                content = nearest_change['fragment']
                content_size = len(content)

                # Track volume of copy/paste operations
                if action in ['EditorCopy', '$Copy']:
                    copy_paste_stats['chars_copied'] += content_size
                elif action in ['EditorPaste', '$Paste']:
                    copy_paste_stats['chars_pasted'] += content_size
                elif action == 'EditorCut':
                    copy_paste_stats['chars_cut'] += content_size

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
                'content_length': content_size,
                'content_size': content_size
            }
            copycutpaste_events.append(copycutpaste_event)

            # Also add to global detailed_events for summary
            detailed_event = copycutpaste_event.copy()
            detailed_event['context'] = event['context']
            detailed_events.append(detailed_event)

    # Accumulate to global volume statistics
    combined_volume_stats['chars_written'] += writing_stats['chars_written']
    combined_volume_stats['chars_deleted'] += writing_stats['chars_deleted']
    combined_volume_stats['chars_copied'] += copy_paste_stats['chars_copied']
    combined_volume_stats['chars_pasted'] += copy_paste_stats['chars_pasted']
    combined_volume_stats['chars_cut'] += copy_paste_stats['chars_cut']
    combined_volume_stats['total_keystrokes'] += len(keystroke_events)
    combined_volume_stats['total_copy_paste_ops'] += len(copycutpaste_events)

    # Write per-user-task output files
    output_dir = os.path.join(output_folder, user_info, task_num)
    os.makedirs(output_dir, exist_ok=True)

    keystroke_file = os.path.join(output_dir, 'keystrokes.csv')
    copycutpaste_file = os.path.join(output_dir, 'copycutpaste.csv')
    pd.DataFrame(keystroke_events).to_csv(keystroke_file, index=False)
    pd.DataFrame(copycutpaste_events).to_csv(copycutpaste_file, index=False)

    # Write volume statistics
    volume_stats_file = os.path.join(output_dir, 'code_volume_stats.csv')
    volume_data = {
        'user': user_info.replace('user_', ''),
        'task': task_num,
        'chars_written': writing_stats['chars_written'],
        'chars_deleted': writing_stats['chars_deleted'],
        'net_chars_written': writing_stats['chars_written'] - writing_stats['chars_deleted'],
        'chars_copied': copy_paste_stats['chars_copied'],
        'chars_pasted': copy_paste_stats['chars_pasted'],
        'chars_cut': copy_paste_stats['chars_cut'],
        'total_keystrokes': len(keystroke_events),
        'total_copy_paste_ops': len(copycutpaste_events)
    }
    pd.DataFrame([volume_data]).to_csv(volume_stats_file, index=False)

    print(f"  Keystrokes saved to {keystroke_file}")
    print(f"  Copy/Cut/Paste saved to {copycutpaste_file}")
    print(f"  Volume stats: {writing_stats['chars_written']} chars written, {copy_paste_stats['chars_pasted']} chars pasted")

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

def get_human_readable_name(action):
    """Convert action names to human-readable format"""
    readable_names = {
        'EditorCopy': 'Copy',
        '$Copy': 'Copy',
        'EditorCut': 'Cut',
        '$Paste': 'Paste',
        'EditorPaste': 'Paste',
        '$Undo': 'Undo',
        'EditorEnter': 'Enter/New Line',
        'EditorBackSpace': 'Backspace',
        'EditorDelete': 'Delete',
        'EditorLeft': 'Arrow Left',
        'EditorRight': 'Arrow Right',
        'EditorUp': 'Arrow Up',
        'EditorDown': 'Arrow Down',
        'EditorCharTyped': 'Character Typed',
        'EditorInput': 'Text Input',
        'EditorTab': 'Tab'
    }
    return readable_names.get(action, action)

def combine_similar_actions(action_dict):
    """Combine similar actions (e.g., $Copy and EditorCopy) into single entries with readable names"""
    combined = {}

    for action, count in action_dict.items():
        readable_name = get_human_readable_name(action)
        if readable_name in combined:
            combined[readable_name] += count
        else:
            combined[readable_name] = count

    return combined

def write_csv(output_file, action_dict, volume_stats=None):
    """Write action counts and optionally volume statistics to CSV file"""
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(["Metric", "Value"])

            # Write volume statistics first if provided
            if volume_stats:
                writer.writerow(["=== CODE VOLUME METRICS ===", ""])
                writer.writerow(["Characters Written", volume_stats['chars_written']])
                writer.writerow(["Characters Deleted", volume_stats['chars_deleted']])
                writer.writerow(["Net Characters Written", volume_stats['chars_written'] - volume_stats['chars_deleted']])
                writer.writerow(["Characters Copied", volume_stats['chars_copied']])
                writer.writerow(["Characters Pasted", volume_stats['chars_pasted']])
                writer.writerow(["Characters Cut", volume_stats['chars_cut']])
                writer.writerow(["Total Keystrokes", volume_stats['total_keystrokes']])
                writer.writerow(["Total Copy/Paste Operations", volume_stats['total_copy_paste_ops']])
                writer.writerow(["", ""])  # Empty row separator

            # Write action counts with combined and readable names
            writer.writerow(["=== ACTION COUNTS ===", ""])
            combined_actions = combine_similar_actions(action_dict)
            # Sort actions by count (highest first) and only write actions that occurred
            sorted_actions = sorted(combined_actions.items(), key=lambda x: x[1], reverse=True)
            for action, count in sorted_actions:
                if count > 0:
                    writer.writerow([action, count])
    except Exception as e:
        print(f"Error writing {output_file}: {e}")

def write_all_summaries(output_folder):
    """Write all summary files: overall, per-user, and per-task with consistent directory structure"""
    # Write combined summary with volume statistics
    print("Writing combined summary...")
    combined_file = os.path.join(output_folder, 'combined_copy_paste_counts.csv')
    write_csv(combined_file, combined_action_dict, combined_volume_stats)

    # Write detailed events log with content
    if detailed_events:
        detailed_file = os.path.join(output_folder, 'detailed_copy_paste_events_with_content.csv')
        df = pd.DataFrame(detailed_events)
        df.to_csv(detailed_file, index=False)
        print(f"Detailed events with content saved to {detailed_file}")
        
        # Also create a summary of content operations
        content_summary_file = os.path.join(output_folder, 'content_operations_summary.csv')
        create_content_summary(detailed_events, content_summary_file)
    
    # Aggregate volume statistics from all user/task folders
    volume_stats = []
    for user_folder in glob.glob(os.path.join(output_folder, 'user_*')):
        for task_folder in glob.glob(os.path.join(user_folder, '*')):
            volume_file = os.path.join(task_folder, 'code_volume_stats.csv')
            if os.path.exists(volume_file):
                df = pd.read_csv(volume_file)
                volume_stats.append(df)

    if volume_stats:
        combined_volume = pd.concat(volume_stats, ignore_index=True)
        volume_summary_file = os.path.join(output_folder, 'code_volume_summary.csv')
        combined_volume.to_csv(volume_summary_file, index=False)
        print(f"Code volume summary saved to {volume_summary_file}")

        # Create summaries directory structure
        summaries_dir = os.path.join(output_folder, 'summaries')
        by_user_dir = os.path.join(summaries_dir, 'by_user')
        by_task_dir = os.path.join(summaries_dir, 'by_task')
        os.makedirs(by_user_dir, exist_ok=True)
        os.makedirs(by_task_dir, exist_ok=True)

        # Per-user summaries
        print("Creating per-user summaries...")
        for user in combined_volume['user'].unique():
            user_data = combined_volume[combined_volume['user'] == user]
            user_summary_file = os.path.join(by_user_dir, f'user_{user}_summary.csv')
            user_data.to_csv(user_summary_file, index=False)

            # User totals
            user_totals = {
                'user': user,
                'total_chars_written': user_data['chars_written'].sum(),
                'total_chars_pasted': user_data['chars_pasted'].sum(),
                'total_chars_copied': user_data['chars_copied'].sum(),
                'total_keystrokes': user_data['total_keystrokes'].sum(),
                'total_copy_paste_ops': user_data['total_copy_paste_ops'].sum(),
                'num_tasks': len(user_data)
            }
            user_totals_file = os.path.join(by_user_dir, f'user_{user}_totals.csv')
            pd.DataFrame([user_totals]).to_csv(user_totals_file, index=False)

        # Per-task summaries (aggregating across all users for each task)
        print("Creating per-task summaries...")
        for task in combined_volume['task'].unique():
            task_data = combined_volume[combined_volume['task'] == task]
            task_summary_file = os.path.join(by_task_dir, f'task_{task}_summary.csv')
            task_data.to_csv(task_summary_file, index=False)

            # Task totals
            task_totals = {
                'task': task,
                'total_chars_written': task_data['chars_written'].sum(),
                'total_chars_pasted': task_data['chars_pasted'].sum(),
                'total_chars_copied': task_data['chars_copied'].sum(),
                'total_keystrokes': task_data['total_keystrokes'].sum(),
                'total_copy_paste_ops': task_data['total_copy_paste_ops'].sum(),
                'num_users': len(task_data),
                'avg_chars_written': task_data['chars_written'].mean(),
                'avg_chars_pasted': task_data['chars_pasted'].mean()
            }
            task_totals_file = os.path.join(by_task_dir, f'task_{task}_totals.csv')
            pd.DataFrame([task_totals]).to_csv(task_totals_file, index=False)

        # Calculate totals
        total_written = combined_volume['chars_written'].sum()
        total_pasted = combined_volume['chars_pasted'].sum()
        total_copied = combined_volume['chars_copied'].sum()

        print(f"\n📝 CODE VOLUME SUMMARY:")
        print(f"  Total characters written: {total_written:,}")
        print(f"  Total characters pasted: {total_pasted:,}")
        print(f"  Total characters copied: {total_copied:,}")
        print(f"  Write vs Paste ratio: {total_written/(total_pasted+1):.2f}:1")

    # Print summary statistics
    actions_with_counts = sum(1 for _, count in combined_action_dict.items() if count > 0)
    total_copy = combined_action_dict.get('EditorCopy', 0) + combined_action_dict.get('$Copy', 0)
    total_cut = combined_action_dict.get('EditorCut', 0)
    total_paste = combined_action_dict.get('EditorPaste', 0) + combined_action_dict.get('$Paste', 0)
    total_writing = sum(combined_action_dict.get(action, 0) for action in WRITING_ACTIONS)
    
    print(f"\n📊 ACTION COUNT SUMMARY:")
    print(f"  Total copy events: {total_copy:,}")
    print(f"  Total cut events: {total_cut:,}")
    print(f"  Total paste events: {total_paste:,}")
    print(f"  Total writing keystrokes: {total_writing:,}")
    print(f"  Total detailed events logged: {len(detailed_events):,}")
    print(f"\nSuccessfully created:")
    print(f"  - Combined summaries in output folder")
    print(f"  - Per-user summaries in summaries/by_user/")
    print(f"  - Per-task summaries in summaries/by_task/")



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
    """Create professional visualizations from the summary CSVs in output_folder."""
    try:
        # Set style for cleaner plots
        plt.style.use('seaborn-v0_8-darkgrid')

        combined_file = os.path.join(output_folder, 'combined_copy_paste_counts.csv')
        volume_file = os.path.join(output_folder, 'code_volume_summary.csv')
        visuals_dir = os.path.join(output_folder, 'visuals')
        os.makedirs(visuals_dir, exist_ok=True)

        # 1. Combined action counts bar chart
        if os.path.exists(combined_file):
            df_comb = pd.read_csv(combined_file)
            if not df_comb.empty:
                # Filter to only action count rows (skip volume metrics and separator rows)
                # Action counts start after "=== ACTION COUNTS ===" row
                action_start_idx = None
                for idx, row in df_comb.iterrows():
                    if row['Metric'] == '=== ACTION COUNTS ===':
                        action_start_idx = idx + 1
                        break

                if action_start_idx is not None:
                    action_data = df_comb.iloc[action_start_idx:].copy()
                    # Remove any empty rows
                    action_data = action_data[action_data['Metric'].notna() & (action_data['Metric'] != '')]

                    if not action_data.empty:
                        # Sort by value for better visualization
                        action_data = action_data.sort_values('Value', ascending=False)

                        # Define color scheme for different action types
                        colors = []
                        for metric in action_data['Metric']:
                            if metric in ['Copy', 'Cut', 'Paste']:
                                colors.append('#e74c3c')  # Red for clipboard operations
                            elif metric in ['Character Typed', 'Text Input', 'Enter/New Line', 'Tab']:
                                colors.append('#3498db')  # Blue for writing
                            elif metric in ['Backspace', 'Delete']:
                                colors.append('#e67e22')  # Orange for deletion
                            elif metric in ['Undo']:
                                colors.append('#9b59b6')  # Purple for undo
                            else:
                                colors.append('#95a5a6')  # Gray for navigation

                        fig, ax = plt.subplots(figsize=(14, 7))
                        bars = ax.bar(action_data['Metric'].astype(str), action_data['Value'].astype(int),
                                     color=colors, edgecolor='black', linewidth=1.2, alpha=0.8)
                        ax.set_xlabel('Action Type', fontsize=12, fontweight='bold')
                        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
                        ax.set_title('Editor Action Counts: Writing, Copy/Paste, and Navigation',
                                    fontsize=14, fontweight='bold', pad=20)
                        plt.xticks(rotation=45, ha='right')
                        ax.grid(axis='y', alpha=0.3)

                        # Add value labels on bars
                        for bar in bars:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height,
                                   f'{int(height):,}', ha='center', va='bottom', fontsize=9)

                        # Add legend
                        from matplotlib.patches import Patch
                        legend_elements = [
                            Patch(facecolor='#3498db', edgecolor='black', label='Writing'),
                            Patch(facecolor='#e74c3c', edgecolor='black', label='Clipboard'),
                            Patch(facecolor='#e67e22', edgecolor='black', label='Deletion'),
                            Patch(facecolor='#95a5a6', edgecolor='black', label='Navigation'),
                            Patch(facecolor='#9b59b6', edgecolor='black', label='Undo')
                        ]
                        ax.legend(handles=legend_elements, loc='upper right')

                        plt.tight_layout()
                        out_comb = os.path.join(visuals_dir, 'combined_action_counts.png')
                        plt.savefig(out_comb, dpi=300, bbox_inches='tight')
                        plt.close()
                        print(f"Saved action count visualization to {out_comb}")

                # 1b. Create visualization for volume metrics
                volume_start_idx = None
                volume_end_idx = None
                for idx, row in df_comb.iterrows():
                    if row['Metric'] == '=== CODE VOLUME METRICS ===':
                        volume_start_idx = idx + 1
                    elif row['Metric'] == '=== ACTION COUNTS ===':
                        volume_end_idx = idx
                        break

                if volume_start_idx is not None and volume_end_idx is not None:
                    volume_data = df_comb.iloc[volume_start_idx:volume_end_idx].copy()
                    volume_data = volume_data[volume_data['Metric'].notna() & (volume_data['Metric'] != '')]

                    if not volume_data.empty:
                        fig, ax = plt.subplots(figsize=(12, 7))
                        bars = ax.barh(volume_data['Metric'].astype(str), volume_data['Value'].astype(float),
                                      color='#2ecc71', edgecolor='darkgreen', linewidth=1.2)
                        ax.set_xlabel('Count/Characters', fontsize=12, fontweight='bold')
                        ax.set_ylabel('Metric', fontsize=12, fontweight='bold')
                        ax.set_title('Code Volume Metrics Overview',
                                    fontsize=14, fontweight='bold', pad=20)
                        ax.grid(axis='x', alpha=0.3)

                        # Add value labels on bars
                        for bar in bars:
                            width = bar.get_width()
                            ax.text(width, bar.get_y() + bar.get_height()/2.,
                                   f'{int(width):,}', ha='left', va='center', fontsize=9,
                                   fontweight='bold', color='darkgreen')

                        plt.tight_layout()
                        out_vol_metrics = os.path.join(visuals_dir, 'volume_metrics_overview.png')
                        plt.savefig(out_vol_metrics, dpi=300, bbox_inches='tight')
                        plt.close()
                        print(f"Saved volume metrics visualization to {out_vol_metrics}")

        # 2. Code volume comparison: Written vs Pasted
        if os.path.exists(volume_file):
            df_vol = pd.read_csv(volume_file)
            if not df_vol.empty:
                # Aggregate totals
                total_written = df_vol['chars_written'].sum()
                total_pasted = df_vol['chars_pasted'].sum()
                total_copied = df_vol['chars_copied'].sum()
                total_cut = df_vol['chars_cut'].sum()

                # Overall pie charts
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

                # Left: Written vs Pasted
                sizes = [total_written, total_pasted]
                labels = ['Written', 'Pasted']
                colors = ['#27ae60', '#e74c3c']
                explode = (0.05, 0.05)
                wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                                     startangle=90, explode=explode, textprops={'fontsize': 11})
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                ax1.set_title(f'Code Volume: Written vs Pasted\n({total_written:,} vs {total_pasted:,} chars)',
                             fontsize=13, fontweight='bold', pad=15)

                # Right: Copy/Cut/Paste operations
                cp_sizes = [total_copied, total_pasted, total_cut]
                cp_labels = ['Copied', 'Pasted', 'Cut']
                cp_colors = ['#3498db', '#e74c3c', '#f39c12']
                cp_explode = (0.05, 0.05, 0.05)
                wedges2, texts2, autotexts2 = ax2.pie(cp_sizes, labels=cp_labels, colors=cp_colors,
                                                        autopct='%1.1f%%', startangle=90, explode=cp_explode,
                                                        textprops={'fontsize': 11})
                for autotext in autotexts2:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                ax2.set_title(f'Copy/Cut/Paste Distribution\n(Total: {sum(cp_sizes):,} chars)',
                             fontsize=13, fontweight='bold', pad=15)

                plt.tight_layout()
                out_volume = os.path.join(visuals_dir, 'code_volume_comparison.png')
                plt.savefig(out_volume, dpi=300, bbox_inches='tight')
                plt.close()
                print(f"Saved code volume visualization to {out_volume}")

                # 3. Enhanced per-user comparison
                user_aggregated = df_vol.groupby('user').agg({
                    'chars_written': 'sum',
                    'chars_pasted': 'sum',
                    'chars_copied': 'sum'
                }).reset_index()

                if len(user_aggregated) > 1:
                    fig, ax = plt.subplots(figsize=(max(12, len(user_aggregated) * 0.6), 7))
                    users = user_aggregated['user'].astype(str)
                    x = range(len(users))
                    width = 0.28

                    bars1 = ax.bar([i - width for i in x], user_aggregated['chars_written'], width,
                                   label='Written', color='#27ae60', edgecolor='darkgreen', linewidth=1.2)
                    bars2 = ax.bar(x, user_aggregated['chars_pasted'], width,
                                   label='Pasted', color='#e74c3c', edgecolor='darkred', linewidth=1.2)
                    bars3 = ax.bar([i + width for i in x], user_aggregated['chars_copied'], width,
                                   label='Copied', color='#3498db', edgecolor='darkblue', linewidth=1.2)

                    ax.set_xlabel('User', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Characters', fontsize=12, fontweight='bold')
                    ax.set_title('Code Activity by User: Written vs Copied vs Pasted',
                                fontsize=14, fontweight='bold', pad=20)
                    ax.set_xticks(x)
                    ax.set_xticklabels([f'User {u}' for u in users], rotation=45, ha='right')
                    ax.legend(loc='upper right', framealpha=0.9, fontsize=10)
                    ax.grid(axis='y', alpha=0.3)

                    # Add value labels on bars
                    for bars in [bars1, bars2, bars3]:
                        for bar in bars:
                            height = bar.get_height()
                            if height > 0:
                                ax.text(bar.get_x() + bar.get_width()/2., height,
                                       f'{int(height):,}', ha='center', va='bottom',
                                       fontsize=8, rotation=0)

                    plt.tight_layout()
                    out_per_user = os.path.join(visuals_dir, 'code_volume_by_user.png')
                    plt.savefig(out_per_user, dpi=300, bbox_inches='tight')
                    plt.close()
                    print(f"Saved per-user volume visualization to {out_per_user}")

                # 4. Per-task comparison
                task_aggregated = df_vol.groupby('task').agg({
                    'chars_written': 'sum',
                    'chars_pasted': 'sum',
                    'chars_copied': 'sum'
                }).reset_index()

                if len(task_aggregated) > 1:
                    fig, ax = plt.subplots(figsize=(max(12, len(task_aggregated) * 0.6), 7))
                    tasks = task_aggregated['task'].astype(str)
                    x = range(len(tasks))
                    width = 0.28

                    bars1 = ax.bar([i - width for i in x], task_aggregated['chars_written'], width,
                                   label='Written', color='#27ae60', edgecolor='darkgreen', linewidth=1.2)
                    bars2 = ax.bar(x, task_aggregated['chars_pasted'], width,
                                   label='Pasted', color='#e74c3c', edgecolor='darkred', linewidth=1.2)
                    bars3 = ax.bar([i + width for i in x], task_aggregated['chars_copied'], width,
                                   label='Copied', color='#3498db', edgecolor='darkblue', linewidth=1.2)

                    ax.set_xlabel('Task', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Characters', fontsize=12, fontweight='bold')
                    ax.set_title('Code Activity by Task: Written vs Copied vs Pasted',
                                fontsize=14, fontweight='bold', pad=20)
                    ax.set_xticks(x)
                    ax.set_xticklabels([f'Task {t}' for t in tasks], rotation=45, ha='right')
                    ax.legend(loc='upper right', framealpha=0.9, fontsize=10)
                    ax.grid(axis='y', alpha=0.3)

                    # Add value labels
                    for bars in [bars1, bars2, bars3]:
                        for bar in bars:
                            height = bar.get_height()
                            if height > 0:
                                ax.text(bar.get_x() + bar.get_width()/2., height,
                                       f'{int(height):,}', ha='center', va='bottom',
                                       fontsize=8, rotation=0)

                    plt.tight_layout()
                    out_per_task = os.path.join(visuals_dir, 'code_volume_by_task.png')
                    plt.savefig(out_per_task, dpi=300, bbox_inches='tight')
                    plt.close()
                    print(f"Saved per-task volume visualization to {out_per_task}")

                # 5. Individual per-user visuals in summaries/by_user/
                summaries_dir = os.path.join(output_folder, 'summaries', 'by_user')
                if os.path.exists(summaries_dir):
                    for user in df_vol['user'].unique():
                        user_data = df_vol[df_vol['user'] == user]
                        if len(user_data) > 0:
                            fig, ax = plt.subplots(figsize=(10, 6))
                            tasks = user_data['task'].astype(str)
                            x = range(len(tasks))
                            width = 0.35

                            bars1 = ax.bar([i - width/2 for i in x], user_data['chars_written'], width,
                                          label='Written', color='#27ae60', edgecolor='darkgreen')
                            bars2 = ax.bar([i + width/2 for i in x], user_data['chars_pasted'], width,
                                          label='Pasted', color='#e74c3c', edgecolor='darkred')

                            ax.set_xlabel('Task', fontsize=11, fontweight='bold')
                            ax.set_ylabel('Characters', fontsize=11, fontweight='bold')
                            ax.set_title(f'User {user}: Code Volume by Task', fontsize=13, fontweight='bold')
                            ax.set_xticks(x)
                            ax.set_xticklabels([f'Task {t}' for t in tasks])
                            ax.legend()
                            ax.grid(axis='y', alpha=0.3)

                            plt.tight_layout()
                            user_visual = os.path.join(summaries_dir, f'user_{user}_visual.png')
                            plt.savefig(user_visual, dpi=300, bbox_inches='tight')
                            plt.close()

                # 6. Individual per-task visuals in summaries/by_task/
                summaries_task_dir = os.path.join(output_folder, 'summaries', 'by_task')
                if os.path.exists(summaries_task_dir):
                    for task in df_vol['task'].unique():
                        task_data = df_vol[df_vol['task'] == task]
                        if len(task_data) > 0:
                            fig, ax = plt.subplots(figsize=(10, 6))
                            users = task_data['user'].astype(str)
                            x = range(len(users))
                            width = 0.35

                            bars1 = ax.bar([i - width/2 for i in x], task_data['chars_written'], width,
                                          label='Written', color='#27ae60', edgecolor='darkgreen')
                            bars2 = ax.bar([i + width/2 for i in x], task_data['chars_pasted'], width,
                                          label='Pasted', color='#e74c3c', edgecolor='darkred')

                            ax.set_xlabel('User', fontsize=11, fontweight='bold')
                            ax.set_ylabel('Characters', fontsize=11, fontweight='bold')
                            ax.set_title(f'Task {task}: Code Volume by User', fontsize=13, fontweight='bold')
                            ax.set_xticks(x)
                            ax.set_xticklabels([f'User {u}' for u in users], rotation=45, ha='right')
                            ax.legend()
                            ax.grid(axis='y', alpha=0.3)

                            plt.tight_layout()
                            task_visual = os.path.join(summaries_task_dir, f'task_{task}_visual.png')
                            plt.savefig(task_visual, dpi=300, bbox_inches='tight')
                            plt.close()

        print(f"\nAll visualizations saved to {visuals_dir}")
        print(f"Per-user visuals in summaries/by_user/")
        print(f"Per-task visuals in summaries/by_task/")

    except Exception as e:
        print(f"Error creating visuals: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()