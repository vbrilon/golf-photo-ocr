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
- **Dependencies**: easyocr, opencv-python, numpy, pillow (cleaned up: removed pandas, matplotlib, pytest)
- **Environment Setup**: The project uses a Python virtual environment (venv)

## Project Structure

```
/
├── main.py                 # Main CLI application (EasyOCR-based system)
├── config.json             # Configuration with bounding boxes and ground truth
├── photos/                 # Input images (40 golf app screenshots)
├── test_validation.py      # Validation test with ground truth comparison
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

### **Test Coverage & Validation**
- **40 test images** with complete ground truth data in `config.json`
- **360 total validation points** (9 metrics × 40 images)
- **100% accuracy** maintained across all metrics
- **Run tests**: `python test_validation.py` for full validation
- **Type-safe validation**: Fixed comparison logic handles string/numeric type differences
- **Regression protection**: Validates system maintains accuracy after code changes

## Architecture Decisions & Discoveries

### **Key Technical Insights**
1. **EasyOCR superiority**: Neural OCR significantly outperforms Tesseract for this use case
2. **Hardcoded coordinates**: More reliable than dynamic region detection
3. **Pattern matching**: Essential for structured data like shot IDs and dates
4. **Configuration externalization**: Enables easy tuning without code changes
5. **Simple architecture**: ~300 lines total, 80% reduction from complex previous versions

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

## Code Quality & Technical Debt

### **Recent Code Quality Improvements** (2025-07-15)
- ✅ **Removed Dead Code**: Deleted `photos/detect.py` and debug images (debug.png, debug_largest_box.png)
- ✅ **Cleaned Dependencies**: Removed unused packages (pandas, matplotlib, pytest) from requirements.txt
- ✅ **Fixed Test Validation**: Resolved type comparison bugs in test_validation.py with proper normalization
- ⚠️ **Remaining Technical Debt**: Some config.json sections not actively used (typical_range, ocr_settings)

### **Architecture Strengths**
- **Single Responsibility**: Each method has clear, focused purpose
- **Configuration-Driven**: All settings externalized to config.json
- **Pattern-Based**: Successful use of regex patterns for structured data
- **Error Handling**: Graceful handling of missing data with empty strings
- **Testability**: Comprehensive ground truth enables regression protection

### **Next Recommended Improvements**
1. ✅ **Dead Code Removed**: Completed - deleted unused files and dependencies
2. ✅ **Test Validation Fixed**: Completed - resolved type comparison issues
3. **Input Validation**: Add validation for bounding box coordinates in GolfOCR constructor
4. **Error Handling**: Standardize exception handling patterns across methods
5. **Configuration Cleanup**: Remove unused fields from config.json
6. **Logging**: Replace print statements with proper logging framework

## System Status: Production Ready
- ✅ **100% Accuracy** on all 9 metrics
- ✅ **40 images processed** successfully (with full ground truth coverage)
- ✅ **Comprehensive testing** with full ground truth coverage (360 validation points)
- ✅ **Robust error handling** for missing data
- ✅ **Clean architecture** with minimal dependencies (recently cleaned up)
- ✅ **Full documentation** and regression protection
- ✅ **Code quality improvements** completed (dead code removal, dependency cleanup, test fixes)

## Future Development Guidelines

### **Adding New Metrics**
1. **Configuration First**: Add metric to `config.json` with bounding box coordinates
2. **Pattern Development**: Create regex pattern if structured data (like dates/IDs)
3. **Testing**: Test on sample images before full implementation
4. **Ground Truth**: Update all test images in `config.json` with new metric values
5. **Validation**: Ensure 100% accuracy maintained on existing metrics

### **Maintenance Checklist**
- Run full regression test: `python main.py --input-dir photos --output-dir output`
- Run validation test: `python test_validation.py` (verifies 100% accuracy against ground truth)
- Verify 100% success rate and output accuracy on both tests
- Monitor for golf app UI changes that might affect bounding boxes
- Update ground truth data if new test images are added
- Keep documentation current in both CLAUDE.md and PLAN.md
- Use feature branches for all development work (never work directly in main)

### **Troubleshooting Common Issues**
- **Empty extractions**: Check bounding box coordinates and OCR confidence
- **Pattern mismatches**: Verify regex patterns handle all text variations
- **Accuracy drops**: Compare against ground truth in `config.json`
- **New app versions**: UI changes may require bounding box adjustments