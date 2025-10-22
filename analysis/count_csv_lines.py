"""
CSV Line Counter

Counts total lines across all CSV files in a directory structure.
Perfect for getting a sense of dataset size.

Usage:
python count_csv_lines.py [directory_path]
"""

import glob
import os
import sys
import argparse
import matplotlib.pyplot as plt


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
    print(f"\U0001F4CA FINAL RESULTS:")
    print(f"   Total CSV files: {file_count:,}")
    print(f"   Total lines: {total_lines:,}")
    print(f"   Average lines per file: {total_lines // file_count if file_count > 0 else 0:,}")

    if largest_file:
        print(f"   Largest file: {os.path.basename(largest_file)} ({largest_file_lines:,} lines)")

    # Fun comparisons
    # if total_lines > 100000:
    #     print(f"   That's {total_lines / 100000:.1f}x your original estimate!")

    # if total_lines > 1000000:
    #     print(f"   \U0001F389 Congrats! You've officially hit the million+ line club!")


def main():
    parser = argparse.ArgumentParser(description='Count CSV lines and optionally create visuals')
    parser.add_argument('input_folder', help='Folder to scan for CSV files (e.g. study_data)')
    parser.add_argument('output_folder', nargs='?', default=None, help='Folder to write visuals (optional)')
    parser.add_argument('--visuals', action='store_true', help='Create visualizations (histogram of file line counts)')
    args = parser.parse_args()

    if not os.path.isdir(args.input_folder):
        print(f"Error: {args.input_folder} is not a valid directory")
        sys.exit(1)

    # Run the count
    csv_files = glob.glob(os.path.join(args.input_folder, '**', '*.csv'), recursive=True)
    if not csv_files:
        print("No CSV files found!")
        return

    # If visuals requested, gather per-file line counts for plotting
    per_file_counts = []
    total_lines = 0
    file_count = 0
    largest_file = None
    largest_file_lines = 0

    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
                per_file_counts.append((csv_file, line_count))
                total_lines += line_count
                file_count += 1
                if line_count > largest_file_lines:
                    largest_file = csv_file
                    largest_file_lines = line_count
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

    # Print results (same as before)
    print("=" * 50)
    print(f"\U0001F4CA FINAL RESULTS:")
    print(f"   Total CSV files: {file_count:,}")
    print(f"   Total lines: {total_lines:,}")
    print(f"   Average lines per file: {total_lines // file_count if file_count > 0 else 0:,}")
    if largest_file:
        print(f"   Largest file: {os.path.basename(largest_file)} ({largest_file_lines:,} lines)")

    # Create visuals if requested
    if args.visuals:
        out_dir = args.output_folder or os.path.join(os.getcwd(), 'results', 'csv_line_counts')
        os.makedirs(out_dir, exist_ok=True)
        counts = [c for _, c in per_file_counts]
        plt.figure(figsize=(8,5))
        plt.hist(counts, bins=30, color='C0', edgecolor='k')
        plt.xlabel('Line counts')
        plt.ylabel('Frequency')
        plt.title('Distribution of CSV line counts')
        out_path = os.path.join(out_dir, 'csv_line_counts_histogram.png')
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close()
        print(f"Saved histogram to {out_path}")


if __name__ == '__main__':
    main()