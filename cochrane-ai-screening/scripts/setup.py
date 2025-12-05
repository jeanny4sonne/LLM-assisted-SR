#!/usr/bin/env python3
"""
Setup script to create directory structure
"""

from pathlib import Path
import sys

def create_structure():
    base = Path.cwd()
    
    directories = [
        base / 'scripts',
        base / 'src' / 'screening',
        base / 'src' / 'comparison',
        base / 'src' / 'performance',
        base / 'data' / 'input' / 'insulin_review',
        base / 'data' / 'input' / 'glp1_review',
        base / 'data' / 'output' / 'insulin_review',
        base / 'data' / 'output' / 'glp1_review',
        base / 'config',
        base / 'notebooks',
        base / 'docs',
        base / 'tests'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created: {directory}")
    
    # Create __init__.py files
    init_files = [
        base / 'src' / '__init__.py',
        base / 'src' / 'screening' / '__init__.py',
        base / 'src' / 'comparison' / '__init__.py',
        base / 'src' / 'performance' / '__init__.py'
    ]
    
    for init_file in init_files:
        init_file.touch()
        print(f"Created: {init_file}")
    
    print("\n✅ Directory structure created successfully!")
    print("\nNext steps:")
    print("1. Copy your RIS files to data/input/")
    print("2. Create configuration files in config/")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Run screening: python scripts/run_screening.py --help")

if __name__ == "__main__":
    create_structure()