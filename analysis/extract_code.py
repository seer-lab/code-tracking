"""
CSV Code Extractor

This script extracts Python code fragments from CSV files containing code activity data.
It processes CSV files to find code fragments, cleans them by removing comments and
empty lines, and saves the extracted code as individual Python files with appropriate naming.

Usage:
python extract_code_from_csv.py [input_directory] [--output-dir output_directory]
"""

import os
import csv
import re
import argparse


def extract_code_from_csv(csv_path):
    """
    Extract code fragments from a CSV file.

    Args:
        csv_path (str): Path to the CSV file to process

    Returns:
        tuple: (output_filename, cleaned_code) or (None, None) if no code found
    """
    try:
        # Open and read the CSV file
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            rows = list(csv.DictReader(csvfile))

            # Filter rows that contain code fragments with the target comment
            code_rows = [row['fragment'] for row in rows
                         if 'fragment' in row and row['fragment'] and '# Write your code here' in row['fragment']]

            # Return None if no code fragments found
            if not code_rows:
                return None, None

            # Process the last (most recent) code fragment
            # Remove comments and clean up the code
            code = '\n'.join(
                line.split('#')[0].rstrip()  # Remove comments and trailing whitespace
                for line in code_rows[-1].split('\n')
                # Keep lines that aren't pure comments (except the target comment)
                if not (line.strip().startswith('#') and "# Write your code here" not in line)
            )

            # Replace multiple consecutive newlines with double newlines
            code = re.sub(r'\n{3,}', '\n\n', code)

            # Generate output filename with 'test_' prefix using first 3 parts of CSV filename
            output_filename = 'test_' + '_'.join(os.path.basename(csv_path).split('_')[:3]) + '.py'

            return output_filename, code

    except Exception as e:
        print(f"Error processing {csv_path}: {e}")
        return None, None


def get_user_id(csv_path):
    """
    Extract user ID from the CSV file path or contents.

    Args:
        csv_path (str): Path to the CSV file

    Returns:
        str: User ID string or "unknown_user" if not found
    """
    # First try to find user ID in the file path
    for part in csv_path.split(os.sep):
        if part.startswith('user_'):
            return part

    # If not in path, try to find it in the CSV contents
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            for row in csv.DictReader(csvfile):
                if 'userId' in row and row['userId']:
                    return f"user_{row['userId']}"
    except:
        pass

    return "unknown_user"


def save_code(output_dir, csv_path, user_id, output_filename, code):
    """
    Save the extracted code to a Python file.

    Args:
        output_dir (str): Base output directory (optional)
        csv_path (str): Original CSV file path
        user_id (str): User identifier
        output_filename (str): Name for the output Python file
        code (str): Code content to save
    """
    # Determine output path based on whether output_dir is specified
    if output_dir:
        output_path = os.path.join(output_dir, user_id, output_filename)
    else:
        output_path = os.path.join(os.path.dirname(csv_path), output_filename)

    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write the code to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"Extracted from {csv_path} and saved to {output_path}")


def process_directory(directory_path, output_dir=None):
    """
    Process all CSV files in a directory and extract code from them.

    Args:
        directory_path (str): Root directory to search for CSV files
        output_dir (str, optional): Directory to save extracted Python files
    """
    # Check if the input directory exists
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")
        return

    # Find all CSV files in the directory and subdirectories
    csv_files = [os.path.join(root, file)
                 for root, _, files in os.walk(directory_path)
                 for file in files if file.endswith('.csv')]

    print(f"Found {len(csv_files)} CSV files.")

    # Process each CSV file
    for csv_path in csv_files:
        output_filename, code = extract_code_from_csv(csv_path)

        if code:
            user_id = get_user_id(csv_path)
            save_code(output_dir, csv_path, user_id, output_filename, code)
        else:
            print(f"No code found in {csv_path}")


if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Extract Python code from CSV files.')
    parser.add_argument('directory', type=str,
                        help='Root directory containing the CSV files')
    parser.add_argument('--output-dir', type=str,
                        help='Directory to save the extracted Python files (optional)')

    # Parse arguments and run the main processing function
    args = parser.parse_args()
    process_directory(args.directory, args.output_dir)
    print("Extraction completed.")