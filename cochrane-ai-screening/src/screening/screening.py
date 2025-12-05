#!/usr/bin/env python3
"""
Screening module
"""

import rispy
import pandas as pd
import numpy as np
import re
import yaml
import json
from typing import List, Dict, Tuple, Any
from pathlib import Path
import logging

class SystematicReviewScreener:
    """Main screening class"""
    
    def __init__(self, config_path: str = None):
        self.config = self.load_config(config_path)
        self.results = {}
        
    def load_config(self, config_path: str = None) -> Dict:
        """Load screening configuration"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'inclusion_terms': {'population': [], 'intervention': [], 'study_design': []},
            'exclusion_terms': {'population': [], 'intervention': [], 'study_design': []},
            'duration': {'minimum_days': 180, 'long_term': [], 'short_term': []},
            'rules': {'require_two_interventions': False, 'require_two_exclusions': False}
        }
    
    def load_ris_file(self, file_path: str) -> List[Dict]:
        """Load RIS file with encoding detection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return rispy.load(f)
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return rispy.load(f)
    
    def screen(self, ris_file_path: str, review_name: str = None) -> Dict:
        """
        Main screening function
        Returns: Dict with screening results
        """
        print(f"📚 Screening: {review_name or 'Unknown Review'}")
        print(f"   Input: {ris_file_path}")
        
        # Load records
        entries = self.load_ris_file(ris_file_path)
        print(f"   Loaded {len(entries)} records")
        
        # Screen each record
        results = {
            'include': [], 'maybe': [], 'exclude': [],
            'exclude_population': [], 'exclude_intervention': [],
            'exclude_design': [], 'exclude_duration': []
        }
        
        for i, entry in enumerate(entries, 1):
            decision, reason = self._screen_record(entry)
            entry['screening_decision'] = decision
            entry['screening_reason'] = reason
            
            if decision == 'include':
                results['include'].append(entry)
            elif decision == 'maybe':
                results['maybe'].append(entry)
            else:  # exclude
                results['exclude'].append(entry)
                if 'population' in reason:
                    results['exclude_population'].append(entry)
                elif 'intervention' in reason:
                    results['exclude_intervention'].append(entry)
                elif 'design' in reason:
                    results['exclude_design'].append(entry)
                elif 'duration' in reason:
                    results['exclude_duration'].append(entry)
        
        # Save to class
        self.results = results
        self.entries = entries
        
        return results
    
    def _screen_record(self, record: Dict) -> Tuple[str, str]:
        """
        Screen individual record
        Adapt this with YOUR EXACT LOGIC from original code
        """
        # THIS IS WHERE YOU PUT YOUR ORIGINAL SCREENING LOGIC
        # Copy the exact logic from your insulin_screening_original.py
        
        # For now, placeholder:
        text = f"{record.get('title', '')} {record.get('abstract', '')}".lower()
        
        # Your original logic here...
        # ... 
        
        return 'maybe', 'placeholder - insert your logic'
    
    def save_results(self, output_dir: str, review_name: str = None):
        """Save screening results"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save comprehensive CSV
        data = []
        for i, entry in enumerate(self.entries):
            data.append({
                'Title': entry.get('title', ''),
                'Authors': '; '.join(entry.get('authors', [])) if entry.get('authors') else '',
                'Abstract': entry.get('abstract', ''),
                'DOI': entry.get('doi', ''),
                'Accession_Number': entry.get('accession_number', ''),
                'Decision': entry.get('screening_decision', ''),
                'Reason': entry.get('screening_reason', ''),
                'RIS_ID': f"RIS_{i:04d}"
            })
        
        df = pd.DataFrame(data)
        csv_file = output_path / f"screening_decisions_{review_name or 'unknown'}.csv"
        df.to_csv(csv_file, index=False)
        
        # Save summary
        summary = {
            'review_name': review_name,
            'total_records': len(self.entries),
            'included': len(self.results['include']),
            'maybe': len(self.results['maybe']),
            'excluded': len(self.results['exclude']),
            'excluded_by_population': len(self.results['exclude_population']),
            'excluded_by_intervention': len(self.results['exclude_intervention']),
            'excluded_by_design': len(self.results['exclude_design']),
            'excluded_by_duration': len(self.results['exclude_duration'])
        }
        
        summary_file = output_path / "screening_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Results saved to: {output_path}")
        return summary