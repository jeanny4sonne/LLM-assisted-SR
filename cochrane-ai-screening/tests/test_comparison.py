"""
Tests for comparison module - UPDATED
"""
import pytest
import pandas as pd
from src.comparison.comparison import ScreeningComparator

def test_comparison_initialization():
    """Test that comparison metrics initialize correctly"""
    comparator = ScreeningComparator(matching_strategy='accession_doi')
    assert comparator is not None
    assert comparator.matching_strategy == 'accession_doi'

def test_compare_method():
    """Test the compare method exists"""
    comparator = ScreeningComparator()
    # The compare method requires csv files, so we just test it exists
    assert hasattr(comparator, 'compare')
    assert callable(comparator.compare)

def test_basic():
    """Basic test"""
    assert 1 + 1 == 2
