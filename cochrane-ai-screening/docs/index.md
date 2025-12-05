# Cochrane AI Screening Tool

## Overview
An AI-assisted screening tool for systematic reviews, specifically designed for Cochrane reviews of diabetes interventions.

## Quick Links
- [User Guide](user_guide.md)
- [API Documentation](api_documentation.md)
- [Validation Report](validation_report.md)

## Features
- Automated article screening using transformer models
- Comparison with human screening decisions
- Performance metrics and visualization
- Support for multiple review types (GLP-1, Insulin)

## Getting Started
```bash
# Install dependencies
pip install -r requirements.txt

# Run screening for GLP-1 review
python scripts/run1_screening.py --config config/glp1_config.yaml

# Run complete pipeline
python scripts/run_all.py --review both