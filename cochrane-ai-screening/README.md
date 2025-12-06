# Cochrane AI Screening Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

An AI-powered tool for accelerating title/abstract screening in systematic reviews, validated on two Cochrane reviews.

## 📊 Validation Results

| Review | Sensitivity | Specificity | Workload Reduction | Time Saved |
|--------|-------------|-------------|-------------------|------------|
| Insulin Analogues | 58.2% | 98.1% | 97.4% | 95.8 hours |
| GLP-1 Receptor Agonists | 61.9% | 95.5% | 93.1% | 719.8 hours |

## 🚀 Quick Start

### For Reviewers (No coding required):
1. Download your RIS file from PubMed/Embase
2. Run our web tool: [Link to be added]
3. Get screened results in 2 minutes

### For Developers:
```bash
# Clone repository
git clone https://github.com/jeanny4sonne/cochrane-ai-screening.git
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

## Acknowledgement
**Data Sharing**: We thank the Cochrane Evidence Synthesis Subunit Düsseldorf at Heinrich-Heine University Düsseldorf for providing access to completed systematic review datasets on GLP-1 receptor agonists (Articles with the following doi: 10.1002/14651858.CD016018; 10.1002/14651858.CD016017.; 10.1002/14651858.CD015092.pub2) and ultra-short-acting insulin analogues (unpublished). These datasets served as the gold standard for validating our AI screening tool. For data access requests, please contact guoyang2010@outlook.com.

**AI Tools**: AI screening was implemented using deepseek, ChatGPT, Gemini. The tool leverages large language models to simulate human screening decisions based on study titles and abstracts.
