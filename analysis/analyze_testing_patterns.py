"""
Testing Pattern Analyzer Script (Enhanced Version)

Analyzes student testing patterns from task-specific files with enhanced reporting.
Each session is assigned to exactly one pattern category.
Provides detailed per-user, per-task pattern summaries and visualizations.

Features:
- Detailed per-user pattern analysis
- Per-task pattern summaries
- Individual user reports
- Comprehensive visualizations
- Statistical summaries

Usage:
python analyze_testing_patterns.py [prepared_data_folder] [output_base_filename]

Example:
python analyze_testing_patterns.py prepared_data results/enhanced_analysis
"""

import os
import sys
import csv
import json
from datetime import datetime
import glob
from collections import defaultdict, Counter
import subprocess

# Constants
BREAK_THRESHOLD = 10  # seconds

# Categories of IDE actions
EVENT_CATEGORIES = {
    'WRITE': ['EditorEnter', 'EditorTab', 'EditorChooseLookupItem', 'InsertInlineCompletionAction'],
    'DELETE': ['EditorBackSpace', '$Delete', 'EditorDeleteLine'],
    'CLIPBOARD': ['$Copy', '$Cut', '$Paste'],
    'RUN': ['Run', 'Debug', 'Execute'],
    'EXECUTION': ['Execution'],
    'NAVIGATION': ['EditorRight', 'EditorLeft', 'EditorUp', 'EditorDown']
}

# Pattern colors for visualizations
PATTERN_COLORS = {
    "Copy/paste + write + compile": "#1f77b4",  # blue
    "Heavy editing": "#d62728",  # red
    "Iterative write/compile": "#ff7f0e",  # orange
    "Write entire test then compile and run": "#2ca02c",  # green
    "Write without running": "#9467bd",  # purple
    "Run with minimal changes": "#17becf",  # cyan
    "Read only": "#8c564b"  # brown
}

# Task names for better labeling
TASK_NAMES = {
    "1": "Print Error Statement Coverage",
    "2": "Read Statement Coverage", 
    "3": "Write Branch Coverage",
    "4": "Read Path Coverage"
}

def analyze_patterns(prepared_data_folder, output_base_filename):
    """Main analysis function."""
    print(f"Starting analysis on folder: {prepared_data_folder}")
    
    # Define tasks
    tasks = {
        "1": "print_error_statement_coverage",
        "2": "read_statement_coverage",
        "3": "write_branch_coverage",
        "4": "read_path_coverage"
    }
    
    # Initialize results
    results = {
        task_id: {"task_name": name, "users": [], "overall": {}} 
        for task_id, name in tasks.items()
    }
    
    # Find all user folders
    user_folders = glob.glob(os.path.join(prepared_data_folder, "user_*"))
    print(f"Found {len(user_folders)} user folders")
    
    # Process each user
    for user_folder in user_folders:
        user_id = os.path.basename(user_folder)
        print(f"Processing {user_id}...")
        
        # Process each task for this user
        for task_id, task_name in tasks.items():
            # Look for task-specific IDE events file (try both compressed and regular naming)
            ide_events_file = os.path.join(user_folder, f"{user_id}_task{task_id}_ide_events.csv")
            if not os.path.isfile(ide_events_file):
                # Try compressed version
                ide_events_file = os.path.join(user_folder, f"{user_id}_task{task_id}_ide_events_compressed.csv")
                if not os.path.isfile(ide_events_file):
                    print(f"No IDE events file found for {user_id}, task {task_id}")
                    continue
            
            # Look for task-specific code changes file
            code_file = os.path.join(user_folder, f"{user_id}_task{task_id}_code_changes.csv")
            if not os.path.isfile(code_file):
                print(f"No code changes file found for {user_id}, task {task_id}")
                continue
            
            # Read and process IDE events
            ide_events = read_csv_file(ide_events_file)
            if not ide_events:
                print(f"No events read from {ide_events_file}")
                continue
            
            print(f"Read {len(ide_events)} IDE events for {user_id}, task {task_id}")
            
            # Process events - add datetime objects and categories
            valid_events = []
            for event in ide_events:
                # Add datetime object for timestamp
                if 'timestamp' in event:
                    try:
                        event['dateObj'] = parse_datetime(event['timestamp'])
                        # Add category
                        event['category'] = categorize_event(event)
                        valid_events.append(event)
                    except Exception as e:
                        print(f"Error parsing timestamp: {event.get('timestamp')} - {e}")
            
            # Read and process code changes
            code_changes = read_csv_file(code_file)
            if not code_changes:
                print(f"No code changes read from {code_file}")
                continue
            
            print(f"Read {len(code_changes)} code changes for {user_id}, task {task_id}")
            
            # Process code changes - add datetime objects
            valid_changes = []
            for change in code_changes:
                # Add datetime object for timestamp
                if 'date' in change:
                    try:
                        change['dateObj'] = parse_datetime(change['date'])
                        valid_changes.append(change)
                    except Exception as e:
                        print(f"Error parsing date: {change.get('date')} - {e}")
            
            # Analyze if we have both valid events and changes
            if valid_events and valid_changes:
                analyze_user_task(user_id, task_id, valid_events, valid_changes, results)
    
    # Calculate overall statistics
    for task_id, task_results in results.items():
        calculate_overall_stats(task_results)
    
    # Save results
    save_results(results, output_base_filename)
    
    # Generate enhanced reports and visualizations
    generate_enhanced_reports(results, output_base_filename)
    
    # Generate visualizations using external scripts
    generate_visualizations_external(results, output_base_filename)
    
    # Print summary
    print_summary(results)
    
    return results

def analyze_user_task(user_id, task_id, ide_events, code_changes, results):
    """Analyze testing patterns for a specific user on a specific task."""
    if not ide_events or not code_changes:
        return
    
    # Find sessions
    sessions = find_sessions(ide_events)
    print(f"Found {len(sessions)} sessions for {user_id}, task {task_id}")
    
    # Identify patterns in each session
    user_patterns = []
    for session in sessions:
        pattern = identify_pattern(session)
        if pattern:
            user_patterns.append(pattern)
    
    # Calculate active time
    active_time = calculate_active_time(ide_events)
    
    # Create user result
    user_result = {
        'user_id': user_id,
        'total_events': len(ide_events),
        'sessions': len(sessions),
        'active_time_seconds': active_time,
        'patterns': user_patterns
    }
    
    # Add to results
    results[task_id]['users'].append(user_result)
    print(f"Added user {user_id} to results for task {task_id} with {len(user_patterns)} patterns")

def find_sessions(events):
    """Group events into sessions based on time gaps."""
    if not events:
        return []
    
    # Sort events by time
    events.sort(key=lambda x: x['dateObj'])
    
    sessions = []
    current_session = {'start': events[0]['dateObj'], 'end': events[0]['dateObj'], 'events': [events[0]]}
    
    for i in range(1, len(events)):
        event = events[i]
        time_diff = (event['dateObj'] - current_session['end']).total_seconds()
        
        if time_diff > BREAK_THRESHOLD:
            # End current session and start new one
            sessions.append(current_session)
            current_session = {'start': event['dateObj'], 'end': event['dateObj'], 'events': [event]}
        else:
            # Continue current session
            current_session['events'].append(event)
            current_session['end'] = event['dateObj']
    
    # Add the last session
    if current_session['events']:
        sessions.append(current_session)
    
    return sessions

def identify_pattern(session):
    """Identify a single pattern for a session.
    Each session is assigned the most significant pattern that applies to it.
    Patterns are checked in order of priority."""
    # Count event categories
    category_counts = Counter(event['category'] for event in session['events'])
    
    # Calculate session duration
    duration = (session['end'] - session['start']).total_seconds()
    
    # Skip very short sessions
    if duration < 5:
        return None
    
    # Create pattern object template
    pattern_obj = {
        'duration': duration,
        'start_time': session['start'].isoformat(),
        'end_time': session['end'].isoformat()
    }
    
    # Check for patterns in priority order:
    
    # 1. Cut/copy/pasted + write + compile (highest priority)
    if (category_counts.get('CLIPBOARD', 0) > 0 and 
            category_counts.get('WRITE', 0) > 0 and 
            (category_counts.get('RUN', 0) > 0 or category_counts.get('EXECUTION', 0) > 0)):
        pattern_obj['pattern'] = "Copy/paste + write + compile"
        return pattern_obj
    
    # 2. Iterative write/compile
    if (category_counts.get('WRITE', 0) > 0 and 
            (category_counts.get('RUN', 0) > 1 or category_counts.get('EXECUTION', 0) > 1)):
        pattern_obj['pattern'] = "Iterative write/compile"
        return pattern_obj
    
    # 3. Write entire test then compile and run
    if (category_counts.get('WRITE', 0) > 5 and 
            (category_counts.get('RUN', 0) > 0 or category_counts.get('EXECUTION', 0) > 0)):
        pattern_obj['pattern'] = "Write entire test then compile and run"
        return pattern_obj
    
    # 4. Heavy editing
    if (category_counts.get('WRITE', 0) > 10 or 
            category_counts.get('DELETE', 0) > 5):
        pattern_obj['pattern'] = "Heavy editing"
        return pattern_obj
    
    # 5. Run with minimal changes
    if ((category_counts.get('RUN', 0) > 0 or category_counts.get('EXECUTION', 0) > 0) and
            category_counts.get('WRITE', 0) < 5):
        pattern_obj['pattern'] = "Run with minimal changes"
        return pattern_obj
    
    # 6. Write without running
    if category_counts.get('WRITE', 0) > 0:
        pattern_obj['pattern'] = "Write without running"
        return pattern_obj
    
    # 7. Read only (navigation but no edits)
    if category_counts.get('NAVIGATION', 0) > 0:
        pattern_obj['pattern'] = "Read only"
        return pattern_obj
    
    # Skip any other activity that doesn't fit the above patterns
    return None

def calculate_active_time(events):
    """Calculate total active time excluding breaks."""
    if not events:
        return 0
    
    # Sort events by time
    events.sort(key=lambda x: x['dateObj'])
    
    total_time = 0
    prev_time = events[0]['dateObj']
    
    for i in range(1, len(events)):
        curr_time = events[i]['dateObj']
        time_diff = (curr_time - prev_time).total_seconds()
        
        if time_diff <= BREAK_THRESHOLD:
            total_time += time_diff
        
        prev_time = curr_time
    
    return total_time

def categorize_event(event):
    """Categorize an IDE event based on its action type."""
    action = event.get('actionType', '')
    
    for category, actions in EVENT_CATEGORIES.items():
        if any(a in action for a in actions if action):
            return category
    
    if event.get('eventType') == 'Execution':
        return 'EXECUTION'
    
    return 'OTHER'

def calculate_overall_stats(task_results):
    """Calculate overall statistics for a task."""
    users = task_results.get('users', [])
    if not users:
        return
    
    # Count patterns
    all_patterns = [p for user in users for p in user.get('patterns', [])]
    pattern_counts = Counter(p['pattern'] for p in all_patterns)
    
    # Calculate average active time per user
    total_active_time = sum(user.get('active_time_seconds', 0) for user in users)
    avg_active_time = total_active_time / len(users) if users else 0
    
    task_results['overall'] = {
        'total_users': len(users),
        'total_events': sum(user.get('total_events', 0) for user in users),
        'total_sessions': sum(user.get('sessions', 0) for user in users),
        'avg_active_time_seconds': avg_active_time,
        'pattern_summary': dict(pattern_counts)
    }

def generate_enhanced_reports(results, output_base_filename):
    """Generate enhanced per-user and per-task reports."""
    base_name = os.path.splitext(output_base_filename)[0]
    
    # Create detailed user-task pattern matrix
    user_task_matrix_file = f"{base_name}_user_task_patterns.csv"
    with open(user_task_matrix_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'task_id', 'task_name', 'total_patterns', 
                        'total_events', 'sessions', 'active_time_minutes',
                        'dominant_pattern', 'pattern_diversity',
                        'Copy/paste + write + compile', 'Iterative write/compile',
                        'Write entire test then compile and run', 'Heavy editing',
                        'Run with minimal changes', 'Write without running', 'Read only'])
        
        for task_id, task_data in results.items():
            task_name = TASK_NAMES.get(task_id, task_data.get('task_name', f'Task {task_id}'))
            
            for user in task_data.get('users', []):
                user_id = user.get('user_id', 'unknown')
                patterns = user.get('patterns', [])
                
                # Count patterns by type
                pattern_counts = Counter(p['pattern'] for p in patterns)
                total_patterns = len(patterns)
                
                # Calculate pattern diversity (number of unique patterns)
                pattern_diversity = len(pattern_counts)
                
                # Find dominant pattern
                dominant_pattern = pattern_counts.most_common(1)[0][0] if pattern_counts else 'None'
                
                # Individual pattern counts
                copy_paste_count = pattern_counts.get('Copy/paste + write + compile', 0)
                iterative_count = pattern_counts.get('Iterative write/compile', 0)
                write_then_run_count = pattern_counts.get('Write entire test then compile and run', 0)
                heavy_edit_count = pattern_counts.get('Heavy editing', 0)
                minimal_run_count = pattern_counts.get('Run with minimal changes', 0)
                write_only_count = pattern_counts.get('Write without running', 0)
                read_only_count = pattern_counts.get('Read only', 0)
                
                writer.writerow([
                    user_id, task_id, task_name, total_patterns,
                    user.get('total_events', 0), user.get('sessions', 0),
                    round(user.get('active_time_seconds', 0) / 60, 2),
                    dominant_pattern, pattern_diversity,
                    copy_paste_count, iterative_count, write_then_run_count,
                    heavy_edit_count, minimal_run_count, write_only_count, read_only_count
                ])
    
    print(f"Enhanced user-task pattern matrix saved to {user_task_matrix_file}")
    
    # Generate individual user summary reports
    generate_individual_user_reports(results, base_name)
    
    # Generate task comparison report
    generate_task_comparison_report(results, base_name)

def generate_individual_user_reports(results, base_name):
    """Generate individual reports for each user across all tasks."""
    # Collect all users
    all_users = set()
    for task_data in results.values():
        for user in task_data.get('users', []):
            all_users.add(user.get('user_id'))
    
    user_reports_dir = f"{base_name}_user_reports"
    os.makedirs(user_reports_dir, exist_ok=True)
    
    for user_id in sorted(all_users):
        user_report_file = os.path.join(user_reports_dir, f"user_{user_id}_summary.csv")
        
        with open(user_report_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'task_id', 'task_name', 'patterns_found',
                           'active_time_minutes', 'sessions', 'events', 'most_common_pattern',
                           'pattern_breakdown'])
            
            for task_id, task_data in results.items():
                task_name = TASK_NAMES.get(task_id, task_data.get('task_name', f'Task {task_id}'))
                
                # Find this user's data for this task
                user_data = None
                for user in task_data.get('users', []):
                    if user.get('user_id') == user_id:
                        user_data = user
                        break
                
                if user_data:
                    patterns = user_data.get('patterns', [])
                    pattern_counts = Counter(p['pattern'] for p in patterns)
                    most_common = pattern_counts.most_common(1)[0][0] if pattern_counts else 'None'
                    pattern_breakdown = '; '.join([f"{p}: {c}" for p, c in pattern_counts.most_common()])
                    
                    writer.writerow([
                        user_id, task_id, task_name, len(patterns),
                        round(user_data.get('active_time_seconds', 0) / 60, 2),
                        user_data.get('sessions', 0), user_data.get('total_events', 0),
                        most_common, pattern_breakdown
                    ])
                else:
                    writer.writerow([user_id, task_id, task_name, 0, 0, 0, 0, 'No Data', ''])
    
    print(f"Individual user reports saved to {user_reports_dir}/")

def generate_task_comparison_report(results, base_name):
    """Generate a comprehensive task comparison report."""
    task_comparison_file = f"{base_name}_task_comparison.csv"
    
    with open(task_comparison_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['task_id', 'task_name', 'total_users', 'avg_patterns_per_user',
                        'avg_active_time_minutes', 'most_common_pattern', 'pattern_diversity_score',
                        'total_sessions', 'avg_sessions_per_user'])
        
        for task_id, task_data in results.items():
            task_name = TASK_NAMES.get(task_id, task_data.get('task_name', f'Task {task_id}'))
            users = task_data.get('users', [])
            
            if not users:
                continue
                
            # Calculate metrics
            total_users = len(users)
            all_patterns = [p for user in users for p in user.get('patterns', [])]
            pattern_counts = Counter(p['pattern'] for p in all_patterns)
            
            avg_patterns_per_user = len(all_patterns) / total_users if total_users > 0 else 0
            avg_active_time = sum(user.get('active_time_seconds', 0) for user in users) / total_users / 60 if total_users > 0 else 0
            most_common_pattern = pattern_counts.most_common(1)[0][0] if pattern_counts else 'None'
            pattern_diversity = len(pattern_counts)  # Number of unique patterns in this task
            total_sessions = sum(user.get('sessions', 0) for user in users)
            avg_sessions_per_user = total_sessions / total_users if total_users > 0 else 0
            
            writer.writerow([
                task_id, task_name, total_users, round(avg_patterns_per_user, 2),
                round(avg_active_time, 2), most_common_pattern, pattern_diversity,
                total_sessions, round(avg_sessions_per_user, 2)
            ])
    
    print(f"Task comparison report saved to {task_comparison_file}")

def generate_visualizations_external(results, output_base_filename):
    """Generate visualizations using external visualization scripts."""
    base_name = os.path.splitext(output_base_filename)[0]
    json_file = f"{base_name}.json"
    viz_dir = f"{base_name}_visualizations"
    
    print(f"\nGenerating visualizations...")
    
    # Check if the generate_all_visualizations.py script exists
    if not os.path.exists("generate_all_visualizations.py"):
        print("Warning: generate_all_visualizations.py not found. Skipping visualizations.")
        print("To generate visualizations manually, use the individual viz_*.py scripts.")
        return
    
    try:
        # Run the visualization generation script
        cmd = [sys.executable, "generate_all_visualizations.py", json_file, viz_dir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Visualizations generated successfully!")
        else:
            print(f"Visualization generation failed: {result.stderr}")
            print("You can generate visualizations manually using:")
            print(f"python generate_all_visualizations.py {json_file} {viz_dir}")
            
    except Exception as e:
        print(f"Error running visualization scripts: {e}")
        print("You can generate visualizations manually using the individual viz_*.py scripts.")

def save_results(results, output_base_filename):
    """Save analysis results to CSV and JSON files."""
    # Create output directory if needed
    output_dir = os.path.dirname(output_base_filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Remove file extension if present
    base_name = os.path.splitext(output_base_filename)[0]
    
    # Save JSON
    json_file = f"{base_name}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Complete results saved to {json_file}")
    
    # Save CSV: Summary
    summary_file = f"{base_name}_summary.csv"
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['task_id', 'task_name', 'total_users', 'total_events', 
                         'total_sessions', 'avg_active_time_seconds'])
        
        for task_id, task_data in results.items():
            if 'overall' not in task_data:
                continue
            writer.writerow([
                task_id,
                task_data['task_name'],
                task_data['overall'].get('total_users', 0),
                task_data['overall'].get('total_events', 0),
                task_data['overall'].get('total_sessions', 0),
                task_data['overall'].get('avg_active_time_seconds', 0)
            ])
    print(f"Summary saved to {summary_file}")
    
    # Save CSV: Patterns
    patterns_file = f"{base_name}_patterns.csv"
    with open(patterns_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['task_id', 'task_name', 'pattern', 'count'])
        
        for task_id, task_data in results.items():
            if 'overall' not in task_data or 'pattern_summary' not in task_data['overall']:
                continue
            
            for pattern, count in task_data['overall']['pattern_summary'].items():
                writer.writerow([
                    task_id,
                    task_data['task_name'],
                    pattern,
                    count
                ])
    print(f"Pattern summary saved to {patterns_file}")
    
    # Save CSV: User details and pattern details for each task
    for task_id, task_data in results.items():
        if not task_data.get('users'):
            continue
        
        # User details
        user_file = f"{base_name}_task{task_id}_users.csv"
        with open(user_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['task_id', 'user_id', 'total_events', 'sessions', 
                             'active_time_seconds', 'pattern_count'])
            
            for user in task_data['users']:
                writer.writerow([
                    task_id,
                    user.get('user_id', 'unknown'),
                    user.get('total_events', 0),
                    user.get('sessions', 0),
                    user.get('active_time_seconds', 0),
                    len(user.get('patterns', []))
                ])
        print(f"User details for task {task_id} saved to {user_file}")
        
        # Pattern details
        pattern_file = f"{base_name}_task{task_id}_pattern_details.csv"
        with open(pattern_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['task_id', 'user_id', 'pattern', 'duration_seconds', 
                             'start_time', 'end_time'])
            
            for user in task_data['users']:
                user_id = user.get('user_id', 'unknown')
                for pattern in user.get('patterns', []):
                    writer.writerow([
                        task_id,
                        user_id,
                        pattern.get('pattern', 'unknown'),
                        pattern.get('duration', 0),
                        pattern.get('start_time', ''),
                        pattern.get('end_time', '')
                    ])
        print(f"Pattern details for task {task_id} saved to {pattern_file}")

def print_summary(results):
    """Print enhanced summary of testing patterns."""
    print("\n" + "="*80)
    print("ENHANCED TESTING PATTERN ANALYSIS SUMMARY")
    print("="*80)
    
    # Overall statistics
    total_users = sum(len(task_result.get('users', [])) for task_result in results.values())
    total_patterns = sum(len([p for user in task_result.get('users', []) for p in user.get('patterns', [])]) for task_result in results.values())
    
    print(f"\nOverall Statistics:")
    print(f"  Total Users Analyzed: {total_users}")
    print(f"  Total Pattern Instances: {total_patterns}")
    print(f"  Tasks Analyzed: {len(results)}")
    
    # Per-task summary
    for task_id, task_result in results.items():
        if 'overall' not in task_result or 'total_users' not in task_result['overall']:
            print(f"\nTask {task_id}: No data")
            continue
            
        task_name = TASK_NAMES.get(task_id, task_result.get('task_name', f'Task {task_id}'))
        print(f"\n{'-'*60}")
        print(f"Task {task_id}: {task_name}")
        print(f"{'-'*60}")
        print(f"  Users: {task_result['overall']['total_users']}")
        
        avg_time = task_result['overall'].get('avg_active_time_seconds', 0)
        if avg_time > 0:
            print(f"  Average active time per user: {avg_time / 60:.2f} minutes")
        
        print(f"  Total sessions: {task_result['overall'].get('total_sessions', 0)}")
        
        print(f"  Pattern distribution:")
        pattern_summary = task_result['overall'].get('pattern_summary', {})
        total_task_patterns = sum(pattern_summary.values())
        
        for pattern, count in sorted(pattern_summary.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_task_patterns * 100) if total_task_patterns > 0 else 0
            print(f"    • {pattern}: {count} ({percentage:.1f}%)")
    
    # Pattern analysis across all tasks
    print(f"\n{'-'*60}")
    print("CROSS-TASK PATTERN ANALYSIS")
    print(f"{'-'*60}")
    
    all_patterns = []
    for task_result in results.values():
        for user in task_result.get('users', []):
            all_patterns.extend([p['pattern'] for p in user.get('patterns', [])])
    
    overall_pattern_counts = Counter(all_patterns)
    total_overall_patterns = sum(overall_pattern_counts.values())
    
    print(f"Overall pattern distribution across all tasks:")
    for pattern, count in sorted(overall_pattern_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_overall_patterns * 100) if total_overall_patterns > 0 else 0
        print(f"  • {pattern}: {count} ({percentage:.1f}%)")
    
    # User diversity analysis
    user_pattern_diversity = {}
    all_users = set()
    for task_result in results.values():
        for user in task_result.get('users', []):
            user_id = user.get('user_id')
            all_users.add(user_id)
            if user_id not in user_pattern_diversity:
                user_pattern_diversity[user_id] = set()
            user_pattern_diversity[user_id].update([p['pattern'] for p in user.get('patterns', [])])
    
    avg_diversity = sum(len(patterns) for patterns in user_pattern_diversity.values()) / len(user_pattern_diversity) if user_pattern_diversity else 0
    
    print(f"\nUser Pattern Diversity:")
    print(f"  Average patterns per user: {avg_diversity:.1f}")
    print(f"  Most diverse users (top 5):")
    
    top_diverse_users = sorted(user_pattern_diversity.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    for user_id, patterns in top_diverse_users:
        print(f"    User {user_id}: {len(patterns)} unique patterns")
    
    print(f"\n{'='*80}")
    print("Analysis complete! Check the generated files and visualizations for detailed insights.")
    print(f"{'='*80}\n")

# Helper functions
def read_csv_file(file_path):
    """Read a CSV file and return a list of dictionaries."""
    if not os.path.isfile(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Check if file is empty
            sample = f.read(1024)
            if not sample.strip():
                return []
            
            f.seek(0)  # Go back to beginning of file
            
            # Try to parse as CSV
            reader = csv.DictReader(f)
            rows = list(reader)
            return rows
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def parse_datetime(date_str):
    """Parse datetime string to datetime object."""
    if not date_str:
        raise ValueError("Empty date string")
    
    # Handle different formats
    try:
        if '-04:00' in date_str:  # Handle timezone format
            return datetime.fromisoformat(date_str.replace('-04:00', '+00:00'))
        else:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        # Fall back to more lenient parsing
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except:
                # Try one more format
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")

def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python analyze_testing_patterns.py [prepared_data_folder] [output_base_filename]")
        print("Example: python analyze_testing_patterns.py prepared_data results/analysis")
        sys.exit(1)
    
    prepared_data_folder = sys.argv[1]
    output_base_filename = sys.argv[2]
    
    # Verify the data folder exists
    if not os.path.isdir(prepared_data_folder):
        print(f"ERROR: Data folder does not exist: {prepared_data_folder}")
        sys.exit(1)
    
    analyze_patterns(prepared_data_folder, output_base_filename)

if __name__ == "__main__":
    main()