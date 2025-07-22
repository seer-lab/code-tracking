"""
Generate All Visualizations Script

Runs all visualization scripts to create a complete set of charts from analysis results.

Usage:
python generate_all_visualizations.py [analysis_results.json] [output_directory]

Example:
python generate_all_visualizations.py test_results/enhanced_analysis.json charts/
"""

import sys
import os
import subprocess

def run_visualization(script_name, json_file, output_file):
    """Run a visualization script."""
    try:
        cmd = [sys.executable, script_name, json_file, output_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] {script_name} completed successfully")
        else:
            print(f"[FAIL] {script_name} failed: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"[ERROR] Error running {script_name}: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_all_visualizations.py [analysis_results.json] [output_directory]")
        print("Example: python generate_all_visualizations.py results.json charts/")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(json_file):
        print(f"Error: Input file {json_file} not found.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # List of visualization scripts and their output files
    visualizations = [
        ("viz_pattern_distribution.py", "pattern_distribution.png"),
        ("viz_patterns_by_task.py", "patterns_by_task.png"),
        ("viz_active_time_by_task.py", "active_time_by_task.png"),
        ("viz_user_pattern_diversity.py", "user_pattern_diversity.png"),
        ("viz_pattern_duration.py", "pattern_duration.png"),
        ("viz_user_activity_heatmap.py", "user_activity_heatmap.png")
    ]
    
    print(f"Generating visualizations from {json_file}...")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    success_count = 0
    total_count = len(visualizations)
    
    for script_name, output_filename in visualizations:
        output_file = os.path.join(output_dir, output_filename)
        if run_visualization(script_name, json_file, output_file):
            success_count += 1
    
    print("-" * 50)
    print(f"Completed: {success_count}/{total_count} visualizations generated successfully")
    
    if success_count == total_count:
        print(f"All visualizations saved to {output_dir}")
    else:
        print("Some visualizations failed. Check error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
