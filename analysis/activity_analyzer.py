"""
Activity Tracker CSV Analyzer with IDE Events Integration

This script analyzes activity tracking CSV files by merging code fragment data
from task files (1_, 2_, 3_, 4_) with explicit IDE actions from ide-events files.
All consecutive actions of the same type are grouped together.

Usage:
python activity_analyzer.py [input_path] [--output output_path] [--directory] [--threshold ms]
"""

import csv
import sys
import argparse
import difflib
from pathlib import Path
from datetime import datetime


class ActivityAnalyzer:
    """Analyzes activity tracking CSV files and merges with IDE event data."""

    # Action descriptions for known IDE actions
    ACTION_DESCRIPTIONS = {
        'Active': 'IDE gained focus',
        'Inactive': 'IDE lost focus',
        'NoProject': 'All projects closed',
        'NewProject': 'Create new project',
        'SaveAs': 'Save file as',
        'SaveAll': 'Save all files',
        'NewPythonFile': 'Create Python file',
        'ChooseRunConfiguration': 'Choose run configuration',
        'Run': 'Run program',
        'Rerun': 'Run program again',
        'RunClass': 'Run class',
        'DebugClass': 'Debug class',
        'ToggleLineBreakpoint': 'Toggle line breakpoint',
        'Debug': 'Debug program',
        'Stop': 'Stop debug/run',
        'Resume': 'Resume debug program',
        'StepInto': 'Step into (debugging)',
        'CompileDirty': 'Compile',
        'EditorBackSpace': 'Press Backspace',
        'EditorLeft': 'Press Left arrow',
        'EditorRight': 'Press Right arrow',
        'EditorEnter': 'Press Enter',
        'EditorTab': 'Press Tab',
        'EditorDown': 'Press Down arrow',
        'EditorUp': 'Press Up arrow',
        'EditorDelete': 'Press Delete',
        'EditorChooseLookupItem': 'Choose autocomplete item',
        'EditorSplitLine': 'Split line',
        'EditorRightWithSelection': 'Select right',
        'EditorLeftWithSelection': 'Select left',
        'EditorDuplicate': 'Duplicate line',
        'EditorCopy': 'Copy text',
        'EditorPaste': 'Paste text',
        'EditorCut': 'Cut text',
        'CopyPaths': 'Copy file path',
        'ReformatCode': 'Reformat code',
        'NewElement': 'Create new element',
        'ShowPopupMenu': 'Show popup menu',
        'SearchEverywhere': 'Search everywhere',
        'InsertInlineCompletionAction': 'Accept inline completion',
        '$Undo': 'Undo (Ctrl+Z)',
        '$Paste': 'Paste (Ctrl+V)',
        '$Copy': 'Copy (Ctrl+C)',
        '$Redo': 'Redo (Ctrl+Y)',
        'CompilationFinished': 'Compilation finished',
    }

    def __init__(self, inactivity_threshold_ms=60000, log_content=True, max_content_length=0):
        """
        Initialize the analyzer.

        Args:
            inactivity_threshold_ms (int): Threshold for detecting inactivity in milliseconds
            log_content (bool): Whether to log actual content changes
            max_content_length (int): Maximum length of content to log (0 = unlimited)
        """
        self.inactivity_threshold_ms = inactivity_threshold_ms
        self.log_content = log_content
        self.max_content_length = max_content_length

    def _is_task_file(self, filepath):
        """Check if file is a task file (1_, 2_, 3_, 4_ prefix)."""
        filename = Path(filepath).name
        return any(filename.startswith(prefix) for prefix in ['1_', '2_', '3_', '4_'])

    def _find_ide_events_file(self, task_file_path):
        """
        Find the corresponding ide-events file for a task file.

        Args:
            task_file_path (str): Path to the task CSV file

        Returns:
            str: Path to ide-events file or None if not found
        """
        task_path = Path(task_file_path)
        directory = task_path.parent

        ide_events_files = list(directory.glob("ide-events*.csv"))

        if ide_events_files:
            return str(ide_events_files[0])
        return None

    def analyze_file(self, input_path, output_path=None):
        """
        Analyze a single CSV file and generate output.

        Args:
            input_path (str): Path to input CSV file
            output_path (str): Path to output CSV file (optional)
        """
        if output_path is None:
            input_file = Path(input_path)
            output_path = input_file.parent / f"{input_file.stem}_analyzed.csv"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        print(f"Processing: {input_path}")

        # Check if this is a task file and find corresponding ide-events
        ide_events_data = {}
        if self._is_task_file(input_path):
            ide_events_file = self._find_ide_events_file(input_path)
            if ide_events_file:
                print(f"  Found IDE events: {Path(ide_events_file).name}")
                ide_events_data = self._read_ide_events(ide_events_file)
            else:
                print(f"  Warning: No IDE events file found")

        rows = self._read_csv(input_path)

        if not rows:
            print(f"Warning: No data found in {input_path}")
            return

        actions = self._analyze_actions(rows, ide_events_data)
        self._write_output_csv(output_path, actions)

        print(f"✓ Output saved to: {output_path}")
        print(f"  Total actions logged: {len(actions)}")
        print()

    def analyze_directory(self, directory_path, output_dir=None):
        """
        Analyze all CSV files in a directory recursively.

        Args:
            directory_path (str): Root directory containing CSV files
            output_dir (str): Directory to save output files (optional)
        """
        directory = Path(directory_path)

        if not directory.exists() or not directory.is_dir():
            print(f"Error: {directory_path} is not a valid directory")
            return

        # Find only task files (1_, 2_, 3_, 4_)
        csv_files = []
        for pattern in ['1_*.csv', '2_*.csv', '3_*.csv', '4_*.csv']:
            csv_files.extend(directory.rglob(pattern))

        if not csv_files:
            print(f"No task CSV files found in {directory_path}")
            return

        print(f"Found {len(csv_files)} task file(s) to process\n")

        output_root = Path(output_dir) if output_dir else None
        if output_root:
            output_root.mkdir(parents=True, exist_ok=True)

        for i, csv_file in enumerate(csv_files, 1):
            print(f"[{i}/{len(csv_files)}] ", end="")

            if output_root:
                try:
                    rel = csv_file.relative_to(directory)
                except Exception:
                    rel = Path(csv_file.name)

                target_dir = output_root / rel.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                output_file = target_dir / f"{csv_file.stem}_analyzed.csv"
            else:
                output_file = None

            self.analyze_file(str(csv_file), str(output_file) if output_file else None)

        print(f"\n{'='*60}")
        print(f"Batch processing complete! Processed {len(csv_files)} file(s)")
        print(f"{'='*60}")

    def _read_csv(self, file_path):
        """Read CSV file and return list of row dictionaries."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _read_ide_events(self, file_path):
        """
        Read IDE events file and return dictionary mapping timestamps to actions.

        Args:
            file_path (str): Path to ide-events CSV file

        Returns:
            dict: Dictionary with timestamp (ms) as key and action info as value
        """
        events = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    timestamp_str = parts[0]
                    event_type = parts[1]
                    action = parts[2]

                    # Only process Action events (not IdeState)
                    if event_type == 'Action':
                        ts_ms = self._parse_timestamp(timestamp_str)
                        events[ts_ms] = {
                            'action': action,
                            'raw_line': line.strip()
                        }

        return events

    def _find_matching_ide_event(self, timestamp_ms, ide_events_data, window_ms=200):
        """
        Find IDE event matching a timestamp within a time window.

        Args:
            timestamp_ms (int): Timestamp to match
            ide_events_data (dict): Dictionary of IDE events
            window_ms (int): Time window in milliseconds

        Returns:
            str: Action name or None if no match found
        """
        for event_ts, event_info in ide_events_data.items():
            if abs(event_ts - timestamp_ms) <= window_ms:
                return event_info['action']
        return None

    def _parse_timestamp(self, value):
        """
        Parse timestamp from various formats to milliseconds since epoch.

        Args:
            value: Timestamp value (int, float, or ISO string)

        Returns:
            int: Milliseconds since epoch
        """
        if value is None:
            return 0

        if isinstance(value, (int, float)):
            iv = int(value)
            return int(iv * 1000) if iv < 10**11 else iv

        s = str(value).strip()
        if not s:
            return 0

        if s.isdigit():
            iv = int(s)
            return int(iv * 1000) if iv < 10**11 else iv

        if s.endswith('Z'):
            s = s[:-1] + '+00:00'

        try:
            dt = datetime.fromisoformat(s)
            return int(dt.timestamp() * 1000)
        except Exception:
            try:
                fv = float(s)
                iv = int(fv)
                return int(iv * 1000) if iv < 10**11 else iv
            except Exception:
                return 0

    def _analyze_actions(self, rows, ide_events_data):
        """
        Analyze rows and extract human-readable actions with timing.
        Groups ALL consecutive actions of the same type together.

        Args:
            rows (list): List of CSV row dictionaries
            ide_events_data (dict): Dictionary of IDE events by timestamp

        Returns:
            list: List of action dictionaries
        """
        actions = []

        if not rows:
            return actions

        # Initialize session
        session_start = self._parse_timestamp(rows[0].get('date'))

        # Tracking variables
        previous_row = None
        previous_fragment = ''
        pending_group = None  # Current action group being accumulated

        # Edit and delete action types for grouping
        edit_types = {'Type character', 'Type text', 'Insert text', 'Copy/Paste (internal)', 'Paste (external)'}
        delete_types = {'Delete character', 'Delete text', 'Delete block'}

        # Add session start action
        first_ts = self._parse_timestamp(rows[0].get('date'))
        second_ts = self._parse_timestamp(rows[1].get('date')) if len(rows) > 1 else first_ts

        actions.append({
            'action': 'Session started',
            'start': 0,
            'duration': max(0, second_ts - first_ts),
            'inactivity': 0,
            'details': f"File: {rows[0].get('fileName','')}, Task: {rows[0].get('chosenTask','')}",
            'content': ''
        })

        for i, row in enumerate(rows[1:], 1):
            curr_ts = self._parse_timestamp(row.get('date'))
            prev_ts = self._parse_timestamp(previous_row.get('date')) if previous_row else session_start

            # Calculate timing
            time_since_last = max(0, curr_ts - prev_ts)
            start_relative = max(0, curr_ts - session_start)

            # Get next timestamp for duration calculation
            if i + 1 < len(rows):
                next_ts = self._parse_timestamp(rows[i + 1].get('date'))
                duration_to_next = max(0, next_ts - curr_ts)
            else:
                duration_to_next = 0

            # Check for inactivity
            if time_since_last >= self.inactivity_threshold_ms:
                # Finalize any pending group
                if pending_group:
                    self._finalize_group(actions, pending_group)
                    pending_group = None

                # Add inactivity action
                inactivity_start = prev_ts - session_start
                actions.append({
                    'action': 'Inactivity',
                    'start': inactivity_start,
                    'duration': time_since_last,
                    'inactivity': time_since_last / 60000,
                    'details': f"Inactive for {time_since_last/1000:.1f} seconds",
                    'content': ''
                })

            # Check for matching IDE event
            ide_action = self._find_matching_ide_event(curr_ts, ide_events_data)

            if ide_action:
                # Found explicit IDE action
                action_desc = self.ACTION_DESCRIPTIONS.get(ide_action, ide_action)
                content = self._extract_ide_action_content(
                    ide_action,
                    previous_fragment,
                    row.get('fragment', '')
                )

                # Check if we should group this with pending group
                if pending_group is None or pending_group['action'] != action_desc:
                    # Finalize previous group if exists
                    if pending_group:
                        self._finalize_group(actions, pending_group)

                    # Start new group
                    pending_group = {
                        'action': action_desc,
                        'start': start_relative,
                        'end': start_relative + duration_to_next,
                        'content': content,
                        'count': 1
                    }
                else:
                    # Extend existing group (same action type)
                    pending_group['end'] = start_relative + duration_to_next
                    if content:
                        pending_group['content'] += content
                    pending_group['count'] += 1

                previous_row = row
                previous_fragment = row.get('fragment', '')
                continue

            # No IDE event - detect action from fragment changes
            if previous_row is not None:
                action_info = self._detect_action(previous_row, row, previous_fragment)

                if action_info:
                    action_type = action_info['type']

                    # Determine grouping category
                    if action_type in edit_types:
                        group_category = 'Edit'
                    elif action_type in delete_types:
                        group_category = 'Delete'
                    else:
                        # Other actions get grouped by their exact type
                        group_category = action_type

                    # Check if we should group this
                    if pending_group is None or pending_group['action'] != group_category:
                        # Finalize previous group if exists
                        if pending_group:
                            self._finalize_group(actions, pending_group)

                        # Start new group
                        pending_group = {
                            'action': group_category,
                            'start': start_relative,
                            'end': start_relative + duration_to_next,
                            'content': action_info.get('content', ''),
                            'count': 1
                        }
                    else:
                        # Extend existing group
                        pending_group['end'] = start_relative + duration_to_next
                        pending_group['content'] += action_info.get('content', '')
                        pending_group['count'] += 1

            previous_row = row
            previous_fragment = row.get('fragment', '')

        # Finalize any remaining pending group
        if pending_group:
            self._finalize_group(actions, pending_group)

        # Add session total
        last_ts = self._parse_timestamp(rows[-1].get('date'))
        total_duration = max(0, last_ts - session_start)

        actions.append({
            'action': 'Session total',
            'start': 0,
            'duration': total_duration,
            'inactivity': 0,
            'details': f"Total session duration: {total_duration/1000:.1f} seconds",
            'content': ''
        })

        return actions

    def _finalize_group(self, actions, group):
        """
        Finalize a pending action group and add it to actions.

        Args:
            actions (list): List to append the finalized action
            group (dict): Group information to finalize
        """
        duration = max(0, group['end'] - group['start'])

        # Format details based on count
        if group['count'] == 1:
            details = group['action']
        else:
            details = f"{group['action']} (grouped {group['count']} actions)"

        actions.append({
            'action': group['action'],
            'start': group['start'],
            'duration': duration,
            'inactivity': 0,
            'details': details,
            'content': self._format_content(group['content']) if self.log_content else ''
        })

    def _detect_action(self, prev_row, curr_row, prev_fragment):
        """
        Detect what action occurred between two rows.

        Args:
            prev_row (dict): Previous row data
            curr_row (dict): Current row data
            prev_fragment (str): Previous code fragment

        Returns:
            dict: Action information or None
        """
        prev_fragment = prev_row.get('fragment', '')
        curr_fragment = curr_row.get('fragment', '')

        if prev_fragment == curr_fragment:
            if prev_row.get('testMode') != curr_row.get('testMode'):
                return {
                    'type': 'Mode change',
                    'details': f"Test mode: {prev_row.get('testMode')} → {curr_row.get('testMode')}",
                    'content': ''
                }
            return None

        length_diff = len(curr_fragment) - len(prev_fragment)

        # Large insertion - detect paste
        if length_diff > 10:
            added_text = self._find_added_text(prev_fragment, curr_fragment)
            if added_text:
                if added_text.strip() in prev_fragment:
                    return {
                        'type': 'Copy/Paste (internal)',
                        'details': f"Pasted {len(added_text)} character(s) from same file",
                        'content': added_text if self.log_content else ''
                    }
                else:
                    return {
                        'type': 'Paste (external)',
                        'details': f"Pasted {len(added_text)} character(s) from clipboard",
                        'content': added_text if self.log_content else ''
                    }

        # Text added
        if length_diff > 0:
            added_text = self._find_added_text(prev_fragment, curr_fragment)
            if length_diff == 1:
                return {
                    'type': 'Type character',
                    'details': f"Added character",
                    'content': added_text if self.log_content else ''
                }
            elif length_diff <= 10:
                return {
                    'type': 'Type text',
                    'details': f"Added {length_diff} character(s)",
                    'content': added_text if self.log_content else ''
                }
            else:
                return {
                    'type': 'Insert text',
                    'details': f"Inserted {length_diff} character(s)",
                    'content': added_text if self.log_content else ''
                }

        # Text deleted
        elif length_diff < 0:
            deleted_count = abs(length_diff)
            deleted_text = self._find_removed_text(prev_fragment, curr_fragment)

            if deleted_count == 1:
                return {
                    'type': 'Delete character',
                    'details': f"Deleted 1 character",
                    'content': deleted_text if self.log_content else ''
                }
            elif deleted_count <= 10:
                return {
                    'type': 'Delete text',
                    'details': f"Deleted {deleted_count} character(s)",
                    'content': deleted_text if self.log_content else ''
                }
            else:
                return {
                    'type': 'Delete block',
                    'details': f"Deleted {deleted_count} character(s)",
                    'content': deleted_text if self.log_content else ''
                }

        # Text replaced
        else:
            diff_content = self._get_diff_content(prev_fragment, curr_fragment)
            return {
                'type': 'Replace text',
                'details': f"Modified text (same length)",
                'content': diff_content if self.log_content else ''
            }

    def _extract_ide_action_content(self, action, prev_fragment, curr_fragment):
        """Extract content for IDE actions."""
        if not self.log_content:
            return ''

        if action in ('$Undo', '$Redo'):
            return self._get_diff_content(prev_fragment, curr_fragment)

        if action in ['EditorCopy', '$Copy']:
            return '[Copied]'

        if action in ['EditorPaste', '$Paste']:
            added = self._find_added_text(prev_fragment, curr_fragment)
            return added if added else ''

        if action in ['EditorCut', 'EditorBackSpace', 'EditorDelete']:
            removed = self._find_removed_text(prev_fragment, curr_fragment)
            return removed if removed else ''

        return ''

    def _find_added_text(self, prev_text, curr_text):
        """Find text that was added between two versions."""
        matcher = difflib.SequenceMatcher(None, prev_text, curr_text)
        added_text = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                added_text.append(curr_text[j1:j2])
        return ''.join(added_text)

    def _find_removed_text(self, prev_text, curr_text):
        """Find text that was removed between two versions."""
        matcher = difflib.SequenceMatcher(None, prev_text, curr_text)
        removed_text = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                removed_text.append(prev_text[i1:i2])
        return ''.join(removed_text)

    def _get_diff_content(self, prev_text, curr_text):
        """Get a summary of changes between two texts."""
        matcher = difflib.SequenceMatcher(None, prev_text, curr_text)
        changes = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                changes.append(f"[-{prev_text[i1:i2]}]")
            elif tag == 'insert':
                changes.append(f"[+{curr_text[j1:j2]}]")
            elif tag == 'replace':
                changes.append(f"[-{prev_text[i1:i2]}] [+{curr_text[j1:j2]}]")
        return ' '.join(changes)

    def _format_content(self, content):
        """Format content for display in CSV."""
        if not content:
            return ''

        content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')

        if self.max_content_length > 0 and len(content) > self.max_content_length:
            content = content[:self.max_content_length] + '...'

        return content

    def _format_time(self, ms):
        """
        Format time in milliseconds to seconds and minutes (only when >= 60s).

        Args:
            ms (int): Time in milliseconds

        Returns:
            tuple: (seconds_str, minutes_str) where minutes_str is empty if < 60s
        """
        seconds = ms / 1000
        minutes = ms / 60000

        seconds_str = f"{seconds:.2f}"
        minutes_str = f"{minutes:.2f}" if seconds >= 60 else ''

        return seconds_str, minutes_str

    def _write_output_csv(self, output_path, actions):
        """
        Write actions to output CSV file.

        Args:
            output_path (str): Path to output CSV file
            actions (list): List of action dictionaries
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'action',
                'start_sec',
                'start_min',
                'end_sec',
                'end_min',
                'duration_sec',
                'duration_min',
                'details'
            ]

            if self.log_content:
                fieldnames.append('content')

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for action in actions:
                start = action.get('start', 0)
                duration = action.get('duration', 0)
                end = start + duration
                inactivity = action.get('inactivity', 0)

                # Format times
                start_sec, start_min = self._format_time(start)
                end_sec, end_min = self._format_time(end)
                duration_sec, duration_min = self._format_time(duration)


                row_data = {
                    'action': action['action'],
                    'start_sec': start_sec,
                    'start_min': start_min,
                    'end_sec': end_sec,
                    'end_min': end_min,
                    'duration_sec': duration_sec,
                    'duration_min': duration_min,
                    'details': action['details']
                }

                if self.log_content:
                    row_data['content'] = action.get('content', '')

                writer.writerow(row_data)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Analyze activity tracking CSV files with IDE events integration.'
    )
    parser.add_argument(
        'input',
        help='Input CSV file or directory containing CSV files'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (for single file) or directory (for batch)'
    )
    parser.add_argument(
        '-t', '--threshold',
        type=int,
        default=60000,
        help='Inactivity threshold in milliseconds (default: 60000)'
    )
    parser.add_argument(
        '-d', '--directory',
        action='store_true',
        help='Process all CSV files in the input directory'
    )
    # Include the 'content' column only when --content is passed.
    parser.add_argument(
        '--content',
        action='store_true',
        help="Include the 'content' column in the output (default: excluded)"
    )

    parser.add_argument(
        '--max-content',
        type=int,
        default=0,
        help='Maximum length of content to log (default: 0 = unlimited)'
    )

    args = parser.parse_args()

    analyzer = ActivityAnalyzer(
        inactivity_threshold_ms=args.threshold,
        log_content=args.content,
        max_content_length=args.max_content
    )

    print(f"\n{'='*60}")
    print("Activity Tracker CSV Analyzer with IDE Events")
    print(f"{'='*60}")
    print(f"Inactivity threshold: {args.threshold}ms ({args.threshold/1000}s)")
    print(f"Content column included: {'YES' if args.content else 'NO'}")
    if args.content:
        max_len = args.max_content if args.max_content > 0 else 'Unlimited'
        print(f"Max content length: {max_len}")
    print(f"{'='*60}\n")

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: {args.input} does not exist")
        sys.exit(1)

    if input_path.is_dir() or args.directory:
        analyzer.analyze_directory(args.input, args.output)
    else:
        analyzer.analyze_file(args.input, args.output)


if __name__ == '__main__':
    main()
