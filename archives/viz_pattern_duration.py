"""
Pattern Duration Analysis Visualization Script

Creates box plots showing the duration distribution for each testing pattern.

Usage:
python viz_pattern_duration.py [analysis_results.json] [output_file.png]

Example:
python viz_pattern_duration.py test_results/enhanced_analysis.json charts/pattern_duration.png
"""

import sys
import json
import os
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    print("Warning: visualization libraries not available")
    import sys
    if len(sys.argv) >= 3: 
        print(f"Would create chart at: {sys.argv[2]}")
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

def create_pattern_duration_plot(results, output_file):
    """Create pattern duration analysis."""
    pattern_durations = defaultdict(list)
    
    for task_data in results.values():
        for user in task_data.get('users', []):
            for pattern in user.get('patterns', []):
                pattern_durations[pattern['pattern']].append(pattern['duration'])
    
    if not pattern_durations:
        print("No pattern duration data found.")
        return
    
    # Set up the plot
    plt.style.use('default')
    sns.set_palette("deep")
    sns.set_context("talk")
    
    # Create box plot
    plt.figure(figsize=(14, 8))
    patterns = list(pattern_durations.keys())
    durations_data = [pattern_durations[pattern] for pattern in patterns]
    
    box_plot = plt.boxplot(durations_data, labels=patterns, patch_artist=True)
    
    # Color the boxes
    for patch, pattern in zip(box_plot['boxes'], patterns):
        patch.set_facecolor(PATTERN_COLORS.get(pattern, '#gray'))
        patch.set_alpha(0.7)
    
    plt.title('Pattern Duration Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Testing Pattern', fontsize=12)
    plt.ylabel('Duration (seconds)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Pattern duration chart saved to {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python viz_pattern_duration.py [analysis_results.json] [output_file.png]")
        print("Example: python viz_pattern_duration.py results.json pattern_duration.png")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(json_file):
        print(f"Error: Input file {json_file} not found.")
        sys.exit(1)
    
    try:
        with open(json_file, 'r') as f:
            results = json.load(f)
        
        create_pattern_duration_plot(results, output_file)
        
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
