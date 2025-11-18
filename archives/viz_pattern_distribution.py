"""
Pattern Distribution Visualization Script

Creates a bar chart showing the distribution of testing patterns across tasks as percentages.

Usage:
python viz_pattern_distribution.py [analysis_results.json] [output_file.png]

Example:
python viz_pattern_distribution.py test_results/enhanced_analysis.json charts/pattern_distribution.png
"""

import sys
import json
import os
from collections import Counter
import numpy as np

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("Warning: matplotlib/seaborn not available in current environment")
    print("Visualization will be skipped")
    # Still allow the script to run for testing
    import sys
    if len(sys.argv) < 3:
        print("Usage: python viz_pattern_distribution.py [analysis_results.json] [output_file.png]")
        sys.exit(1)
    print(f"Would create pattern distribution chart at: {sys.argv[2]}")
    sys.exit(0)

# Pattern colors for consistency
PATTERN_COLORS = {
    "Copy/Paste + Write + Compile": "#1f77b4",  # blue
    "Heavy Editing": "#d62728",  # red
    "Iterative Write/Compile": "#ff7f0e",  # orange
    "Write Without Running": "#9467bd",  # purple
    "Miscellaneous": "#8c564b"  # brown
}

# Define the pattern order for consistent display
PATTERN_ORDER = [
    "Copy/Paste + Write + Compile",
    "Heavy Editing", 
    "Iterative Write/Compile",
    "Write Without Running",
    "Miscellaneous"
]

def map_pattern(pattern):
    """Map original pattern names to our standardized categories."""
    pattern = pattern.lower()
    if "copy" in pattern or "paste" in pattern:
        return "Copy/Paste + Write + Compile"
    elif "heavy" in pattern or "edit" in pattern:
        return "Heavy Editing"
    elif "iterative" in pattern:
        return "Iterative Write/Compile"
    elif "without running" in pattern or "then run" in pattern or "write entire test then" in pattern:
        return "Write Without Running"
    else:
        return "Miscellaneous"

def create_pattern_distribution_plot(results, output_file):
    """Create pattern distribution by task chart showing percentages."""
    # Define task mapping
    tasks = [
        "Print Error Statement Coverage",
        "Read Statement Coverage",
        "Write Branch Coverage",
        "Read Path Coverage"
    ]
    
    # Collect patterns by task
    patterns_by_task = {task: Counter() for task in tasks}
    for task_id, task_data in results.items():
        if not str(task_id).isdigit():
            continue
            
        # Map task numbers to proper names
        task_idx = int(task_id) - 1
        task_name = tasks[task_idx]
        
        # Collect all patterns for this task
        task_patterns = []
        for user in task_data.get('users', []):
            for pattern in user.get('patterns', []):
                mapped_pattern = map_pattern(pattern['pattern'])
                task_patterns.append(mapped_pattern)
                
        if task_patterns:
            patterns_by_task[task_name].update(task_patterns)
    
    if not patterns_by_task:
        print("No patterns found in the data.")
        return
    
    # Set up the plot
    plt.style.use('default')
    
    # Create figure and axis objects
    fig, ax = plt.subplots(figsize=(20, 10))
    
    # Set font sizes
    title_fs = 32
    axis_fs = 28
    tick_fs = 24
    bar_label_fs = 22
    
    # Calculate positions for grouped bars
    x = np.arange(len(tasks)) * 3.0  # Even more spacing between task groups
    width = 0.375  # Width of individual bars
    
    # Calculate offsets to center the group of bars
    total_width = width * len(PATTERN_ORDER)
    offsets = np.linspace(-total_width/2, total_width/2, len(PATTERN_ORDER))
    
    # Plot each pattern group
    bars = []
    for i, pattern in enumerate(PATTERN_ORDER):
        percentages = []
        for task in tasks:
            total = sum(patterns_by_task[task].values())
            count = patterns_by_task[task].get(pattern, 0)
            percentage = (count / total * 100) if total > 0 else 0
            percentages.append(percentage)
            
        # Create bars for this pattern, centered within each task position
        position = x + offsets[i]
        bar = ax.bar(position, percentages, width, label=pattern,
                    color=PATTERN_COLORS.get(pattern))
        bars.append(bar)
        
        # Add value labels above bars
        for j, rect in enumerate(bar):
            height = rect.get_height()
            if height > 0:  # Only show label if there's a value
                label_y = height + max(1, 55 * 0.02)  # Add small offset
                ax.text(rect.get_x() + rect.get_width() / 2, label_y,
                       f'{int(height)}', ha='center', va='bottom',
                       fontsize=bar_label_fs, clip_on=False)
    
    # Set title and labels with specified font sizes
    ax.set_title('Testing Pattern Distribution by Task (Percentage)', 
                fontsize=title_fs, fontweight='bold', pad=20)
    ax.set_xlabel('Task', fontsize=axis_fs)
    ax.set_ylabel('Percentage (%)', fontsize=axis_fs)
    
    # Adjust x-axis and y-axis ticks
    ax.set_xticks(x)  # Center tick marks under groups
    # Use short captions 'Task 1'..'Task 4' centered and horizontal as requested
    caption_labels = [f"Task {i+1}" for i in range(len(tasks))]
    ax.set_xticklabels(caption_labels, rotation=0, ha='center', fontsize=tick_fs)
    ax.tick_params(axis='y', labelsize=tick_fs)
    
    # Add legend to the right with larger font
    ax.legend(title="Pattern", bbox_to_anchor=(1.05, 1), loc='upper left',
             fontsize=tick_fs, title_fontsize=axis_fs)
    
    # Set y-axis limit and add grid
    ax.set_ylim(0, 55 * 1.12)  # Add 12% headroom for labels
    ax.grid(axis='y', alpha=0.25)

    # Add a caption below the plot that maps Task 1..4 to the full task names
    caption_fs = 26
    caption_lines = [f"Task {i+1}: {tasks[i]}" for i in range(len(tasks))]
    # Join with two spaces for separation so it reads as a single caption line
    caption_text = "   ".join(caption_lines)
    # Adjust layout to make room for the caption and legend
    plt.tight_layout()
    try:
        # leave more bottom space for the caption and move legend area to the right
        fig.subplots_adjust(bottom=0.2, right=0.82)
    except Exception:
        pass

    # Place the caption centered below the axes
    fig.text(0.5, 0.04, caption_text, ha='center', va='top', fontsize=caption_fs)
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Pattern distribution chart saved to {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python viz_pattern_distribution.py [analysis_results.json] [output_file.png]")
        print("Example: python viz_pattern_distribution.py results.json pattern_distribution.png")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(json_file):
        print(f"Error: Input file {json_file} not found.")
        sys.exit(1)
    
    try:
        with open(json_file, 'r') as f:
            results = json.load(f)
        
        create_pattern_distribution_plot(results, output_file)
        
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
