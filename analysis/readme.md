# IDE Usage Analysis Scripts

This repository contains scripts for analyzing IDE usage data collected through KOALA (JetBrains Research's updated IDE tracking system). The analysis focuses on user behavior patterns, action frequencies, and state transitions during coding sessions.

## Overview

The analysis toolkit consists of:
1. **Data Preparation** (`prepare_data.py`) - Processes raw KOALA data files  
2. **Action Analysis** (`tasktracker_actions_count.py`) - Counts IDE action frequencies
3. **State Analysis** (`tasktracker_states.py`) - Analyzes IDE state durations and transitions

## Key Features

### Comprehensive Data Processing
- **Batch processing** of entire user study datasets
- **Hierarchical organization** by user and task
- **Flexible input handling** for single files or complete directory structures
- **Multiple output formats** for different analysis needs

### Action Analysis
- **Frequency counting** of all IDE actions (typing, navigation, debugging, etc.)
- **Hierarchical summaries** at combined, user, and task levels
- **Sorted output** by frequency for easy pattern identification

### State Analysis  
- **Duration tracking** for Active, Inactive, and NoProject states
- **Session grouping** that combines consecutive identical states
- **Temporal analysis** with detailed start/end timestamps

## Scripts

### 1. Data Preparation Script (`prepare_data.py`)

Processes raw KOALA data files and creates standardized versions for analysis.

#### Usage
```bash
# Standard processing
python prepare_data.py [raw_data_folder] [output_folder]

# With IDE events compression (reduces file size by grouping consecutive identical events)
python prepare_data.py [raw_data_folder] [output_folder] --compress-ide-events
```

#### What it does
- Reads CSV files containing IDE events and code changes from KOALA
- Standardizes data formats and timestamps
- Creates per-user and per-task files for targeted analysis
- Combines all data into aggregate files for cross-user analysis
- **Optional**: Compresses consecutive identical IDE events to reduce file size

#### Input Structure
Expects directory structure:
```
raw_data/
├── user_24/
│   ├── 1/
│   │   ├── ide-events-file.csv
│   │   └── code-changes.csv
│   └── 2/
│       └── ide-events-file.csv
└── user_25/
    └── 1/
        └── ide-events-file.csv
```

### 2. Action Analysis Script (`tasktracker_actions_count.py`)

Analyzes IDE action frequencies across users and tasks.

#### Usage
```bash
# Single file analysis
python tasktracker_actions_count.py [ide_events_file.csv] [output_folder]

# Batch analysis
python tasktracker_actions_count.py [study_data_folder] [output_folder]
```

#### What it does
- Counts occurrences of each IDE action (defined in `tasktracker_actions.py`)
- Generates frequency reports at multiple levels:
  - **Combined**: Total counts across all users and tasks
  - **By User**: Individual user summaries across all their tasks  
  - **By Task**: Individual task summaries organized by user

#### Output Structure
```
output_folder/
├── combined_action_counts.csv          # Overall totals
├── by_user/
│   ├── user_24_action_counts.csv       # All tasks for user_24
│   └── user_25_action_counts.csv       # All tasks for user_25
└── by_task/
    ├── user_24/
    │   ├── user_24_1_action_counts.csv # Specific user/task combinations
    │   └── user_24_2_action_counts.csv
    └── user_25/
        └── user_25_1_action_counts.csv
```

### 3. State Analysis Script (`tasktracker_states.py`)

Analyzes IDE state durations and transitions between Active, Inactive, and NoProject states.

#### Usage
```bash
# Single file analysis  
python tasktracker_states.py [ide_events_file.csv] [output_folder]

# Batch analysis
python tasktracker_states.py [study_data_folder] [output_folder]
```

#### What it does
- Tracks time spent in each IDE state
- Groups consecutive identical states into meaningful sessions
- Generates two types of analysis:
  - **State Totals**: Cumulative time spent in each state
  - **State Sessions**: Individual state transition records with durations

#### State Detection Logic
- **Explicit States**: When Column 1 = "IdeState", Column 2 contains state name
- **Implicit Active**: When Column 1 = "Action", assumes "Active" state (user performing IDE action)
- **Session Grouping**: Consecutive periods in the same state are combined into single sessions

#### Output Files
- `*_state_totals.csv` - Cumulative time analysis (State, Total_Seconds, Total_Minutes, Total_Hours)
- `*_state_sessions.csv` - Individual session records (Start_Time, End_Time, State, Duration, User, Task)

## KOALA Data Format

### Expected CSV Structure
KOALA generates CSV files with the following structure:
- **Column 0**: Timestamp
- **Column 1**: Event Type ("IdeState" or "Action")  
- **Column 2**: State name (Active/Inactive/NoProject) or Action name
- **Column 3**: Context information (optional)
- **Column 4**: Additional metadata (optional)

### State Definitions
- **Active**: User actively working in the IDE (explicitly marked or performing actions)
- **Inactive**: IDE open but user not actively working
- **NoProject**: No project loaded in the IDE

## Dependencies

### Required
- Python 3.6+
- Standard library modules: `csv`, `glob`, `os`, `sys`, `collections`, `datetime`

### Configuration Files
- `tasktracker_actions.py` - Contains list of IDE actions to count
- `tasktracker.states` - Contains list of IDE states to track (if using external module)

## Usage Examples

### Complete Analysis Workflow
```bash
# Step 1: Prepare raw KOALA data
python prepare_data.py raw_koala_data/ prepared_data/

# Step 2: Analyze action frequencies  
python tasktracker_actions_count.py prepared_data/ action_results/

# Step 3: Analyze state transitions
python tasktracker_states.py prepared_data/ state_results/
```

### Quick Analysis (if data already prepared)
```bash
python tasktracker_actions_count.py prepared_data/ quick_actions/
python tasktracker_states.py prepared_data/ quick_states/
```

### Single User Analysis
```bash
python tasktracker_actions_count.py prepared_data/user_24/user_24_task1_ide_events.csv single_user_results/
```

## Output Analysis

### Action Analysis Results
- **High-frequency actions**: Indicate primary IDE usage patterns
- **User variations**: Different coding/debugging approaches
- **Task differences**: How task complexity affects IDE usage

### State Analysis Results  
- **Active time**: Actual engagement duration per user/task
- **Session patterns**: Work rhythm and break frequency
- **State transitions**: Task engagement and disengagement patterns

### Comparative Analysis
- **Cross-user comparisons**: Identify different working styles
- **Task complexity indicators**: Actions and states that suggest difficulty
- **Temporal patterns**: How usage changes throughout study sessions

## Study Transition Notes

### From Legacy TaskTracker to KOALA
- **Improved data quality**: KOALA provides more reliable event capture
- **Enhanced state tracking**: Better distinction between active/inactive periods  
- **Consistent formatting**: More predictable CSV structure
- **Reduced data corruption**: More stable event logging

### Backward Compatibility
These scripts are designed to work with KOALA data format while maintaining compatibility with analysis approaches from the original study.

## Troubleshooting

### Common Issues

1. **No user folders found**
   ```
   Found 0 user folders
   ```
   **Solution**: Ensure directory structure matches expected format (user_*/task_*/)

2. **No IDE event files found**
   ```
   Found 0 IDE event files
   ```
   **Solution**: Verify files contain "ide-events" in filename and have .csv extension

3. **Missing configuration files**
   ```
   ModuleNotFoundError: No module named 'tasktracker_actions'
   ```
   **Solution**: Ensure `tasktracker_actions.py` exists with proper `actions` list

### Performance Considerations
- Large datasets (100,000+ events) may take several minutes to process
- State analysis is more computationally intensive than action counting
- Batch processing scales linearly with number of users and tasks

### Data Quality
- KOALA provides more consistent timestamps than legacy TaskTracker
- Fewer missing or corrupted events expected
- State transitions should be more reliable and complete

## Future Enhancements

Potential additions for advanced analysis:
- Statistical significance testing between user groups
- Temporal pattern analysis (time-of-day effects)
- Learning progression tracking across tasks
- Integration with code quality metrics