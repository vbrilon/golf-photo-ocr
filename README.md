# Golf Photo OCR

Simple, accurate OCR system for extracting golf metrics from screenshots. Achieves **100% accuracy** on test data.

## What it does

Extracts 4 golf metrics from golf app screenshots:
- **Distance to Pin** (yards)
- **Carry** (yards) 
- **From Pin** (yards)
- **Strokes Gained** (+/- value)

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

Creates two files:
- `golf_ocr_results.json` - Complete results
- `golf_ocr_results.csv` - Spreadsheet format

## Requirements

- Python 3.8+
- ~1GB RAM (for OCR models)
- Golf app screenshots in PNG/JPG format

## Accuracy

**100% accuracy** on all test images. Direct decimal and sign extraction - no complex processing needed.

## Testing

Validate the system accuracy:

```bash
# Quick test (single image)
python test_validation.py --quick

# Full ground truth validation (all 15 test images)
python test_validation.py
```

## Support

- Check `docs/` folder for technical details
- Run with `--verbose` flag to see processing steps
- Ensure images show the 4 white metric boxes clearly
