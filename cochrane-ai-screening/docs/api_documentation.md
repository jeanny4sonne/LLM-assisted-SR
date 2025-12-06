# API Documentation

## Screening Module

### `SystematicReviewScreener`
Main class for AI-assisted screening.

#### Methods
- `__init__(config_path=None)`: Initialize with optional config
- `load_ris_file(file_path)`: Load studies from RIS file
- `screen(ris_file_path, review_name=None)`: Screen all studies
- `save_results(output_dir, review_name=None)`: Save screening results

#### Example
```python
from screening import SystematicReviewScreener

screener = SystematicReviewScreener("config/glp1_config.yaml")
results = screener.screen("data/input/studies.ris")
screener.save_results("data/output/")