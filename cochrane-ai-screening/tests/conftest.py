import pytest
import pandas as pd
import tempfile
import yaml
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def sample_ris_data():
    """Fixture providing sample RIS data."""
    return """TY  - JOUR
TI  - Sample Article Title 1
AB  - This is a sample abstract for testing purposes.
AU  - Smith, J
PY  - 2023
KW  - clinical trial
KW  - diabetes
ER  - 

TY  - JOUR
TI  - Sample Article Title 2
AB  - Another abstract for testing the screening system.
AU  - Johnson, A
PY  - 2022
KW  - systematic review
ER  - """

@pytest.fixture
def sample_csv_data():
    """Fixture providing sample CSV data."""
    data = {
        'title': ['Study A', 'Study B', 'Study C'],
        'abstract': ['Abstract A', 'Abstract B', 'Abstract C'],
        'included': [1, 0, 1]
    }
    return pd.DataFrame(data)

@pytest.fixture
def temp_config_file():
    """Fixture providing a temporary config file."""
    config = {
        'screening': {
            'model_name': 'bert-base-uncased',
            'threshold': 0.5,
            'batch_size': 16
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        temp_path = f.name
    
    yield temp_path
    Path(temp_path).unlink(missing_ok=True)

@pytest.fixture
def sample_config():
    """Fixture providing sample configuration."""
    return {
        'review_type': 'intervention',
        'population': 'adults',
        'intervention': 'GLP-1 receptor agonists',
        'comparator': 'placebo',
        'outcomes': ['HbA1c', 'weight', 'hypoglycemia']
    }