# User Guide: Cochrane AI Screening Tool

## 📋 Overview
The Cochrane AI Screening Tool is an AI-powered system to accelerate title/abstract screening for systematic reviews. This guide covers installation, usage, and interpretation of results.

## 🚀 Quick Start

### For Researchers (No Coding Required):
1. **Prepare your RIS file** from PubMed, Embase, or other databases
2. **Use our web interface** (coming soon) for instant screening
3. **Download results** in Covidence-compatible format

# User Guide

## Installation

```bash
# Clone repository
git clone https://github.com/jeanny4sonne/cochrane-ai-screening.git
cd cochrane-ai-screening

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install package
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
