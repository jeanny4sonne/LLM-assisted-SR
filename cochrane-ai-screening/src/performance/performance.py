import re
#!/usr/bin/env python3
"""
Performance calculation module: choose best matched strategy
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from pathlib import Path
import json

class PerformanceCalculator:
    """Calculate screening performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        
    def calculate(self, python_csv: str, covidence_total_csv: str) -> Dict:
        """
        Calculate performance metrics
        - python_csv: Python screening decisions (include/maybe/exclude)
        - covidence_total_csv: Covidence decisions (included/excluded)
        """
        print("📊 Calculating performance metrics...")
        
        # Load data
        python_df = pd.read_csv(python_csv)
        covidence_df = pd.read_csv(covidence_total_csv)
        
        # Standardize
        python_df.columns = [col.lower().replace(' ', '_') for col in python_df.columns]
        covidence_df.columns = [col.lower().replace(' ', '_') for col in covidence_df.columns]
        
        # Create match keys (same as comparison.py)
        python_df['match_key'] = self._create_match_keys(python_df)
        covidence_df['match_key'] = self._create_match_keys(covidence_df)
        
        # Merge on match keys
        merged = pd.merge(python_df, covidence_df, on='match_key', 
                          suffixes=('_python', '_covidence'), how='inner')
        
        # Get decisions
        python_positive = merged[merged['decision_python'].isin(['include', 'maybe'])]
        python_negative = merged[merged['decision_python'] == 'exclude']
        
        covidence_positive = merged[merged['decision_covidence'].str.contains('include', na=False, case=False)]
        covidence_negative = merged[~merged['decision_covidence'].str.contains('include', na=False, case=False)]
        
        # Confusion matrix
        tp = len(python_positive[python_positive['match_key'].isin(covidence_positive['match_key'])])
        fp = len(python_positive[python_positive['match_key'].isin(covidence_negative['match_key'])])
        fn = len(python_negative[python_negative['match_key'].isin(covidence_positive['match_key'])])
        tn = len(python_negative[python_negative['match_key'].isin(covidence_negative['match_key'])])
        
        # Calculate metrics
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        f1 = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0
        
        self.metrics = {
            'true_positives': int(tp),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_negatives': int(tn),
            'sensitivity': float(sensitivity),
            'specificity': float(specificity),
            'precision': float(precision),
            'accuracy': float(accuracy),
            'f1_score': float(f1),
            'total_matched': len(merged)
        }
        
        return self.metrics
    
    def _create_match_keys(self, df: pd.DataFrame) -> List[str]:
        """Same as in comparison.py"""
        keys = []
        for idx, row in df.iterrows():
            key = None
            
            # Try Accession Number
            acc = str(row.get('accession_number', '')).strip()
            if acc and acc.lower() not in ['nan', '']:
                key = f"accession:{re.sub(r'\s+', '', acc.lower())}"
            
            # Try DOI
            if not key:
                doi = str(row.get('doi', '')).strip()
                if doi and doi.lower() not in ['nan', '']:
                    clean_doi = re.sub(r'https?://doi\.org/', '', doi.lower())
                    clean_doi = re.sub(r'^doi:', '', clean_doi)
                    key = f"doi:{clean_doi}"
            
            if not key:
                key = f"no_id:{idx}"
            
            keys.append(key)
        
        return keys
    
    def generate_report(self, output_dir: str, review_name: str = None):
        """Generate performance report"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save metrics
        metrics_file = output_path / "performance_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        # Create simple visualization
        self._create_visualization(output_path, review_name)
        
        print(f"✅ Performance report saved to: {output_path}")
    
    def _create_visualization(self, output_path: Path, review_name: str = None):
        """Create simple performance visualization"""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Metrics bar chart
        metrics_to_plot = ['sensitivity', 'specificity', 'precision', 'accuracy']
        values = [self.metrics[m] for m in metrics_to_plot]
        
        axes[0].bar(metrics_to_plot, values)
        axes[0].set_ylim(0, 1)
        axes[0].set_title(f'Performance Metrics: {review_name or ""}')
        axes[0].set_ylabel('Score')
        
        # Confusion matrix heatmap
        cm = [[self.metrics['true_positives'], self.metrics['false_positives']],
              [self.metrics['false_negatives'], self.metrics['true_negatives']]]
        
        sns.heatmap(cm, annot=True, fmt='d', ax=axes[1],
                    xticklabels=['Python Positive', 'Python Negative'],
                    yticklabels=['Covidence Positive', 'Covidence Negative'])
        axes[1].set_title('Confusion Matrix')
        
        plt.tight_layout()
        plt.savefig(output_path / 'performance_plot.png', dpi=150)
        plt.close()