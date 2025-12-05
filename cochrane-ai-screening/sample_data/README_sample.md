# Sample Data for Testing

This folder contains sample data to test the complete Cochrane AI Screening workflow.

## 📊 Sample Study Characteristics
- **10 total studies** representing realistic mix
- **1 included study** (RCT on insulin therapy)
- **9 excluded studies** for various reasons

## 🧪 Testing Workflow

### Step 1: Screening
```bash
python ../code/screening_engine.py --input sample.ris --output my_screening.csv
