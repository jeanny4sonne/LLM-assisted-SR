# Update the main README to showcase the screening tool
cat > README.md << 'EOF'
# LLM-assisted Systematic Review (LLM-assisted-SR)

A comprehensive suite of AI tools for systematic review automation.

## 🎯 Available Tools

### 1. 📋 Cochrane AI Screening Tool (`cochrane-ai-screening/`)
**Status: ✅ Production Ready**

AI-assisted title/abstract screening for Cochrane systematic reviews.

#### Features:
- **Modular pipeline**: Screening → Comparison → Performance evaluation
- **Multiple reviews**: Pre-configured for GLP-1 and insulin analogue reviews
- **Comprehensive testing**: Full test suite with sample data
- **Configuration management**: YAML configs for different reviews
- **Reproducible**: Sample data included for testing

### 2. Future Extensions (`future-tools/`)
**Status: 🔨 In Development**
- Data extraction from PDFs
- Risk of bias assessment (RoB 2.0)
- GRADE certainty assessment

#### Quick Start:
```bash
cd cochrane-ai-screening
pip install -e .
python scripts/run1_screening.py --review sample