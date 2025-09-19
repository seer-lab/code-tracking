"""
CSV Line Counter

Counts total lines across all CSV files in a directory structure.
Perfect for getting a sense of dataset size.

Usage:
python count_csv_lines.py [directory_path]
"""

import csv
import glob
import os
import sys


def count_csv_lines(directory_path):
    """
    Count total lines across all CSV files in directory structure
    Args:
        directory_path: Path to directory containing CSV files
    """

    # Find all CSV files recursively
    csv_files = glob.glob(os.path.join(directory_path, '**', '*.csv'), recursive=True)

    if not csv_files:
        print("No CSV files found!")
        return

    total_lines = 0
    file_count = 0
    largest_file = None
    largest_file_lines = 0

    print(f"Scanning CSV files in: {directory_path}")
    print("=" * 50)

    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Count lines efficiently
                line_count = sum(1 for line in f)
                total_lines += line_count
                file_count += 1

                # Track largest file
                if line_count > largest_file_lines:
                    largest_file = csv_file
                    largest_file_lines = line_count

                # Show progress for large datasets
                if file_count % 10 == 0:
                    print(f"Processed {file_count} files... ({total_lines:,} lines so far)")

        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

    # Final results
    print("=" * 50)
    print(f"📊 FINAL RESULTS:")
    print(f"   Total CSV files: {file_count:,}")
    print(f"   Total lines: {total_lines:,}")
    print(f"   Average lines per file: {total_lines // file_count if file_count > 0 else 0:,}")

    if largest_file:
        print(f"   Largest file: {os.path.basename(largest_file)} ({largest_file_lines:,} lines)")

    # Fun comparisons
    # if total_lines > 100000:
    #     print(f"   That's {total_lines / 100000:.1f}x your original estimate!")

    # if total_lines > 1000000:
    #     print(f"   🎉 Congrats! You've officially hit the million+ line club!")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python count_csv_lines.py [directory_path]")
        print("Example: python count_csv_lines.py study_data/")
        sys.exit(1)

    directory_path = sys.argv[1]

    if not os.path.isdir(directory_path):
        print(f"Error: {directory_path} is not a valid directory")
        sys.exit(1)

    count_csv_lines(directory_path)


if __name__ == '__main__':
    main()