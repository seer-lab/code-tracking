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
    # ACTION_DESCRIPTIONS = {
    #     'Active': 'IDE gained focus',
    #     'Inactive': 'IDE lost focus',
    #     'NoProject': 'All projects closed',
    #     'NewProject': 'Create new project',
    #     'SaveAs': 'Save file as',
    #     'SaveAll': 'Save all files',
    #     'NewPythonFile': 'Create Python file',
    #     'ChooseRunConfiguration': 'Choose run configuration',
    #     'Run': 'Run program',
    #     'Rerun': 'Run program again',
    #     'RunClass': 'Run class',
    #     'DebugClass': 'Debug class',
    #     'ToggleLineBreakpoint': 'Toggle line breakpoint',
    #     'Debug': 'Debug program',
    #     'Stop': 'Stop debug/run',
    #     'Resume': 'Resume debug program',
    #     'StepInto': 'Step into (debugging)',
    #     'CompileDirty': 'Compile',
    #     'EditorBackSpace': 'Press Backspace',
    #     'EditorLeft': 'Press Left arrow',
    #     'EditorRight': 'Press Right arrow',
    #     'EditorEnter': 'Press Enter',
    #     'EditorTab': 'Press Tab',
    #     'EditorDown': 'Press Down arrow',
    #     'EditorUp': 'Press Up arrow',
    #     'EditorDelete': 'Press Delete',
    #     'EditorChooseLookupItem': 'Choose autocomplete item',
    #     'EditorSplitLine': 'Split line',
    #     'EditorRightWithSelection': 'Select right',
    #     'EditorLeftWithSelection': 'Select left',
    #     'EditorDuplicate': 'Duplicate line',
    #     'EditorCopy': 'Copy text',
    #     'EditorPaste': 'Paste text',
    #     'EditorCut': 'Cut text',
    #     'CopyPaths': 'Copy file path',
    #     'ReformatCode': 'Reformat code',
    #     'NewElement': 'Create new element',
    #     'ShowPopupMenu': 'Show popup menu',
    #     'SearchEverywhere': 'Search everywhere',
    #     'InsertInlineCompletionAction': 'Accept inline completion',
    #     '$Undo': 'Undo (Ctrl+Z)',
    #     '$Paste': 'Paste (Ctrl+V)',
    #     '$Copy': 'Copy (Ctrl+C)',
    #     '$Redo': 'Redo (Ctrl+Y)',
    #     'CompilationFinished': 'Compilation finished',
    # }

    ACTION_DESCRIPTIONS = {
        'Active': 'Gained Focus',
        'Inactive': 'Lost Focus',
        'NoProject': 'No Project',
        'NewProject': 'New Project',
        'SaveAs': 'Save File',
        'SaveAll': 'Save All',
        'NewPythonFile': 'New Python File',
        'ChooseRunConfiguration': 'Choose Run Configuration',
        'Run': 'Run',
        'Rerun': 'Rerun',
        'RunClass': 'Run Class',
        'DebugClass': 'Debug Class',
        'ToggleLineBreakpoint': 'Toggle Line Breakpoint',
        'Debug': 'Debug',
        'Stop': 'Stop debug/run',
        'Resume': 'Resume debug',
        'StepInto': 'Step into (debugging)',
        'CompileDirty': 'Compile',
        'EditorBackSpace': 'Backspace',
        'EditorLeft': 'Left Arrow',
        'EditorRight': 'Right Arrow',
        'EditorEnter': 'Enter',
        'EditorTab': 'Tab',
        'EditorDown': 'Down Arrow',
        'EditorUp': 'Up Arrow',
        'EditorDelete': 'Delete',
        'EditorChooseLookupItem': 'Choose Autocomplete Item',
        'EditorSplitLine': 'Split Line',
        'EditorRightWithSelection': 'Select Right',
        'EditorLeftWithSelection': 'Select Left',
        'EditorDuplicate': 'Duplicate Line',
        'EditorCopy': 'Copy',
        'EditorPaste': 'Paste',
        'EditorCut': 'Cut',
        'CopyPaths': 'Copy File Path',
        'ReformatCode': 'Reformat Code',
        'NewElement': 'Create New Element',
        'ShowPopupMenu': 'Show Popup Menu',
        'SearchEverywhere': 'Search Everywhere',
        'InsertInlineCompletionAction': 'Accept Inline Completion',
        '$Undo': 'Undo',
        '$Paste': 'Paste',
        '$Copy': 'Copy',
        '$Redo': 'Redo',
        'CompilationFinished': 'Compilation Finished',
    }

    # Hardcoded inactivity threshold (ms) for gaps between *different* Tableau groups
    # (e.g. a pause between a Copy/Paste action and a Writing action).
    CROSS_GROUP_INACTIVITY_THRESHOLD_MS = 500  # 0.5 seconds

    def __init__(self, inactivity_threshold_ms=60000, log_content=True, max_content_length=0):
        """
        Initialize the analyzer.

        Args:
            inactivity_threshold_ms (int): Threshold for detecting inactivity within the
                same Tableau group in milliseconds (configurable via CLI --threshold).
            log_content (bool): Whether to log actual content changes
            max_content_length (int): Maximum length of content to log (0 = unlimited)
        """
        self.inactivity_threshold_ms = inactivity_threshold_ms
        self.log_content = log_content
        self.max_content_length = max_content_length

    # Maps output action names to their Tableau group (mirrors the calculated field)
    TABLEAU_GROUPS = {
        # Writing
        'Edit':                    'Writing',
        'EditorStartNewLine':      'Writing',
        'EditorIndentSelection':   'Writing',
        'EditorUnindentSelection': 'Writing',
        'EditorDeleteToWordStart': 'Writing',
        'Replace text':            'Writing',
        'Backspace':               'Writing',
        'Delete':                  'Writing',
        'Enter':                   'Writing',
        'Undo':                    'Writing',
        # Copy / Paste
        'Paste':                   'Copy / Paste',
        'Paste (external)':        'Copy / Paste',
        'Copy/Paste (internal)':   'Copy / Paste',
        'Cut':                     'Copy / Paste',
        # Navigation
        'Left Arrow':              'Navigation',
        'Right Arrow':             'Navigation',
        'Up Arrow':                'Navigation',
        'Down Arrow':              'Navigation',
        'Tab':                     'Navigation',
        # Autocomplete
        'Accept Inline Completion':      'Autocomplete',
        'Choose Autocomplete':           'Autocomplete',
        'Choose Autocomplete Item':      'Autocomplete',
        'EditorChooseLookupItem':        'Autocomplete',
        'EditorChooseLookupItemReplace': 'Autocomplete',
        'EditorIndentSelection':         'Autocomplete',
        # Inactivity maps to itself so same-group logic works transparently
        'Inactivity':              'Inactivity',
    }

    def _get_tableau_group(self, action_name):
        """Return the Tableau group for a given action name, or 'Other' if not mapped."""
        return self.TABLEAU_GROUPS.get(action_name, 'Other')

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

    def analyze_file_to_actions(self, input_path):
        """
        Analyze a single CSV file and return the list of action dictionaries.

        Args:
            input_path (str): Path to input CSV file

        Returns:
            list: List of action dictionaries, or None if no data found
        """
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
            return None

        actions = self._analyze_actions(rows, ide_events_data)
        print(f"  Total actions logged: {len(actions)}")
        print()
        return actions

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

        # ── Find the true session start ──
        # Scan forward from row 0 until the 'fragment' column changes.
        # The first row where fragment differs from row 0 becomes the effective
        # session start (time = 0 in all output timestamps).  All rows before it
        # are skipped but the last skipped row seeds previous_row/previous_fragment
        # so that action detection works correctly on the very first processed row.
        initial_fragment = rows[0].get('fragment', '')
        first_active_index = 0
        for _fi, _fr in enumerate(rows):
            if _fr.get('fragment', '') != initial_fragment:
                first_active_index = _fi
                break
        # If every row has the same fragment, fall back to index 1 (original behaviour
        # of skipping only row 0).
        if first_active_index == 0:
            first_active_index = min(1, len(rows) - 1)

        session_start = self._parse_timestamp(rows[first_active_index].get('date'))

        # Seed previous_row and previous_fragment from the last skipped row so that
        # the first processed row can be compared against the state just before it.
        previous_row = rows[first_active_index - 1] if first_active_index > 0 else None
        previous_fragment = rows[first_active_index - 1].get('fragment', '') if first_active_index > 0 else ''

        # Tracking variables
        pending_group = None  # Current action group being accumulated
        # Track the absolute (ms since epoch) end time of the last finalized action
        last_action_end_ms = session_start

        # Edit and delete action types for grouping
        edit_types = {'Type character', 'Type text', 'Insert text'}
        delete_types = {'Delete character', 'Delete text', 'Delete block'}
        # Actions that should NOT be grouped and should appear individually
        non_groupable_actions = {'Copy', 'Paste', 'Cut', 'Copy/Paste (internal)', 'Paste (external)',
                                 'EditorCopy', '$Copy', 'EditorPaste', '$Paste', 'EditorCut'}

        # Track the Tableau group of the most-recently finalised action so we can
        # enforce the "inactivity only within the same group" rule.
        last_action_group = None  # None = no action yet

        for i, row in enumerate(rows[first_active_index:], first_active_index):
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

            # ── Determine this row's action category BEFORE the inactivity check ──
            # so we know whether the current row continues the pending group or not.
            curr_ide_action = self._find_matching_ide_event(curr_ts, ide_events_data)
            curr_action_info = None
            if curr_ide_action:
                curr_action_desc = self.ACTION_DESCRIPTIONS.get(curr_ide_action, curr_ide_action)
                curr_is_non_groupable = curr_action_desc in non_groupable_actions
                curr_group_category = curr_action_desc
            elif previous_row is not None:
                curr_action_info = self._detect_action(previous_row, row, previous_fragment)
                if curr_action_info:
                    curr_action_type = curr_action_info['type']
                    if curr_action_type in edit_types:
                        curr_group_category = 'Edit'
                    elif curr_action_type in delete_types:
                        curr_group_category = 'Delete'
                    else:
                        curr_group_category = curr_action_type
                    curr_is_non_groupable = curr_action_type in non_groupable_actions or curr_group_category in non_groupable_actions
                else:
                    curr_group_category = None
                    curr_is_non_groupable = False
            else:
                curr_group_category = None
                curr_is_non_groupable = False

            # ── Inactivity check ──
            # Measure the raw gap between consecutive rows (prev_ts → curr_ts).
            # This correctly catches gaps that occur mid-group (e.g. two Delete rows
            # with a 30-minute gap between them) which the old end-of-group measure missed.
            #
            # Rules:
            #  1. Gap must meet or exceed the inactivity threshold.
            #  2. Both the action before the gap and the action after must belong to
            #     the same Tableau group. A gap between different groups (e.g. Edit →
            #     Left Arrow) is just a natural transition and is NOT inactivity.
            #  3. At session start (last_action_group is None) we always allow inactivity
            #     so the initial idle period is captured.

            # Tableau group of the incoming action.
            # If the current row has no detectable action (curr_group_category is None),
            # treat it as belonging to the same group as whatever was active before —
            # it's a heartbeat/no-change row and should inherit the previous context.
            if curr_group_category is not None:
                curr_tableau_group = self._get_tableau_group(curr_group_category)
            elif pending_group is not None:
                curr_tableau_group = self._get_tableau_group(pending_group['action'])
            elif last_action_group is not None:
                curr_tableau_group = last_action_group
            else:
                curr_tableau_group = 'Other'

            # The "previous" group: if a pending group is open use its action, else
            # use the last_action_group recorded when the previous action was finalised.
            prev_tableau_group = (
                self._get_tableau_group(pending_group['action']) if pending_group
                else last_action_group
            )

            # Gate: same Tableau group on both sides of the gap.
            # When prev_tableau_group is None, no real action has been seen yet —
            # that initial gap precedes any real action and should not create an Inactivity row.
            same_tableau_group = (prev_tableau_group is not None and prev_tableau_group == curr_tableau_group)

            # Cross-group: both sides must have a known group, and they must differ.
            # A hardcoded 0.5-second threshold is used for these transitions (e.g. a pause
            # between Copy/Paste and Writing), rather than the user-configurable threshold
            # which only applies within the same Tableau group.
            cross_tableau_group = (
                prev_tableau_group is not None
                and curr_tableau_group is not None
                and prev_tableau_group != curr_tableau_group
            )

            is_inactivity = (
                (same_tableau_group and time_since_last >= self.inactivity_threshold_ms)
                or (cross_tableau_group and time_since_last >= self.CROSS_GROUP_INACTIVITY_THRESHOLD_MS)
            )

            if is_inactivity:
                # Finalise any open pending group up to the previous row before inserting inactivity
                if pending_group:
                    # Cap the group's end at prev_ts (not curr_ts) — the gap belongs to inactivity
                    pending_group['end'] = max(0, prev_ts - session_start)
                    self._finalize_group(actions, pending_group)
                    last_action_group = self._get_tableau_group(pending_group['action'])
                    pending_group = None
                    last_action_end_ms = prev_ts
                elif actions:
                    last_action_end_ms = session_start + actions[-1].get('start', 0) + actions[-1].get('duration', 0)

                # Inactivity spans from end of last action to start of current row
                inactivity_start_abs = last_action_end_ms
                inactivity_duration_abs = max(0, curr_ts - inactivity_start_abs)

                if inactivity_duration_abs > 0:
                    inactivity_code = previous_fragment if previous_fragment else ''
                    actions.append({
                        'action': 'Inactivity',
                        'start': max(0, inactivity_start_abs - session_start),
                        'duration': inactivity_duration_abs,
                        'inactivity': inactivity_duration_abs / 60000,
                        'details': f"Inactive for {inactivity_duration_abs/1000:.1f} seconds",
                        'content': '',
                        'code': inactivity_code,
                        'change_len': 0,
                        'lines_added': 0,
                        'lines_removed': 0
                    })

                last_action_end_ms = max(last_action_end_ms, curr_ts)

            # ── Check whether the current row continues the same action type ──
            is_same_type = (pending_group is not None
                            and curr_group_category is not None
                            and not curr_is_non_groupable
                            and pending_group['action'] == curr_group_category)

            # Check for matching IDE event (already determined above)
            ide_action = curr_ide_action

            if ide_action:
                # Found explicit IDE action
                action_desc = curr_action_desc
                content = self._extract_ide_action_content(
                    ide_action,
                    previous_fragment,
                    row.get('fragment', '')
                )

                # compute numeric change length for this action
                change_len = self._compute_change_length(previous_fragment, row.get('fragment', '')) if self.log_content else 0
                lines_added, lines_removed = self._compute_line_change(previous_fragment, row.get('fragment', ''))

                # If this action is non-groupable, finalize any pending group and append it immediately
                if action_desc in non_groupable_actions:
                    if pending_group:
                        # Trim group end to current row's start (don't extend into different-type gap)
                        # group end unchanged — duration_to_next fills timeline
                        abs_end = session_start + pending_group.get('end', 0)
                        self._finalize_group(actions, pending_group)
                        last_action_group = self._get_tableau_group(pending_group['action'])
                        pending_group = None
                        last_action_end_ms = abs_end

                    actions.append({
                        'action': action_desc,
                        'start': start_relative,
                        'duration': duration_to_next,
                        'inactivity': 0,
                        'details': action_desc,
                        'content': content if self.log_content else '',
                        'code': row.get('fragment', '') if row.get('fragment') is not None else '',
                        'change_len': change_len,
                        'lines_added': lines_added,
                        'lines_removed': lines_removed
                    })
                    # update last action end and group
                    last_action_end_ms = session_start + start_relative + duration_to_next
                    last_action_group = self._get_tableau_group(action_desc)
                    previous_row = row
                    previous_fragment = row.get('fragment', '')
                    continue

                # Check if we should group this with pending group
                if pending_group is None or pending_group['action'] != action_desc:
                    # Finalize previous group if exists — trim end to this row's start
                    if pending_group:
                        # group end unchanged — duration_to_next fills timeline
                        abs_end = session_start + pending_group.get('end', 0)
                        self._finalize_group(actions, pending_group)
                        last_action_group = self._get_tableau_group(pending_group['action'])
                        last_action_end_ms = abs_end

                    # Start new group. Use end = start + duration_to_next so group end covers the span.
                    pending_group = {
                        'action': action_desc,
                        'start': start_relative,
                        'end': start_relative + duration_to_next,
                        'content': content,
                        'snapshot': row.get('fragment', ''),
                        'count': 1,
                        'change_len': change_len,
                        'lines_added': lines_added,
                        'lines_removed': lines_removed
                    }
                else:
                    # Extend existing group (same action type)
                    pending_group['end'] = start_relative + duration_to_next
                    if content:
                        pending_group['content'] += content
                    # always update snapshot to the latest fragment so group 'code' uses the end-state
                    pending_group['snapshot'] = row.get('fragment', '')
                    pending_group['count'] += 1
                    pending_group['change_len'] = pending_group.get('change_len', 0) + change_len
                    pending_group['lines_added'] = pending_group.get('lines_added', 0) + lines_added
                    pending_group['lines_removed'] = pending_group.get('lines_removed', 0) + lines_removed

                previous_row = row
                previous_fragment = row.get('fragment', '')
                continue

            # No IDE event - use the already-detected action from fragment changes
            if previous_row is not None and curr_action_info:
                    action_type = curr_action_info['type']
                    group_category = curr_group_category

                    # numeric change length (from action_info if present)
                    change_len = curr_action_info.get('change_len', 0)
                    lines_added, lines_removed = self._compute_line_change(previous_fragment, row.get('fragment', ''))

                    # If this detected action is non-groupable (e.g., paste/copy/cut), append immediately
                    if curr_is_non_groupable:
                        if pending_group:
                            # Trim group end to current row's start
                            # group end unchanged — duration_to_next fills timeline
                            abs_end = session_start + pending_group.get('end', 0)
                            self._finalize_group(actions, pending_group)
                            last_action_group = self._get_tableau_group(pending_group['action'])
                            pending_group = None
                            last_action_end_ms = abs_end

                        actions.append({
                            'action': action_type,
                            'start': start_relative,
                            'duration': duration_to_next,
                            'inactivity': 0,
                            'details': curr_action_info.get('details', action_type),
                            'content': curr_action_info.get('content', '') if self.log_content else '',
                            'code': row.get('fragment', '') if row.get('fragment') is not None else '',
                            'change_len': change_len,
                            'lines_added': lines_added,
                            'lines_removed': lines_removed
                        })
                        last_action_end_ms = session_start + start_relative + duration_to_next
                        last_action_group = self._get_tableau_group(action_type)
                        # Continue to next row without creating/extending a pending group
                        previous_row = row
                        previous_fragment = row.get('fragment', '')
                        continue

                    # Check if we should group this
                    if pending_group is None or pending_group['action'] != group_category:
                        # Finalize previous group if exists — trim end to this row's start
                        if pending_group:
                            # group end unchanged — duration_to_next fills timeline
                            abs_end = session_start + pending_group.get('end', 0)
                            self._finalize_group(actions, pending_group)
                            last_action_group = self._get_tableau_group(pending_group['action'])
                            last_action_end_ms = abs_end

                        # Start new group
                        pending_group = {
                            'action': group_category,
                            'start': start_relative,
                            'end': start_relative + duration_to_next,
                            'content': curr_action_info.get('content', ''),
                            'snapshot': row.get('fragment', ''),
                            'count': 1,
                            'change_len': change_len,
                            'lines_added': lines_added,
                            'lines_removed': lines_removed
                        }
                    else:
                        # Extend existing group
                        pending_group['end'] = start_relative + duration_to_next
                        pending_group['content'] += curr_action_info.get('content', '')
                        pending_group['snapshot'] = row.get('fragment', '')
                        pending_group['count'] += 1
                        pending_group['change_len'] = pending_group.get('change_len', 0) + change_len
                        pending_group['lines_added'] = pending_group.get('lines_added', 0) + lines_added
                        pending_group['lines_removed'] = pending_group.get('lines_removed', 0) + lines_removed

            previous_row = row
            previous_fragment = row.get('fragment', '')

        # Finalize any remaining pending group
        if pending_group:
            abs_end = session_start + pending_group.get('end', 0)
            self._finalize_group(actions, pending_group)
            last_action_group = self._get_tableau_group(pending_group['action'])
            last_action_end_ms = abs_end

        # Post-process: ensure Inactivity entries do not overlap actions. Trim action durations
        # that extend into an Inactivity period to ensure inactivity is exclusive.
        cleaned = []
        # Track the last known code snapshot so it's never lost when actions are dropped
        last_known_code = ''
        for idx, act in enumerate(actions):
            a_start = float(act.get('start', 0))
            a_dur = float(act.get('duration', 0))
            a_end = a_start + a_dur

            # Update last known code from this action (if it has one)
            act_code = act.get('code', '')
            if act_code:
                last_known_code = act_code

            if act.get('action') == 'Inactivity':
                # Ensure inactivity starts after last cleaned action end
                prev_end = cleaned[-1]['start'] + cleaned[-1]['duration'] if cleaned else 0
                if a_start < prev_end:
                    # shift inactivity forward and reduce duration
                    a_dur = max(0.0, a_end - prev_end)
                    a_start = prev_end
                    a_end = a_start + a_dur
                if a_dur <= 0:
                    continue
                act['start'] = a_start
                act['duration'] = a_dur
                # Ensure inactivity always carries the last known code
                if not act.get('code'):
                    act['code'] = last_known_code
                cleaned.append(act)
                continue

            # If next action is inactivity, trim this action to not overlap
            if idx + 1 < len(actions) and actions[idx + 1].get('action') == 'Inactivity':
                next_start = float(actions[idx + 1].get('start', 0))
                if a_end > next_start:
                    a_dur = max(0.0, next_start - a_start)
                    a_end = a_start + a_dur

            # Avoid overlapping previous cleaned action
            prev_end = cleaned[-1]['start'] + cleaned[-1]['duration'] if cleaned else 0
            if a_start < prev_end:
                a_start = prev_end
                a_dur = max(0.0, a_end - prev_end)
                a_end = a_start + a_dur

            if a_dur <= 0:
                # Don't drop actions that carry a code snapshot — the code state
                # would be lost. Keep them with zero duration.
                if not act.get('code'):
                    continue
                a_dur = 0
                a_end = a_start
            act['start'] = a_start
            act['duration'] = a_dur
            # If this action somehow has no code, fill from last known
            if not act.get('code'):
                act['code'] = last_known_code
            cleaned.append(act)

        actions = cleaned

        # Add session total
        last_ts = self._parse_timestamp(rows[-1].get('date'))
        total_duration = max(0, last_ts - session_start)

        actions.append({
            'action': 'Session total',
            'start': 0,
            'duration': total_duration,
            'inactivity': 0,
            'details': f"Total session duration: {total_duration/1000:.1f} seconds",
            'content': '',
            'code': '',
            'change_len': 0,
            'lines_added': 0,
            'lines_removed': 0
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
            # preserve original content behavior
            'content': self._format_content(group.get('content', '')) if self.log_content else '',
            # new 'code' column: snapshot at group end
            'code': group.get('snapshot', ''),
            'change_len': group.get('change_len', 0),
            'lines_added': group.get('lines_added', 0),
            'lines_removed': group.get('lines_removed', 0)
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
                    'content': '',
                    'change_len': 0
                }
            return None

        length_diff = len(curr_fragment) - len(prev_fragment)

        # compute numeric change length using opcode analysis
        change_len = self._compute_change_length(prev_fragment, curr_fragment)

        # Large insertion - detect paste
        if length_diff > 10:
            added_text = self._find_added_text(prev_fragment, curr_fragment)
            if added_text:
                if added_text.strip() in prev_fragment:
                    return {
                        'type': 'Copy/Paste (internal)',
                        'details': f"Pasted {len(added_text)} character(s) from same file",
                        'content': added_text if self.log_content else '',
                        'change_len': len(added_text)
                    }
                else:
                    return {
                        'type': 'Paste (external)',
                        'details': f"Pasted {len(added_text)} character(s) from clipboard",
                        'content': added_text if self.log_content else '',
                        'change_len': len(added_text)
                    }

        # Text added
        if length_diff > 0:
            added_text = self._find_added_text(prev_fragment, curr_fragment)
            if length_diff == 1:
                return {
                    'type': 'Type character',
                    'details': f"Added character",
                    'content': added_text if self.log_content else '',
                    'change_len': change_len
                }
            elif length_diff <= 10:
                return {
                    'type': 'Type text',
                    'details': f"Added {length_diff} character(s)",
                    'content': added_text if self.log_content else '',
                    'change_len': change_len
                }
            else:
                return {
                    'type': 'Insert text',
                    'details': f"Inserted {length_diff} character(s)",
                    'content': added_text if self.log_content else '',
                    'change_len': change_len
                }

        # Text deleted
        elif length_diff < 0:
            deleted_count = abs(length_diff)
            deleted_text = self._find_removed_text(prev_fragment, curr_fragment)

            if deleted_count == 1:
                return {
                    'type': 'Delete character',
                    'details': f"Deleted 1 character",
                    'content': deleted_text if self.log_content else '',
                    'change_len': change_len
                }
            elif deleted_count <= 10:
                return {
                    'type': 'Delete text',
                    'details': f"Deleted {deleted_count} character(s)",
                    'content': deleted_text if self.log_content else '',
                    'change_len': change_len
                }
            else:
                return {
                    'type': 'Delete block',
                    'details': f"Deleted {deleted_count} character(s)",
                    'content': deleted_text if self.log_content else '',
                    'change_len': change_len
                }

        # Text replaced
        else:
            diff_content = self._get_diff_content(prev_fragment, curr_fragment)
            return {
                'type': 'Replace text',
                'details': f"Modified text (same length)",
                'content': diff_content if self.log_content else '',
                'change_len': change_len
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

    def _compute_change_length(self, prev_text, curr_text):
        """Compute a numeric change length between two text versions.

        This counts the number of inserted and removed characters (and replaces as max of removed/inserted).
        """
        matcher = difflib.SequenceMatcher(None, prev_text or '', curr_text or '')
        change = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                change += (i2 - i1)
            elif tag == 'insert':
                change += (j2 - j1)
            elif tag == 'replace':
                # count the larger side of a replace as the change size
                change += max(i2 - i1, j2 - j1)
        return change

    def _compute_line_change(self, prev_text, curr_text):
        """Compute the number of lines added and removed between two text versions.

        Returns:
            tuple: (lines_added, lines_removed)
        """
        prev_lines = (prev_text or '').splitlines()
        curr_lines = (curr_text or '').splitlines()
        matcher = difflib.SequenceMatcher(None, prev_lines, curr_lines)
        added = 0
        removed = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                removed += (i2 - i1)
            elif tag == 'insert':
                added += (j2 - j1)
            elif tag == 'replace':
                removed += (i2 - i1)
                added += (j2 - j1)
        return added, removed

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
        Format time in milliseconds to seconds and minutes.

        Args:
            ms (int): Time in milliseconds

        Returns:
            tuple: (seconds_str, minutes_str)
        """
        seconds = ms / 1000
        minutes = ms / 60000

        seconds_str = f"{seconds:.2f}"
        minutes_str = f"{minutes:.2f}"

        return seconds_str, minutes_str

    def _write_output_csv(self, output_path, actions):
        """
        Write actions to output CSV file.

        Args:
            output_path (str): Path to output CSV file
            actions (list): List of action dictionaries
        """
        # Build time_percent: linear 0-100% across all real actions (excluding Session total).
        # The first real action = 0%, the last real action = 100%.
        real_actions = [a for a in actions if a.get('action') != 'Session total']
        num_real = len(real_actions)
        # Map each action dict id to its percent value
        time_percent_map = {}
        for idx, a in enumerate(real_actions):
            if num_real <= 1:
                pct = 0.0
            else:
                pct = idx / (num_real - 1) * 100.0
            time_percent_map[id(a)] = pct

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'action',
                'time_percent',
                'start_sec',
                'start_min',
                'end_sec',
                'end_min',
                'duration_sec',
                'duration_min',
                'details',
                'change_len',
                'lines_added',
                'lines_removed',
                # always include 'code' (fragment snapshot / group snapshot at end)
                'code',
                # length of code fragment (characters)
                'code_len'
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

                # time_percent: 0% for first action, 100% for last, linear in between
                time_percent = time_percent_map.get(id(action), 0.0)

                # Format times
                start_sec, start_min = self._format_time(start)
                end_sec, end_min = self._format_time(end)
                duration_sec, duration_min = self._format_time(duration)


                code_val = action.get('code', '') or ''
                try:
                    code_len_val = len(code_val)
                except Exception:
                    code_len_val = 0

                row_data = {
                    'action': action['action'],
                    'time_percent': f"{time_percent:.2f}",
                    'start_sec': start_sec,
                    'start_min': start_min,
                    'end_sec': end_sec,
                    'end_min': end_min,
                    'duration_sec': duration_sec,
                    'duration_min': duration_min,
                    'details': action['details'],
                    'change_len': action.get('change_len', 0),
                    'lines_added': action.get('lines_added', 0),
                    'lines_removed': action.get('lines_removed', 0),
                    # always include the 'code' column
                    'code': code_val,
                    'code_len': code_len_val
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