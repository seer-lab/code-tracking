"""
User Activity Heatmap Visualization Script

Creates a heatmap showing user activity (number of patterns) across tasks.

Usage:
python viz_user_activity_heatmap.py [analysis_results.json] [output_file.png]

Example:
python viz_user_activity_heatmap.py test_results/enhanced_analysis.json charts/user_activity_heatmap.png
"""

import sys
import json
import os

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

def create_user_activity_heatmap(results, output_file):
    """Create user activity heatmap across tasks."""
    # Prepare data matrix
    all_users = set()
    for task_data in results.values():
        for user in task_data.get('users', []):
            all_users.add(user.get('user_id'))
    
    if not all_users:
        print("No user data found.")
        return
    
    users = sorted(all_users)
    tasks = sorted(results.keys())
    
    # Create matrix: rows = users, columns = tasks, values = pattern count
    data_matrix = np.zeros((len(users), len(tasks)))
    
    for j, task_id in enumerate(tasks):
        task_data = results[task_id]
        for i, user_id in enumerate(users):
            pattern_count = 0
            for user in task_data.get('users', []):
                if user.get('user_id') == user_id:
                    pattern_count = len(user.get('patterns', []))
                    break
            data_matrix[i, j] = pattern_count
    
    # Set up the plot
    plt.style.use('default')
    sns.set_context("talk")
    
    plt.figure(figsize=(8, 12))
    sns.heatmap(data_matrix, 
                xticklabels=[TASK_NAMES.get(t, f'Task {t}') for t in tasks],
                yticklabels=[f'User {str(u).replace("user_", "")}' for u in users],
                annot=True, fmt='g', cmap='YlOrRd')
    
    plt.title('User Activity Heatmap\n(Number of Patterns per Task)', fontsize=14, fontweight='bold')
    plt.xlabel('Task', fontsize=12)
    plt.ylabel('User', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"User activity heatmap saved to {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python viz_user_activity_heatmap.py [analysis_results.json] [output_file.png]")
        print("Example: python viz_user_activity_heatmap.py results.json user_activity_heatmap.png")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(json_file):
        print(f"Error: Input file {json_file} not found.")
        sys.exit(1)
    
    try:
        with open(json_file, 'r') as f:
            results = json.load(f)
        
        create_user_activity_heatmap(results, output_file)
        
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
