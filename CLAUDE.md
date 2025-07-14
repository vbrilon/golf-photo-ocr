# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a golf photo OCR (Optical Character Recognition) project that extracts **9 specific metrics** from golf app screenshots:
- **Date** - Date from top of screen, converted to YYYYMMDD format
- **Shot ID** - Shot list ID number following # symbol  
- **Distance to Pin** - Distance to the pin in yards
- **Carry** - Carry distance in yards  
- **From Pin** - Distance from pin after shot in yards
- **Strokes Gained** - Strokes gained/lost metric
- **Yardage Range** - Yardage range for strokes gained analysis (e.g., "30-50")
- **Yardage From** - Lower bound of yardage range (e.g., "30")
- **Yardage To** - Upper bound of yardage range (e.g., "50")

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
- **Accuracy**: 100% on ground truth test set (40 images, 360 data points)

### **Bounding Box Configuration**
```python
metrics = {
    "DATE": {"bbox": [985, 41, 301, 116]},           # Date extraction (top center)
    "SHOT_ID": {"bbox": [60, 175, 84, 81]},          # Shot ID with # pattern
    "DISTANCE_TO_PIN": {"bbox": [184, 396, 175, 148]}, # Distance to pin
    "CARRY": {"bbox": [147, 705, 252, 145]},         # Carry distance
    "FROM_PIN": {"bbox": [188, 982, 170, 136]},      # From pin distance
    "STROKES_GAINED": {"bbox": [94, 1249, 323, 149]}, # Strokes gained (+/-)
    "YARDAGE_RANGE": {"bbox": [1783, 525, 150, 60]}  # Yardage range (right panel)
}
```

### **Key Features**
- **Pattern Matching**: Regex patterns for SHOT_ID (#3), DATE (JULY 1, 2025), and YARDAGE_RANGE (30-50 yds)
- **Date Conversion**: Automatic conversion from "JULY 1, 2025" → "20250701"
- **Sign Handling**: Proper +/- detection for strokes gained
- **Range Parsing**: Single extraction of "30-50 yds" generates 3 metrics (yardage_range, yardage_from, yardage_to)
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
- `yardage_range` - Yardage range (e.g., "30-50", "50-75")
- `yardage_from` - Lower bound of range (e.g., "30", "50")
- `yardage_to` - Upper bound of range (e.g., "50", "75")

## Ground Truth & Testing

### **Comprehensive Test Coverage**
- **40 test images** with complete ground truth data in `config.json`
- **360 total validation points** (9 metrics × 40 images)
- **100% accuracy** maintained across all metrics
- **Regression protection** for future development

### **Date Extraction Patterns**
- **July 1, 2025** → "20250701" (1 image)
- **July 10, 2025** → "20250710" (10 images)  
- **July 11, 2025** → "20250711" (16 images)
- **Missing dates** → "" (13 images without visible dates)

### **Validation Examples**
```
✅ 2025-07-01_1939_shot1.png: date=20250701, shot_id=3, distance_to_pin=38, carry=39.9, from_pin=6, sg_individual=+0.22, yardage_range="", yardage_from="", yardage_to=""
✅ 2025-07-12_1105_shot1.png: date=20250711, shot_id=1, distance_to_pin=66, carry=59.8, from_pin=20, sg_individual=-0.72, yardage_range="50-75", yardage_from="50", yardage_to="75"
✅ 2025-07-01_1942_shot1.png: date="", shot_id=25, distance_to_pin=40, carry=44.0, from_pin=13, sg_individual=-0.15, yardage_range="30-50", yardage_from="30", yardage_to="50"
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

### **Yardage Range Implementation**
**Challenge**: Extract yardage range like "30-50 yds" and parse into 3 separate metrics
**Solution**:
- Single bounding box [1783, 525, 150, 60] captures full text like "30-50 yds"
- Regex pattern: `(\d+-\d+)\s*(?:yards?|yds?)?` handles variations ("30-50 yds", "50-75 yards")
- Parse helper method `parse_yardage_range()` splits "30-50" into components
- Generates 3 output fields: yardage_range="30-50", yardage_from="30", yardage_to="50"
- Graceful handling of missing data (empty strings for all 3 fields)

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
- ✅ **100% Accuracy** on all 9 metrics
- ✅ **42 images processed** successfully  
- ✅ **Comprehensive testing** with full ground truth coverage (360 validation points)
- ✅ **Robust error handling** for missing data
- ✅ **Clean architecture** with minimal dependencies
- ✅ **Full documentation** and regression protection

## Future Development Guidelines

### **Adding New Metrics**
1. **Configuration First**: Add metric to `config.json` with bounding box coordinates
2. **Pattern Development**: Create regex pattern if structured data (like dates/IDs)
3. **Testing**: Test on sample images before full implementation
4. **Ground Truth**: Update all test images in `config.json` with new metric values
5. **Validation**: Ensure 100% accuracy maintained on existing metrics

### **Maintenance Checklist**
- Run full regression test: `python main.py --input-dir photos --output-dir output`
- Verify 100% success rate and output accuracy
- Monitor for golf app UI changes that might affect bounding boxes
- Update ground truth data if new test images are added
- Keep documentation current in both CLAUDE.md and PLAN.md

### **Troubleshooting Common Issues**
- **Empty extractions**: Check bounding box coordinates and OCR confidence
- **Pattern mismatches**: Verify regex patterns handle all text variations
- **Accuracy drops**: Compare against ground truth in `config.json`
- **New app versions**: UI changes may require bounding box adjustments