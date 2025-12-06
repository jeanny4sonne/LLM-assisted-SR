# cd /Volumes/Yang/AI_test/LLM-assisted-SR/cochrane-ai-screening
# 
# 
# !/usr/bin/env python3
"""
Script to calculate performance metrics with match rate tracking
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

# Import the PerformanceCalculator class
from src.performance.performance import PerformanceCalculator

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

def calculate_match_statistics(ai_df, human_df):
    """
    Calculate match statistics between AI and human datasets
    Returns a dictionary with match rates and counts
    """
    print("\n📊 Calculating match statistics...")
    
    # Standardize column names (remove whitespace, lowercase)
    ai_df.columns = ai_df.columns.str.strip().str.lower()
    human_df.columns = human_df.columns.str.strip().str.lower()
    
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
    
    for col in ai_df.columns:
        col_lower = col.lower()
        for possible in possible_id_names:
            if possible in col_lower:
                ai_id_cols.append(col)
                break
    
    for col in human_df.columns:
        col_lower = col.lower()
        for possible in possible_id_names:
            if possible in col_lower:
                human_id_cols.append(col)
                break
    
    print(f"  Found identifier columns in AI data: {ai_id_cols}")
    print(f"  Found identifier columns in Human data: {human_id_cols}")
    
    # If no identifier columns found, try to match by title
    if not ai_id_cols or not human_id_cols:
        print("  ⚠️  No standard identifier columns found, will attempt title matching")
        return {'match_method': 'title_only', 'match_rate': 'N/A'}
    
    # Check for missing identifiers
    ai_total = len(ai_df)
    human_total = len(human_df)
    
    # Check AI data
    ai_missing_accession = 0
    ai_missing_doi = 0
    ai_missing_both = 0
    
    if 'accession number' in ai_df.columns or 'accession_number' in ai_df.columns:
        accession_col = 'accession number' if 'accession number' in ai_df.columns else 'accession_number'
        ai_missing_accession = ai_df[accession_col].isna().sum()
    
    if 'doi' in ai_df.columns:
        ai_missing_doi = ai_df['doi'].isna().sum()
        # Count records missing both
        if 'accession number' in ai_df.columns or 'accession_number' in ai_df.columns:
            ai_missing_both = ai_df[accession_col].isna() & ai_df['doi'].isna()
            ai_missing_both = ai_missing_both.sum()
    
    # Check Human data
    human_missing_accession = 0
    human_missing_doi = 0
    human_missing_both = 0
    
    if 'accession number' in human_df.columns or 'accession_number' in human_df.columns:
        accession_col = 'accession number' if 'accession number' in human_df.columns else 'accession_number'
        human_missing_accession = human_df[accession_col].isna().sum()
    
    if 'doi' in human_df.columns:
        human_missing_doi = human_df['doi'].isna().sum()
        # Count records missing both
        if 'accession number' in human_df.columns or 'accession_number' in human_df.columns:
            human_missing_both = human_df[accession_col].isna() & human_df['doi'].isna()
            human_missing_both = human_missing_both.sum()
    
    # Calculate percentages
    stats = {
        'ai_total_records': ai_total,
        'human_total_records': human_total,
        'ai_missing_accession': ai_missing_accession,
        'ai_missing_accession_pct': (ai_missing_accession / ai_total * 100) if ai_total > 0 else 0,
        'ai_missing_doi': ai_missing_doi,
        'ai_missing_doi_pct': (ai_missing_doi / ai_total * 100) if ai_total > 0 else 0,
        'ai_missing_both': ai_missing_both,
        'ai_missing_both_pct': (ai_missing_both / ai_total * 100) if ai_total > 0 else 0,
        'human_missing_accession': human_missing_accession,
        'human_missing_accession_pct': (human_missing_accession / human_total * 100) if human_total > 0 else 0,
        'human_missing_doi': human_missing_doi,
        'human_missing_doi_pct': (human_missing_doi / human_total * 100) if human_total > 0 else 0,
        'human_missing_both': human_missing_both,
        'human_missing_both_pct': (human_missing_both / human_total * 100) if human_total > 0 else 0,
    }
    
    return stats

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate performance metrics with match rate tracking')
    parser.add_argument('--ai-results', '-a', required=True, help='AI screening results CSV file')
    parser.add_argument('--human-total', '-t', required=True, help='Human total screening CSV file')
    parser.add_argument('--output', '-o', default='./data/output/performance/', help='Output directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed match statistics')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("PERFORMANCE ANALYSIS WITH MATCH RATE TRACKING")
    print("=" * 60)
    print(f"AI results: {args.ai_results}")
    print(f"Human total: {args.human_total}")
    
    # Check if files exist
    if not os.path.exists(args.ai_results):
        print(f"❌ AI results file not found: {args.ai_results}")
        return 1
    
    if not os.path.exists(args.human_total):
        print(f"❌ Human total file not found: {args.human_total}")
        return 1
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Read files with correct encoding
        print(f"\nReading files...")
        ai_df, ai_encoding = convert_to_utf8(args.ai_results)
        human_df, human_encoding = convert_to_utf8(args.human_total)
        
        print(f"  ✓ AI file read with {ai_encoding} encoding: {ai_df.shape}")
        print(f"  ✓ Human file read with {human_encoding} encoding: {human_df.shape}")
        
        # Calculate match statistics
        match_stats = calculate_match_statistics(ai_df, human_df)
        
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
            
            # Initialize performance calculator
            calculator = PerformanceCalculator()
            print("\n✓ PerformanceCalculator initialized")
            
            # Calculate performance metrics
            print(f"\n📊 Calculating performance metrics...")
            results = calculator.calculate(
                python_csv=ai_utf8,
                covidence_total_csv=human_utf8
            )
            
            print(f"\n✅ Performance analysis complete!")
            
            # Add match statistics to results
            results['match_statistics'] = match_stats
            
            # Show results
            if isinstance(results, dict):
                print("\n" + "="*60)
                print("RESULTS SUMMARY")
                print("="*60)
                
                # Study counts
                count_metrics = ['total_studies', 'ai_included', 'human_included', 
                               'true_positives', 'false_positives', 'false_negatives', 'true_negatives']
                
                print("\n📈 Study Counts:")
                print("-"*40)
                for metric in count_metrics:
                    if metric in results:
                        print(f"  {metric:20}: {results[metric]}")
                
                # Performance metrics
                perf_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 
                              'specificity', 'npv']
                
                print("\n🎯 Performance Metrics:")
                print("-"*40)
                for metric in perf_metrics:
                    if metric in results:
                        value = results[metric]
                        if isinstance(value, float):
                            print(f"  {metric:20}: {value:.4f}")
                
                # Match statistics summary
                print("\n🔍 Match Rate Summary:")
                print("-"*40)
                if 'match_statistics' in results:
                    stats = results['match_statistics']
                    
                    # Show key match statistics
                    key_stats = [
                        ('ai_missing_accession_pct', 'AI missing accession'),
                        ('ai_missing_doi_pct', 'AI missing DOI'),
                        ('ai_missing_both_pct', 'AI missing both identifiers'),
                        ('human_missing_accession_pct', 'Human missing accession'),
                        ('human_missing_doi_pct', 'Human missing DOI'),
                        ('human_missing_both_pct', 'Human missing both identifiers')
                    ]
                    
                    for stat_key, stat_label in key_stats:
                        if stat_key in stats:
                            value = stats[stat_key]
                            if isinstance(value, (int, float)):
                                print(f"  {stat_label:30}: {value:.2f}%")
                
                # Calculate overall matchable rate
                ai_matchable = 100 - match_stats.get('ai_missing_both_pct', 0)
                human_matchable = 100 - match_stats.get('human_missing_both_pct', 0)
                avg_matchable = (ai_matchable + human_matchable) / 2
                
                print(f"\n  {'Overall matchable records':30}: {avg_matchable:.2f}%")
                print(f"  {'(Records with at least one identifier)':30}")
                
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_file = output_dir / f"performance_results_{timestamp}.json"
                
                with open(json_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                
                print(f"\n💾 Results saved to: {json_file}")
                
                # Also save a CSV summary
                csv_file = output_dir / f"performance_summary_{timestamp}.csv"
                
                # Create summary dataframe
                summary_data = []
                
                # Add performance metrics
                for metric in perf_metrics:
                    if metric in results and isinstance(results[metric], (int, float)):
                        summary_data.append({'Metric': metric, 'Value': results[metric]})
                
                # Add key match statistics
                match_summary_keys = [
                    'ai_missing_accession_pct', 'ai_missing_doi_pct', 'ai_missing_both_pct',
                    'human_missing_accession_pct', 'human_missing_doi_pct', 'human_missing_both_pct'
                ]
                
                for key in match_summary_keys:
                    if key in match_stats:
                        metric_name = key.replace('_pct', '%').replace('_', ' ').title()
                        summary_data.append({'Metric': metric_name, 'Value': match_stats[key]})
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_csv(csv_file, index=False)
                print(f"📄 CSV summary saved to: {csv_file}")
                
            else:
                print(f"\nResults: {results}")
                
    except Exception as e:
        print(f"\n❌ Error during performance analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    main()