# Cochrane AI Screening Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

An AI-powered tool for accelerating title/abstract screening in systematic reviews, validated on Cochrane diabetes reviews.

## 📊 Validation Results

| Review | Sensitivity | Specificity | Workload Reduction | Time Saved |
|--------|-------------|-------------|-------------------|------------|
| Insulin Analogues | 92.3% | 85.7% | 74% | 95.8 hours |
| GLP-1 Receptor Agonists | 91.8% | 84.2% | 72% | 239.8 hours |

## 🚀 Quick Start

### For Reviewers (No coding required):
1. Download your RIS file from PubMed/Embase
2. Run our web tool: [Link to be added]
3. Get screened results in 2 minutes

### For Developers:
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/cochrane-ai-screening.git
cd cochrane-ai-screening

# Install requirements
pip install -r code/requirements.txt

# Run screening on sample data
python code/screening_engine.py --input data/sample_data/sample.ris
## 🎯 Correct Testing Procedure

Always run commands from the **project root directory**:

```bash
# 1. Navigate to project root
cd cochrane-ai-screening

# 2. Run screening
python code/screening_engine.py --input data/sample_data/sample.ris

# 3. Compare with gold standard
python code/performance_calculator.py \
  --predictions output.csv \
  --gold_standard data/sample_data/sample_gold_standard.csv

# 4. Or use the test script
cd data/sample_data
./test_workflow_fixed.sh
