# # cd /Volumes/Yang/AI_test/LLM-assisted-SR/cochrane-ai-screening


#!/usr/bin/env python3
"""
Main script to run screening with configurable paths
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import
from src.screening.screening import SystematicReviewScreener

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Run systematic review screening')
    parser.add_argument('--input', '-i', required=True, help='Input RIS file path')
    parser.add_argument('--output', '-o', default='./data/output/', help='Output directory')
    parser.add_argument('--config', '-c', help='Configuration YAML file')
    parser.add_argument('--review-name', '-n', required=True, help='Name of the review')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output) / args.review_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting screening for {args.review_name}...")
    print(f"Input file: {args.input}")
    print(f"Output directory: {output_dir}")
    print(f"Config file: {args.config}")
    
    # Initialize screening engine
    engine = SystematicReviewScreener(config_path=args.config)
    
    # Run the screening process
    print(f"\nRunning screening...")
    
    try:
        # Call screen() with ris_file_path parameter
        print(f"Calling engine.screen(ris_file_path='{args.input}')...")
        results = engine.screen(ris_file_path=args.input)
        
        print(f"\n✅ Screening completed successfully!")
        
        # Show results
        if isinstance(results, dict):
            print(f"\nResults:")
            for key, value in results.items():
                print(f"  {key}: {value}")
        elif results is not None:
            print(f"\nResults returned: {results}")
        
        # Save results
        print(f"\nSaving results to {output_dir}...")
        engine.save_results(output_dir=str(output_dir))
        
        print(f"\n🎉 All done! Results saved to: {output_dir}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    main()
