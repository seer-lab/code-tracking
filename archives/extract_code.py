import os
import csv
import re
import argparse

def extract_code_from_csv(csv_path):
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            rows = list(csv.DictReader(csvfile))
            code_rows = [row['fragment'] for row in rows if 'fragment' in row and row['fragment'] and '# Write your code here' in row['fragment']]
            if not code_rows:
                return None, None

            code = '\n'.join(
                line.split('#')[0].rstrip()
                for line in code_rows[-1].split('\n')
                if not (line.strip().startswith('#') and "# Write your code here" not in line)
            )
            code = re.sub(r'\n{3,}', '\n\n', code)
            # Add 'test_' prefix to the output filename
            output_filename = 'test_' + '_'.join(os.path.basename(csv_path).split('_')[:3]) + '.py'
            return output_filename, code
    except Exception as e:
        print(f"Error processing {csv_path}: {e}")
        return None, None

def get_user_id(csv_path):
    for part in csv_path.split(os.sep):
        if part.startswith('user_'):
            return part
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            for row in csv.DictReader(csvfile):
                if 'userId' in row and row['userId']:
                    return f"user_{row['userId']}"
    except:
        pass
    return "unknown_user"

def save_code(output_dir, csv_path, user_id, output_filename, code):
    output_path = os.path.join(output_dir, user_id, output_filename) if output_dir else os.path.join(os.path.dirname(csv_path), output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"Extracted from {csv_path} and saved to {output_path}")

def process_directory(directory_path, output_dir=None):
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")
        return

    csv_files = [os.path.join(root, file) for root, _, files in os.walk(directory_path) for file in files if file.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files.")

    for csv_path in csv_files:
        output_filename, code = extract_code_from_csv(csv_path)
        if code:
            user_id = get_user_id(csv_path)
            save_code(output_dir, csv_path, user_id, output_filename, code)
        else:
            print(f"No code found in {csv_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract Python code from CSV files.')
    parser.add_argument('directory', type=str, help='Root directory containing the CSV files')
    parser.add_argument('--output-dir', type=str, help='Directory to save the extracted Python files (optional)')
    args = parser.parse_args()
    process_directory(args.directory, args.output_dir)
    print("Extraction completed.")