## This is for performance metrics calculation
# changed to match by: accession number and doi
# running in Terminal: 
# cd /Volumes/Yang/AI_test/code_for_screening/deepseek_screen/performance_metrics #navigate to the working directory
# /opt/homebrew/bin/python3 -m venv venv # Create virtual environment
# source venv/bin/activate #Activate virtual environment
# pip install pandas numpy scikit-learn seaborn  # Install packages
# python performance6.py 2>&1 | tee output.txt  #save output

import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
from typing import List
from datetime import datetime

class FinalPerformanceCalculator:
    """
    Performance calculator with:
    1. Maybe records treated as "included" in Python screening
    2. SIMPLIFIED matching: ONLY Accession Number OR DOI
    3. Complete Covidence data (included + excluded)
    """
    
    def __init__(self):
        self.metrics = {}
        self.comparison = None
    
    def load_data(self, python_csv_path: str, covidence_csv_path: str):
        """Load and prepare data"""
        print("="*70)
        print("LOADING DATA")
        print("="*70)
        print("IMPORTANT: Python 'maybe' records are treated as 'included'")
        print("MATCHING: ONLY Accession Number or DOI (no title/author/year)")
        print("="*70)
        
        # Load Python data
        self.python_df = pd.read_csv(python_csv_path)
        self.python_df.columns = [col.lower().replace(' ', '_').replace('.', '_') for col in self.python_df.columns]
        print(f"Python screening data: {len(self.python_df)} records")
        
        # Load Covidence data with encoding detection
        self.covidence_df = self._load_with_encoding(covidence_csv_path)
        self.covidence_df.columns = [col.lower().replace(' ', '_').replace('.', '_') for col in self.covidence_df.columns]
        print(f"Covidence complete data: {len(self.covidence_df)} records (included + excluded)")
        
        return True
    
    def _load_with_encoding(self, file_path: str):
        """Load CSV with encoding detection"""
        encodings = ['latin1', 'iso-8859-1', 'cp1252', 'windows-1252', 'utf-8']
        
        for encoding in encodings:
            try:
                return pd.read_csv(file_path, encoding=encoding)
            except:
                continue
        
        return pd.read_csv(file_path, encoding='utf-8', errors='replace')
    
    def create_accession_doi_match_keys(self):
        """Create match keys using ONLY Accession Number or DOI"""
        print("\n" + "="*70)
        print("CREATING MATCH KEYS")
        print("="*70)
        print("USING ONLY: Accession Number OR DOI")
        print("="*70)
        
        # Create match keys
        self.python_df['match_key'] = self._create_accession_doi_key(self.python_df, 'Python')
        self.covidence_df['match_key'] = self._create_accession_doi_key(self.covidence_df, 'Covidence')
        
        # Count types of keys used
        python_keys = self.python_df['match_key']
        covidence_keys = self.covidence_df['match_key']
        
        python_accession = sum(1 for k in python_keys if k.startswith('accession:'))
        python_doi = sum(1 for k in python_keys if k.startswith('doi:'))
        python_none = sum(1 for k in python_keys if k.startswith('no_id:'))
        
        covidence_accession = sum(1 for k in covidence_keys if k.startswith('accession:'))
        covidence_doi = sum(1 for k in covidence_keys if k.startswith('doi:'))
        covidence_none = sum(1 for k in covidence_keys if k.startswith('no_id:'))
        
        print(f"\n=== IDENTIFIER STATISTICS ===")
        print(f"\nPython screening:")
        print(f"  Accession Number: {python_accession} ({python_accession/len(python_keys):.1%})")
        print(f"  DOI: {python_doi} ({python_doi/len(python_keys):.1%})")
        print(f"  No identifier: {python_none} ({python_none/len(python_keys):.1%})")
        
        print(f"\nCovidence data:")
        print(f"  Accession Number: {covidence_accession} ({covidence_accession/len(covidence_keys):.1%})")
        print(f"  DOI: {covidence_doi} ({covidence_doi/len(covidence_keys):.1%})")
        print(f"  No identifier: {covidence_none} ({covidence_none/len(covidence_keys):.1%})")
        
        # Get unique counts
        python_unique = len(set(self.python_df['match_key']))
        covidence_unique = len(set(self.covidence_df['match_key']))
        
        print(f"\nUnique keys:")
        print(f"  Python: {python_unique}")
        print(f"  Covidence: {covidence_unique}")
        
        # Show real matches (excluding 'no_id:' keys)
        python_real_keys = set([k for k in python_keys if not k.startswith('no_id:')])
        covidence_real_keys = set([k for k in covidence_keys if not k.startswith('no_id:')])
        common_real_keys = python_real_keys.intersection(covidence_real_keys)
        
        accession_matches = len([k for k in common_real_keys if k.startswith('accession:')])
        doi_matches = len([k for k in common_real_keys if k.startswith('doi:')])
        
        print(f"\n=== MATCHING POTENTIAL ===")
        print(f"Records with identifiers:")
        print(f"  Python: {len(python_real_keys)}")
        print(f"  Covidence: {len(covidence_real_keys)}")
        print(f"  Possible matches: {len(common_real_keys)}")
        print(f"    • Accession matches: {accession_matches}")
        print(f"    • DOI matches: {doi_matches}")
        
        return python_unique, covidence_unique
    
    def _create_accession_doi_key(self, df: pd.DataFrame, source_name: str) -> List[str]:
        """Create match keys using ONLY Accession Number or DOI"""
        keys = []
        accession_count = 0
        doi_count = 0
        none_count = 0
        
        for idx, row in df.iterrows():
            key = self._get_accession_or_doi_key(row, idx)
            keys.append(key)
            
            if key.startswith('accession:'):
                accession_count += 1
            elif key.startswith('doi:'):
                doi_count += 1
            else:
                none_count += 1
        
        print(f"\n{source_name} - Identifier types:")
        print(f"  Accession: {accession_count} ({accession_count/len(df):.1%})")
        print(f"  DOI: {doi_count} ({doi_count/len(df):.1%})")
        print(f"  None: {none_count} ({none_count/len(df):.1%})")
        
        return keys
    
    def _get_accession_or_doi_key(self, row, idx):
        """Get match key using ONLY Accession Number or DOI"""
        # Strategy 1: Accession Number (priority 1)
        accession_key = self._get_accession_key(row)
        if accession_key:
            return accession_key
        
        # Strategy 2: DOI (priority 2)
        doi_key = self._get_doi_key(row)
        if doi_key:
            return doi_key
        
        # No identifier found
        return f"no_id:{idx}"
    
    def _get_accession_key(self, row):
        """Create key from Accession Number"""
        # Try multiple column names for accession number
        accession_fields = [
            'accession_number', 'accession', 'accession_no', 'accession#',
            'record_id', 'reference_id', 'id', 'unique_id', 'accession_number'
        ]
        
        for field in accession_fields:
            accession = str(row.get(field, '')).strip()
            if not accession or accession.lower() in ['nan', 'none', '', 'null']:
                continue
            
            # Clean accession number
            accession_clean = accession.lower()
            
            # Remove common prefixes
            accession_clean = re.sub(r'^(accession|acc|id|number|no):\s*', '', accession_clean, flags=re.IGNORECASE)
            
            # Remove whitespace and special characters
            accession_clean = re.sub(r'\s+', '', accession_clean)
            
            if accession_clean and len(accession_clean) > 3:
                return f"accession:{accession_clean}"
        
        return None
    
    def _get_doi_key(self, row):
        """Create key from DOI"""
        # Try multiple column names for DOI
        doi_fields = ['doi', 'digital_object_identifier', 'doi_number', 'doi_id']
        
        for field in doi_fields:
            doi = str(row.get(field, '')).strip()
            if not doi or doi.lower() in ['nan', 'none', '', 'null']:
                continue
            
            # Clean DOI
            doi_clean = doi.lower()
            doi_clean = re.sub(r'^doi:\s*', '', doi_clean, flags=re.IGNORECASE)
            doi_clean = re.sub(r'https?://doi\.org/', '', doi_clean)
            doi_clean = re.sub(r'https?://dx\.doi\.org/', '', doi_clean)
            
            # Remove any remaining special characters
            doi_clean = re.sub(r'[^\w\./-]', '', doi_clean)
            
            if doi_clean and len(doi_clean) > 5:
                return f"doi:{doi_clean}"
        
        return None
    
    def calculate_performance(self):
        """Calculate ALL performance metrics"""
        print("\n" + "="*70)
        print("CALCULATING PERFORMANCE METRICS")
        print("="*70)
        print("IMPORTANT: Python 'maybe' records are treated as 'included'")
        print("MATCHING: ONLY Accession Number or DOI")
        print("="*70)
        
        # Create match keys if not already created
        if 'match_key' not in self.python_df.columns:
            self.create_accession_doi_match_keys()
        
        # Find decision columns
        python_decision_col = self._find_decision_column(self.python_df, ['decision'])
        covidence_decision_col = self._find_decision_column(self.covidence_df, ['decision', 'included', 'inclusion_decision'])
        
        if not python_decision_col:
            print("ERROR: No decision column found in Python data")
            return None
        
        if not covidence_decision_col:
            print("ERROR: No decision column found in Covidence data")
            print("Please ensure Covidence file has 'decision' column with 'include'/'exclude' values")
            return None
        
        print(f"Python decision column: '{python_decision_col}'")
        print(f"Covidence decision column: '{covidence_decision_col}'")
        
        # Get Python predictions - INCLUDE 'maybe' as POSITIVE (as you requested)
        python_positive = set(self.python_df[
            self.python_df[python_decision_col].astype(str).str.lower().str.contains('include|maybe', na=False, regex=True)
        ]['match_key'])
        
        python_negative = set(self.python_df[
            self.python_df[python_decision_col].astype(str).str.lower().str.contains('exclude', na=False)
        ]['match_key'])
        
        print(f"\nPython predictions (treating 'maybe' as included):")
        print(f"  Positive (include+maybe): {len(python_positive):,} records")
        print(f"  Negative (exclude only): {len(python_negative):,} records")
        
        # Count Python decisions
        include_count = len(self.python_df[
            self.python_df[python_decision_col].astype(str).str.lower().str.contains('include', na=False)
        ])
        maybe_count = len(self.python_df[
            self.python_df[python_decision_col].astype(str).str.lower().str.contains('maybe', na=False)
        ])
        exclude_count = len(self.python_df[
            self.python_df[python_decision_col].astype(str).str.lower().str.contains('exclude', na=False)
        ])
        
        print(f"  Include: {include_count:,}, Maybe: {maybe_count:,}, Exclude: {exclude_count:,}")
        
        # Get Covidence gold standard
        covidence_series = self.covidence_df[covidence_decision_col].astype(str).str.lower()
        
        covidence_positive = set(self.covidence_df[
            covidence_series.str.contains('include', na=False)
        ]['match_key'])
        
        covidence_negative = set(self.covidence_df[
            ~covidence_series.str.contains('include', na=False) & covidence_series.notna()
        ]['match_key'])
        
        print(f"\nCovidence gold standard:")
        print(f"  Included studies: {len(covidence_positive):,}")
        print(f"  Excluded studies: {len(covidence_negative):,}")
        
        # Find matches between datasets (EXCLUDE 'no_id:' keys - these are not real matches)
        python_keys = set(self.python_df['match_key'])
        covidence_keys = set(self.covidence_df['match_key'])
        common_keys = python_keys.intersection(covidence_keys)
        
        # Filter out 'no_id:' keys from analysis
        real_common_keys = [k for k in common_keys if not k.startswith('no_id:')]
        real_python_keys = [k for k in python_keys if not k.startswith('no_id:')]
        real_covidence_keys = [k for k in covidence_keys if not k.startswith('no_id:')]
        
        # Count matches by type
        accession_matches = len([k for k in real_common_keys if k.startswith('accession:')])
        doi_matches = len([k for k in real_common_keys if k.startswith('doi:')])
        
        print(f"\n=== MATCHING RESULTS ===")
        print(f"Total records with identifiers:")
        print(f"  Python: {len(real_python_keys)}")
        print(f"  Covidence: {len(real_covidence_keys)}")
        print(f"\nMatched studies (with identifiers): {len(real_common_keys):,}")
        print(f"  • Matched by Accession Number: {accession_matches}")
        print(f"  • Matched by DOI: {doi_matches}")
        print(f"  • Total matches: {len(real_common_keys)}")
        print(f"\nRecords without identifiers (cannot be matched):")
        print(f"  Python: {len(python_keys) - len(real_python_keys)}")
        print(f"  Covidence: {len(covidence_keys) - len(real_covidence_keys)}")
        
        # Calculate confusion matrix (ONLY for records with identifiers)
        true_positives = len([k for k in real_common_keys 
                             if k in python_positive and k in covidence_positive])
        false_positives = len([k for k in real_common_keys 
                              if k in python_positive and k in covidence_negative])
        false_negatives = len([k for k in real_common_keys 
                              if k in python_negative and k in covidence_positive])
        true_negatives = len([k for k in real_common_keys 
                             if k in python_negative and k in covidence_negative])
        
        total_comparisons = true_positives + false_positives + false_negatives + true_negatives
        
        print(f"\n=== CONFUSION MATRIX (based on {total_comparisons:,} matched studies with identifiers) ===")
        print(f"True Positives (TP): {true_positives:,}  - Python include/maybe, Covidence include")
        print(f"False Positives (FP): {false_positives:,} - Python include/maybe, Covidence exclude")
        print(f"False Negatives (FN): {false_negatives:,} - Python exclude, Covidence include")
        print(f"True Negatives (TN): {true_negatives:,}  - Python exclude, Covidence exclude")
        
        # Calculate ALL performance metrics
        sensitivity = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        specificity = true_negatives / (true_negatives + false_positives) if (true_negatives + false_positives) > 0 else 0
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        npv = true_negatives / (true_negatives + false_negatives) if (true_negatives + false_negatives) > 0 else 0
        accuracy = (true_positives + true_negatives) / total_comparisons if total_comparisons > 0 else 0
        f1_score = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0
        
        # Calculate Cohen's Kappa
        p_o = accuracy
        p_yes = (len([k for k in real_common_keys if k in python_positive]) / total_comparisons) * \
                (len([k for k in real_common_keys if k in covidence_positive]) / total_comparisons) if total_comparisons > 0 else 0
        p_no = (len([k for k in real_common_keys if k in python_negative]) / total_comparisons) * \
               (len([k for k in real_common_keys if k in covidence_negative]) / total_comparisons) if total_comparisons > 0 else 0
        p_e = p_yes + p_no
        cohens_kappa = (p_o - p_e) / (1 - p_e) if p_e != 1 else 0
        
        print(f"\n=== PERFORMANCE METRICS ===")
        print(f"Sensitivity (Recall): {sensitivity:.1%}  - Ability to identify included studies")
        print(f"Specificity: {specificity:.1%}         - Ability to identify excluded studies")
        print(f"Precision: {precision:.1%}           - Of Python's include/maybe, how many were actually included")
        print(f"Negative Predictive Value: {npv:.1%} - Of Python's exclude, how many were actually excluded")
        print(f"Accuracy: {accuracy:.1%}             - Overall agreement")
        print(f"F1 Score: {f1_score:.3f}                - Balance of precision and recall")
        print(f"Cohen's Kappa: {cohens_kappa:.3f}        - Agreement beyond chance")
        
        # Calculate workload reduction
        total_records = len(self.python_df)
        manual_review_with_tool = include_count + maybe_count  # Both include and maybe need review
        workload_reduction = exclude_count / total_records
        
        print(f"\n=== WORKLOAD ANALYSIS ===")
        print(f"Total records: {total_records:,}")
        print(f"Include decisions: {include_count:,} ({include_count/total_records:.1%})")
        print(f"Maybe decisions: {maybe_count:,} ({maybe_count/total_records:.1%})")
        print(f"Exclude decisions: {exclude_count:,} ({exclude_count/total_records:.1%})")
        print(f"Records needing manual review: {manual_review_with_tool:,} ({manual_review_with_tool/total_records:.1%})")
        print(f"Workload reduction: {workload_reduction:.1%}")
        
        # Store all metrics
        self.metrics = {
            # Confusion matrix
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'true_negatives': true_negatives,
            'total_comparisons': total_comparisons,
            
            # Performance metrics
            'sensitivity': sensitivity,
            'specificity': specificity,
            'precision': precision,
            'negative_predictive_value': npv,
            'accuracy': accuracy,
            'f1_score': f1_score,
            'cohens_kappa': cohens_kappa,
            
            # Workload metrics
            'total_records': total_records,
            'include_count': include_count,
            'maybe_count': maybe_count,
            'exclude_count': exclude_count,
            'manual_review_with_tool': manual_review_with_tool,
            'workload_reduction': workload_reduction,
            
            # Matching info
            'python_total': len(python_keys),
            'covidence_total': len(covidence_keys),
            'common_studies': len(real_common_keys),
            'accession_matches': accession_matches,
            'doi_matches': doi_matches,
            'matching_rate': len(real_common_keys) / len(covidence_keys) if len(covidence_keys) > 0 else 0,
            
            # Settings
            'treat_maybe_as_included': True,
            'matching_method': 'accession_or_doi_only'
        }
        
        # Store comparison data for visualizations
        self.comparison = {
            'python_total': len(self.python_df),
            'python_positive': len(python_positive),
            'python_negative': len(python_negative),
            'covidence_total': len(self.covidence_df),
            'covidence_positive': len(covidence_positive),
            'covidence_negative': len(covidence_negative),
            'common_keys': len(real_common_keys),
            'accession_matches': accession_matches,
            'doi_matches': doi_matches,
            'python_only': len(real_python_keys) - len(real_common_keys),
            'covidence_only': len(real_covidence_keys) - len(real_common_keys),
            'python_no_id': len(python_keys) - len(real_python_keys),
            'covidence_no_id': len(covidence_keys) - len(real_covidence_keys)
        }
        
        # Show what studies were matched
        if len(real_common_keys) > 0:
            print(f"\n=== MATCHED STUDIES ANALYSIS ===")
            print(f"Found {len(real_common_keys)} matched studies")
            
            # Show sample of matched studies
            print(f"\nSample of matched studies (first 3):")
            sample_count = 0
            for key in list(real_common_keys)[:3]:
                python_row = self.python_df[self.python_df['match_key'] == key]
                covidence_row = self.covidence_df[self.covidence_df['match_key'] == key]
                
                if len(python_row) > 0 and len(covidence_row) > 0:
                    python_row = python_row.iloc[0]
                    covidence_row = covidence_row.iloc[0]
                    
                    print(f"\n{sample_count + 1}. {python_row.get('title', '')[:80]}...")
                    print(f"   Python decision: {python_row.get(python_decision_col, '')}")
                    print(f"   Covidence decision: {covidence_row.get(covidence_decision_col, '')}")
                    print(f"   Match key: {key[:60]}...")
                    sample_count += 1
        
        return self.metrics
    
    def _find_decision_column(self, df, possible_names):
        """Find decision column in dataframe"""
        for name in possible_names:
            if name in df.columns:
                return name
        
        # Try pattern matching
        for col in df.columns:
            if any(word in col.lower() for word in ['decision', 'include', 'exclude', 'inclusion']):
                return col
        
        return None
    
    def calculate_time_efficiency(self, python_time_minutes: float, manual_time_hours: float):
        """Calculate time efficiency metrics"""
        manual_time_minutes = manual_time_hours * 60
        time_saved = manual_time_minutes - python_time_minutes
        percent_saved = time_saved / manual_time_minutes if manual_time_minutes > 0 else 0
        speed_increase = manual_time_minutes / python_time_minutes if python_time_minutes > 0 else 0
        
        time_metrics = {
            'python_time_minutes': python_time_minutes,
            'manual_time_hours': manual_time_hours,
            'manual_time_minutes': manual_time_minutes,
            'time_saved_minutes': time_saved,
            'time_saved_hours': time_saved / 60,
            'percent_saved': percent_saved,
            'speed_increase': speed_increase
        }
        
        self.metrics.update(time_metrics)
        
        print(f"\n=== TIME EFFICIENCY ===")
        print(f"Python screening: {python_time_minutes} minutes")
        print(f"Manual screening: {manual_time_hours:.1f} hours ({manual_time_minutes:.0f} minutes)")
        print(f"Time saved: {time_saved/60:.1f} hours ({time_saved:.0f} minutes)")
        print(f"Percent time saved: {percent_saved:.1%}")
        print(f"Speed increase: {speed_increase:.1f}x faster")
        
        return time_metrics
    
    def generate_dashboard(self, review_name=""):
        """Generate comprehensive visualization dashboard"""
        print("\n" + "="*70)
        print("GENERATING VISUALIZATION DASHBOARD")
        print("="*70)
        
        if not self.metrics or not self.comparison:
            print("Please calculate metrics first")
            return
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))
        fig.suptitle(f'Systematic Review Screening Performance: {review_name}\n(Python include+maybe vs Covidence | Matching: Accession Number or DOI only)', 
                    fontsize=14, fontweight='bold', y=0.98)
        
        # Define grid layout
        gs = fig.add_gridspec(3, 4, hspace=0.5, wspace=0.5)
        
        # 1. Performance Metrics
        ax1 = fig.add_subplot(gs[0, :2])
        metrics = ['Sensitivity', 'Specificity', 'Precision', 'Accuracy']
        values = [
            self.metrics['sensitivity'],
            self.metrics['specificity'],
            self.metrics['precision'],
            self.metrics['accuracy']
        ]
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        
        bars = ax1.bar(metrics, values, color=colors, edgecolor='black')
        ax1.set_ylim(0, 1)
        ax1.set_title('Core Performance Metrics', fontsize=14, fontweight='bold', pad=15)
        ax1.set_ylabel('Score', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Confusion Matrix
        ax2 = fig.add_subplot(gs[0, 2:])
        cm = np.array([
            [self.metrics['true_positives'], self.metrics['false_positives']],
            [self.metrics['false_negatives'], self.metrics['true_negatives']]
        ])
        
        sns.heatmap(cm, annot=True, fmt=',.0f', cmap='YlOrRd', 
                   xticklabels=['Python\nPositive\n(Include+Maybe)', 'Python\nNegative\n(Exclude)'],
                   yticklabels=['Covidence\nPositive\n(Included)', 'Covidence\nNegative\n(Excluded)'],
                   cbar_kws={'label': 'Count'}, ax=ax2, annot_kws={'size': 12})
        ax2.set_title(f'Confusion Matrix\n(Matched studies: {self.metrics["total_comparisons"]:,})', 
                     fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlabel('Predicted (Python)', fontsize=12, labelpad=10)
        ax2.set_ylabel('Actual (Covidence)', fontsize=12, labelpad=10)
        
        # 3. Decision Distribution
        ax3 = fig.add_subplot(gs[1, 0])
        labels = ['Include', 'Maybe', 'Exclude']
        sizes = [
            self.metrics['include_count'],
            self.metrics['maybe_count'],
            self.metrics['exclude_count']
        ]
        colors = ['#4CAF50', '#FF9800', '#F44336']
        
        wedges, texts, autotexts = ax3.pie(sizes, colors=colors, 
                                          autopct=lambda p: f'{p:.1f}%\n({int(p*sum(sizes)/100):,})',
                                          startangle=90, textprops={'fontsize': 10})
        ax3.set_title('Python Screening Decisions\n(Maybe treated as included)', fontsize=12, fontweight='bold', pad=12)
        ax3.legend(wedges, labels, title="Decisions", loc="center left",
                  bbox_to_anchor=(1.1, 0, 0.5, 1))
        
        # 4. Workload Reduction
        ax4 = fig.add_subplot(gs[1, 1])
        categories = ['Manual Review\n(Include+Maybe)', 'Auto-Excluded']
        counts = [
            self.metrics['manual_review_with_tool'],
            self.metrics['exclude_count']
        ]
        colors = ['#FF6B6B', '#4ECDC4']
        
        bars = ax4.bar(categories, counts, color=colors, edgecolor='black')
        ax4.set_title('Workload Distribution', fontsize=14, fontweight='bold', pad=12)
        ax4.set_ylabel('Number of Records', fontsize=12)
        ax4.grid(True, alpha=0.3, axis='y')
        
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.02*max(counts),
                    f'{count:,}', ha='center', va='bottom', fontweight='bold')
        
        reduction = self.metrics['workload_reduction']
        ax4.text(0.5, 0.95, f'Workload Reduction: {reduction:.1%}',
                transform=ax4.transAxes, ha='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
        
        # 5. Matching Results
        ax5 = fig.add_subplot(gs[1, 2])
        categories = ['Accession\nMatches', 'DOI\nMatches', 'No ID\n(No Match)']
        counts = [
            self.comparison['accession_matches'],
            self.comparison['doi_matches'],
            self.comparison['python_no_id'] + self.comparison['covidence_no_id']
        ]
        colors = ['#2196F3', '#FF9800', '#757575']
        
        bars = ax5.bar(categories, counts, color=colors, edgecolor='black')
        ax5.set_title('Matching by Identifier Type', fontsize=14, fontweight='bold', pad=12)
        ax5.set_ylabel('Number of Studies', fontsize=12)
        ax5.grid(True, alpha=0.5, axis='y')
        
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + 0.02*max(counts),
                    f'{count:,}', ha='center', va='bottom', fontweight='bold')
        
        total_matches = self.comparison['accession_matches'] + self.comparison['doi_matches']
        total_records = self.comparison['python_total'] + self.comparison['covidence_total']
        match_rate = total_matches / total_records * 2 if total_records > 0 else 0
        ax5.text(0.5, 0.95, f'Total Matches: {total_matches}',
                transform=ax5.transAxes, ha='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
        
        # 6. Time Efficiency
        ax6 = fig.add_subplot(gs[1, 3])
        if 'python_time_minutes' in self.metrics:
            methods = ['Manual\nScreening', 'Python\nScreening']
            times_hours = [
                self.metrics['manual_time_hours'],
                self.metrics['python_time_minutes'] / 60
            ]
            colors = ['#FF5252', '#4CAF50']
            
            bars = ax6.bar(methods, times_hours, color=colors, edgecolor='black')
            ax6.set_title('Time Efficiency', fontsize=14, fontweight='bold', pad=15)
            ax6.set_ylabel('Time (hours)', fontsize=12)
            ax6.grid(True, alpha=0.3, axis='y')
            
            for bar, hours in zip(bars, times_hours):
                height = bar.get_height()
                ax6.text(bar.get_x() + bar.get_width()/2., height + 0.02*max(times_hours),
                        f'{hours:.1f} h', ha='center', va='bottom', fontweight='bold')
            
            speed_up = self.metrics['speed_increase']
            ax6.text(0.5, 0.95, f'{speed_up:.1f}x faster',
                    transform=ax6.transAxes, ha='center', fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        
        # 7. Advanced Metrics
        ax7 = fig.add_subplot(gs[2, 0])
        metrics2 = ['F1 Score', 'Cohen\'s Kappa', 'NPV']
        values2 = [
            self.metrics['f1_score'],
            self.metrics['cohens_kappa'],
            self.metrics['negative_predictive_value']
        ]
        colors2 = ['#27AE60', '#8E44AD', '#E74C3C']
        
        bars = ax7.bar(metrics2, values2, color=colors2, edgecolor='black')
        ax7.set_ylim(0, 1)
        ax7.set_title('Advanced Metrics', fontsize=14, fontweight='bold', pad=15)
        ax7.set_ylabel('Score', fontsize=12)
        ax7.grid(True, alpha=0.3, axis='y')
        ax7.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars, values2):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 8. Summary
        ax8 = fig.add_subplot(gs[2, 1:])
        ax8.axis('off')
        
        summary_text = [
            "📊 PERFORMANCE SUMMARY",
            f"• Sensitivity: {self.metrics['sensitivity']:.1%}",
            f"• Specificity: {self.metrics['specificity']:.1%}",
            f"• F1 Score: {self.metrics['f1_score']:.3f}",
            f"• Cohen's Kappa: {self.metrics['cohens_kappa']:.3f}",
            "",
            "⚡ EFFICIENCY GAINS",
            f"• Workload Reduction: {self.metrics['workload_reduction']:.1%}",
            f"• Auto-excluded: {self.metrics['exclude_count']:,} records",
            f"• Manual review: {self.metrics['manual_review_with_tool']:,} records",
            "",
            "🔍 MATCHING (Accession/DOI only)",
            f"• Total Matches: {self.comparison['common_keys']:,}",
            f"  - Accession: {self.comparison['accession_matches']:,}",
            f"  - DOI: {self.comparison['doi_matches']:,}",
            f"• Python Records: {self.comparison['python_total']:,}",
            f"• Covidence Records: {self.comparison['covidence_total']:,}"
        ]
        
        if 'time_saved_hours' in self.metrics:
            summary_text.extend([
                "",
                "⏱️ TIME SAVINGS",
                f"• Time Saved: {self.metrics.get('time_saved_hours', 0):.1f} hours",
                f"• Speed Increase: {self.metrics.get('speed_increase', 0):.1f}x"
            ])
        
        summary_str = "\n".join(summary_text)
        ax8.text(0.02, 0.98, summary_str, transform=ax8.transAxes,
                fontsize=11, family='monospace', verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='whitesmoke', alpha=0.8))
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        fig.text(0.98, 0.02, f"Generated: {timestamp}", fontsize=9, ha='right', style='italic', alpha=0.7)
        
        plt.tight_layout()
        
        # Save figure
        filename = f'performance_accession_doi_only_{review_name.replace(" ", "_").lower()}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ Dashboard saved as: {filename}")
        
        return filename
    
    def print_final_summary(self, review_name=""):
        """Print final summary for Cochrane proposal"""
        print("\n" + "="*80)
        print(f"FINAL SUMMARY FOR COCHRANE PROPOSAL: {review_name}")
        print("="*80)
        print("Matching method: Accession Number or DOI only")
        print("="*80)
        
        print("\n✅ KEY FINDINGS:")
        print(f"1. The AI screening tool achieved {self.metrics['sensitivity']:.1%} sensitivity")
        print(f"   and {self.metrics['specificity']:.1%} specificity")
        print(f"2. Workload was reduced by {self.metrics['workload_reduction']:.1%}")
        print(f"3. {self.metrics['exclude_count']:,} of {self.metrics['total_records']:,} records auto-excluded")
        print(f"4. Only {self.metrics['manual_review_with_tool']:,} records require manual review")
        print(f"5. Matched {self.comparison['common_keys']:,} studies for performance calculation")
        print(f"   - Accession Number matches: {self.comparison['accession_matches']:,}")
        print(f"   - DOI matches: {self.comparison['doi_matches']:,}")
        
        if 'time_saved_hours' in self.metrics:
            print(f"6. Time saved: {self.metrics['time_saved_hours']:.1f} hours")
            print(f"7. Speed increase: {self.metrics['speed_increase']:.1f}x faster")
        
        print(f"\n📝 SUGGESTED WORDING FOR METHODS SECTION:")
        print("-" * 40)
        print(f'The AI-assisted screening tool demonstrated {self.metrics["sensitivity"]:.1%} sensitivity')
        print(f'and {self.metrics["specificity"]:.1%} specificity in identifying relevant studies.')
        print(f'Screening workload was reduced by {self.metrics["workload_reduction"]:.1%}, with')
        print(f'{self.metrics["exclude_count"]:,} records auto-excluded and only')
        print(f'{self.metrics["manual_review_with_tool"]:,} records requiring manual review.')
        print(f'Performance was calculated based on {self.comparison["common_keys"]:,} matched studies')
        print(f'using Accession Numbers and DOIs as unique identifiers.')
        
        if 'time_saved_hours' in self.metrics:
            print(f'Screening time was reduced from {self.metrics["manual_time_hours"]:.0f} hours')
            print(f'to {self.metrics["python_time_minutes"]} minutes, representing a')
            print(f'{self.metrics["speed_increase"]:.1f}-fold increase in efficiency.')

def analyze_final_review(python_file, covidence_total_file, review_name, python_time_min, manual_time_hrs):
    """Final analysis with Accession Number/DOI only matching"""
    print("\n" + "="*80)
    print(f"FINAL ANALYSIS: {review_name}")
    print("="*80)
    print("Using SIMPLIFIED matching: Accession Number OR DOI only")
    print("No title/author/year matching")
    print("Treating Python 'maybe' records as 'included'")
    print("="*80)
    
    # Initialize calculator
    calculator = FinalPerformanceCalculator()
    
    # Load data
    calculator.load_data(python_file, covidence_total_file)
    
    # Create match keys (Accession Number/DOI only)
    calculator.create_accession_doi_match_keys()
    
    # Calculate performance
    calculator.calculate_performance()
    
    # Calculate time efficiency
    calculator.calculate_time_efficiency(python_time_min, manual_time_hrs)
    
    # Generate dashboard
    dashboard_file = calculator.generate_dashboard(review_name)
    
    # Print final summary
    calculator.print_final_summary(review_name)
    
    return calculator

def main():
    """Main function"""
    print("="*80)
    print("FINAL PERFORMANCE CALCULATOR")
    print("="*80)
    print("With Accession Number/DOI matching only")
    print("No title/author/year matching")
    print("="*80)
    
    # Insulin Review
    print("\n" + "="*80)
    print("1. INSULIN ANALOGUES REVIEW")
    
    insulin_analysis = analyze_final_review(
        python_file='insulin_screening_decisions2.csv',
        covidence_total_file='insulin_total_covidence.csv',
        review_name='Insulin Analogues',
        python_time_min=9,
        manual_time_hrs=96
    )
    
    # Ask about GLP-1
    print("\n" + "="*80)
    response = input("\nAnalyze GLP-1 review? (y/n): ")
    
    if response.lower() == 'y':
        print("\n" + "="*80)
        print("2. GLP-1 RECEPTOR AGONISTS REVIEW")
        
        glp1_analysis = analyze_final_review(
            python_file='GLP1_screening_decisions_comprehensive.csv',
            covidence_total_file='GLP1_total_covidence.csv',
            review_name='GLP-1 Receptor Agonists',
            python_time_min=12,
            manual_time_hrs=720
        )
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\n✅ Files generated:")
    print("   • performance_accession_doi_only_*.png - Comprehensive dashboard")
    print("\n📋 For your Cochrane proposal:")
    print("   1. Use the sensitivity and specificity metrics")
    print("   2. Highlight the workload reduction percentage")
    print("   3. Include the time savings")
    print("   4. Note that matching was based only on Accession Numbers and DOIs")
    print("   5. Use the suggested wording in methods section")

if __name__ == "__main__":
    import os
    
    print("Checking required files...")
    
    files_to_check = [
        ('insulin_screening_decisions.csv', 'Python insulin decisions'),
        ('insulin_total_covidence.csv', 'Covidence insulin total (included+excluded)')
    ]
    
    for file, desc in files_to_check:
        if os.path.exists(file):
            print(f"✓ {desc}")
        else:
            print(f"✗ Missing: {file}")
    
    print("\n" + "="*80)
    
    # Run analysis
    main()