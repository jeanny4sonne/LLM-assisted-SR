#!/usr/bin/env python
"""
Script to clean output directories while preserving structure.
"""
import shutil
from pathlib import Path
import argparse

def clean_directory(dir_path: Path, preserve_structure: bool = True):
    """Clean a directory while optionally preserving its structure."""
    if not dir_path.exists():
        print(f"Directory does not exist: {dir_path}")
        return
    
    if preserve_structure:
        # Remove files but keep directory structure
        for item in dir_path.rglob("*"):
            if item.is_file():
                item.unlink()
                print(f"Removed file: {item}")
    else:
        # Remove entire directory
        shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True)
        print(f"Cleaned directory: {dir_path}")

def main():
    parser = argparse.ArgumentParser(description="Clean output directories")
    parser.add_argument("--all", action="store_true", help="Clean all output directories")
    parser.add_argument("--data", action="store_true", help="Clean data/output only")
    parser.add_argument("--logs", action="store_true", help="Clean logs directory")
    parser.add_argument("--models", action="store_true", help="Clean model cache")
    parser.add_argument("--preserve-structure", action="store_true", 
                       help="Preserve directory structure (only remove files)")
    
    args = parser.parse_args()
    
    # Define directories to clean
    directories = []
    
    if args.all or args.data:
        directories.append(Path("data/output"))
    
    if args.all or args.logs:
        directories.append(Path("logs"))
    
    if args.all or args.models:
        directories.append(Path(".cache/models"))
    
    if not directories:
        print("No directories specified. Use --help for options.")
        return
    
    # Clean each directory
    for dir_path in directories:
        clean_directory(dir_path, args.preserve_structure)

if __name__ == "__main__":
    main()