# Validation Report: Cochrane AI Screening Tool

## 📋 Executive Summary
This report validates the performance of the AI-assisted screening tool for Cochrane systematic reviews. The tool was evaluated on two systematic reviews: GLP-1 receptor agonists and insulin analogues.

## 🎯 Validation Objectives
1. Assess screening accuracy compared to human reviewers
2. Evaluate different matching strategies for study identification
3. Measure performance metrics (accuracy, precision, recall, F1-score)
4. Validate reproducibility across different reviews

## 📊 Validation Datasets

### Review 1: GLP-1 Receptor Agonists
- **Total studies**: [14882] from `GLP1_all.ris`
- **Included studies**: [670] from `included_covidence.csv`
- **Excluded studies**: [14212] from `glp1_total_covidence.csv`

### Review 2: Insulin Analogues  
- **Total studies**: [4416] from `short_acting_insulin_all.ris`
- **Included studies**: [56] from `included_covidence.csv`
- **Excluded studies**: [4360] from `insulin_total_covidence.csv`

## 🔧 Validation Methodology

### 1. Study Matching Strategy
- **Accession/DOI matching**: Primary method for study identification
- **Title/author matching**: Fallback method when accession not available
- **Manual verification**: Sample verification of automated matches

### 2. Performance Metrics Calculated
- **Accuracy**: (TP + TN) / (TP + TN + FP + FN)
- **Precision**: TP / (TP + FP)
- **Recall (Sensitivity)**: TP / (TP + FN)
- **Specificity**: TN / (TN + FP)
- **F1-Score**: 2 × (Precision × Recall) / (Precision + Recall)

### 3. Comparison Method
- AI screening decisions vs. human reviewer decisions (gold standard)
- Confusion matrix analysis
- Threshold optimization for inclusion/exclusion

## 📈 Results
# GLP-1 review
**Performance Metrics:**
- Matched with identifiers: 97.6%
- Sensitivity: 61.9% (95% CI: 57.8-65.8)
- Specificity: 95.5% (95% CI: 95.1-95.9)
- Precision: 39.1%
- Workload reduction: 93.1%
- Time saved: 719.8 hours (3600x faster)
- Records needing manual review: 1,034/14,881 (6.9%)

# Insulin review
**Performance Metrics:**
- Matched with identifiers: 98.9%
- Sensitivity: 58.2% (95% CI: 48.3-67.4)
- Specificity: 98.1% (95% CI: 97.6-98.5)
- Precision: 27.6%
- Workload reduction: 97.4%
- Time saved: 95.8 hours (640x faster)
- Records needing manual review: 116/4,415 (2.6%)

## Extra from author:
YG: For insulin review, all included trials could be found by the AI screening method. It even detected four previously included studies which were excluded by human screening. However, we didn't include those four for performance calculation; For GLP-1 RA review, AI method detected all except one (ROMANCE trial). 
