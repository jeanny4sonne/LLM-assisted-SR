#!/usr/bin/env python3
"""
Check if all required dependencies are installed
"""
import sys
import subprocess

def check_python_version():
    """Check Python version"""
    required = (3, 8)
    current = sys.version_info[:2]
    
    if current < required:
        print(f"❌ Python {required[0]}.{required[1]}+ required. Found {current[0]}.{current[1]}")
        return False
    else:
        print(f"✅ Python {current[0]}.{current[1]} (>= {required[0]}.{required[1]} required)")
        return True

def check_package(package, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package
    
    try:
        __import__(import_name)
        print(f"✅ {package}")
        return True
    except ImportError:
        print(f"❌ {package} (missing)")
        return False

def main():
    print("Checking environment...")
    print("-" * 40)
    
    # Check Python
    if not check_python_version():
        return False
    
    print("\nChecking required packages:")
    print("-" * 40)
    
    required = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn"),
        ("transformers", "transformers"),
        ("torch", "torch"),
        ("pyyaml", "yaml"),
        ("rispy", "rispy"),
    ]
    
    all_ok = True
    for package, import_name in required:
        if not check_package(package, import_name):
            all_ok = False
    
    if not all_ok:
        print("\n❌ Some packages are missing.")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✅ All checks passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)