# cd /Volumes/Yang/AI_test/code_for_screening/deepseek_screen/LLM-assisted-SR/cochrane-ai-screening
# 
# 
#!/usr/bin/env python3
"""
Fixed insulin screening: Revised with original exclusion logic but fixed issues
File: run1_screen_insulin_fixed.py
"""

import rispy
import pandas as pd
import numpy as np
import re
import os
import json
import argparse
from typing import List, Dict, Tuple
from pathlib import Path

# Step 1: Load .ris file
def load_ris_file(file_path: str) -> List[Dict]:
    with open(file_path, 'r') as file:
        entries = rispy.load(file)
    return entries

# Step 2: Define screening criteria (SAME AS ORIGINAL)
INCLUSION_TERMS = {
    'population': ['type 1 diabetes', 'type-1 diabetic', 't1d', 'type 1 dm', 'diabetes mellitus type 1', 'adult'],
    'intervention_and_comparator': ['insulin aspart', 'novorapid', 'novolog', 'insulin lispro', 'humalog',
                     'insulin glulisine', 'apidra', 'fiasp', 'fast-acting insulin aspart', 'faster aspart', 'ultra-rapid aspart',
                     'lymjev', 'ultra-rapid lispro', 'ultra rapid lispro', 'urli', 'LY900014',
                     # Regular human insulin (reference)
                     'regular human insulin', 'rhi', 'regular insulin', 'humulin r', 'novolin r'],
    'study_design': ['randomized', 'randomised', 'rct', 'randomised controlled trial', 'clinical trial', 'controlled trial']
}

EXCLUSION_TERMS = {
    'population': ['type 2 diabetes', 't2d', 'type 2 dm', 'gestational diabetes', 'gdm', 'pregnant women', 'pregnant females',
                   'children', 'pediatric', 'MODY', 'LADA'], 
    'intervention_and_comparator': ['inhaled insulin', 'inhaled technosphere insulin', 'Afrezza', 
                                    'insulin pump', 'closed loop', 'closed-loop',
                                    'open loop', 'open-loop', 'artificial pancreas', 
                                    'continuous subcutaneous insulin infusion', 'CSII', 'intraveneous insulin', 
                                    'premixed', 'biphasic', 'intermediate-acting insulin'],
    'study_design': ['systematic review', 'observational study', 'observational trial', 'meta-analysis']
}

# Step 3: Define follow-up duration (SAME AS ORIGINAL)
def extract_duration(text: str) -> Tuple:
    patterns = [r'(\d+)\s*day', r'(\d+)\s*week', 
                r'(\d+)\s*month', r'(\d+)\s*year'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = int(match.group(1))
            unit = 'day' if 'day' in pattern else 'week' if 'week' in pattern else 'month' if 'month' in pattern else 'year'
            return value, unit
    return None, None

def meets_duration_requirement(text: str) -> bool:
    value, unit = extract_duration(text)
    if value is None:
        return False
    
    if unit == 'day':
        return value >= 180
    elif unit == 'week':
        return value >= 24
    elif unit == 'month':
        return value >= 6
    elif unit == 'year':
        return value >= 0.5
    return False

def check_duration(text: str) -> str:
    text = text.lower()
    
    long_term_indicators = ['24 weeks', 'week 24', '24-week', '26 weeks', '26-week', 'week 26',
                            '52 weeks', '52-week', 'week 52', '6 months', '6-month', 
                            '12 months', '12-month', '1 year', '2 years']
    if any(term in text for term in long_term_indicators):
        return 'yes'
    
    if meets_duration_requirement(text):
        return 'yes'
    
    short_term_indicators = ['short-term', 'short term', 'acute', 'pharmacokenetic', 'pharmacodynamic', 
                             'minute', 'hour', 'days', '7-day', '1 week', '2 weeks', '2-week', 
                             '4 weeks', '4-week', '12 weeks', '12-week', 
                             '16 weeks', '16-week','20 weeks', '20-week']
    if any(term in text for term in short_term_indicators):
        return 'no'
    
    return 'unclear'

# Step 4: Check intervention/comparator - require at least 2 different interventions
def count_interventions(text: str) -> int:
    """Count how many different interventions are mentioned in the text"""
    found_interventions = set()
    
    for intervention_term in INCLUSION_TERMS['intervention_and_comparator']:
        if intervention_term in text:
            found_interventions.add(intervention_term)
    
    return len(found_interventions)

# Step 5: FIXED screening logic - based on ORIGINAL but with bug fixes
def screen_record(record: Dict) -> Tuple[str, str]:
    """Screen a single record and return (decision, reason) - REVISED VERSION"""
    text = f"{record.get('title', '')} {record.get('abstract', '')}".lower()
    
    # 1). Check exclusion criteria first - count how many exclusion reasons met
    exclusion_reasons = []
    
    # Check population exclusions
    for exclusion_term in EXCLUSION_TERMS['population']:
        if exclusion_term in text:
            exclusion_reasons.append(f'excluded population: {exclusion_term}')
    
    # Check intervention/comparator exclusions
    for exclusion_term in EXCLUSION_TERMS['intervention_and_comparator']:
        if exclusion_term in text:
            exclusion_reasons.append(f'excluded intervention/comparator: {exclusion_term}')
    
    # Check study design exclusions
    for exclusion_term in EXCLUSION_TERMS['study_design']:
        if exclusion_term in text:
            exclusion_reasons.append(f'excluded study design: {exclusion_term}')
    
    # ORIGINAL LOGIC: If at least 2 exclusion reasons are met, exclude immediately
    if len(exclusion_reasons) >= 2:
        primary_reason = exclusion_reasons[0]  # Use the first reason as primary
        return ('exclude', primary_reason)
    
    # If exactly 1 exclusion reason, store it but continue checking
    single_exclusion_reason = exclusion_reasons[0] if exclusion_reasons else None

    # 2). Check inclusion criteria
    # Check study design
    has_design = any(term in text for term in INCLUSION_TERMS['study_design'])
    if not has_design:
        return ('exclude', 'ineligible study design')
    
    # Check population
    has_population = any(term in text for term in INCLUSION_TERMS['population'])
    if not has_population:
        return ('exclude', 'ineligible population')
    
    # Check intervention/comparator - require at least 2 interventions
    intervention_count = count_interventions(text)
    if intervention_count < 2:
        return ('exclude', f'ineligible intervention/comparator (found {intervention_count}, need at least 2)')
 
    # 3). Check duration
    duration_status = check_duration(text)
    
    # ORIGINAL LOGIC: If we passed all inclusion criteria but had one exclusion reason, still exclude
    if single_exclusion_reason:
        return ('exclude', single_exclusion_reason)

    # All criteria met
    if duration_status == 'yes':
        return ('include', 'meets all criteria')
    elif duration_status == 'no':
        return ('exclude', 'ineligible follow-up duration')
    else:
        return ('maybe', 'partially meets PICO but unclear follow-up duration')

# Step 6: Extract comprehensive metadata
def extract_comprehensive_metadata(record: Dict, record_index: int) -> Dict:
    """Extract comprehensive metadata from RIS record including all requested columns"""
    
    def get_value(key, default=''):
        value = record.get(key, default)
        if isinstance(value, list):
            return '; '.join([str(v) for v in value])
        return str(value) if value else default
    
    # Extract publication year and month
    year = get_value('year', '')
    month = ''
    pub_date = get_value('custom3', '') or get_value('date', '')
    if pub_date:
        month_match = re.search(r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\b)', pub_date, re.IGNORECASE)
        if month_match:
            month = month_match.group(1)
    
    # Extract authors
    authors_raw = record.get('authors', [])
    authors = '; '.join(authors_raw) if isinstance(authors_raw, list) else str(authors_raw)
    
    # Extract volume, issue, pages
    volume = get_value('volume', '')
    issue = get_value('number', '') or get_value('issue', '')
    pages = get_value('pages', '') or get_value('start_page', '')
    
    # Extract identifiers
    accession_number = get_value('accession_number', '')
    doi = get_value('doi', '')
    ref_id = get_value('primary_id', '') or get_value('id', '')
    
    # Study type
    study_type = get_value('type', '')
    
    # Clean title
    title = get_value('title', '')
    title_cleaned = re.sub(r'\s+', ' ', title).strip()
    
    return {
        'Title': title,
        'Authors': authors,
        'Abstract': get_value('abstract', ''),
        'Published Year': year,
        'Published Month': month,
        'Journal': get_value('journal_name', '') or get_value('secondary_title', ''),
        'Volume': volume,
        'Issue': issue,
        'Pages': pages,
        'Accession Number': accession_number,
        'DOI': doi,
        'Ref': ref_id,
        'Covidence #': '',  # Empty for manual entry
        'Study': study_type,
        'Notes': '',
        'decision': '',
        'Title_Cleaned': title_cleaned,
        'Database': get_value('database', ''),
        'Language': get_value('language', ''),
        'URL': get_value('url', ''),
        'ISSN': get_value('issn', ''),
    }

# Step 7: Classify and save results
def classify_and_save_results(entries: List[Dict]):
    """Screen all records and save with classified reasons"""
    
    results = {
        'include': [],
        'exclude_population': [],
        'exclude_intervention': [],
        'exclude_study_design': [],
        'exclude_duration': [],
        'maybe': []
    }
    
    exclusion_reasons_count = {
        'population': 0,
        'intervention': 0,
        'study_design': 0,
        'duration': 0
    }
    
    for entry in entries:
        decision, reason = screen_record(entry)
        
        # Store the reason in the record
        entry['screening_reason'] = reason
        
        # Classify based on reason
        if decision == 'include':
            results['include'].append(entry)
        elif decision == 'maybe':
            results['maybe'].append(entry)
        elif decision == 'exclude':
            if 'population' in reason:
                results['exclude_population'].append(entry)
                exclusion_reasons_count['population'] += 1
            elif 'intervention' in reason:
                results['exclude_intervention'].append(entry)
                exclusion_reasons_count['intervention'] += 1
            elif 'study design' in reason:
                results['exclude_study_design'].append(entry)
                exclusion_reasons_count['study_design'] += 1
            elif 'duration' in reason:
                results['exclude_duration'].append(entry)
                exclusion_reasons_count['duration'] += 1
            else:
                # Fallback for any unclassified exclusions
                results['exclude_study_design'].append(entry)
    
    return results, exclusion_reasons_count

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run insulin screening with fixed logic')
    parser.add_argument('--input', default='short_acting_insulin_all.ris',
                       help='Input RIS file path (default: short_acting_insulin_all.ris)')
    parser.add_argument('--output', default='screening_results.csv',
                       help='Output CSV file path (default: screening_results.csv)')
    parser.add_argument('--output-dir', default='.',
                       help='Output directory for results (default: current directory)')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("INSULIN SCREENING - FIXED VERSION (run1_screen_insulin_fixed.py)")
    print("=" * 80)
    print(f"Input file: {args.input}")
    print(f"Output file: {args.output}")
    print(f"Output directory: {args.output_dir}")
    print()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Looking for: {os.path.abspath(args.input)}")
        return
    
    # Load .ris file
    print("Loading RIS file...")
    try:
        entries = load_ris_file(args.input)
        print(f"✓ Loaded {len(entries)} records from {args.input}")
    except Exception as e:
        print(f"❌ Error loading RIS file: {e}")
        return
    
    # Screen and classify all records
    print("\nScreening records with FIXED logic...")
    results, exclusion_counts = classify_and_save_results(entries)
    
    # Print detailed results
    print("\n" + "=" * 60)
    print("SCREENING RESULTS")
    print("=" * 60)
    print(f"Included: {len(results['include'])} records")
    print(f"Uncertain ('maybe'): {len(results['maybe'])} records")
    print(f"\nExcluded by category:")
    print(f"  - Population: {len(results['exclude_population'])} records")
    print(f"  - Intervention/Comparator: {len(results['exclude_intervention'])} records")
    print(f"  - Study Design: {len(results['exclude_study_design'])} records")
    print(f"  - Duration: {len(results['exclude_duration'])} records")
    
    total_excluded = (len(results['exclude_population']) + 
                     len(results['exclude_intervention']) + 
                     len(results['exclude_study_design']) + 
                     len(results['exclude_duration']))
    
    print(f"\nTotal excluded: {total_excluded} records")
    print(f"Total screened: {len(entries)} records")
    
    # Calculate inclusion rate
    inclusion_rate = len(results['include']) / len(entries) if len(entries) > 0 else 0
    print(f"Inclusion rate: {inclusion_rate:.2%}")
    
    # Create comprehensive screening data
    print("\nCreating comprehensive screening CSV...")
    screening_data = []
    
    for i, entry in enumerate(entries):
        # Extract comprehensive metadata
        metadata = extract_comprehensive_metadata(entry, i)
        
        # Get screening decision and reason
        decision, reason = screen_record(entry)
        
        # Update metadata with screening results
        metadata['decision'] = decision
        
        # Add additional screening info
        metadata['Screening_Reason'] = reason
        
        # Map to requested column names
        screening_data.append({
            'Title': metadata['Title'],
            'Authors': metadata['Authors'],
            'Abstract': metadata['Abstract'],
            'Published Year': metadata['Published Year'],
            'Published Month': metadata['Published Month'],
            'Journal': metadata['Journal'],
            'Volume': metadata['Volume'],
            'Issue': metadata['Issue'],
            'Pages': metadata['Pages'],
            'Accession Number': metadata['Accession Number'],
            'DOI': metadata['DOI'],
            'Ref': metadata['Ref'],
            'Covidence #': metadata['Covidence #'],
            'Study': metadata['Study'],
            'Notes': metadata['Notes'],
            'decision': metadata['decision'],
            'Title_Cleaned': metadata['Title_Cleaned'],
        })
    
    # Create DataFrame
    df = pd.DataFrame(screening_data)
    
    # Reorder columns
    column_order = [
        'Title', 'Authors', 'Abstract', 'Published Year', 'Published Month',
        'Journal', 'Volume', 'Issue', 'Pages', 'Accession Number', 'DOI',
        'Ref', 'Covidence #', 'Study', 'Notes', 'decision',
        'Title_Cleaned'
    ]
    
    df = df[column_order]
    
    # Ensure output directory exists
    output_path = os.path.join(args.output_dir, args.output)
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\n✓ Comprehensive screening decisions saved: {output_path}")
    print(f"  - Contains {len(df)} records with {len(df.columns)} columns")
    print(f"  - Covidence # column is empty for manual entry")
    
    # Also save a simplified version
    simple_output = os.path.join(args.output_dir, 'screening_decisions_simple.csv')
    simple_columns = ['Title', 'Authors', 'Journal', 'Published Year', 'DOI', 'decision', 'Notes']
    df_simple = df[simple_columns]
    df_simple.to_csv(simple_output, index=False)
    print(f"✓ Simplified CSV saved: {simple_output}")
    
    # Create a summary report
    summary_report = {
        'screening_summary': {
            'total_records': len(entries),
            'included': len(results['include']),
            'excluded': total_excluded,
            'uncertain': len(results['maybe']),
            'inclusion_rate': inclusion_rate
        },
        'exclusion_breakdown': exclusion_counts,
        'output_files': {
            'comprehensive_csv': output_path,
            'simple_csv': simple_output,
            'note': 'Covidence # column intentionally left empty for manual entry'
        }
    }
    
    # Save summary report next to output file
    summary_path = os.path.join(args.output_dir, 'screening_summary_fixed.json')
    with open(summary_path, 'w') as f:
        json.dump(summary_report, f, indent=2)
    print(f"✓ Screening summary saved: {summary_path}")
    
    print("\n" + "=" * 60)
    print("✅ SCREENING COMPLETE!")
    print("=" * 60)
    print(f"Main output file: {output_path}")
    print(f"\nSummary:")
    print(f"  - Included: {len(results['include'])} records")
    print(f"  - Excluded: {total_excluded} records")
    print(f"  - Uncertain: {len(results['maybe'])} records")
    print(f"  - Total: {len(entries)} records")
    print(f"\nNote: Covidence # column is intentionally left empty for manual entry.")

if __name__ == "__main__":
    main()