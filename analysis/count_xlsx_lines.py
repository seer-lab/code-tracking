"""
Excel File Line Counter

Counts the total number of rows across all Excel files (.xlsx, .xls, .xlsm, .xlsb) in a directory structure.
Provides summary statistics, including largest files by size and row count, and displays top 5 files in each category.

Usage:
    python count_xlsx_lines.py [directory_path] [--output OUTPUT_DIR]

Arguments:
    directory_path (optional): Path to the directory to scan. If not provided, prompts the user or defaults to the current directory.
    --output, -o (optional): Directory to save results (default: results)

Features:
- Recursively scans the specified directory and all subdirectories for Excel files.
- Counts the total number of rows across all sheets in each Excel file.
- Reports file size (bytes and human-readable format).
- Saves all results to CSV files in the output directory:
    - all_files.csv: All scanned files with size and row count
    - top5_by_size.csv: Top 5 largest files by size
    - top5_by_row_count.csv: Top 5 largest files by row count
    - summary.csv: Overall summary statistics
- Displays a brief summary to the console.
- Handles unreadable files and sheets gracefully with warnings.

Example:
    python count_xlsx_lines.py study_data/ --output my_results

Output:
- CSV files in the output directory (default: results)
- Console summary for quick feedback

Dependencies:
- pandas

"""

import os
import pandas as pd
from pathlib import Path
import sys


def get_file_size(file_path):
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def get_excel_row_count(file_path):
    """Get the total number of rows across all sheets in an Excel file"""
    try:
        # Read all sheets from the Excel file
        excel_file = pd.ExcelFile(file_path)
        total_rows = 0

        for sheet_name in excel_file.sheet_names:
            try:
                # Read each sheet and count rows
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                total_rows += len(df)
            except Exception as e:
                print(f"Warning: Could not read sheet '{sheet_name}' in {file_path}: {e}")
                continue

        return total_rows
    except Exception as e:
        print(f"Warning: Could not read Excel file {file_path}: {e}")
        return 0


def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f} {size_names[i]}"


def scan_excel_files(root_directory):
    """Scan directory and subdirectories for Excel files"""
    print(f"Scanning directory: {root_directory}")
    print("=" * 60)

    # Excel file extensions to look for
    excel_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb']

    files_info = []

    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = Path(file_path).suffix.lower()

            if file_extension in excel_extensions:
                print(f"Processing: {file_path}")

                # Get file size
                file_size = get_file_size(file_path)

                # Get row count
                row_count = get_excel_row_count(file_path)

                files_info.append({
                    'path': file_path,
                    'name': file,
                    'size_bytes': file_size,
                    'size_formatted': format_file_size(file_size),
                    'row_count': row_count,
                    'relative_path': os.path.relpath(file_path, root_directory)
                })

    return files_info


def display_results(files_info):
    """Display the results"""
    if not files_info:
        print("No Excel files found in the specified directory.")
        return

    print(f"\nFound {len(files_info)} Excel files")
    print("=" * 60)

    # Find largest by file size
    largest_by_size = max(files_info, key=lambda x: x['size_bytes'])

    # Find largest by row count
    largest_by_rows = max(files_info, key=lambda x: x['row_count'])

    print("\n🏆 LARGEST FILE BY SIZE:")
    print(f"File: {largest_by_size['name']}")
    print(f"Path: {largest_by_size['relative_path']}")
    print(f"Size: {largest_by_size['size_formatted']} ({largest_by_size['size_bytes']:,} bytes)")
    print(f"Rows: {largest_by_rows['row_count']:,}")

    print("\n🏆 LARGEST FILE BY ROW COUNT:")
    print(f"File: {largest_by_rows['name']}")
    print(f"Path: {largest_by_rows['relative_path']}")
    print(f"Size: {largest_by_rows['size_formatted']} ({largest_by_rows['size_bytes']:,} bytes)")
    print(f"Rows: {largest_by_rows['row_count']:,}")

    # Show top 5 by size
    print("\n📊 TOP 5 LARGEST BY SIZE:")
    sorted_by_size = sorted(files_info, key=lambda x: x['size_bytes'], reverse=True)[:5]
    for i, file_info in enumerate(sorted_by_size, 1):
        print(f"{i}. {file_info['name']} - {file_info['size_formatted']} ({file_info['row_count']:,} rows)")

    # Show top 5 by rows
    print("\n📊 TOP 5 LARGEST BY ROW COUNT:")
    sorted_by_rows = sorted(files_info, key=lambda x: x['row_count'], reverse=True)[:5]
    for i, file_info in enumerate(sorted_by_rows, 1):
        print(f"{i}. {file_info['name']} - {file_info['row_count']:,} rows ({file_info['size_formatted']})")


def save_results_to_csv(files_info, output_dir):
    import csv
    import os
    os.makedirs(output_dir, exist_ok=True)
    # Save all file details
    all_files_csv = os.path.join(output_dir, 'all_files.csv')
    with open(all_files_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['relative_path', 'name', 'size_bytes', 'size_formatted', 'row_count'])
        writer.writeheader()
        for file_info in files_info:
            writer.writerow({k: file_info[k] for k in writer.fieldnames})
    # Save top 5 by size
    top5_size = sorted(files_info, key=lambda x: x['size_bytes'], reverse=True)[:5]
    top5_size_csv = os.path.join(output_dir, 'top5_by_size.csv')
    with open(top5_size_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['relative_path', 'name', 'size_bytes', 'size_formatted', 'row_count'])
        writer.writeheader()
        for file_info in top5_size:
            writer.writerow({k: file_info[k] for k in writer.fieldnames})
    # Save top 5 by row count
    top5_rows = sorted(files_info, key=lambda x: x['row_count'], reverse=True)[:5]
    top5_rows_csv = os.path.join(output_dir, 'top5_by_row_count.csv')
    with open(top5_rows_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['relative_path', 'name', 'size_bytes', 'size_formatted', 'row_count'])
        writer.writeheader()
        for file_info in top5_rows:
            writer.writerow({k: file_info[k] for k in writer.fieldnames})
    # Save summary
    summary_csv = os.path.join(output_dir, 'summary.csv')
    with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['statistic', 'value'])
        writer.writerow(['total_files', len(files_info)])
        writer.writerow(['total_rows', sum(f['row_count'] for f in files_info)])
        if files_info:
            largest_by_size = max(files_info, key=lambda x: x['size_bytes'])
            largest_by_rows = max(files_info, key=lambda x: x['row_count'])
            writer.writerow(['largest_file_by_size', largest_by_size['relative_path']])
            writer.writerow(['largest_file_by_size_bytes', largest_by_size['size_bytes']])
            writer.writerow(['largest_file_by_row_count', largest_by_rows['relative_path']])
            writer.writerow(['largest_file_by_row_count_rows', largest_by_rows['row_count']])
    print(f"Results saved to {output_dir}")


def main():
    """Main function"""
    # Get directory to scan
    import argparse
    parser = argparse.ArgumentParser(description='Count rows in Excel files and output results to a directory.')
    parser.add_argument('directory', nargs='?', default=None, help='Directory to scan for Excel files')
    parser.add_argument('--output', '-o', default='results', help='Directory to save results (default: results)')
    args = parser.parse_args()
    directory = args.directory
    output_dir = args.output
    if not directory:
        directory = input("Enter the directory path to scan (or press Enter for current directory): ").strip()
        if not directory:
            directory = "."
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a directory.")
        return
    try:
        # Scan for Excel files
        files_info = scan_excel_files(directory)
        # Save results to CSVs
        save_results_to_csv(files_info, output_dir)
        # Display brief summary
        display_results(files_info)

    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()