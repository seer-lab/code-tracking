"""
Writing and Copy/Paste Content Analyzer

Analyzes what users actually write, copy, cut, and paste by correlating IDE events with code changes.
Captures the actual content of each operation along with frequency, location, and timing.
Follows the same directory structure as states_count and actions_count.

Usage:
python count_writing_and_copy_paste.py [study_data_folder] [output_folder]
"""

import os
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

# Poster-friendly save helper
def save_fig_variants(fig, out_base, dpi=600, transparent=True):
    """Save a figure to PNG (transparent) and vector formats (PDF, SVG) with tight layout.
    out_base: full path without extension (e.g. os.path.join(visuals_dir, 'name'))
    """
    # Ensure transparent backgrounds for figure and axes
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
    # Vector outputs
    try:
        fig.savefig(pdf_path, dpi=dpi, transparent=transparent, bbox_inches='tight', pad_inches=0.02, facecolor='none')
        fig.savefig(svg_path, dpi=dpi, transparent=transparent, bbox_inches='tight', pad_inches=0.02, facecolor='none')
    except Exception:
        # Some backends may not support PDF/SVG; ignore gracefully
        pass

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

# --- New: simple grouping map and helper ---
# Primary mapping: internal action name -> high-level group
ACTION_GROUPS_INTERNAL = {
    # Clipboard
    'EditorCopy': 'Clipboard',
    '$Copy': 'Clipboard',
    'EditorCut': 'Clipboard',
    'EditorPaste': 'Clipboard',
    '$Paste': 'Clipboard',

    # Deletion
    'EditorBackSpace': 'Deletion',
    'EditorDelete': 'Deletion',

    # Navigation
    'EditorLeft': 'Navigation',
    'EditorRight': 'Navigation',
    'EditorUp': 'Navigation',
    'EditorDown': 'Navigation',

    # Undo/Redo
    '$Undo': 'Undo/Redo',
    # Add other internal undo/redo names here if present

    # Writing (these are primarily typing actions)
    'EditorEnter': 'Writing',
    'EditorCharTyped': 'Writing',
    'EditorInput': 'Writing',
    'EditorTab': 'Writing',
}

# Secondary mapping: human-readable action name -> high-level group
ACTION_GROUPS_READABLE = {
    'Clipboard': {'Copy', 'Cut', 'Paste'},
    'Deletion': {'Backspace', 'Delete'},
    'Navigation': {'Arrow Left', 'Arrow Right', 'Arrow Up', 'Arrow Down'},
    'Undo/Redo': {'Undo', 'Redo'},
    'Writing': {'Enter/New Line', 'Character Typed', 'Text Input', 'Tab'},
}


def get_action_group(action_name):
    """
    Return the high-level group for an action name.
    Accepts either internal action names (e.g. 'EditorCopy', '$Paste') or
    human-readable names (e.g. 'Copy', 'Paste'). Preference is given to
    the internal mapping if available.
    """
    # 1) Direct internal mapping
    if action_name in ACTION_GROUPS_INTERNAL:
        return ACTION_GROUPS_INTERNAL[action_name]

    # 2) If the provided name looks like a readable name, match against readable groups
    #    Also handle cases where the caller passed a human-readable name (e.g., 'Copy').
    # Convert internal-like names to their human-readable equivalent and try again.
    readable = get_human_readable_name(action_name)

    for group, members in ACTION_GROUPS_READABLE.items():
        if readable in members or action_name in members:
            return group

    # 3) Not matched
    return 'Other'

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
    """Create a simple combined action counts bar chart using the produced CSV.

    This version intentionally stays minimal: it reads the combined summary CSV
    (which already collapses internal names to human-readable labels), extracts
    the action rows and plots them as a vertical bar chart sorted by count.
    The output is saved in PNG (transparent) and vector (PDF/SVG) formats.
    """
    combined_file = os.path.join(output_folder, 'combined_copy_paste_counts.csv')
    visuals_dir = os.path.join(output_folder, 'visuals')
    os.makedirs(visuals_dir, exist_ok=True)

    if not os.path.exists(combined_file):
        print(f"No combined summary CSV found at {combined_file}; skipping visuals.")
        return

    try:
        df = pd.read_csv(combined_file)
    except Exception as e:
        print(f"Failed to read {combined_file}: {e}")
        return

    # Find the start of action rows (after the === ACTION COUNTS === marker)
    action_start = None
    for idx, row in df.iterrows():
        if str(row.get('Metric', '')).strip() == '=== ACTION COUNTS ===':
            action_start = idx + 1
            break

    if action_start is None:
        print('No action counts section found in combined CSV; nothing to plot.')
        return

    actions = df.iloc[action_start:].copy()
    actions = actions[actions['Metric'].notna() & (actions['Metric'].astype(str).str.strip() != '')]
    if actions.empty:
        print('Action counts section is empty; no visuals created.')
        return

    # Ensure numeric values and convert to int
    def to_int(v):
        try:
            return int(v)
        except Exception:
            try:
                return int(float(v))
            except Exception:
                return 0

    actions['Count'] = actions['Value'].apply(to_int)
    actions['Action'] = actions['Metric'].astype(str).str.strip()

    # Sort descending
    actions = actions.sort_values('Count', ascending=False)

    # Plot: mimic original look (vertical bars, readable labels)
    fig, ax = plt.subplots(figsize=(12, max(4, len(actions) * 0.3)))
    bars = ax.bar(actions['Action'], actions['Count'], color='#4C72B0')
    ax.set_ylabel('Count', fontsize=11)
    ax.set_xlabel('Action', fontsize=11)
    ax.set_title('Combined Action Counts', fontsize=14, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.25)

    # Add small labels on top of bars for clarity (only for visible bars)
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h, f'{int(h):,}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    out_base = os.path.join(visuals_dir, 'combined_action_counts')
    save_fig_variants(fig, out_base, dpi=600)
    plt.close(fig)
    print(f'Combined action counts visual saved to {out_base}.png/.pdf/.svg')

if __name__ == '__main__':
    # Run main() when executed as a script. Keep simple usage info.
    import sys
    if len(sys.argv) < 3:
        print('Usage: python analysis/count_writing_and_copy_paste.py <study_data_folder> <output_folder> [--visuals]')
    main()
