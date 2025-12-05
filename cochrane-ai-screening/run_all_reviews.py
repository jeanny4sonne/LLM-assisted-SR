#!/usr/bin/env python3
"""
Master script to run complete pipeline for all reviews
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed: {result.stderr}")
        return False
    else:
        print(f"✅ Success")
        if result.stdout:
            print(f"Output: {result.stdout[:500]}...")
        return True

def main():
    reviews = [
        {
            "name": "glp1",
            "input_ris": "data/input/glp1_review/GLP1_all.ris",
            "ai_results": "data/output/glp1_review/screening_decisions_comprehensive.csv",
            "human_included": "data/input/glp1_review/included_covidence.csv",
            "human_total": "data/input/glp1_review/glp1_total_covidence.csv",
            "config": "config/glp1_config.yaml"
        },
        {
            "name": "insulin",
            "input_ris": "data/input/insulin_review/short_acting_insulin_all.ris",
            "ai_results": "data/output/insulin_review/screening_decisions_insulin_analogues.csv",
            "human_included": "data/input/insulin_review/included_covidence.csv",
            "human_total": "data/input/insulin_review/insulin_total_covidence.csv",
            "config": "config/insulin_config.yaml"
        }
    ]
    
    for review in reviews:
        print(f"\n{'#'*70}")
        print(f"PROCESSING {review['name'].upper()} REVIEW")
        print(f"{'#'*70}")
        
        # 1. Screening
        if not run_command([
            sys.executable, "scripts/run1_screening.py",
            "--input", review["input_ris"],
            "--review-name", f"{review['name']}_review",
            "--config", review["config"]
        ], f"1. Screening for {review['name']}"):
            print(f"Skipping further steps for {review['name']}")
            continue
        
        # 2. Comparison
        run_command([
            sys.executable, "scripts/run2_comparison.py",
            "--ai-results", review["ai_results"],
            "--human-results", review["human_included"]
        ], f"2. Comparison for {review['name']}")
        
        # 3. Performance
        run_command([
            sys.executable, "scripts/run3_performance.py",
            "--ai-results", review["ai_results"],
            "--human-total", review["human_total"]
        ], f"3. Performance analysis for {review['name']}")
    
    print(f"\n{'🎉'*35}")
    print("ALL REVIEWS COMPLETED SUCCESSFULLY!")
    print(f"{'🎉'*35}")

if __name__ == "__main__":
    main()
