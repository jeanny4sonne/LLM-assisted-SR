#!/usr/bin/env python3
"""
Generate summary report from results
"""
import json
from pathlib import Path
from datetime import datetime

def main():
    print("Cochrane AI Screening - Summary Report")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Look for results files
    comparison_dir = Path("data/output/comparison")
    performance_dir = Path("data/output/performance")
    
    reports = []
    
    if comparison_dir.exists():
        for json_file in comparison_dir.glob("*.json"):
            with open(json_file, 'r') as f:
                data = json.load(f)
                reports.append({
                    "type": "comparison",
                    "file": json_file.name,
                    "data": data
                })
    
    if performance_dir.exists():
        for json_file in performance_dir.glob("*.json"):
            with open(json_file, 'r') as f:
                data = json.load(f)
                reports.append({
                    "type": "performance", 
                    "file": json_file.name,
                    "data": data
                })
    
    for report in reports:
        print(f"\n📊 {report['type'].upper()} Report: {report['file']}")
        print("-" * 40)
        
        data = report['data']
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    if isinstance(value, float):
                        print(f"  {key:25}: {value:.4f}")
                    else:
                        print(f"  {key:25}: {value}")
    
    print(f"\n{'='*60}")
    print("Report complete!")

if __name__ == "__main__":
    main()
