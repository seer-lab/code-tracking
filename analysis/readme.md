# Analysis Scripts for Code Tracking Study

This folder contains scripts for analyzing user code tracking data, including keystrokes, copy/paste actions, code changes, and task tracking. The scripts are designed to process raw study data and produce clean, organized results for further analysis.

## Quick Start: Run All Analyses

To run all analysis scripts in the correct order, use the master script:

```
python run_all_analyses.py
```

This will process the data in `study_data/` and output results to the appropriate subfolders in `results/`.

## Script Overview

- **count_csv_lines.py**: Counts lines in all CSV files in the study data.
- **count_execute_events.py**: Analyzes code execution events.
- **count_writing_and_copy_paste.py**: Logs keystrokes and copy/cut/paste actions, with per-user and per-task breakdowns.
- **count_xlsx_lines.py**: Counts lines in all XLSX files in the study data.
- **extract_code.py**: Extracts code fragments from the study data.
- **merge_csv_data.py**: Merges multiple CSV data files into a unified dataset.
- **prepare_data.py**: Prepares and cleans the merged data for further analysis.
- **tasktracker.py**: Analyzes task tracking data.
- **tasktracker_actions.py**: Analyzes user actions related to task tracking.
- **tasktracker_states.py**: Analyzes user state changes related to task tracking.

## Output Structure

All results are written to the `results/` directory, with each script creating its own subfolder. For example:

```
results/
    csv_line_counts/
    execute_events/
    write_copy_paste/
    xlsx_line_counts/
    extracted_code/
    merged_data/
    prepared_data/
    tasktracker/
    tasktracker_actions/
    tasktracker_states/
```

Each subfolder contains CSV files and summaries relevant to that analysis.

## Notes
- The `analysis/study_data/` and `analysis/results/` folders are ignored by Git (see .gitignore).
- You can run individual scripts manually if you wish, but the master script is recommended for consistency.
- Make sure you have all required Python dependencies installed (see requirements.txt).
