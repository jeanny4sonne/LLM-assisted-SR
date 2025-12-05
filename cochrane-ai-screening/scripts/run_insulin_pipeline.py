#!/usr/bin/env python3
"""
Complete insulin review pipeline with match rate tracking
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def run_command(cmd, description):
    """Run a command and print output"""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Completed successfully")
        # Print last 10 lines of output
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines[-10:]:
                if line.strip():
                    print(f"  {line}")
        return True
    else:
        print(f"❌ Failed with exit code {result.returncode}")
        print("STDERR:", result.stderr[-500:] if result.stderr else "No error output")
        return False

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define paths
    scripts_dir = Path(__file__).parent
    data_dir = Path("data/input/insulin_review")
    output_dir = Path(f"data/output/insulin_review_pipeline_{timestamp}")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 INSULIN REVIEW PIPELINE")
    print(f"Timestamp: {timestamp}")
    print(f"Output directory: {output_dir}")
    
    # Check input files
    required_files = {
        "RIS file": data_dir / "short_acting_insulin_all.ris",
        "Human included": data_dir / "included_covidence.csv",
        "Human total": data_dir / "insulin_total_covidence.csv"
    }
    
    print("\n🔍 Checking input files:")
    for name, path in required_files.items():
        if path.exists():
            print(f"  ✓ {name}: {path}")
        else:
            print(f"  ❌ {name} not found: {path}")
            return 1
    
    # Step 1: Screening
    screening_output = output_dir / "screening_results.csv"
    success = run_command(
        [
            sys.executable, str(scripts_dir / "run1_screen_insulin_fixed.py"),
            f"--input={str(data_dir / 'short_acting_insulin_all.ris')}",
            f"--output={str(screening_output)}",
            f"--output-dir={str(output_dir)}"
        ],
        "Step 1: Automated Screening"
    )
    
    if not success:
        return 1
    
    # Step 2: Comparison
    comparison_dir = output_dir / "comparison"
    success = run_command(
        [
            sys.executable, str(scripts_dir / "run2_comparison.py"),
            f"--ai-results={str(screening_output)}",
            f"--human-results={str(data_dir / 'included_covidence.csv')}",
            f"--output={str(comparison_dir)}",
            "--verbose"
        ],
        "Step 2: AI vs Human Comparison"
    )
    
    if not success:
        return 1
    
    # Step 3: Performance
    performance_dir = output_dir / "performance"
    success = run_command(
        [
            sys.executable, str(scripts_dir / "run3_performance.py"),
            f"--ai-results={str(screening_output)}",
            f"--human-total={str(data_dir / 'insulin_total_covidence.csv')}",
            f"--output={str(performance_dir)}",
            "--verbose"
        ],
        "Step 3: Performance Analysis"
    )
    
    if not success:
        return 1
    
    # Generate final report
    print(f"\n{'='*60}")
    print("🎉 PIPELINE COMPLETE!")
    print(f"{'='*60}")
    print(f"\n📁 Output directory: {output_dir}")
    print("\n📊 Generated files:")
    
    # List generated files
    for root, dirs, files in os.walk(output_dir):
        level = root.replace(str(output_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in sorted(files):
            if file.endswith(('.json', '.csv', '.txt')):
                print(f"{subindent}{file}")
    
    print(f"\n📈 Next steps:")
    print(f"  1. Review match rate statistics in JSON files")
    print(f"  2. Check performance metrics")
    print(f"  3. Compare with GLP1 review results")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())