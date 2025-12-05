#!/usr/bin/env python3
"""
Comparison module - compares included+maybe records from Python screening with included recordds from Covidence
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path
import logging

class ScreeningComparator:
    """Compare Python screening results with Covidence"""
    
    def __init__(self, matching_strategy: str = 'accession_doi'):
        self.matching_strategy = matching_strategy
        
    def compare(self, python_csv: str, covidence_csv: str) -> Dict:
        """
        Compare Python screening (include+maybe) with Covidence included
        """
        print("🔍 Comparing screening results...")
        
        # Load data
        python_df = self._load_and_prepare(python_csv, 'python')
        covidence_df = self._load_and_prepare(covidence_csv, 'covidence')
        
        # Create match keys
        python_df['match_key'] = self._create_match_keys(python_df)
        covidence_df['match_key'] = self._create_match_keys(covidence_df)
        
        # Find matches
        python_keys = set(python_df['match_key'])
        covidence_keys = set(covidence_df['match_key'])
        common_keys = python_keys.intersection(covidence_keys)
        
        # Filter real matches (not 'no_id')
        real_common = [k for k in common_keys if not k.startswith('no_id:')]
        
        comparison = {
            'python_total': len(python_df),
            'covidence_total': len(covidence_df),
            'common_studies': len(real_common),
            'python_only': len(python_keys - covidence_keys),
            'covidence_only': len(covidence_keys - python_keys)
        }
        
        return comparison
    
    def _load_and_prepare(self, csv_path: str, source: str) -> pd.DataFrame:
        """Load and prepare CSV data"""
        df = pd.read_csv(csv_path)
        
        # Standardize column names
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # Filter based on source
        if source == 'python':
            if 'decision' in df.columns:
                df = df[df['decision'].isin(['include', 'maybe'])]
        elif source == 'covidence':
            if 'decision' in df.columns:
                df = df[df['decision'].str.lower().str.contains('include', na=False)]
        
        return df
    
    def _create_match_keys(self, df: pd.DataFrame) -> List[str]:
        """Create match keys based on strategy"""
        keys = []
        
        for idx, row in df.iterrows():
            key = None
            
            # Try Accession Number first
            accession = str(row.get('accession_number', '')).strip()
            if accession and accession.lower() not in ['nan', '']:
                clean_acc = re.sub(r'\s+', '', accession.lower())
                key = f"accession:{clean_acc}"
            
            # Try DOI if no accession
            if not key:
                doi = str(row.get('doi', '')).strip()
                if doi and doi.lower() not in ['nan', '']:
                    clean_doi = re.sub(r'https?://doi\.org/', '', doi.lower())
                    clean_doi = re.sub(r'^doi:', '', clean_doi)
                    key = f"doi:{clean_doi}"
            
            # Fallback
            if not key:
                key = f"no_id:{idx}"
            
            keys.append(key)
        
        return keys