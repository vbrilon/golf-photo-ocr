# Test Suite

Comprehensive unit tests for the Golf Photo OCR project covering all utility functions and main application components.

## Test Coverage

### `test_parsing.py` (15 tests)
- **Date conversion**: Valid formats, edge cases, invalid inputs, spacing variations
- **Yardage range parsing**: Various formats, embedded text, invalid patterns
- Tests both functions with verbose mode and error conditions

### `test_ocr_processing.py` (18 tests)  
- **OCR result scoring**: Proximity-based scoring, confidence weighting
- **Decimal preference**: Bonus system for decimal values when expected
- **Pattern matching**: Custom regex patterns vs numeric extraction
- **Edge cases**: Empty results, tie-breaking, coordinate calculations

### `test_validation.py` (17 tests)
- **Bounding box validation**: Coordinate bounds, format checking, dimension validation
- **Configuration validation**: Required metrics, structure validation, error handling
- **Error conditions**: Invalid formats, missing sections, coordinate limits

### `test_golf_ocr.py` (8 tests)
- **Integration testing**: Full workflow with mocked EasyOCR reader
- **Error handling**: Image loading failures, invalid configurations
- **Partial extraction**: Mixed success/failure scenarios
- **Configuration loading**: Pattern metrics, decimal preferences

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_parsing.py -v

# Run with coverage (if pytest-cov installed)
python -m pytest tests/ --cov=utils --cov=main

# Quick summary
python -m pytest tests/ -q
```

## Test Results

- **Total Tests**: 58
- **Success Rate**: 100%
- **Coverage**: All utility functions and main application components
- **Mocking**: EasyOCR reader and OpenCV functions properly mocked for isolation

## Test Philosophy

Tests focus on:
1. **Critical functions**: Parsing and OCR processing that affect accuracy
2. **Edge cases**: Invalid inputs, boundary conditions, error scenarios  
3. **Integration**: Full workflow validation with realistic mock data
4. **Regression protection**: Prevent future changes from breaking existing functionality

The test suite provides confidence for refactoring and ensures the 100% accuracy system remains reliable.