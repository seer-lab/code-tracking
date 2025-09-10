"""
Pattern Distribution Visualization Script

Creates a bar chart showing the overall distribution of testing patterns across all tasks.

Usage:
python viz_pattern_distribution.py [analysis_results.json] [output_file.png]

Example:
python viz_pattern_distribution.py test_results/enhanced_analysis.json charts/pattern_distribution.png
"""

import sys
import json
import os
from collections import Counter

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
    "Copy/paste + write + compile": "#1f77b4",  # blue
    "Heavy editing": "#d62728",  # red
    "Iterative write/compile": "#ff7f0e",  # orange
    "Write entire test then compile and run": "#2ca02c",  # green
    "Write without running": "#9467bd",  # purple
    "Run with minimal changes": "#17becf",  # cyan
    "Read only": "#8c564b"  # brown
}

def create_pattern_distribution_plot(results, output_file):
    """Create overall pattern distribution chart."""
    # Collect all patterns
    all_patterns = []
    for task_data in results.values():
        for user in task_data.get('users', []):
            all_patterns.extend([p['pattern'] for p in user.get('patterns', [])])
    
    if not all_patterns:
        print("No patterns found in the data.")
        return
    
    pattern_counts = Counter(all_patterns)
    
    # Set up the plot
    plt.style.use('default')
    sns.set_palette("deep")
    sns.set_context("talk")
    
    plt.figure(figsize=(12, 8))
    patterns = list(pattern_counts.keys())
    counts = list(pattern_counts.values())
    colors = [PATTERN_COLORS.get(p, '#gray') for p in patterns]
    
    bars = plt.bar(patterns, counts, color=colors)
    plt.title('Overall Testing Pattern Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Testing Pattern', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    
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
