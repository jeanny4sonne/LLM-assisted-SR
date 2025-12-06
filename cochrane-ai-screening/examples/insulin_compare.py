# Machting strategy: DOI and Accession Number (Title contained sometimes chaotic marks, DOI were missing sometimes, only Accession numbers were unique)

# run the following first:
# pip install pandas numpy chardet openpyxl
# python compare5.py 2>&1 | tee output.txt

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Set
import chardet

class ScreeningComparison:
    """
    Compare Python screening (include+maybe) with Covidence included studies
    """
    
    def __init__(self):
        self.comparison_results = {}
    
    def detect_encoding(self, file_path: str) -> str:
        """Detect the encoding of a file"""
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            print(f"Detected encoding: {encoding} with confidence: {result['confidence']:.2f}")
            return encoding
    
    def load_python_include_maybe(self, python_csv_path: str) -> pd.DataFrame:
        """Load Python screening results and filter to include + maybe"""
        try:
            df = pd.read_csv(python_csv_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(python_csv_path, encoding='latin1')
        
        # Debug: print column names
        print(f"\nColumns in Python CSV: {list(df.columns)}")
        
        # Standardize column names
        df.columns = [str(col).lower().replace(' ', '_') for col in df.columns]
        print(f"Standardized columns: {list(df.columns)}")
        
        # Filter to include + maybe
        if 'decision' in df.columns:
            include_maybe_df = df[df['decision'].isin(['include', 'maybe'])].copy()
        else:
            print("WARNING: No 'decision' column found. Using all records.")
            include_maybe_df = df.copy()
        
        print(f"Filtered to {len(include_maybe_df)} records (include + maybe)")
        
        # Create match keys - USING ACCESSION NUMBER OR DOI
        match_keys = self._create_accession_doi_match_key(include_maybe_df)
        
        # Debug: check match keys
        print(f"Generated {len(match_keys)} match keys")
        print(f"First 5 match keys: {match_keys[:5]}")
        
        if len(match_keys) != len(include_maybe_df):
            print(f"ERROR: Mismatch! DataFrame has {len(include_maybe_df)} rows, but got {len(match_keys)} match keys")
            return include_maybe_df
        
        include_maybe_df['match_key'] = match_keys
        
        # Count identifier types
        accession_count = include_maybe_df['match_key'].apply(lambda x: x.startswith('accession:')).sum()
        doi_count = include_maybe_df['match_key'].apply(lambda x: x.startswith('doi:')).sum()
        neither_count = include_maybe_df['match_key'].apply(lambda x: x.startswith('no_id:')).sum()
        
        print(f"\nIdentifier statistics:")
        print(f"  Records with Accession Number: {accession_count}")
        print(f"  Records with DOI: {doi_count}")
        print(f"  Records with neither: {neither_count}")
        
        return include_maybe_df
    
    def load_covidence_included(self, covidence_csv_path: str) -> pd.DataFrame:
        """Load Covidence included studies with encoding detection"""
        try:
            # Try UTF-8 first
            df = pd.read_csv(covidence_csv_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Try common encodings
                encodings = ['latin1', 'iso-8859-1', 'cp1252', 'windows-1252']
                for encoding in encodings:
                    try:
                        print(f"Trying encoding: {encoding}")
                        df = pd.read_csv(covidence_csv_path, encoding=encoding)
                        print(f"Success with encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # If all else fails, detect encoding
                    detected_encoding = self.detect_encoding(covidence_csv_path)
                    df = pd.read_csv(covidence_csv_path, encoding=detected_encoding)
            except Exception as e:
                print(f"Error loading CSV: {e}")
                # Last resort: try with error handling
                df = pd.read_csv(covidence_csv_path, encoding='utf-8', errors='replace')
        
        # Debug: print column names
        print(f"\nColumns in Covidence CSV: {list(df.columns)}")
        
        # Standardize column names
        df.columns = [str(col).lower().replace(' ', '_') for col in df.columns]
        print(f"Standardized columns: {list(df.columns)}")
        
        # Filter to included only (Covidence might have different decision values)
        decision_column = None
        possible_decision_columns = ['decision', 'included', 'final_decision', 'inclusion_decision']
        
        for col in possible_decision_columns:
            if col in df.columns:
                decision_column = col
                break
        
        if decision_column:
            # Handle different decision formats in Covidence
            df[decision_column] = df[decision_column].astype(str).str.lower()
            included_df = df[df[decision_column].str.contains('include', na=False)].copy()
            print(f"Filtered to {len(included_df)} records using column '{decision_column}'")
        else:
            # If no decision column, assume all are included
            included_df = df.copy()
            print("No decision column found - assuming all records are included")
        
        # Create match keys - USING ACCESSION NUMBER OR DOI
        match_keys = self._create_accession_doi_match_key(included_df)
        
        # Debug: check match keys
        print(f"Generated {len(match_keys)} match keys")
        
        if len(match_keys) != len(included_df):
            print(f"ERROR: Mismatch! DataFrame has {len(included_df)} rows, but got {len(match_keys)} match keys")
            return included_df
        
        included_df['match_key'] = match_keys
        
        # Count identifier types
        accession_count = included_df['match_key'].apply(lambda x: x.startswith('accession:')).sum()
        doi_count = included_df['match_key'].apply(lambda x: x.startswith('doi:')).sum()
        neither_count = included_df['match_key'].apply(lambda x: x.startswith('no_id:')).sum()
        
        print(f"\nIdentifier statistics:")
        print(f"  Records with Accession Number: {accession_count}")
        print(f"  Records with DOI: {doi_count}")
        print(f"  Records with neither: {neither_count}")
        
        print(f"Loaded {len(included_df)} included records from Covidence")
        return included_df
    
    def _create_accession_doi_match_key(self, df: pd.DataFrame) -> List[str]:
        """Create match keys using Accession Number OR DOI (priority: Accession > DOI)"""
        keys = []
        
        print(f"\nCreating match keys (Accession Number OR DOI) for {len(df)} records...")
        
        for idx, row in df.iterrows():
            # Helper function to safely handle NaN values
            def safe_get(field, default=''):
                if field in row:
                    value = row[field]
                else:
                    # Try case-insensitive match
                    field_lower = field.lower()
                    matching_fields = [col for col in row.index if str(col).lower() == field_lower]
                    if matching_fields:
                        value = row[matching_fields[0]]
                    else:
                        value = default
                return default if pd.isna(value) else str(value)
            
            # Helper function to clean identifier
            def clean_identifier(identifier: str, id_type: str) -> str:
                """Clean identifier for matching"""
                if not identifier or str(identifier).lower() == 'nan':
                    return ''
                
                # Remove extra spaces, lowercase, strip
                identifier = re.sub(r'\s+', ' ', str(identifier).strip()).lower()
                
                if id_type == 'accession':
                    # Remove common prefixes from accession numbers
                    identifier = re.sub(r'^(accession|acc|id|number|no):\s*', '', identifier)
                elif id_type == 'doi':
                    # Remove DOI prefixes and URLs
                    identifier = re.sub(r'^doi:\s*', '', identifier)
                    identifier = re.sub(r'https?://doi\.org/', '', identifier)
                    identifier = re.sub(r'https?://dx\.doi\.org/', '', identifier)
                
                return identifier
            
            # 1. Try Accession Number first (higher priority)
            accession = ''
            accession_key = ''
            
            # Try common column names for accession number
            possible_accession_columns = [
                'accession_number', 'accession', 'accession_no', 'accession#',
                'record_id', 'reference_id', 'id', 'unique_id'
            ]
            
            for col in possible_accession_columns:
                temp_accession = safe_get(col, '')
                if temp_accession and temp_accession.lower() != 'nan':
                    accession = temp_accession
                    break
            
            if accession:
                accession_clean = clean_identifier(accession, 'accession')
                if accession_clean and accession_clean != '':
                    accession_key = f"accession:{accession_clean}"
            
            # 2. Try DOI if no valid accession found
            doi = ''
            doi_key = ''
            
            if not accession_key:  # Only try DOI if we don't have a good accession
                possible_doi_columns = ['doi', 'digital_object_identifier', 'doi_number']
                
                for col in possible_doi_columns:
                    temp_doi = safe_get(col, '')
                    if temp_doi and temp_doi.lower() != 'nan':
                        doi = temp_doi
                        break
                
                if doi:
                    doi_clean = clean_identifier(doi, 'doi')
                    if doi_clean and doi_clean != '':
                        doi_key = f"doi:{doi_clean}"
            
            # 3. Determine final key
            if accession_key:
                key = accession_key
                key_type = "Accession"
            elif doi_key:
                key = doi_key
                key_type = "DOI"
            else:
                key = f"no_id:{idx}"
                key_type = "None"
            
            keys.append(key)
            
            # Debug: print first few keys
            if idx < 5:
                print(f"  Row {idx}: [{key_type}] '{key}'")
        
        print(f"Created {len(keys)} match keys total")
        return keys
    
    def _get_study_details(self, df: pd.DataFrame, keys: Set[str], source: str) -> List[Dict]:
        """Get detailed information for studies"""
        details = []
        
        for key in keys:
            matching_rows = df[df['match_key'] == key]
            if len(matching_rows) == 0:
                continue
                
            row = matching_rows.iloc[0]
            
            # Safely handle string conversion for all fields
            def safe_str(value, default=''):
                if pd.isna(value):
                    return default
                return str(value)
            
            def safe_truncate(value, max_length, default=''):
                if pd.isna(value):
                    return default
                value_str = str(value)
                if len(value_str) > max_length:
                    return value_str[:max_length] + '...'
                return value_str
            
            study_info = {
                'match_key': key,
                'title': safe_truncate(row.get('title', ''), 100),
                'authors': safe_truncate(row.get('authors', ''), 50),
                'year': safe_str(row.get('year', row.get('published_year', ''))),
                'doi': safe_str(row.get('doi', '')),
                'journal': safe_str(row.get('journal', '')),
                'covidence_nr': safe_str(row.get('covidence_#', row.get('covidence_nr', row.get('covidence', '')))),
                'accession_number': safe_str(row.get('accession_number', row.get('accession', '')))
            }
            
            if source == 'python':
                study_info['python_decision'] = safe_str(row.get('decision', ''))
                study_info['screening_reason'] = safe_str(row.get('reason', ''))
            elif source == 'common':
                study_info['python_decision'] = safe_str(row.get('decision', ''))
            
            details.append(study_info)
        
        return details
    
    def compare_screening_results(self, python_df: pd.DataFrame, covidence_df: pd.DataFrame) -> Dict:
        """Compare Python (include+maybe) with Covidence (included)"""
        
        print(f"\nPython include+maybe: {len(python_df)} records")
        print(f"Covidence included: {len(covidence_df)} records")
        
        # Find matches using match keys
        python_keys = set(python_df['match_key'])
        covidence_keys = set(covidence_df['match_key'])
        
        common_keys = python_keys & covidence_keys
        python_only_keys = python_keys - covidence_keys
        covidence_only_keys = covidence_keys - python_keys
        
        # Filter out 'no_id' keys from matches (these are not real matches)
        real_common_keys = [k for k in common_keys if not k.startswith('no_id:')]
        real_python_only_keys = [k for k in python_only_keys if not k.startswith('no_id:')]
        real_covidence_only_keys = [k for k in covidence_only_keys if not k.startswith('no_id:')]
        
        # Analyze match types
        accession_matches = [k for k in real_common_keys if k.startswith('accession:')]
        doi_matches = [k for k in real_common_keys if k.startswith('doi:')]
        
        print(f"\n=== MATCHING RESULTS ===")
        print(f"Total possible matches: {len(common_keys)}")
        print(f"Real matches (with identifiers): {len(real_common_keys)}")
        print(f"  - Matched by Accession Number: {len(accession_matches)}")
        print(f"  - Matched by DOI: {len(doi_matches)}")
        print(f"Python-only (no match in Covidence): {len(real_python_only_keys)}")
        print(f"Covidence-only (no match in Python): {len(real_covidence_only_keys)}")
        print(f"Records without identifiers (excluded from matching):")
        print(f"  - Python: {len(python_only_keys) - len(real_python_only_keys)}")
        print(f"  - Covidence: {len(covidence_only_keys) - len(real_covidence_only_keys)}")
        
        # Create detailed results
        comparison = {
            'summary': {
                'python_include_maybe': len(python_df),
                'covidence_included': len(covidence_df),
                'common_studies': len(real_common_keys),
                'common_by_accession': len(accession_matches),
                'common_by_doi': len(doi_matches),
                'python_only': len(real_python_only_keys),
                'covidence_only': len(real_covidence_only_keys),
                'agreement_rate': len(real_common_keys) / len(covidence_df) if len(covidence_df) > 0 else 0,
                'sensitivity': len(real_common_keys) / len(covidence_df) if len(covidence_df) > 0 else 0,
                'coverage': len(real_common_keys) / len(python_df) if len(python_df) > 0 else 0
            },
            'common_studies': self._get_study_details(python_df, set(real_common_keys), 'common'),
            'python_only': self._get_study_details(python_df, set(real_python_only_keys), 'python'),
            'covidence_only': self._get_study_details(covidence_df, set(real_covidence_only_keys), 'covidence'),
            'match_analysis': {
                'accession_matches': accession_matches,
                'doi_matches': doi_matches
            }
        }
        
        return comparison
    
    def generate_comparison_report(self, comparison: Dict):
        """Generate comprehensive comparison report"""
        
        # Print summary
        summary = comparison['summary']
        print(f"\n=== SCREENING COMPARISON: Python (include+maybe) vs Covidence (included) ===")
        print(f"Python include+maybe: {summary['python_include_maybe']}")
        print(f"Covidence included: {summary['covidence_included']}")
        print(f"\nCommon studies (matched by identifier): {summary['common_studies']}")
        print(f"  - Matched by Accession Number: {summary['common_by_accession']}")
        print(f"  - Matched by DOI: {summary['common_by_doi']}")
        print(f"\nStudies only in Python (no match in Covidence): {summary['python_only']}")
        print(f"Studies only in Covidence (no match in Python): {summary['covidence_only']}")
        print(f"\nAgreement rate: {summary['agreement_rate']:.1%}")
        print(f"Sensitivity (Python detecting Covidence inclusions): {summary['sensitivity']:.1%}")
        print(f"Coverage (Covidence inclusions in Python selection): {summary['coverage']:.1%}")
        
        # Save detailed results to Excel
        try:
            with pd.ExcelWriter('screening_comparison_accession_doi.xlsx', engine='openpyxl') as writer:
                
                # Summary sheet
                summary_df = pd.DataFrame([summary])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Common studies
                if comparison['common_studies']:
                    common_df = pd.DataFrame(comparison['common_studies'])
                    common_df.to_excel(writer, sheet_name='Common_Studies', index=False)
                
                # Python-only studies
                if comparison['python_only']:
                    python_only_df = pd.DataFrame(comparison['python_only'])
                    python_only_df.to_excel(writer, sheet_name='Python_Only', index=False)
                
                # Covidence-only studies
                if comparison['covidence_only']:
                    covidence_only_df = pd.DataFrame(comparison['covidence_only'])
                    covidence_only_df.to_excel(writer, sheet_name='Covidence_Only', index=False)
                
                # Match analysis
                match_df = pd.DataFrame({
                    'Match_Type': ['Accession Number', 'DOI'],
                    'Count': [summary['common_by_accession'], summary['common_by_doi']]
                })
                match_df.to_excel(writer, sheet_name='Match_Analysis', index=False)
            
            print(f"\nDetailed report saved to: screening_comparison_accession_doi.xlsx")
        except Exception as e:
            print(f"Error saving Excel file: {e}")
            # Fallback to CSV
            self._save_as_csv(comparison)
        
        # Save quick summary to CSV
        quick_summary = pd.DataFrame([summary])
        quick_summary.to_csv('screening_comparison_summary.csv', index=False)
        print(f"Quick summary saved to: screening_comparison_summary.csv")
    
    def _save_as_csv(self, comparison: Dict):
        """Save comparison results as separate CSV files"""
        if comparison['common_studies']:
            pd.DataFrame(comparison['common_studies']).to_csv('common_studies.csv', index=False)
        if comparison['python_only']:
            pd.DataFrame(comparison['python_only']).to_csv('python_only_studies.csv', index=False)
        if comparison['covidence_only']:
            pd.DataFrame(comparison['covidence_only']).to_csv('covidence_only_studies.csv', index=False)
        print("Comparison results saved as CSV files")
    
    def analyze_discrepancies(self, comparison: Dict):
        """Analyze reasons for discrepancies"""
        
        print(f"\n=== DISCREPANCY ANALYSIS ===")
        
        # Python-only studies (include+maybe but not in Covidence)
        if comparison['python_only']:
            print(f"\nStudies in Python (include+maybe) but not in Covidence ({len(comparison['python_only'])}):")
            
            # Count by decision type
            include_count = sum(1 for study in comparison['python_only'] if study.get('python_decision') == 'include')
            maybe_count = sum(1 for study in comparison['python_only'] if study.get('python_decision') == 'maybe')
            
            print(f"  - Include decisions: {include_count}")
            print(f"  - Maybe decisions: {maybe_count}")
            
            for i, study in enumerate(comparison['python_only'][:5], 1):  # Show first 5
                print(f"  {i}. [{study.get('python_decision', 'unknown')}] {study['title']}")
                print(f"     Accession: {study.get('accession_number', 'None')}")
                print(f"     DOI: {study.get('doi', 'None')}")
                print()
            
            if len(comparison['python_only']) > 5:
                print(f"  ... and {len(comparison['python_only']) - 5} more")
        
        # Covidence-only studies (in Covidence but not in Python include+maybe)
        if comparison['covidence_only']:
            print(f"\nStudies in Covidence but not in Python include+maybe ({len(comparison['covidence_only'])}):")
            for i, study in enumerate(comparison['covidence_only'][:5], 1):  # Show first 5
                print(f"  {i}. {study['title']}")
                print(f"     Accession: {study.get('accession_number', 'None')}")
                print(f"     DOI: {study.get('doi', 'None')}")
                print(f"     Covidence #: {study.get('covidence_nr', 'None')}")
                print()
            
            if len(comparison['covidence_only']) > 5:
                print(f"  ... and {len(comparison['covidence_only']) - 5} more")
        
        # Common studies analysis
        if comparison['common_studies']:
            print(f"\nCommon studies analysis ({len(comparison['common_studies'])}):")
            
            # Count by Python decision type in common studies
            include_common = sum(1 for study in comparison['common_studies'] if study.get('python_decision') == 'include')
            maybe_common = sum(1 for study in comparison['common_studies'] if study.get('python_decision') == 'maybe')
            
            print(f"  - Python 'include' decisions that matched Covidence: {include_common}")
            print(f"  - Python 'maybe' decisions that matched Covidence: {maybe_common}")
            print(f"  - 'Maybe' that turned out to be correct: {maybe_common/len(comparison['common_studies']):.1%}")

def main():
    """Main comparison workflow"""
    comparer = ScreeningComparison()
    
    # Load data
    print("Loading data...")
    
    try:
        # Your Python screening results (include + maybe)
        python_include_maybe = comparer.load_python_include_maybe('screening_decisions2.csv')
        
        # Covidence included studies
        covidence_included = comparer.load_covidence_included('included_covidence.csv')
        
        # Compare screening results
        print("\nComparing Python (include+maybe) with Covidence (included)...")
        comparison = comparer.compare_screening_results(python_include_maybe, covidence_included)
        
        # Generate reports
        comparer.generate_comparison_report(comparison)
        
        # Analyze discrepancies
        comparer.analyze_discrepancies(comparison)
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()