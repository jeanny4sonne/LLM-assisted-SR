# cd /Volumes/Yang/AI_test/code_for_screening/deepseek_screen/LLM-assisted-SR/cochrane-ai-screening
# 

# !/usr/bin/env python3
"""
Script to compare AI screening results with human decisions
"""

import sys
import os
from pathlib import Path
import tempfile
import pandas as pd

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the correct class
from src.comparison.comparison import ScreeningComparator

def convert_to_utf8(input_file):
    """Convert a file from Latin-1 to UTF-8 encoding and return DataFrame"""
    
    # Try different encodings
    encodings = ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(input_file, encoding=encoding)
            return df, encoding
        except Exception as e:
            continue
    
    raise ValueError(f"Could not read file {input_file} with any encoding")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare AI screening results with human decisions')
    parser.add_argument('--ai-results', '-a', required=True, help='AI screening results CSV file')
    parser.add_argument('--human-results', required=True, help='Human screening results CSV file')
    parser.add_argument('--output', '-o', default='./data/output/comparison/', help='Output directory')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("COMPARISON ANALYSIS")
    print("=" * 60)
    print(f"AI results: {args.ai_results}")
    print(f"Human results: {args.human_results}")
    
    # Check if files exist
    if not os.path.exists(args.ai_results):
        print(f"❌ AI results file not found: {args.ai_results}")
        return 1
    
    if not os.path.exists(args.human_results):
        print(f"❌ Human results file not found: {args.human_results}")
        return 1
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Read files with correct encoding
        print(f"\nReading files...")
        ai_df, ai_encoding = convert_to_utf8(args.ai_results)
        human_df, human_encoding = convert_to_utf8(args.human_results)
        
        print(f"  ✓ AI file read with {ai_encoding} encoding: {ai_df.shape}")
        print(f"  ✓ Human file read with {human_encoding} encoding: {human_df.shape}")
        
        # Save temporary UTF-8 versions
        with tempfile.TemporaryDirectory() as tmpdir:
            ai_utf8 = os.path.join(tmpdir, "ai_utf8.csv")
            human_utf8 = os.path.join(tmpdir, "human_utf8.csv")
            
            ai_df.to_csv(ai_utf8, index=False, encoding='utf-8')
            human_df.to_csv(human_utf8, index=False, encoding='utf-8')
            
            # Initialize screening comparator
            comparator = ScreeningComparator()
            print("\n✓ ScreeningComparator initialized")
            
            # Run comparison with UTF-8 files
            print(f"\n🔍 Running comparison (matching by accession + DOI)...")
            results = comparator.compare(python_csv=ai_utf8, covidence_csv=human_utf8)
            
            print(f"\n✅ Comparison complete!")
            
            # Show results
            if isinstance(results, dict):
                print("\n" + "="*60)
                print("COMPARISON RESULTS")
                print("="*60)
                
                for key, value in results.items():
                    if isinstance(value, float):
                        print(f"{key:25}: {value:.4f}")
                    else:
                        print(f"{key:25}: {value}")
                
                # Save results
                import json
                from datetime import datetime
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_file = output_dir / f"comparison_results_{timestamp}.json"
                
                with open(json_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                
                print(f"\n💾 Results saved to: {json_file}")
                
            else:
                print(f"\nResults: {results}")
                
    except Exception as e:
        print(f"\n❌ Error during comparison: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    main()
