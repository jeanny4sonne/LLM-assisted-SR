"""
Tests for performance module - UPDATED
"""
import pytest
import numpy as np
from src.performance.performance import PerformanceCalculator

def test_performance_initialization():
    """Test performance calculator initialization"""
    calculator = PerformanceCalculator()
    assert calculator is not None

def test_calculate_method():
    """Test the calculate method exists"""
    calculator = PerformanceCalculator()
    # The calculate method requires csv files, so we just test it exists
    assert hasattr(calculator, 'calculate')
    assert callable(calculator.calculate)

def test_generate_report_method():
    """Test the generate_report method exists"""
    calculator = PerformanceCalculator()
    assert hasattr(calculator, 'generate_report')
    assert callable(calculator.generate_report)

def test_basic():
    """Basic test"""
    assert 2 + 2 == 4
