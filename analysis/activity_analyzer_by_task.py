"""
Activity Analyzer (by-task output layout)

This script reuses ActivityAnalyzer from activity_analyzer.py but when batch-processing
an input directory writes outputs into an output directory with the following layout:

output_dir/
  task1.xlsx    (sheets: student1, student2, ...)
  task2.xlsx    (sheets: student1, student3, ...)
  task3.xlsx
  task4.xlsx

Student numbering (student1, student2, ...) is assigned once per unique student key
(discovered from the input directory structure) and remains stable across tasks.

Usage:
python activity_analyzer_by_task.py input_dir -o output_dir -d [--content] [--threshold ms]
"""

import sys
from pathlib import Path
import argparse
from collections import defaultdict

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# Reuse existing ActivityAnalyzer implementation
try:
    from activity_analyzer import ActivityAnalyzer
except Exception:
    # If running as a module or different cwd, try importing by file path
    # (fallback: duplicate minimal import behavior)
    from activity_analyzer import ActivityAnalyzer


class ActivityAnalyzerByTask:
    """Wrapper around ActivityAnalyzer that writes outputs into per-task Excel files
    with one sheet per student (studentN) where N is a stable index assigned per-student.
    """

    def __init__(self, inactivity_threshold_ms=60000, log_content=False, max_content_length=0):
        self.analyzer = ActivityAnalyzer(
            inactivity_threshold_ms=inactivity_threshold_ms,
            log_content=log_content,
            max_content_length=max_content_length,
        )
        # Mapping from student key -> index (1-based)
        self.student_map = {}
        self.next_student_index = 1

    def _get_student_key(self, file_path: Path, root_dir: Path):
        """Extract a stable student key from path relative to root_dir.

        Strategy:
        - If file_path is inside root_dir: use the first path part of the relative path
          (this matches structures like ROOT/user_1/1/1_*.csv).
        - Otherwise, try to find any ancestor that looks like 'user_' and use that.
        - Fallback to the immediate parent directory name.
        """
        try:
            rel = file_path.relative_to(root_dir)
            parts = rel.parts
            if len(parts) >= 2:
                # first part is student folder (e.g., user_1)
                return parts[0]
            elif parts:
                return parts[0]
        except Exception:
            pass

        # look for ancestor named like 'user_'
        for p in file_path.parents:
            if p.name.startswith('user_'):
                return p.name

        # fallback to parent folder
        return file_path.parent.name

    def _get_student_index(self, student_key: str):
        if student_key in self.student_map:
            return self.student_map[student_key]
        idx = self.next_student_index
        self.student_map[student_key] = idx
        self.next_student_index += 1
        return idx

    def _detect_task_number(self, file_path: Path):
        name = file_path.name
        if name and len(name) > 0 and name[0] in '1234' and name[1] == '_':
            return int(name[0])
        # fallback: look for patterns '1_', '2_', ... anywhere
        for ch in '1234':
            if f"{ch}_" in name:
                return int(ch)
        return None

    def _write_task_excel(self, output_path, task_data):
        """Write all students for a single task into one Excel file with one sheet per student.

        Args:
            output_path (Path): Path to the output .xlsx file
            task_data (dict): Mapping of student_name -> list of action dicts
        """
        wb = Workbook()
        # Remove default sheet
        wb.remove(wb.active)

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
            'code',
            'code_len',
        ]

        if self.analyzer.log_content:
            fieldnames.append('content')

        for student_name in sorted(task_data.keys(), key=lambda s: int(s.replace('student', ''))):
            actions = task_data[student_name]
            ws = wb.create_sheet(title=student_name)

            # Build time_percent: linear 0-100% across all real actions (excluding Session total).
            # The first real action = 0%, the last real action = 100%.
            real_actions = [a for a in actions if a.get('action') != 'Session total']
            num_real = len(real_actions)
            time_percent_map = {}
            for idx, a in enumerate(real_actions):
                if num_real <= 1:
                    pct = 0.0
                else:
                    pct = idx / (num_real - 1) * 100.0
                time_percent_map[id(a)] = pct

            # Write header row
            for col_idx, header in enumerate(fieldnames, 1):
                cell = ws.cell(row=1, column=col_idx, value=header)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')

            # Write data rows
            for row_idx, action in enumerate(actions, 2):
                start = action.get('start', 0)
                duration = action.get('duration', 0)
                end = start + duration

                start_sec, start_min = self.analyzer._format_time(start)
                end_sec, end_min = self.analyzer._format_time(end)
                duration_sec, duration_min = self.analyzer._format_time(duration)

                # time_percent: 0% for first action, 100% for last, linear in between
                time_percent = time_percent_map.get(id(action), 0.0)

                code_val = action.get('code', '') or ''
                try:
                    code_len_val = len(code_val)
                except Exception:
                    code_len_val = 0

                row_data = {
                    'action': action['action'],
                    'time_percent': round(time_percent, 2),
                    'start_sec': round(start / 1000, 2),
                    'start_min': round(start / 60000, 2),
                    'end_sec': round(end / 1000, 2),
                    'end_min': round(end / 60000, 2),
                    'duration_sec': round(duration / 1000, 2),
                    'duration_min': round(duration / 60000, 2),
                    'details': action['details'],
                    'change_len': action.get('change_len', 0),
                    'lines_added': action.get('lines_added', 0),
                    'lines_removed': action.get('lines_removed', 0),
                    'code': code_val,
                    'code_len': code_len_val,
                }

                if self.analyzer.log_content:
                    row_data['content'] = action.get('content', '')

                for col_idx, field in enumerate(fieldnames, 1):
                    ws.cell(row=row_idx, column=col_idx, value=row_data.get(field, ''))

            # Auto-size columns (approximate)
            for col_idx, header in enumerate(fieldnames, 1):
                ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = max(len(header) + 2, 12)

        wb.save(str(output_path))

    def analyze_directory(self, input_dir: str, output_dir: str = None):
        root = Path(input_dir)
        if not root.exists() or not root.is_dir():
            print(f"Error: {input_dir} is not a valid directory")
            return

        # Find all task files
        csv_files = []
        for pattern in ['1_*.csv', '2_*.csv', '3_*.csv', '4_*.csv']:
            csv_files.extend(root.rglob(pattern))

        if not csv_files:
            print(f"No task CSV files found in {input_dir}")
            return

        output_root = Path(output_dir) if output_dir else None
        if output_root:
            output_root.mkdir(parents=True, exist_ok=True)

        print(f"Found {len(csv_files)} task file(s) to process\n")

        # Collect actions grouped by task number -> student name -> actions
        # task_results[task_num][student_name] = actions_list
        task_results = defaultdict(dict)

        for i, csv_file in enumerate(sorted(csv_files), 1):
            print(f"[{i}/{len(csv_files)}] Processing {csv_file}")

            task_num = self._detect_task_number(csv_file)
            if task_num is None:
                print(f"  Warning: Could not detect task number for {csv_file.name}; skipping")
                continue

            student_key = self._get_student_key(csv_file, root)
            student_idx = self._get_student_index(student_key)
            student_name = f"student{student_idx}"

            # Run analysis and collect actions
            try:
                actions = self.analyzer.analyze_file_to_actions(str(csv_file))
                if actions is not None:
                    task_results[task_num][student_name] = actions
            except Exception as e:
                print(f"  Error processing {csv_file}: {e}")

        # Write one Excel file per task
        if output_root:
            for task_num in sorted(task_results.keys()):
                output_file = output_root / f"task{task_num}.xlsx"
                self._write_task_excel(output_file, task_results[task_num])
                sheet_count = len(task_results[task_num])
                print(f"✓ Saved {output_file} ({sheet_count} student sheet(s))")

        print(f"\n{'='*60}")
        print(f"Batch processing complete! Processed {len(csv_files)} file(s)")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze activity CSV files and write outputs into per-task Excel files.'
    )
    parser.add_argument('input', help='Input directory containing student/task CSV files')
    parser.add_argument('-o', '--output', help='Output directory to write task Excel files', required=True)
    parser.add_argument('-t', '--threshold', type=int, default=60000, help='Inactivity threshold in milliseconds')
    parser.add_argument('-d', '--directory', action='store_true', help='Process as directory (required)')
    parser.add_argument('--content', action='store_true', help="Include 'content' column in outputs")
    parser.add_argument('--max-content', type=int, default=0, help='Max content length (0 = unlimited)')

    args = parser.parse_args()

    analyzer = ActivityAnalyzerByTask(
        inactivity_threshold_ms=args.threshold,
        log_content=args.content,
        max_content_length=args.max_content,
    )

    if not Path(args.input).exists():
        print(f"Error: {args.input} does not exist")
        sys.exit(1)

    # Force directory mode
    analyzer.analyze_directory(args.input, args.output)


if __name__ == '__main__':
    main()