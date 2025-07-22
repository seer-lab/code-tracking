"""
Active Time by Task Visualization Script

Creates a bar chart showing average active time spent on each task.

Usage:
python viz_active_time_by_task.py [analysis_results.json] [output_file.png]

Example:
python viz_active_time_by_task.py test_results/enhanced_analysis.json charts/active_time_by_task.png
"""

import sys
import json
import os

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
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

def create_active_time_by_task_plot(results, output_file):
    """Create active time by task chart."""
    task_names = []
    avg_times = []
    
    for task_id, task_data in results.items():
        task_name = TASK_NAMES.get(task_id, f'Task {task_id}')
        users = task_data.get('users', [])
        
        if users:
            avg_time = sum(user.get('active_time_seconds', 0) for user in users) / len(users) / 60
            task_names.append(task_name)
            avg_times.append(avg_time)
    
    if not task_names:
        print("No task data found.")
        return
    
    # Set up the plot
    plt.style.use('default')
    sns.set_palette("deep")
    sns.set_context("talk")
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(task_names, avg_times, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    
    plt.title('Average Active Time by Task', fontsize=16, fontweight='bold')
    plt.xlabel('Task', fontsize=12)
    plt.ylabel('Average Active Time (minutes)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Active time by task chart saved to {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python viz_active_time_by_task.py [analysis_results.json] [output_file.png]")
        print("Example: python viz_active_time_by_task.py results.json active_time_by_task.png")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(json_file):
        print(f"Error: Input file {json_file} not found.")
        sys.exit(1)
    
    try:
        with open(json_file, 'r') as f:
            results = json.load(f)
        
        create_active_time_by_task_plot(results, output_file)
        
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
