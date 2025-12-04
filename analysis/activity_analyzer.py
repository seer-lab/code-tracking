#!/usr/bin/env python3
"""
Activity Tracker CSV Analyzer
Analyzes CSV files containing activity tracking data and outputs human-readable action logs.
"""

import csv
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import difflib
from datetime import datetime


class ActivityAnalyzer:
    """Analyzes activity tracking CSV files and generates human-readable output."""
    
    # Configurable parameters
    INACTIVITY_THRESHOLD_MS = 5000  # Time in milliseconds to consider as a break
    
    # Action type mappings from activity_tracker_keys_info
    ACTION_DESCRIPTIONS = {
        # IDE State
        'Active': 'IDE gained focus',
        'Inactive': 'IDE lost focus',
        'NoProject': 'All projects closed',
        
        # Project/File actions
        'NewProject': 'Create new project',
        'SaveAs': 'Save file as',
        'NewPythonFile': 'Create Python file',
        
        # Run/Debug actions
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
        
        # Navigation actions
        'EditorBackSpace': 'Press BackSpace',
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
        
        # Edit actions
        'EditorCopy': 'Copy text (menu)',
        'EditorPaste': 'Paste text (menu)',
        'EditorCut': 'Cut text (menu)',
        'CopyPaths': 'Copy file path',
        'ReformatCode': 'Reformat code',
        'NewElement': 'Create new element',
        'ShowPopupMenu': 'Show popup menu',
        
        # Keyboard shortcuts
        '$Undo': 'Undo (Ctrl+Z)',
        '$Paste': 'Paste (Ctrl+V)',
        '$Copy': 'Copy (Ctrl+C)',
        
        # Compilation
        'CompilationFinished': 'Compilation finished',
    }
    
    def __init__(self, inactivity_threshold_ms: int = None):
        """
        Initialize the analyzer.
        
        Args:
            inactivity_threshold_ms: Time in milliseconds to consider as a break
        """
        if inactivity_threshold_ms is not None:
            self.INACTIVITY_THRESHOLD_MS = inactivity_threshold_ms
    
    def analyze_file(self, input_path: str, output_path: str = None) -> None:
        """
        Analyze a single CSV file and generate output.
        
        Args:
            input_path: Path to input CSV file
            output_path: Path to output CSV file (auto-generated if None)
        """
        if output_path is None:
            output_path = self._generate_output_path(input_path)
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing: {input_path}")
        
        # Read input CSV
        rows = self._read_csv(input_path)
        
        if not rows:
            print(f"Warning: No data found in {input_path}")
            return
        
        # Analyze actions
        actions = self._analyze_actions(rows)
        
        # Write output CSV
        self._write_output_csv(output_path, actions)
        
        print(f"✓ Output saved to: {output_path}")
        print(f"  Total actions logged: {len(actions)}")
        print()
    
    def analyze_directory(self, directory_path: str, output_dir: str = None) -> None:
        """
        Analyze all CSV files in a directory.
        
        Args:
            directory_path: Path to directory containing CSV files
            output_dir: Directory for output files (if None, saves alongside originals)
        """
        directory = Path(directory_path)
        
        if not directory.exists() or not directory.is_dir():
            print(f"Error: {directory_path} is not a valid directory")
            return
        
        # Find all CSV files
        csv_files = list(directory.glob("*.csv"))
        
        if not csv_files:
            print(f"No CSV files found in {directory_path}")
            return
        
        print(f"Found {len(csv_files)} CSV file(s) to process")
        
        # Create output directory if specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"Output directory: {output_path.absolute()}")
        else:
            print(f"Output location: Same directory as input files")
        
        print()
        
        # Process each file
        for i, csv_file in enumerate(csv_files, 1):
            print(f"[{i}/{len(csv_files)}] ", end="")
            
            if output_dir:
                output_file = Path(output_dir) / f"{csv_file.stem}_analyzed.csv"
            else:
                output_file = None
            
            self.analyze_file(str(csv_file), str(output_file) if output_file else None)
        
        print(f"\n{'='*60}")
        print(f"Batch processing complete!")
        print(f"Processed {len(csv_files)} file(s)")
        if output_dir:
            print(f"All outputs saved to: {Path(output_dir).absolute()}")
        print(f"{'='*60}")
    
    def _read_csv(self, file_path: str) -> List[Dict]:
        """Read CSV file and return list of row dictionaries."""
        rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows
    
    def _analyze_actions(self, rows: List[Dict]) -> List[Dict]:
        """
        Analyze rows and extract human-readable actions.
        
        Returns:
            List of action dictionaries with keys: action, start, duration, details
        """
        actions = []
        
        if not rows:
            return actions
        
        # Check if CSV has an explicit 'action' column
        has_action_column = 'action' in rows[0]
        
        # Start time is 0
        start_time = 0
        previous_row = None
        previous_fragment = None
        
        for i, row in enumerate(rows):
            timestamp = int(row['timestamp'])
            
            # First row
            if i == 0:
                actions.append({
                    'action': 'Session started',
                    'start': 0,
                    'duration': 0,
                    'details': f"File: {row['fileName']}, Task: {row['chosenTask']}"
                })
                previous_row = row
                previous_fragment = row.get('fragment', '')
                continue
            
            # Calculate time since last action
            time_since_last = timestamp - int(previous_row['timestamp'])
            
            # Ensure non-negative duration (handle any timestamp anomalies)
            if time_since_last < 0:
                time_since_last = 0
            
            # Check for inactivity break
            if time_since_last >= self.INACTIVITY_THRESHOLD_MS:
                actions.append({
                    'action': 'Inactive/Break',
                    'start': int(previous_row['timestamp']),
                    'duration': time_since_last,
                    'details': f"No activity for {time_since_last/1000:.2f} seconds"
                })
            
            # Check for explicit action in CSV
            if has_action_column and row.get('action') and row['action'].strip():
                explicit_action = row['action'].strip()
                action_desc = self.ACTION_DESCRIPTIONS.get(explicit_action, explicit_action)
                
                # Special handling for CompilationFinished with error count
                details = action_desc
                if explicit_action == 'CompilationFinished' and row.get('errorCount'):
                    details = f"Compilation finished with {row.get('errorCount')} error(s)"
                
                actions.append({
                    'action': action_desc,
                    'start': int(previous_row['timestamp']),
                    'duration': time_since_last,
                    'details': details
                })
            
            # Detect action from fragment changes
            action_info = self._detect_action(previous_row, row, previous_fragment)
            
            if action_info:
                actions.append({
                    'action': action_info['type'],
                    'start': int(previous_row['timestamp']),
                    'duration': time_since_last,
                    'details': action_info['details']
                })
            
            previous_row = row
            previous_fragment = row.get('fragment', '')
        
        return actions
    
    def _detect_action(self, prev_row: Dict, curr_row: Dict, prev_fragment: str) -> Dict:
        """
        Detect what action occurred between two rows.
        
        Returns:
            Dictionary with 'type' and 'details' keys, or None if no significant action
        """
        prev_fragment = prev_row.get('fragment', '')
        curr_fragment = curr_row.get('fragment', '')
        
        # If fragments are identical, no editing action occurred
        if prev_fragment == curr_fragment:
            # Check for other state changes
            if prev_row.get('testMode') != curr_row.get('testMode'):
                return {
                    'type': 'Mode change',
                    'details': f"Test mode: {prev_row.get('testMode')} → {curr_row.get('testMode')}"
                }
            return None
        
        # Calculate edit distance metrics
        prev_len = len(prev_fragment)
        curr_len = len(curr_fragment)
        length_diff = curr_len - prev_len
        
        # Check if this is likely a copy operation (large insertion of previously seen text)
        if length_diff > 10:
            # Check if inserted text appears earlier in the document
            added_text = self._find_added_text(prev_fragment, curr_fragment)
            if added_text and len(added_text) > 10:
                # Check if this text existed earlier in the previous fragment
                if added_text.strip() in prev_fragment:
                    return {
                        'type': 'Copy/Paste (internal)',
                        'details': f"Pasted {len(added_text)} character(s) from same file"
                    }
                else:
                    return {
                        'type': 'Paste (external)',
                        'details': f"Pasted {len(added_text)} character(s) from clipboard"
                    }
        
        # Determine action type based on changes
        if length_diff > 0:
            # Text was added
            if length_diff == 1:
                added_char = self._find_added_char(prev_fragment, curr_fragment)
                return {
                    'type': 'Type character',
                    'details': f"Added: '{added_char}'"
                }
            elif length_diff <= 10:
                return {
                    'type': 'Type text',
                    'details': f"Added {length_diff} character(s)"
                }
            else:
                # Likely paste or autocomplete
                return {
                    'type': 'Insert text',
                    'details': f"Inserted {length_diff} character(s) (paste/autocomplete)"
                }
        
        elif length_diff < 0:
            # Text was deleted - check if it might be a cut operation
            deleted_count = abs(length_diff)
            
            if deleted_count == 1:
                return {
                    'type': 'Delete character',
                    'details': f"Deleted 1 character"
                }
            elif deleted_count <= 10:
                return {
                    'type': 'Delete text',
                    'details': f"Deleted {deleted_count} character(s)"
                }
            else:
                # Large deletion - might be cut
                return {
                    'type': 'Delete block',
                    'details': f"Deleted {deleted_count} character(s) (possibly cut)"
                }
        
        else:
            # Same length but different content - likely replacement
            return {
                'type': 'Replace text',
                'details': f"Modified text (same length)"
            }
    
    def _find_added_char(self, prev_text: str, curr_text: str) -> str:
        """Find the character that was added."""
        # Simple approach: find first difference
        for i, (p, c) in enumerate(zip(prev_text, curr_text)):
            if p != c:
                return c
        # If we get here, the char was added at the end
        if len(curr_text) > len(prev_text):
            return curr_text[len(prev_text)]
        return '?'
    
    def _find_added_text(self, prev_text: str, curr_text: str) -> str:
        """
        Find the text that was added between two versions.
        Uses a simple algorithm to find the inserted text.
        """
        # Get the differences using difflib
        matcher = difflib.SequenceMatcher(None, prev_text, curr_text)
        
        added_text = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                added_text.append(curr_text[j1:j2])
        
        return ''.join(added_text) if added_text else ''
    
    def _write_output_csv(self, output_path: str, actions: List[Dict]) -> None:
        """Write actions to output CSV file."""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['action', 'start_ms', 'duration_ms', 'start_sec', 'duration_sec', 'details']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for action in actions:
                writer.writerow({
                    'action': action['action'],
                    'start_ms': action['start'],
                    'duration_ms': action['duration'],
                    'start_sec': f"{action['start']/1000:.3f}",
                    'duration_sec': f"{action['duration']/1000:.3f}",
                    'details': action['details']
                })
    
    def _generate_output_path(self, input_path: str) -> str:
        """Generate output file path from input path."""
        path = Path(input_path)
        return str(path.parent / f"{path.stem}_analyzed.csv")


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze activity tracking CSV files and generate human-readable action logs.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file (output in same directory)
  python activity_analyzer.py data.csv
  
  # Single file with custom output location
  python activity_analyzer.py data.csv -o results/analyzed.csv
  
  # Process all CSV files in a directory
  python activity_analyzer.py study_data/ -d
  
  # Process directory and save to different location
  python activity_analyzer.py study_data/ -d -o analyzed_results/
  
  # Custom inactivity threshold (10 seconds)
  python activity_analyzer.py data.csv -o output.csv -t 10000
        """
    )
    parser.add_argument(
        'input',
        help='Input CSV file or directory containing CSV files'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (for single file) or directory (for batch). If not specified, outputs are saved alongside input files with "_analyzed" suffix'
    )
    parser.add_argument(
        '-t', '--threshold',
        type=int,
        default=5000,
        help='Inactivity threshold in milliseconds (default: 5000 = 5 seconds)'
    )
    parser.add_argument(
        '-d', '--directory',
        action='store_true',
        help='Process all CSV files in the input directory'
    )
    
    args = parser.parse_args()
    
    # Create analyzer with custom threshold
    analyzer = ActivityAnalyzer(inactivity_threshold_ms=args.threshold)
    
    print(f"\n{'='*60}")
    print("Activity Tracker CSV Analyzer")
    print(f"{'='*60}")
    print(f"Inactivity threshold: {args.threshold}ms ({args.threshold/1000}s)")
    print(f"{'='*60}\n")
    
    # Process file or directory
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: {args.input} does not exist")
        sys.exit(1)
    
    if input_path.is_dir() or args.directory:
        analyzer.analyze_directory(args.input, args.output)
    else:
        analyzer.analyze_file(args.input, args.output)
        if not args.output:
            print(f"\nTip: Use -o flag to specify custom output location")
            print(f"Example: python activity_analyzer.py {args.input} -o results/output.csv")


if __name__ == '__main__':
    main()
