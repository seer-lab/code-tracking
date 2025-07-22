# Testing Pattern Analysis Scripts

This repository contains scripts for analyzing student testing patterns from IDE events and code changes data. The analysis helps identify how students approach software testing through their coding and testing behaviors.

## Overview

The analysis toolkit consists of:
1. **Data Preparation** (`prepare_data.py`) - Processes raw data files  
2. **Enhanced Pattern Analysis** (`analyze_testing_patterns.py`) - Analyzes testing patterns with comprehensive per-user/per-task reporting
3. **Individual Visualization Scripts** (`viz_*.py`) - Generate specific charts and plots
4. **Batch Visualization** (`generate_all_visualizations.py`) - Creates all visualizations at once

## Key Features

### Enhanced Analysis Capabilities
- **Detailed per-user pattern analysis** across all tasks
- **Individual user reports** with pattern breakdowns
- **Task comparison analysis** with complexity metrics
- **Pattern diversity scoring** for each user
- **Cross-task pattern analysis** showing learning progression
- **Automatic visualization generation** using modular external scripts

### Modular Visualization System
- **Separation of Concerns**: Analysis and visualization are separate
- **Individual Script Usage**: Generate only the charts you need
- **Easy Maintenance**: Update individual visualization scripts independently
- **Flexible Deployment**: Analysis can run without visualization dependencies

## Scripts

### 1. Data Preparation Script (`prepare_data.py`)

This script processes raw data files and creates standardized versions for analysis.

#### Usage
```bash
# Standard processing
python prepare_data.py [raw_data_folder] [output_folder]

# With IDE events compression (reduces file size)
python prepare_data.py [raw_data_folder] [output_folder] --compress-ide-events
```

#### What it does
- Reads CSV files containing IDE events and code changes
- Standardizes data formats and time stamps
- Creates per-user and per-task files for analysis
- Combines all data into aggregate files
- **Optional**: Compresses consecutive identical IDE events to reduce file size

### 2. Enhanced Pattern Analyzer Script (`analyze_testing_patterns.py`)

This script analyzes the prepared data to identify testing patterns with comprehensive reporting and automatic visualization generation.

#### Usage
```bash
python analyze_testing_patterns.py [prepared_data_folder] [output_base_filename]
```

#### What it does
- Reads standardized data files
- Groups events into sessions based on time gaps
- Identifies exactly one testing pattern for each session
- Calculates detailed metrics per user and task
- Generates comprehensive CSV reports and JSON data
- **Automatically runs visualization scripts** if available

### 3. Code Extraction Script (`extract_code.py`)

Utility script for extracting and processing code fragments from the analysis data.

### 4. Individual Visualization Scripts

Each visualization is now a separate, standalone script that can be run independently:

#### `viz_pattern_distribution.py`
Creates a bar chart showing overall pattern frequency across all tasks.

```bash
python viz_pattern_distribution.py [analysis_results.json] [output_file.png]
```

#### `viz_patterns_by_task.py`
Creates a grouped bar chart comparing pattern usage across different tasks.

```bash
python viz_patterns_by_task.py [analysis_results.json] [output_file.png]
```

#### `viz_active_time_by_task.py`
Shows average active time spent on each task.

```bash
python viz_active_time_by_task.py [analysis_results.json] [output_file.png]
```

#### `viz_user_pattern_diversity.py`
Displays the number of unique patterns each user employs.

```bash
python viz_user_pattern_diversity.py [analysis_results.json] [output_file.png]
```

#### `viz_pattern_duration.py`
Creates box plots showing duration distributions for each pattern.

```bash
python viz_pattern_duration.py [analysis_results.json] [output_file.png]
```

#### `viz_user_activity_heatmap.py`
Generates a heatmap showing user engagement across tasks.

```bash
python viz_user_activity_heatmap.py [analysis_results.json] [output_file.png]
```

### 5. Batch Visualization Generator (`generate_all_visualizations.py`)

Runs all visualization scripts automatically to create a complete set of charts.

#### Usage
```bash
python generate_all_visualizations.py [analysis_results.json] [output_directory]
```

#### Example
```bash
python generate_all_visualizations.py test_results/enhanced_analysis.json charts/
```

## Testing Patterns Classification

### Pattern Categories

#### Primary Patterns (in order of complexity):

1. **Copy/paste + write + compile** - Using external code, modifying, and testing
2. **Iterative write/compile** - Frequent write-test cycles
3. **Write entire test then compile and run** - Substantial coding before testing
4. **Heavy editing** - Extensive code modification
5. **Run with minimal changes** - Testing with little modification
6. **Write without running** - Focus on code creation
7. **Read only** - Code navigation and browsing

### Session Definition

A "session" is defined as a continuous period of activity where the time between consecutive events does not exceed 10 seconds. Sessions must be at least 5 seconds long to be considered for analysis.

### Pattern Interpretation Guide

#### High-Value Patterns
- **Copy/paste + write + compile**: Indicates resourcefulness and iterative refinement
- **Iterative write/compile**: Shows test-driven development approach
- **Write entire test then compile**: Suggests planning and structured thinking

#### Concerning Patterns
- **Read only**: May indicate confusion or lack of engagement
- **Write without running**: Could suggest lack of testing awareness

#### Task-Specific Insights
- **Task 1** (Print Error Statement Coverage): Often shows exploratory patterns
- **Task 2** (Read Statement Coverage): Typically more iterative approaches
- **Task 3** (Write Branch Coverage): Usually requires more planning patterns
- **Task 4** (Read Path Coverage): Often shows advanced testing patterns

### Duration Analysis
Pattern duration analysis reveals:
- **Quick patterns** (< 30 seconds): Often navigational or simple edits
- **Medium patterns** (30 seconds - 5 minutes): Typical coding/testing cycles
- **Long patterns** (> 5 minutes): Deep work or complex problem-solving

### Diversity Scoring
User pattern diversity indicates:
- **Low diversity (1-2 patterns)**: Consistent but potentially limited approach
- **Medium diversity (3-4 patterns)**: Balanced and adaptive strategy
- **High diversity (5+ patterns)**: Highly adaptive, possibly exploratory

## Usage Examples

### Complete Analysis Workflow
```bash
# Step 1: Prepare data (if starting from raw files)
python prepare_data.py raw_data/ prepared_data/

# Step 2: Run enhanced analysis
python analyze_testing_patterns.py prepared_data/ results/analysis

# Step 3: Generate all visualizations (done automatically, or manually)
python generate_all_visualizations.py results/analysis.json charts/
```

### Individual Visualization Generation
```bash
# Generate just the pattern distribution chart
python viz_pattern_distribution.py results/analysis.json charts/patterns.png

# Generate user activity heatmap
python viz_user_activity_heatmap.py results/analysis.json charts/heatmap.png
```

### Quick Analysis (if data already prepared)
```bash
python analyze_testing_patterns.py output/ results/quick_analysis
```

## Requirements

### Python Version
- Python 3.6 or higher

### Core Dependencies (always required)
- Standard library modules: `csv`, `json`, `datetime`, `glob`, `collections`, `os`, `sys`

### Visualization Dependencies (optional)
```bash
pip install matplotlib seaborn pandas numpy
```

Or install from requirements file:
```bash
pip install -r requirements.txt
```

**Note**: The analysis script will work without visualization libraries, but charts won't be generated. Individual visualization scripts require these packages.

## Output Files

### Core Analysis Files
- `*_summary.csv` - Overall statistics per task
- `*_patterns.csv` - Pattern frequency per task  
- `*_task*_users.csv` - User details per task
- `*_task*_pattern_details.csv` - Individual pattern instances
- `*.json` - Complete results in JSON format

### Enhanced Reports
- `*_user_task_patterns.csv` - Detailed matrix of all users and tasks with pattern breakdowns
- `*_task_comparison.csv` - Comparative analysis across tasks
- `*_user_reports/user_*_summary.csv` - Individual reports for each user across all tasks

### Visualizations
- `*_visualizations/pattern_distribution.png` - Overall pattern frequency chart
- `*_visualizations/patterns_by_task.png` - Pattern comparison across tasks
- `*_visualizations/active_time_by_task.png` - Time spent per task
- `*_visualizations/user_pattern_diversity.png` - Pattern variety per user
- `*_visualizations/pattern_duration.png` - Duration analysis box plots
- `*_visualizations/user_activity_heatmap.png` - User engagement matrix

## Key Advantages of This Approach

### Modular Design
- **Separation of Concerns**: Analysis and visualization are separate
- **Individual Script Usage**: Generate only the charts you need
- **Easy Maintenance**: Update individual visualization scripts independently
- **Flexible Deployment**: Analysis can run without visualization dependencies

### Enhanced Analysis
- **Comprehensive Reporting**: Multiple output formats for different analysis needs
- **Per-User Insights**: Individual user pattern summaries across all tasks
- **Cross-Task Analysis**: Understanding pattern evolution and consistency
- **Statistical Depth**: Pattern diversity, duration analysis, and comparative metrics

### Practical Benefits
- **Scalable**: Handle large datasets efficiently
- **Extensible**: Easy to add new visualization types
- **Robust**: Analysis continues even if visualization libraries are missing
- **User-Friendly**: Clear documentation and example usage for all scripts

## Advanced Analysis Features

### Pattern Sequences
The enhanced analysis tracks pattern transitions within users, helping identify:
- Learning progression across tasks
- Strategic changes in approach
- Consistent approaches vs. adaptive behavior

### Enhanced Metrics

#### Per User Metrics
- **Pattern Count**: Total number of testing patterns identified
- **Pattern Diversity**: Number of unique pattern types used
- **Dominant Pattern**: Most frequently used testing approach
- **Active Time**: Time spent actively coding/testing
- **Session Count**: Number of distinct work sessions

#### Per Task Metrics
- **User Participation**: How many users attempted the task
- **Average Patterns**: Typical number of patterns per user
- **Pattern Diversity Score**: Variety of approaches used
- **Most Common Pattern**: Dominant testing strategy for the task
- **Average Active Time**: Typical time investment

#### Cross-Analysis
- **User Consistency**: Whether users employ similar patterns across tasks
- **Task Complexity Indicators**: Patterns that suggest task difficulty
- **Learning Progression**: Changes in pattern usage across task sequence

## Customization

### Adding New Patterns
To add new pattern detection:
1. Modify the `identify_pattern()` function in `analyze_testing_patterns.py`
2. Add pattern to `PATTERN_COLORS` dictionary
3. Update documentation

### Modifying Visualizations
Each visualization script can be run independently and modified:
- `viz_pattern_distribution.py` - Overall pattern frequency
- `viz_patterns_by_task.py` - Task comparison charts
- `viz_active_time_by_task.py` - Time analysis
- `viz_user_pattern_diversity.py` - User diversity analysis
- `viz_pattern_duration.py` - Duration box plots
- `viz_user_activity_heatmap.py` - User engagement heatmap

## Troubleshooting

### Common Issues

1. **Missing visualization libraries**
   ```
   Error: Required packages not installed
   ```
   **Solution**: Install with `pip install matplotlib seaborn pandas numpy`

2. **No data files found**
   ```
   No IDE events file found for user_X, task Y
   ```
   **Solution**: Ensure data was properly prepared with `prepare_data.py`

3. **Visualization scripts not found**
   ```
   Warning: generate_all_visualizations.py not found
   ```
   **Solution**: Ensure all `viz_*.py` scripts are in the same directory

### Performance Tips
- Large datasets (>50 users) may take several minutes to process
- Visualization generation adds 30-60 seconds per chart
- Use individual visualization scripts for faster generation of specific charts
- Individual user reports scale with number of users

### Future Enhancements

Potential additions for advanced analysis:
- Time-series analysis of pattern evolution
- Statistical significance testing between groups
- Machine learning clustering of user behavior
- Export to interactive dashboard formats