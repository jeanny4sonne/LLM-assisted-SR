"""
Tests for screening module
"""
import pytest
from src.screening.screening import SystematicReviewScreener

def test_screening_initialization():
    """Test screener initialization"""
    screener = SystematicReviewScreener()
    assert screener is not None

def test_screen_method():
    """Test the screen method exists"""
    screener = SystematicReviewScreener()
    assert hasattr(screener, 'screen')
    assert callable(screener.screen)

def test_load_ris_method():
    """Test the load_ris_file method exists"""
    screener = SystematicReviewScreener()
    assert hasattr(screener, 'load_ris_file')
    assert callable(screener.load_ris_file)

def test_basic():
    """Basic test"""
    assert 3 + 3 == 6
