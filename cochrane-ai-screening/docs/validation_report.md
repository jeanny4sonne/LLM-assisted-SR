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
- **Total studies**: [Number] from `GLP1_all.ris`
- **Included studies**: [Number] from `included_covidence.csv`
- **Excluded studies**: [Number] from `glp1_total_covidence.csv`

### Review 2: Insulin Analogues  
- **Total studies**: [Number] from `short_acting_insulin_all.ris`
- **Included studies**: [Number] from `included_covidence.csv`
- **Excluded studies**: [Number] from `insulin_total_covidence.csv`

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
YG: For insulin review, all included studies had primary references, which were found in AI screening method. It even detected the four studies excluded by human screening and we didn't include those four for performance metrics; For GLP-1 RA review, tirzepatide had 9 included studies, liraglutide had 24 included studies, semaglutide had 18 included studies. Except one record (ROMANCE trial) being not found, AI method detected all the primary refereces. 
