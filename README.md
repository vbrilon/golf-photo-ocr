# Golf Photo OCR

Simple, accurate OCR system for extracting golf metrics from screenshots. Achieves **100% accuracy** on test data.

## What it does

Extracts 9 golf metrics from golf app screenshots:
- **Date** (converted to YYYYMMDD format)
- **Shot ID** (shot list number)
- **Distance to Pin** (yards)
- **Carry** (yards) 
- **From Pin** (yards)
- **Strokes Gained** (+/- value)
- **Yardage Range** (e.g., "30-50", "50-75")
- **Yardage From** (lower bound of range)
- **Yardage To** (upper bound of range)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd golf-photo-ocr
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .
   source bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Single image
```bash
python main.py --single-image photos/your-image.png
```

### All images in directory
```bash
python main.py --input-dir photos --output-dir results
```

### With detailed output
```bash
python main.py --single-image photos/your-image.png --verbose
```

## Output

Creates two files with 9 metrics per image:
- `golf_ocr_results.json` - Complete results with all metrics
- `golf_ocr_results.csv` - Spreadsheet format for analysis

Example output:
```json
{
  "2025-07-12_1105_shot1.png": {
    "date": "20250711",
    "shot_id": "1", 
    "distance_to_pin": "66",
    "carry": "59.8",
    "from_pin": "20",
    "sg_individual": "-0.72",
    "yardage_range": "50-75",
    "yardage_from": "50", 
    "yardage_to": "75"
  }
}
```

## Requirements

- Python 3.8+
- ~1GB RAM (for OCR models)
- Golf app screenshots in PNG/JPG format

## Accuracy

**100% accuracy** on all 9 metrics across 40 test images (360 validation points). Uses EasyOCR neural engine with optimized bounding boxes and pattern matching.

## Testing

The project includes comprehensive testing at multiple levels:

### Unit Tests (97 tests)
Run the complete unit test suite:
```bash
# Run all unit tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_parsing.py -v        # Date & yardage parsing (31 tests)
python -m pytest tests/test_ocr_processing.py -v # OCR scoring algorithms (30 tests)
python -m pytest tests/test_validation.py -v     # Config validation (17 tests)
python -m pytest tests/test_golf_ocr.py -v       # Integration tests (19 tests)
```

### Ground Truth Validation (100% accuracy)
Test against known correct values from 40 images:
```bash
# Full ground truth validation (all 40 images)
python tests/test_ground_truth.py

# Quick validation (single image)
python tests/test_ground_truth.py --quick
```

### Integration Testing
Test the complete system workflow:
```bash
# Test single image with detailed output
python main.py --single-image photos/2025-07-12_1105_shot1.png --verbose

# Process all test images 
python main.py --input-dir photos --output-dir output
```

### Test Data
- **40 test images** with known correct values stored in `config.json`
- **360 validation points** (9 metrics × 40 images)
- **Ground truth data** manually verified for 100% accuracy baseline

## Architecture

- **Engine**: EasyOCR neural OCR system
- **Approach**: Configuration-driven hardcoded bounding boxes
- **Pattern matching**: Regex patterns for structured data (dates, shot IDs, yardage ranges)
- **Single extraction**: Yardage range generates 3 metrics automatically
- **Ground truth**: Complete validation dataset in `config.json`

## Support

- Check `CLAUDE.md` for comprehensive technical documentation
- Check `docs/PLAN.md` for implementation details and status
- Run with `--verbose` flag to see processing steps
- All bounding box coordinates and patterns configurable in `config.json`
