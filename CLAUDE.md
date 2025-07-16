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
├── main.py                 # Main CLI application (285 lines, orchestration)
├── config.json             # Configuration with bounding boxes and ground truth
├── utils/                  # Modular utility functions (2025-07-16)
│   ├── __init__.py         # Public API exports
│   ├── validation.py       # Config and bounding box validation
│   ├── parsing.py          # Date and yardage range parsing
│   └── ocr_processing.py   # OCR result extraction and scoring
├── test_validation.py      # Ground truth validation (100% accuracy)
├── photos/                 # Input images (40 golf app screenshots)
├── output/                 # Results (JSON and CSV files)
├── docs/
│   ├── PLAN.md            # Development priorities and todos
│   └── ANALYSIS.md        # Codebase analysis and recommendations
├── requirements.txt        # Python dependencies
└── .gitignore             # Git ignore patterns (Python project)
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

## Testing & Validation

### **Ground Truth System**
- Complete test coverage with ground truth data in `config.json`
- Validation framework via `test_validation.py` - run with `python test_validation.py`
- 100% accuracy on 40 images (360 data points)
- Type-safe validation with proper normalization
- Regression protection for code changes


## Development Workflow

### **Feature Development Process**
1. **Feature Branches**: Always work in separate branches (e.g., `feature/date-extraction`)
2. **Configuration First**: Add metrics to `config.json` before implementation
3. **Ground Truth Updates**: Update test data after successful implementation
4. **Regression Testing**: Ensure existing metrics maintain 100% accuracy
5. **User Consultation**: Consult before merging feature changes to main
6. **Clean up**: After the feature is merged into main branch, delete the feature branch when it's no longer needed

### **Development Best Practices**
- Always use feature branches for development work
- Run both main application and validation tests before merging
- Maintain 100% accuracy on regression tests
- Update documentation after architectural changes
- Clean up feature branches after successful merge to main
- Use existing pattern matching system for new metrics
- Leverage configuration-driven approach for all settings
- Update ground truth data immediately after successful extraction
- Maintain comprehensive test coverage for regression protection
- Document all discoveries and architectural decisions in this file

## Architecture & Technical Design

### **Current Architecture Strengths**
- **Single Responsibility**: Each method has clear, focused purpose with dedicated validation
- **Configuration-Driven**: All settings externalized to config.json with robust validation
- **Pattern-Based**: Successful use of regex patterns for structured data extraction
- **Robust Error Handling**: Specific exception types with contextual error messages and verbose debugging
- **Comprehensive Validation**: Input validation for bounding boxes, configuration structure validation
- **Testability**: Complete ground truth coverage enables regression protection

### **Modular Architecture (Updated 2025-07-16)**

**Main Application (`main.py` - 285 lines):**
- `GolfOCR` class focuses on orchestration and image processing workflow
- Configuration loading with validation delegation to utilities
- EasyOCR integration and bounding box extraction
- Output mapping and file operations

**Utility Modules (`utils/` package):**
- `validation.py`: Configuration structure and bounding box coordinate validation
- `parsing.py`: Date conversion and yardage range parsing with error handling
- `ocr_processing.py`: OCR result scoring algorithm and candidate selection
- `__init__.py`: Clean public API with explicit exports

**Benefits:**
- 47% code reduction in main application (535 → 285 lines)
- Single responsibility principle - each module has focused purpose
- Enhanced testability - utility functions can be tested independently
- Improved reusability - utilities available for future components

### **Key Technical Insights**
1. **EasyOCR superiority**: Neural OCR significantly outperforms Tesseract for this use case
2. **Hardcoded coordinates**: More reliable than dynamic region detection for consistent app layouts
3. **Pattern matching**: Essential for structured data like shot IDs and dates
4. **Configuration externalization**: Enables easy tuning without code changes
5. **Modular architecture**: Utility functions extracted for better organization and testability
6. **Single extraction approach**: Yardage range generates 3 metrics automatically
7. **Robust validation**: Comprehensive input validation with specific error messages
8. **Ground truth validation**: Complete test coverage enables confident code changes

## System Status

**Production Ready**: 100% accuracy on all 9 metrics (360/360 test points)
**Architecture**: Modular design with extracted utility functions for improved maintainability
**Code Quality**: Comprehensive validation, error handling, and regression protection

See `docs/PLAN.md` for development priorities and todos.

## Future Development Guidelines

### **Adding New Metrics**
1. **Configuration First**: Add metric to `config.json` with bounding box coordinates
2. **Pattern Development**: Create regex pattern if structured data (like dates/IDs)
3. **Testing**: Test on sample images before full implementation
4. **Ground Truth**: Update all test images in `config.json` with new metric values
5. **Validation**: Ensure 100% accuracy maintained on existing metrics


### **Maintenance Guidelines**
- Run full regression test: `python main.py --input-dir photos --output-dir output`
- Run validation test: `python test_validation.py` (verifies 100% accuracy against ground truth)
- Verify 100% success rate and output accuracy on both tests
- Monitor for golf app UI changes that might affect bounding boxes
- Update ground truth data if new test images are added
- Keep documentation current in both CLAUDE.md and PLAN.md
- Use feature branches for all development work (never work directly in main)
- Clean up feature branches after merging to main

### **Technical Reference**
- **Bounding box format**: `[x, y, width, height]` coordinates
- **Configuration file**: All settings in `config.json` including bounding boxes, patterns, and ground truth
- **Pattern matching**: Uses regex for structured data (shot IDs, dates, yardage ranges)
- **Output formats**: JSON and CSV files with all extracted metrics

### **Troubleshooting Common Issues**
- **Empty extractions**: Check bounding box coordinates and OCR confidence
- **Pattern mismatches**: Verify regex patterns handle all text variations
- **Accuracy drops**: Compare against ground truth in `config.json`
- **New app versions**: UI changes may require bounding box adjustments
