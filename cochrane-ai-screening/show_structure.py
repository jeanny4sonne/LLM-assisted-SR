#!/usr/bin/env python3
import os
from pathlib import Path

def print_tree(directory, prefix="", depth=0, max_depth=4):
    """Print directory tree structure"""
    if depth > max_depth:
        return
    
    items = []
    try:
        items = list(Path(directory).iterdir())
    except:
        return
    
    # Sort: directories first, then files
    items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
    
    for i, item in enumerate(items):
        # Skip hidden files and common ignored patterns
        if item.name.startswith('.') or item.name in ['__pycache__', 'venv', '.git']:
            continue
        
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "
        
        print(f"{prefix}{connector}{item.name}")
        
        if item.is_dir():
            extension = "    " if is_last else "│   "
            print_tree(item, prefix + extension, depth + 1, max_depth)

if __name__ == "__main__":
    print("📁 Project Structure")
    print("=" * 50)
    print_tree(".", max_depth=4)
