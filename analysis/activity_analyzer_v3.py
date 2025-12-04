#!/usr/bin/env python3
"""
Activity Tracker CSV Analyzer v3.0 - With Content Logging
Analyzes CSV files and logs actual content of copy/paste/cut/undo operations.
"""

import csv
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import difflib


class ActivityAnalyzer:
    """Analyzes activity tracking CSV files with content logging."""
    
    # Configurable parameters
    INACTIVITY_THRESHOLD_MS = 50000
    LOG_CONTENT = True
    MAX_CONTENT_LENGTH = 100
    SHOW_ESCAPED_NEWLINES = True
    
    ACTION_DESCRIPTIONS = {
        'Active': 'IDE gained focus',
        'Inactive': 'IDE lost focus',
        'NoProject': 'All projects closed',
        'NewProject': 'Create new project',
        'SaveAs': 'Save file as',
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
        'EditorCopy': 'Copy text (menu)',
        'EditorPaste': 'Paste text (menu)',
        'EditorCut': 'Cut text (menu)',
        'CopyPaths': 'Copy file path',
        'ReformatCode': 'Reformat code',
        'NewElement': 'Create new element',
        'ShowPopupMenu': 'Show popup menu',
        '$Undo': 'Undo (Ctrl+Z)',
        '$Paste': 'Paste (Ctrl+V)',
        '$Copy': 'Copy (Ctrl+C)',
        '$Redo': 'Redo (Ctrl+Y)',
        'CompilationFinished': 'Compilation finished',
    }
    
    def __init__(self, inactivity_threshold_ms=None, log_content=None, max_content_length=None):
        if inactivity_threshold_ms is not None:
            self.INACTIVITY_THRESHOLD_MS = inactivity_threshold_ms
        if log_content is not None:
            self.LOG_CONTENT = log_content
        if max_content_length is not None:
            self.MAX_CONTENT_LENGTH = max_content_length
    
    def analyze_file(self, input_path, output_path=None):
        """Analyze a single CSV file and generate output."""
        if output_path is None:
            output_path = self._generate_output_path(input_path)
        
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing: {input_path}")
        
        rows = self._read_csv(input_path)
        
        if not rows:
            print(f"Warning: No data found in {input_path}")
            return
        
        actions = self._analyze_actions(rows)
        self._write_output_csv(output_path, actions)
        
        print(f"✓ Output saved to: {output_path}")
        print(f"  Total actions logged: {len(actions)}")
        print(f"  Content logging: {'ON' if self.LOG_CONTENT else 'OFF'}")
        print()
    
    def analyze_directory(self, directory_path, output_dir=None):
        """Analyze all CSV files in a directory."""
        directory = Path(directory_path)
        
        if not directory.exists() or not directory.is_dir():
            print(f"Error: {directory_path} is not a valid directory")
            return
        
        csv_files = list(directory.glob("*.csv"))
        
        if not csv_files:
            print(f"No CSV files found in {directory_path}")
            return
        
        print(f"Found {len(csv_files)} CSV file(s) to process")
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"Output directory: {output_path.absolute()}")
        else:
            print(f"Output location: Same directory as input files")
        
        print(f"Content logging: {'ON' if self.LOG_CONTENT else 'OFF'}")
        print()
        
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
    
    def _read_csv(self, file_path):
        """Read CSV file and return list of row dictionaries."""
        rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows
    
    def _analyze_actions(self, rows):
        """Analyze rows and extract human-readable actions with content."""
        actions = []
        
        if not rows:
            return actions
        
        has_action_column = 'action' in rows[0]
        previous_row = None
        previous_fragment = None
        
        for i, row in enumerate(rows):
            timestamp = int(row['timestamp'])
            
            if i == 0:
                actions.append({
                    'action': 'Session started',
                    'start': 0,
                    'duration': 0,
                    'details': f"File: {row['fileName']}, Task: {row['chosenTask']}",
                    'content': ''
                })
                previous_row = row
                previous_fragment = row.get('fragment', '')
                continue
            
            time_since_last = timestamp - int(previous_row['timestamp'])
            
            if time_since_last < 0:
                time_since_last = 0
            
            if time_since_last >= self.INACTIVITY_THRESHOLD_MS:
                actions.append({
                    'action': 'Inactive/Break',
                    'start': int(previous_row['timestamp']),
                    'duration': time_since_last,
                    'details': f"No activity for {time_since_last/1000:.2f} seconds",
                    'content': ''
                })
            
            if has_action_column and row.get('action') and row['action'].strip():
                explicit_action = row['action'].strip()
                action_desc = self.ACTION_DESCRIPTIONS.get(explicit_action, explicit_action)
                
                content = self._extract_action_content(explicit_action, previous_fragment, 
                                                       row.get('fragment', ''))
                
                details = action_desc
                if explicit_action == 'CompilationFinished' and row.get('errorCount'):
                    details = f"Compilation finished with {row.get('errorCount')} error(s)"
                
                actions.append({
                    'action': action_desc,
                    'start': int(previous_row['timestamp']),
                    'duration': time_since_last,
                    'details': details,
                    'content': content
                })
            
            action_info = self._detect_action(previous_row, row, previous_fragment)
            
            if action_info:
                actions.append({
                    'action': action_info['type'],
                    'start': int(previous_row['timestamp']),
                    'duration': time_since_last,
                    'details': action_info['details'],
                    'content': action_info.get('content', '')
                })
            
            previous_row = row
            previous_fragment = row.get('fragment', '')
        
        return actions
    
    def _extract_action_content(self, action, prev_fragment, curr_fragment):
        """Extract the actual content involved in an action."""
        if not self.LOG_CONTENT:
            return ''
        
        if action in ['$Undo', '$Redo', 'EditorUndo']:
            return self._get_diff_content(prev_fragment, curr_fragment)
        
        if action in ['EditorCopy', '$Copy']:
            return '[Content copied to clipboard]'
        
        if action in ['EditorPaste', '$Paste']:
            added = self._find_added_text(prev_fragment, curr_fragment)
            return self._format_content(added)
        
        if action in ['EditorCut']:
            removed = self._find_removed_text(prev_fragment, curr_fragment)
            return self._format_content(removed)
        
        return ''
    
    def _detect_action(self, prev_row, curr_row, prev_fragment):
        """Detect what action occurred between two rows."""
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
        
        prev_len = len(prev_fragment)
        curr_len = len(curr_fragment)
        length_diff = curr_len - prev_len
        
        if length_diff > 10:
            added_text = self._find_added_text(prev_fragment, curr_fragment)
            if added_text and len(added_text) > 10:
                if added_text.strip() in prev_fragment:
                    return {
                        'type': 'Copy/Paste (internal)',
                        'details': f"Pasted {len(added_text)} character(s) from same file",
                        'content': self._format_content(added_text) if self.LOG_CONTENT else ''
                    }
                else:
                    return {
                        'type': 'Paste (external)',
                        'details': f"Pasted {len(added_text)} character(s) from clipboard",
                        'content': self._format_content(added_text) if self.LOG_CONTENT else ''
                    }
        
        if length_diff > 0:
            if length_diff == 1:
                added_char = self._find_added_char(prev_fragment, curr_fragment)
                return {
                    'type': 'Type character',
                    'details': f"Added: '{added_char}'",
                    'content': self._format_content(added_char) if self.LOG_CONTENT else ''
                }
            elif length_diff <= 10:
                added_text = self._find_added_text(prev_fragment, curr_fragment)
                return {
                    'type': 'Type text',
                    'details': f"Added {length_diff} character(s)",
                    'content': self._format_content(added_text) if self.LOG_CONTENT else ''
                }
            else:
                added_text = self._find_added_text(prev_fragment, curr_fragment)
                return {
                    'type': 'Insert text',
                    'details': f"Inserted {length_diff} character(s) (paste/autocomplete)",
                    'content': self._format_content(added_text) if self.LOG_CONTENT else ''
                }
        
        elif length_diff < 0:
            deleted_count = abs(length_diff)
            deleted_text = self._find_removed_text(prev_fragment, curr_fragment)
            
            if deleted_count == 1:
                return {
                    'type': 'Delete character',
                    'details': f"Deleted 1 character",
                    'content': self._format_content(deleted_text) if self.LOG_CONTENT else ''
                }
            elif deleted_count <= 10:
                return {
                    'type': 'Delete text',
                    'details': f"Deleted {deleted_count} character(s)",
                    'content': self._format_content(deleted_text) if self.LOG_CONTENT else ''
                }
            else:
                return {
                    'type': 'Delete block',
                    'details': f"Deleted {deleted_count} character(s) (possibly cut)",
                    'content': self._format_content(deleted_text) if self.LOG_CONTENT else ''
                }
        
        else:
            diff_content = self._get_diff_content(prev_fragment, curr_fragment)
            return {
                'type': 'Replace text',
                'details': f"Modified text (same length)",
                'content': self._format_content(diff_content) if self.LOG_CONTENT else ''
            }
    
    def _find_added_char(self, prev_text, curr_text):
        """Find the character that was added."""
        for i, (p, c) in enumerate(zip(prev_text, curr_text)):
            if p != c:
                return c
        if len(curr_text) > len(prev_text):
            return curr_text[len(prev_text)]
        return '?'
    
    def _find_added_text(self, prev_text, curr_text):
        """Find the text that was added between two versions."""
        matcher = difflib.SequenceMatcher(None, prev_text, curr_text)
        
        added_text = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                added_text.append(curr_text[j1:j2])
        
        return ''.join(added_text)
    
    def _find_removed_text(self, prev_text, curr_text):
        """Find the text that was removed between two versions."""
        matcher = difflib.SequenceMatcher(None, prev_text, curr_text)
        
        removed_text = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                removed_text.append(prev_text[i1:i2])
        
        return ''.join(removed_text)
    
    def _get_diff_content(self, prev_text, curr_text):
        """Get a summary of what changed between two texts."""
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
        
        if self.SHOW_ESCAPED_NEWLINES:
            content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        
        if self.MAX_CONTENT_LENGTH > 0 and len(content) > self.MAX_CONTENT_LENGTH:
            content = content[:self.MAX_CONTENT_LENGTH] + '...'
        
        return content
    
    def _write_output_csv(self, output_path, actions):
        """Write actions to output CSV file."""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if self.LOG_CONTENT:
                fieldnames = ['action', 'start_ms', 'duration_ms', 'start_sec', 
                            'duration_sec', 'details', 'content']
            else:
                fieldnames = ['action', 'start_ms', 'duration_ms', 'start_sec', 
                            'duration_sec', 'details']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for action in actions:
                row_data = {
                    'action': action['action'],
                    'start_ms': action['start'],
                    'duration_ms': action['duration'],
                    'start_sec': f"{action['start']/1000:.3f}",
                    'duration_sec': f"{action['duration']/1000:.3f}",
                    'details': action['details']
                }
                if self.LOG_CONTENT:
                    row_data['content'] = action.get('content', '')
                
                writer.writerow(row_data)
    
    def _generate_output_path(self, input_path):
        """Generate output file path from input path."""
        path = Path(input_path)
        return str(path.parent / f"{path.stem}_analyzed.csv")


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze activity tracking CSV files with content logging.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file with content logging (default)
  python activity_analyzer_v3.py data.csv
  
  # Single file with custom output location
  python activity_analyzer_v3.py data.csv -o results/analyzed.csv
  
  # Process all CSV files in a directory
  python activity_analyzer_v3.py study_data/ -d
  
  # Disable content logging for smaller files
  python activity_analyzer_v3.py data.csv --no-content
  
  # Custom content length limit (50 characters)
  python activity_analyzer_v3.py data.csv --max-content 50
  
  # Unlimited content length
  python activity_analyzer_v3.py data.csv --max-content 0
  
  # Batch process with custom settings
  python activity_analyzer_v3.py study_data/ -d -o results/ -t 8000 --max-content 200
        """
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
        default=5000,
        help='Inactivity threshold in milliseconds (default: 5000 = 5 seconds)'
    )
    parser.add_argument(
        '-d', '--directory',
        action='store_true',
        help='Process all CSV files in the input directory'
    )
    parser.add_argument(
        '--no-content',
        action='store_true',
        help='Disable logging of actual content (smaller output files)'
    )
    parser.add_argument(
        '--max-content',
        type=int,
        default=100,
        help='Maximum length of content to log (default: 100, use 0 for unlimited)'
    )
    
    args = parser.parse_args()
    
    analyzer = ActivityAnalyzer(
        inactivity_threshold_ms=args.threshold,
        log_content=not args.no_content,
        max_content_length=args.max_content
    )
    
    print(f"\n{'='*60}")
    print("Activity Tracker CSV Analyzer v3.0 - WITH CONTENT LOGGING")
    print(f"{'='*60}")
    print(f"Inactivity threshold: {args.threshold}ms ({args.threshold/1000}s)")
    print(f"Content logging: {'OFF' if args.no_content else 'ON'}")
    if not args.no_content:
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
        if not args.output:
            print(f"\nTip: Use -o flag to specify custom output location")
            print(f"Example: python activity_analyzer_v3.py {args.input} -o results/output.csv")


if __name__ == '__main__':
    main()
