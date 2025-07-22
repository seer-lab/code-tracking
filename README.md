# Code Tracking Research Project

This repository contains a comprehensive toolkit for collecting, processing, and analyzing student coding behavior data during programming problem-solving sessions. The project is designed to support research in computing education and automated hint generation systems.

## Project Overview

This research project combines data collection tools with advanced analysis capabilities to understand how students approach programming problems, particularly focusing on testing patterns and coding behaviors. The collected data can be used to:

- Analyze programming patterns and student learning progression
- Generate automated hints for problem-solving
- Study software testing behaviors in educational contexts
- Understand coding strategies across different programming tasks

## Repository Structure

### 📱 TaskTracker Plugin (`task-tracker-plugin/`)
An IntelliJ-based IDE plugin for tracking code changes during programming problem-solving sessions.

**Source**: Based on [JetBrains-Research/task-tracker-plugin](https://github.com/JetBrains-Research/task-tracker-plugin)

**Features**:
- Tracks code changes in real-time during problem solving
- Supports multiple programming languages
- Privacy-focused data collection (only tracks plugin-created files)
- Available in English and Russian

### 🖥️ TaskTracker Server (`task-tracker-server/`)
A Node.js server that facilitates interaction with the TaskTracker plugin and manages data collection.

**Source**: Based on [JetBrains-Research/task-tracker-server](https://github.com/JetBrains-Research/task-tracker-server)

**Features**:
- RESTful API for plugin communication
- MongoDB integration for data storage
- User management and task distribution
- Data export and processing capabilities

### 📊 Analysis Toolkit (`analysis/`)
A comprehensive suite of Python scripts for analyzing collected coding behavior data.

**Features**:
- Testing pattern analysis with per-user and per-task reporting
- Data visualization tools for various metrics
- Pattern diversity scoring and cross-task analysis
- Modular visualization system with individual chart generation

## Getting Started

### Prerequisites

- **Java 11+** (for TaskTracker plugin)
- **Node.js and npm** (for TaskTracker server)
- **MongoDB** (for data storage)
- **Python 3.7+** (for analysis scripts)

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/seer-lab/code-tracking.git
   cd code-tracking
   ```

2. **Set up the server**:
   ```bash
   cd task-tracker-server
   npm install
   # Ensure MongoDB is running on localhost:27017
   npm start
   ```

3. **Build the plugin**:
   ```bash
   cd task-tracker-plugin
   ./gradlew build shadowJar
   ```

4. **Install analysis dependencies**:
   ```bash
   cd analysis
   pip install -r requirements.txt
   ```

## Usage

### Data Collection
1. Install the built plugin in IntelliJ IDEA
2. Start the TaskTracker server
3. Use the plugin to solve programming problems
4. Data is automatically collected and stored

### Data Analysis
1. Export data from the server
2. Use the preparation scripts to process raw data
3. Run analysis scripts to generate insights and visualizations

```bash
cd analysis
python prepare_data.py [raw_data_folder] [output_folder]
python analyze_testing_patterns.py [prepared_data_folder]
python generate_all_visualizations.py [analysis_results_folder]
```

## Research Applications

This toolkit has been used in research focusing on:
- **Automated Hint Generation**: Understanding student coding patterns to provide personalized assistance
- **Testing Behavior Analysis**: Studying how students approach software testing
- **Learning Pattern Recognition**: Identifying effective problem-solving strategies
- **Educational Tool Development**: Creating data-driven educational interventions

## Attribution

This project builds upon the excellent work from JetBrains Research:

- **TaskTracker Plugin**: Originally developed by [JetBrains-Research/task-tracker-plugin](https://github.com/JetBrains-Research/task-tracker-plugin)
- **TaskTracker Server**: Originally developed by [JetBrains-Research/task-tracker-server](https://github.com/JetBrains-Research/task-tracker-server)

The analysis toolkit is an original contribution by the SEER Lab at Ontario Tech University.