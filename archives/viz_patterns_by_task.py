"""
Patterns by Task Visualization Script

Creates a grouped bar chart showing how pattern distribution varies by task.

Usage:
python viz_patterns_by_task.py [analysis_results.json] [output_file.png]

Example:
python viz_patterns_by_task.py test_results/enhanced_analysis.json charts/patterns_by_task.png
"""

import sys
import json
import os
from collections import Counter

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
except ImportError:
    print("Warning: visualization libraries not available")
    import sys
    if len(sys.argv) >= 3: 
        print(f"Would create chart at: {sys.argv[2]}")
    sys.exit(0)

# Task names for better labeling
TASK_NAMES = {
    "1": "Print Error Statement Coverage",
    "2": "Read Statement Coverage", 
    "3": "Write Branch Coverage",
    "4": "Read Path Coverage"
}

def create_pattern_by_task_plot(results, output_file):
    """Create pattern distribution by task chart."""
    # Prepare data
    task_pattern_data = {}
    all_patterns = set()
    
    for task_id, task_data in results.items():
        task_name = TASK_NAMES.get(task_id, f'Task {task_id}')
        patterns = [p['pattern'] for user in task_data.get('users', []) for p in user.get('patterns', [])]
        task_pattern_data[task_name] = Counter(patterns)
        all_patterns.update(patterns)
    
    if not all_patterns:
        print("No patterns found in the data.")
        return
    
    # Set up the plot
    plt.style.use('default')
    sns.set_palette("deep")
    sns.set_context("talk")
    
    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(14, 8))
    
    patterns = sorted(all_patterns)
    x = np.arange(len(patterns))
    width = 0.15
    
    task_names = list(task_pattern_data.keys())
    for i, task_name in enumerate(task_names):
        counts = [task_pattern_data[task_name].get(pattern, 0) for pattern in patterns]
        bars = ax.bar(x + i * width, counts, width, label=task_name)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{int(height)}', ha='center', va='bottom', fontsize=8)
    
    ax.set_title('Testing Patterns by Task', fontsize=16, fontweight='bold')
    ax.set_xlabel('Testing Pattern', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_xticks(x + width * (len(task_names) - 1) / 2)
    ax.set_xticklabels(patterns, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Patterns by task chart saved to {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python viz_patterns_by_task.py [analysis_results.json] [output_file.png]")
        print("Example: python viz_patterns_by_task.py results.json patterns_by_task.png")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(json_file):
        print(f"Error: Input file {json_file} not found.")
        sys.exit(1)
    
    try:
        with open(json_file, 'r') as f:
            results = json.load(f)
        
        create_pattern_by_task_plot(results, output_file)
        
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
