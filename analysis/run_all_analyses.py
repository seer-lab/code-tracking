import subprocess
import sys
import os

# Paths to analysis scripts (relative to this script's location)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = [
    ('count_csv_lines.py', ['study_data', 'results/csv_line_counts']),
    ('count_execute_events.py', ['study_data', 'results/execute_events']),
    ('count_writing_and_copy_paste.py', ['study_data', 'results/write_copy_paste']),
    ('count_xlsx_lines.py', ['study_data', 'results/xlsx_line_counts']),
    ('extract_code.py', ['study_data', 'results/extracted_code']),
    ('merge_csv_data.py', ['study_data', 'results/merged_data']),
    ('prepare_data.py', ['study_data', 'results/prepared_data']),
    ('tasktracker.py', ['study_data', 'results/tasktracker']),
    ('tasktracker_actions.py', ['study_data', 'results/tasktracker_actions']),
    ('tasktracker_states.py', ['study_data', 'results/tasktracker_states']),
]

def run_script(script, args):
    script_path = os.path.join(SCRIPT_DIR, script)
    cmd = [sys.executable, script_path] + args
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Script {script} failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def main():
    for script, args in SCRIPTS:
        run_script(script, args)
    print("\nAll analysis scripts completed successfully.")

if __name__ == "__main__":
    main()

