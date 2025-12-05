#!/usr/bin/env python
"""
Script to run the complete Cochrane AI screening pipeline.
"""
import subprocess
import sys
from pathlib import Path
import argparse

def run_command(cmd, description):
    """Run a shell command with error handling."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        
        print(f"Output: {result.stdout}")
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run Cochrane AI Screening Pipeline")
    parser.add_argument("--review", choices=["glp1", "insulin", "both"], 
                       default="glp1", help="Review type to run")
    parser.add_argument("--skip-tests", action="store_true", help="Skip tests")
    parser.add_argument("--skip-screening", action="store_true", help="Skip screening")
    parser.add_argument("--skip-comparison", action="store_true", help="Skip comparison")
    parser.add_argument("--skip-performance", action="store_true", help="Skip performance")
    
    args = parser.parse_args()
    
    # Run tests if not skipped
    if not args.skip_tests:
        success = run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            "Running tests"
        )
        if not success:
            print("Tests failed. Exiting.")
            sys.exit(1)
    
    # Determine which reviews to run
    reviews = []
    if args.review in ["glp1", "both"]:
        reviews.append("glp1")
    if args.review in ["insulin", "both"]:
        reviews.append("insulin")
    
    for review in reviews:
        print(f"\n{'#'*60}")
        print(f"Processing {review.upper()} Review")
        print(f"{'#'*60}")
        
        config_file = f"config/{review}_config.yaml"
        
        # Run screening
        if not args.skip_screening:
            success = run_command(
                [sys.executable, "scripts/run1_screening.py", "--config", config_file],
                f"Screening for {review}"
            )
            if not success:
                print(f"Screening failed for {review}")
                continue
        
        # Run comparison
        if not args.skip_comparison:
            success = run_command(
                [sys.executable, "scripts/run2_comparison.py", "--config", config_file],
                f"Comparison for {review}"
            )
            if not success:
                print(f"Comparison failed for {review}")
                continue
        
        # Run performance
        if not args.skip_performance:
            success = run_command(
                [sys.executable, "scripts/run3_performance.py", "--config", config_file],
                f"Performance analysis for {review}"
            )
            if not success:
                print(f"Performance analysis failed for {review}")
                continue
    
    print("\n" + "="*60)
    print("Pipeline completed!")
    print("="*60)

if __name__ == "__main__":
    main()