# cd /Volumes/Yang/AI_test/LLM-assisted-SR/cochrane-ai-screening

#!/usr/bin/env python3
"""
Script to compare AI screening results with human decisions with match rate tracking
"""

import sys
import os
from pathlib import Path
import tempfile
import pandas as pd
import json
from datetime import datetime

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

def calculate_match_statistics(ai_df, human_df, verbose=False):
    """
    Calculate match statistics between AI and human datasets
    Returns a dictionary with match rates and counts
    """
    if verbose:
        print("\n📊 Calculating match statistics...")
    
    # Standardize column names (remove whitespace, lowercase)
    ai_df_clean = ai_df.copy()
    human_df_clean = human_df.copy()
    
    ai_df_clean.columns = ai_df_clean.columns.str.strip().str.lower()
    human_df_clean.columns = human_df_clean.columns.str.strip().str.lower()
    
    # Find identifier columns
    ai_id_cols = []
    human_id_cols = []
    
    # Common identifier column names
    possible_id_names = [
        'accession', 'accession number', 'accession_number',
        'doi', 'doi number', 'doi_number',
        'pmid', 'pubmed id', 'pubmed_id',
        'id', 'identifier', 'reference id', 'reference_id',
        'citation', 'ref'
    ]
    
    for col in ai_df_clean.columns:
        col_lower = col.lower()
        for possible in possible_id_names:
            if possible in col_lower:
                ai_id_cols.append(col)
                break
    
    for col in human_df_clean.columns:
        col_lower = col.lower()
        for possible in possible_id_names:
            if possible in col_lower:
                human_id_cols.append(col)
                break
    
    if verbose:
        print(f"  Found identifier columns in AI data: {ai_id_cols}")
        print(f"  Found identifier columns in Human data: {human_id_cols}")
    
    # If no identifier columns found
    if not ai_id_cols or not human_id_cols:
        if verbose:
            print("  ⚠️  No standard identifier columns found")
        return {'match_method': 'title_only', 'match_rate': 'N/A'}
    
    # Check for missing identifiers
    ai_total = len(ai_df_clean)
    human_total = len(human_df_clean)
    
    # Initialize counters
    ai_missing_accession = 0
    ai_missing_doi = 0
    ai_missing_both = 0
    human_missing_accession = 0
    human_missing_doi = 0
    human_missing_both = 0
    
    # Check AI data
    accession_col_ai = None
    if 'accession number' in ai_df_clean.columns:
        accession_col_ai = 'accession number'
    elif 'accession_number' in ai_df_clean.columns:
        accession_col_ai = 'accession_number'
    
    if accession_col_ai:
        ai_missing_accession = ai_df_clean[accession_col_ai].isna().sum()
    
    if 'doi' in ai_df_clean.columns:
        ai_missing_doi = ai_df_clean['doi'].isna().sum()
        # Count records missing both
        if accession_col_ai:
            ai_missing_both = ai_df_clean[accession_col_ai].isna() & ai_df_clean['doi'].isna()
            ai_missing_both = ai_missing_both.sum()
    
    # Check Human data
    accession_col_human = None
    if 'accession number' in human_df_clean.columns:
        accession_col_human = 'accession number'
    elif 'accession_number' in human_df_clean.columns:
        accession_col_human = 'accession_number'
    
    if accession_col_human:
        human_missing_accession = human_df_clean[accession_col_human].isna().sum()
    
    if 'doi' in human_df_clean.columns:
        human_missing_doi = human_df_clean['doi'].isna().sum()
        # Count records missing both
        if accession_col_human:
            human_missing_both = human_df_clean[accession_col_human].isna() & human_df_clean['doi'].isna()
            human_missing_both = human_missing_both.sum()
    
    # Calculate percentages
    stats = {
        'ai_total_records': ai_total,
        'human_total_records': human_total,
        'ai_missing_accession': int(ai_missing_accession),
        'ai_missing_accession_pct': float((ai_missing_accession / ai_total * 100) if ai_total > 0 else 0),
        'ai_missing_doi': int(ai_missing_doi),
        'ai_missing_doi_pct': float((ai_missing_doi / ai_total * 100) if ai_total > 0 else 0),
        'ai_missing_both': int(ai_missing_both),
        'ai_missing_both_pct': float((ai_missing_both / ai_total * 100) if ai_total > 0 else 0),
        'human_missing_accession': int(human_missing_accession),
        'human_missing_accession_pct': float((human_missing_accession / human_total * 100) if human_total > 0 else 0),
        'human_missing_doi': int(human_missing_doi),
        'human_missing_doi_pct': float((human_missing_doi / human_total * 100) if human_total > 0 else 0),
        'human_missing_both': int(human_missing_both),
        'human_missing_both_pct': float((human_missing_both / human_total * 100) if human_total > 0 else 0),
    }
    
    # Calculate overall matchable rate
    ai_matchable = 100 - stats['ai_missing_both_pct']
    human_matchable = 100 - stats['human_missing_both_pct']
    avg_matchable = (ai_matchable + human_matchable) / 2
    
    stats['overall_matchable_pct'] = float(avg_matchable)
    
    return stats

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare AI screening results with human decisions')
    parser.add_argument('--ai-results', '-a', required=True, help='AI screening results CSV file')
    parser.add_argument('--human-results', required=True, help='Human screening results CSV file')
    parser.add_argument('--output', '-o', default='./data/output/comparison/', help='Output directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed match statistics')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("COMPARISON ANALYSIS WITH MATCH RATE TRACKING")
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
        
        # Calculate match statistics
        match_stats = calculate_match_statistics(ai_df, human_df, args.verbose)
        
        if args.verbose:
            print("\n📈 MATCH STATISTICS:")
            print("-" * 40)
            for key, value in match_stats.items():
                if isinstance(value, float):
                    if 'pct' in key:
                        print(f"  {key:30}: {value:.2f}%")
                    else:
                        print(f"  {key:30}: {value:.2f}")
                else:
                    print(f"  {key:30}: {value}")
        
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
            
            # Add match statistics to results
            if isinstance(results, dict):
                results['match_statistics'] = match_stats
                
                print("\n" + "="*60)
                print("COMPARISON RESULTS")
                print("="*60)
                
                # Show match statistics summary
                print("\n🔍 Match Rate Summary:")
                print("-"*40)
                print(f"  AI total records: {match_stats.get('ai_total_records', 'N/A')}")
                print(f"  Human total records: {match_stats.get('human_total_records', 'N/A')}")
                print(f"  AI missing both identifiers: {match_stats.get('ai_missing_both_pct', 0):.2f}%")
                print(f"  Human missing both identifiers: {match_stats.get('human_missing_both_pct', 0):.2f}%")
                print(f"  Overall matchable records: {match_stats.get('overall_matchable_pct', 0):.2f}%")
                
                # Show comparison results
                print("\n📊 Comparison Metrics:")
                print("-"*40)
                for key, value in results.items():
                    if key != 'match_statistics':
                        if isinstance(value, float):
                            print(f"  {key:25}: {value:.4f}")
                        else:
                            print(f"  {key:25}: {value}")
                
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_file = output_dir / f"comparison_results_{timestamp}.json"
                
                with open(json_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                
                print(f"\n💾 Results saved to: {json_file}")
                
                # Also save CSV summary
                csv_file = output_dir / f"comparison_summary_{timestamp}.csv"
                
                summary_data = []
                for key, value in results.items():
                    if key != 'match_statistics':
                        if isinstance(value, (int, float)):
                            summary_data.append({'Metric': key, 'Value': value})
                
                # Add key match statistics
                match_keys = ['ai_missing_both_pct', 'human_missing_both_pct', 'overall_matchable_pct']
                for key in match_keys:
                    if key in match_stats:
                        metric_name = key.replace('_pct', '%').replace('_', ' ').title()
                        summary_data.append({'Metric': metric_name, 'Value': match_stats[key]})
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_csv(csv_file, index=False)
                print(f"📄 CSV summary saved to: {csv_file}")
                
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