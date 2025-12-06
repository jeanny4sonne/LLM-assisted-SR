# running in Terminal: 
# cd /Volumes/Yang/AI_test/code_for_screening/deepseek_screen/GLP1 #navigate to the working directory
# /opt/homebrew/bin/python3 -m venv venv # Create virtual environment
# source venv/bin/activate #Activate virtual environment
# pip install rispy pandas numpy  # Install packages
# python ris_screener5.py 2>&1 | tee output.txt  # Run the following script

import rispy
import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple
import logging

# Step 1: Load .ris file
def load_ris_file(file_path: str) -> List[Dict]:
    with open(file_path, 'r') as file:
        entries = rispy.load(file)
    return entries

# Step 2: Define screening criteria for GLP-1 receptor agonists
INCLUSION_TERMS = {
    'population': ['adult', 'obesity', 'obese', 'overweight', 'prediabetes', 'metabolic syndrome', 'NASH', 'abdominal fat', 'aged 18 years', 'BMI of 25', 'BMI ≥ 25', 'BMI ≥ 30'],
    'intervention_and_comparator': ['liraglutide', 'saxenda', 'victoza', 
                                    'semaglutide', 'wegovy', 'ozempic', 'rybelsus',
                                    'tirzepatide', 'mounjaro', 'zepbound', 'LY3298176'],
    'study_design': ['randomized', 'randomised', 'rct', 'randomised controlled trial', 'clinical trial', 'controlled trial', 'parrellel', 'double-blind', 'double blind']
}

EXCLUSION_TERMS = {
    'population': ['child', 'children', 'adolescent', 'youth', 'pediatric', 'paediatric'],
    'intervention_and_comparator': ['bariatric surgery', 'gastric bypass', 'sleeve gastrectomy', 'gastric band',
                                    'exenatide', 'byetta', 'bydureon',
                                    'dulaglutide', 'trulicity',
                                    'dpp-4', 'dipeptidyl peptidase-4', 'gliptin', 'sitagliptin', 'linagliptin', 'saxagliptin', 'alogliptin', 'vildagliptin','teneligliptin',
                                    'sglt2', 'gliflozin', 'flozin', 'empagliflozin', 'dapagliflozin', 'canagliflozin', 'ertugliflozin', 'bexagliflozin','sotagliflozin'],
    'study_design': ['this review', 'systematic review', 'meta-analysis', 'meta-regression', 'observational', 'case-control', 'cross-sectional',
                     'crossover', 'cross-over', 'cost-effectiveness analysis', 'quasi-experimental']
}

# Step 3: Define follow-up duration (first extract then assess)
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
    
    long_term_indicators = ['long-term', 'long term', '24 weeks', 'week 24', '24-week', '26 weeks', '26-week', 'week 26',
                            '52 weeks', '52-week', 'week 52', '6 months', '6-month', '12 months', '12-month', '1 year', 
                            '18 months', '18-month', '2 years', '3 years']
    if any(term in text for term in long_term_indicators):
        return 'yes'
    
    if meets_duration_requirement(text):
        return 'yes'
    
    short_term_indicators = ['pharmacokenetic', 'pharmacodynamic', 'minutes', 'hour', 'days', '7-day', 
                             '1 week', '2 weeks', '2-week', '4 weeks', '4-week', '12 weeks', '12-week', 
                             '16 weeks', '16-week', '20 weeks', '20-week']
    if any(term in text for term in short_term_indicators):
        return 'no'
    
    return 'unclear'

# Step 4: screening with other inclusion/exclusion criteria
def screen_record(record: Dict) -> Tuple[str, str]:
    """Screen a single record and return (decision, reason)"""
    text = f"{record.get('title', '')} {record.get('abstract', '')}".lower()
    
    # 1. Check exclusion criteria first
    # Check study design exclusions
    for exclusion_term in EXCLUSION_TERMS['study_design']:
        if exclusion_term in text:
            return ('exclude', f'excluded study design: {exclusion_term}')
        
    # Check population exclusions
    for exclusion_term in EXCLUSION_TERMS['population']:
        if exclusion_term in text:
            return ('exclude', f'excluded population: {exclusion_term}')
    
    # Check intervention/comparator exclusions
    for exclusion_term in EXCLUSION_TERMS['intervention_and_comparator']:
        if exclusion_term in text:
            return ('exclude', f'excluded intervention/comparator: {exclusion_term}')
    
    
    # 2. Check inclusion criteria
    # Check study design
    has_design = any(term in text for term in INCLUSION_TERMS['study_design'])
    if not has_design:
        return ('exclude', 'unlcear study design')
    
    # Check population
    has_population = any(term in text for term in INCLUSION_TERMS['population'])
    if not has_population:
        return ('exclude', 'ineligible population')

    # Check intervention/comparator
    has_intervention = any(term in text for term in INCLUSION_TERMS['intervention_and_comparator'])
    if not has_intervention:
        return ('exclude', 'ineligible intervention/comparator')   
 
    # 3. Check duration
    duration_status = check_duration(text)
    
    if duration_status == 'yes':
        return ('include', 'meets all criteria')
    elif duration_status == 'no':
        return ('exclude', 'ineligible follow-up duration')
    else:
        return ('maybe', 'partially meets PICO but unclear follow-up duration')


# Step 5: Classify and save results with detailed reasons
def classify_and_save_results(entries: List[Dict]):
    """Screen all records and save with classified reasons"""
    
    # Initialize results with detailed classification
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

def extract_comprehensive_metadata(record: Dict, record_index: int) -> Dict:
    """Extract comprehensive metadata from RIS record including all requested columns"""
    
    # Helper function to safely get values
    def get_value(key, default=''):
        value = record.get(key, default)
        if isinstance(value, list):
            return '; '.join([str(v) for v in value])
        return str(value) if value else default
    
    # Helper function to get first from list
    def get_first(value, default=''):
        if isinstance(value, list) and value:
            return str(value[0])
        return str(value) if value else default
    
    # Extract publication year and month
    year = get_value('year', '')
    month = ''
    pub_date = get_value('custom3', '') or get_value('date', '')
    if pub_date:
        # Try to extract month from date
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
    
    # Extract reference ID (use primary_id if available)
    ref_id = get_value('primary_id', '') or get_value('id', '')
    
    # Covidence # - leave empty for manual entry
    covidence_num = ''
    
    # Study type
    study_type = get_value('type', '')
    
    # Clean title (remove chaotic letters if needed)
    title = get_value('title', '')
    # Basic cleaning - remove extra whitespace and line breaks
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
        'Covidence #': covidence_num,  # Left empty for manual entry
        'Study': study_type,
        'Notes': '',  # For manual notes
        'Tags': '',  # For manual tagging
        'decision': '',  # Will be filled later
        'Title_Cleaned': title_cleaned,  # Added for comparison
        'Database': get_value('database', ''),
        'Language': get_value('language', ''),
        'Keywords': get_value('keywords', ''),
        'URL': get_value('url', ''),
        'ISSN': get_value('issn', ''),
        'RIS_ID': f"RIS_{record_index:04d}"  # Internal reference ID
    }

def main():
    # Load .ris file
    print("Loading RIS file...")
    entries = load_ris_file('GLP1_all.ris') 
    
    # Screen and classify all records
    print("Screening records...")
    results, exclusion_counts = classify_and_save_results(entries)
    
    # Print detailed results
    print(f"\n=== SCREENING RESULTS ===")
    print(f"Included: {len(results['include'])} records")
    print(f"Uncertain: {len(results['maybe'])} records")
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
    
    # Save results to separate .ris files with clear naming
    print(f"\nSaving results to RIS files...")
    
    # Save included studies
    if results['include']:
        rispy.dump(results['include'], open('included_studies.ris', 'w'))
        print(f"✓ Included studies saved: included_studies.ris")
    
    # Save uncertain studies
    if results['maybe']:
        rispy.dump(results['maybe'], open('uncertain_studies.ris', 'w'))
        print(f"✓ Uncertain studies saved: uncertain_studies.ris")
    
    # Save excluded studies by category
    if results['exclude_population']:
        rispy.dump(results['exclude_population'], open('excluded_population.ris', 'w'))
        print(f"✓ Excluded by population saved: excluded_population.ris")
    
    if results['exclude_intervention']:
        rispy.dump(results['exclude_intervention'], open('excluded_intervention.ris', 'w'))
        print(f"✓ Excluded by intervention saved: excluded_intervention.ris")
    
    if results['exclude_study_design']:
        rispy.dump(results['exclude_study_design'], open('excluded_study_design.ris', 'w'))
        print(f"✓ Excluded by study design saved: excluded_study_design.ris")
    
    if results['exclude_duration']:
        rispy.dump(results['exclude_duration'], open('excluded_duration.ris', 'w'))
        print(f"✓ Excluded by duration saved: excluded_duration.ris")
    
    # Save a comprehensive CSV with all decisions and metadata
    print(f"\nCreating comprehensive screening CSV...")
    screening_data = []
    
    for i, entry in enumerate(entries):
        # Extract comprehensive metadata
        metadata = extract_comprehensive_metadata(entry, i)
        
        # Get screening decision and reason
        decision, reason = screen_record(entry)
        
        # Update metadata with screening results
        metadata['decision'] = decision
        metadata['Notes'] = reason  # Store reason in Notes column
        
        # Add additional screening info
        metadata['Screening_Reason'] = reason
        
        # Map to your requested column names exactly
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
            'Covidence #': metadata['Covidence #'],  # Left empty for manual entry
            'Study': metadata['Study'],
            'Notes': metadata['Notes'],  # Contains screening reason
            'Tags': metadata['Tags'],  # Empty for manual tagging
            'decision': metadata['decision'],
            'RIS_ID': metadata['RIS_ID'],  # Internal reference
            'Title_Cleaned': metadata['Title_Cleaned'],  # For comparison
            'Keywords': metadata['Keywords']  # Added bonus
        })
    
    # Create DataFrame
    df = pd.DataFrame(screening_data)
    
    # Reorder columns to match your requested order
    column_order = [
        'Title', 'Authors', 'Abstract', 'Published Year', 'Published Month',
        'Journal', 'Volume', 'Issue', 'Pages', 'Accession Number', 'DOI',
        'Ref', 'Covidence #', 'Study', 'Notes', 'Tags', 'decision',
        'Title_Cleaned', 'RIS_ID', 'Keywords'
    ]
    
    df = df[column_order]
    
    # Save to CSV
    output_file = 'screening_decisions_comprehensive.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ Comprehensive screening decisions saved: {output_file}")
    print(f"  - Contains {len(df)} records with {len(df.columns)} columns")
    print(f"  - Covidence # column is empty for manual entry")
    print(f"  - Title_Cleaned column added for easy comparison")
    
    # Also save a simplified version for quick review
    simple_columns = ['Title', 'Authors', 'Journal', 'Published Year', 'DOI', 'decision', 'Notes']
    df_simple = df[simple_columns]
    df_simple.to_csv('screening_decisions_quickview.csv', index=False)
    print(f"✓ Quick view CSV saved: screening_decisions_quickview.csv")
    
    # Create a summary report
    summary_report = {
        'screening_summary': {
            'total_records': len(entries),
            'included': len(results['include']),
            'excluded': total_excluded,
            'uncertain': len(results['maybe']),
            'inclusion_rate': len(results['include']) / len(entries) if len(entries) > 0 else 0
        },
        'exclusion_breakdown': exclusion_counts,
        'output_files': {
            'comprehensive_csv': output_file,
            'quickview_csv': 'screening_decisions_quickview.csv',
            'included_studies': 'included_studies.ris',
            'uncertain_studies': 'uncertain_studies.ris'
        }
    }
    
    # Save summary report
    with open('screening_summary.json', 'w') as f:
        import json
        json.dump(summary_report, f, indent=2)
    print(f"✓ Screening summary saved: screening_summary.json")
    
    print(f"\n✅ Screening complete!")
    print(f"Main file: {output_file} contains all requested columns")
    print(f"Covidence # column is intentionally left empty for manual entry")

if __name__ == "__main__":
    main()