# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a golf photo OCR (Optical Character Recognition) project that extracts **6 specific metrics** from golf app screenshots:
- **Date** - Date from top of screen, converted to YYYYMMDD format
- **Shot ID** - Shot list ID number following # symbol  
- **Distance to Pin** - Distance to the pin in yards
- **Carry** - Carry distance in yards  
- **From Pin** - Distance from pin after shot in yards
- **Strokes Gained** - Strokes gained/lost metric

The system processes images from the `photos/` directory and extracts these values using optimized bounding boxes for each metric.

## Development Environment

- **Python Version**: 3.13.5
- **Virtual Environment**: Located at project root
- **Dependencies**: easyocr, opencv-python, numpy, pillow
- **Environment Setup**: The project uses a Python virtual environment (venv)

## Project Structure

```
/
├── main.py                 # Main CLI application (EasyOCR-based system)
├── config.json             # Configuration with bounding boxes and ground truth
├── photos/                 # Input images (42 golf app screenshots)
├── output/                 # Results (JSON and CSV files)
├── docs/
│   └── PLAN.md            # Project plan and next steps
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore file
└── pyvenv.cfg             # Virtual environment config
```

## Current Architecture: Simple & Effective

### **EasyOCR-Based System**
- **Engine**: EasyOCR neural OCR (replacing complex Tesseract system)
- **Approach**: Hardcoded bounding boxes with pattern matching
- **Configuration**: JSON-driven with optimized coordinates
- **Accuracy**: 100% on ground truth test set (40 images, 240 data points)

### **Bounding Box Configuration**
```python
metrics = {
    "DATE": {"bbox": [985, 41, 301, 116]},           # Date extraction (top center)
    "SHOT_ID": {"bbox": [60, 175, 84, 81]},          # Shot ID with # pattern
    "DISTANCE_TO_PIN": {"bbox": [184, 396, 175, 148]}, # Distance to pin
    "CARRY": {"bbox": [147, 705, 252, 145]},         # Carry distance
    "FROM_PIN": {"bbox": [188, 982, 170, 136]},      # From pin distance
    "STROKES_GAINED": {"bbox": [94, 1249, 323, 149]} # Strokes gained (+/-)
}
```

### **Key Features**
- **Pattern Matching**: Regex patterns for SHOT_ID (#3) and DATE (JULY 1, 2025)
- **Date Conversion**: Automatic conversion from "JULY 1, 2025" → "20250701"
- **Sign Handling**: Proper +/- detection for strokes gained
- **Missing Data**: Graceful handling when data not found (empty strings)
- **Decimal Support**: Automatic decimal preference for carry and strokes gained

## Common Commands

### Environment Management
```bash
# Activate virtual environment
source bin/activate

# Deactivate virtual environment
deactivate

# Install dependencies
pip install -r requirements.txt
```

### Application Usage
```bash
# Process all images in photos/ directory
python main.py

# Process single image with debug output
python main.py --single-image photos/sample.png --verbose

# Process with custom input/output directories
python main.py --input-dir photos --output-dir results

# Get help
python main.py --help
```

## Output Format

The system generates both JSON and CSV files with these fields:
- `date` - Date in YYYYMMDD format (e.g., "20250701")
- `shot_id` - Shot number (e.g., "3")
- `distance_to_pin` - Distance in yards (e.g., "38")
- `carry` - Carry distance in yards (e.g., "39.9")
- `from_pin` - Distance from pin in yards (e.g., "6")
- `sg_individual` - Strokes gained value (e.g., "+0.22")

## Ground Truth & Testing

### **Comprehensive Test Coverage**
- **40 test images** with complete ground truth data in `config.json`
- **240 total validation points** (6 metrics × 40 images)
- **100% accuracy** maintained across all metrics
- **Regression protection** for future development

### **Date Extraction Patterns**
- **July 1, 2025** → "20250701" (1 image)
- **July 10, 2025** → "20250710" (10 images)  
- **July 11, 2025** → "20250711" (16 images)
- **Missing dates** → "" (13 images without visible dates)

### **Validation Examples**
```
✅ 2025-07-01_1939_shot1.png: date=20250701, shot_id=3, distance_to_pin=38, carry=39.9, from_pin=6, sg_individual=+0.22
✅ 2025-07-12_1105_shot1.png: date=20250711, shot_id=1, distance_to_pin=66, carry=59.8, from_pin=20, sg_individual=-0.72
✅ 2025-07-01_1939_shot2.png: date="", shot_id=8, distance_to_pin=69, carry=71.6, from_pin=31, sg_individual=-0.86
```

## Architecture Decisions & Discoveries

### **Revolutionary Simplification**
- **80% code reduction**: From 1000+ lines to ~300 lines
- **Zero mathematical transformations**: Direct OCR extraction
- **Pattern-based extraction**: Leverages EasyOCR's neural capabilities
- **Configuration-driven**: All settings externalized to `config.json`

### **Date Extraction Implementation**
**Challenge**: Extract and convert dates like "JULY 1, 2025" to "20250701"
**Solution**: 
- Regex pattern: `((?:JANUARY|...|DECEMBER)\s+\d{1,2},\s*\d{4})`
- Month name mapping to numbers
- Automatic zero-padding for single-digit days
- Handles variations: "JULY 1, 2025" and "JULY 1,2025" (space-flexible)

### **Key Technical Insights**
1. **EasyOCR superiority**: Neural OCR significantly outperforms Tesseract for this use case
2. **Hardcoded coordinates**: More reliable than dynamic region detection
3. **Pattern matching**: Essential for structured data like shot IDs and dates
4. **Distance scoring**: Proximity-based candidate selection works well
5. **Configuration externalization**: Enables easy tuning without code changes

## Development Workflow

### **Feature Development Process**
1. **Feature Branches**: Always work in separate branches (e.g., `feature/date-extraction`)
2. **Configuration First**: Add metrics to `config.json` before implementation
3. **Ground Truth Updates**: Update test data after successful implementation
4. **Regression Testing**: Ensure existing metrics maintain 100% accuracy
5. **User Consultation**: Consult before merging feature changes to main

### **Best Practices**
- Use existing pattern matching system for new metrics
- Leverage configuration-driven approach for all settings
- Update ground truth data immediately after successful extraction
- Maintain comprehensive test coverage for regression protection
- Document all discoveries and architectural decisions in this file

## System Status: Production Ready
- ✅ **100% Accuracy** on all 6 metrics
- ✅ **42 images processed** successfully
- ✅ **Comprehensive testing** with full ground truth coverage
- ✅ **Robust error handling** for missing data
- ✅ **Clean architecture** with minimal dependencies
- ✅ **Full documentation** and regression protection