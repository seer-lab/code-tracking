"""
Activity Analyzer (by-task output layout)

This script reuses ActivityAnalyzer from activity_analyzer.py but when batch-processing
an input directory writes outputs into an output directory with the following layout:

output_dir/
  task1/
    student1.csv
    student2.csv
  task2/
    student1.csv
    student3.csv
  task3/
  task4/

Student numbering (student1, student2, ...) is assigned once per unique student key
(discovered from the input directory structure) and remains stable across tasks.

Usage:
python activity_analyzer_by_task.py input_dir -o output_dir -d [--content] [--threshold ms]
"""

import sys
from pathlib import Path
import argparse

# Reuse existing ActivityAnalyzer implementation
try:
    from activity_analyzer import ActivityAnalyzer
except Exception:
    # If running as a module or different cwd, try importing by file path
    # (fallback: duplicate minimal import behavior)
    from activity_analyzer import ActivityAnalyzer


class ActivityAnalyzerByTask:
    """Wrapper around ActivityAnalyzer that writes outputs into per-task folders
    with studentN filenames where N is a stable index assigned per-student.
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

        for i, csv_file in enumerate(sorted(csv_files), 1):
            print(f"[{i}/{len(csv_files)}] Processing {csv_file}")

            task_num = self._detect_task_number(csv_file)
            if task_num is None:
                print(f"  Warning: Could not detect task number for {csv_file.name}; skipping")
                continue

            student_key = self._get_student_key(csv_file, root)
            student_idx = self._get_student_index(student_key)

            if output_root:
                task_dir = output_root / f"task{task_num}"
                task_dir.mkdir(parents=True, exist_ok=True)
                output_file = task_dir / f"student{student_idx}.csv"
            else:
                output_file = None

            # run analysis for single file
            try:
                self.analyzer.analyze_file(str(csv_file), str(output_file) if output_file else None)
            except Exception as e:
                print(f"  Error processing {csv_file}: {e}")

        print(f"\n{'='*60}")
        print(f"Batch processing complete! Processed {len(csv_files)} file(s)")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze activity CSV files and write outputs into per-task student folders.'
    )
    parser.add_argument('input', help='Input directory containing student/task CSV files')
    parser.add_argument('-o', '--output', help='Output directory to write task subfolders', required=True)
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

