"""
User Pattern Diversity Visualization Script

Creates a bar chart showing pattern diversity (number of unique patterns) for each user.

Usage:
python viz_user_pattern_diversity.py [analysis_results.json] [output_file.png]

Example:
python viz_user_pattern_diversity.py test_results/enhanced_analysis.json charts/user_pattern_diversity.png
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

def create_user_pattern_diversity_plot(results, output_file):
    """Create user pattern diversity analysis."""
    user_diversity = {}
    
    # Calculate pattern diversity for each user across all tasks
    all_users = set()
    for task_data in results.values():
        for user in task_data.get('users', []):
            all_users.add(user.get('user_id'))
    
    for user_id in all_users:
        user_patterns = set()
        for task_data in results.values():
            for user in task_data.get('users', []):
                if user.get('user_id') == user_id:
                    user_patterns.update([p['pattern'] for p in user.get('patterns', [])])
        user_diversity[user_id] = len(user_patterns)
    
    if not user_diversity:
        print("No user data found.")
        return
    
    # Set up the plot
    plt.style.use('default')
    sns.set_palette("deep")
    sns.set_context("talk")
    
    plt.figure(figsize=(12, 6))
    users = sorted(user_diversity.keys())
    diversities = [user_diversity[user] for user in users]
    
    bars = plt.bar(range(len(users)), diversities)
    plt.title('Pattern Diversity by User', fontsize=16, fontweight='bold')
    plt.xlabel('User ID', fontsize=12)
    plt.ylabel('Number of Unique Patterns Used', fontsize=12)
    plt.xticks(range(len(users)), [f'User {str(u).replace("user_", "")}' for u in users], rotation=45)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"User pattern diversity chart saved to {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python viz_user_pattern_diversity.py [analysis_results.json] [output_file.png]")
        print("Example: python viz_user_pattern_diversity.py results.json user_pattern_diversity.png")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(json_file):
        print(f"Error: Input file {json_file} not found.")
        sys.exit(1)
    
    try:
        with open(json_file, 'r') as f:
            results = json.load(f)
        
        create_user_pattern_diversity_plot(results, output_file)
        
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
