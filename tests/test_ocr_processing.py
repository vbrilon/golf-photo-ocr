"""
Unit tests for OCR processing utilities.

Tests the extract_best_number function with various OCR result scenarios,
including proximity scoring, confidence weighting, pattern matching,
and decimal preference.
"""

import unittest
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ocr_processing import extract_best_number


class TestExtractBestNumber(unittest.TestCase):
    """Test cases for extract_best_number function."""
    
    def setUp(self):
        """Set up common test data."""
        # Box center for proximity testing
        self.box_center = (100.0, 100.0)
        
    def create_ocr_result(self, text: str, confidence: float, bbox_coords: tuple) -> tuple:
        """Helper to create mock OCR result tuple."""
        # EasyOCR bbox format: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
        x1, y1, x2, y2 = bbox_coords
        bbox = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        return (bbox, text, confidence)
    
    def test_empty_ocr_results(self):
        """Test with empty OCR results."""
        result = extract_best_number([], self.box_center)
        self.assertEqual(result, "")
        
    def test_no_numeric_text(self):
        """Test with OCR results containing no numeric text."""
        ocr_results = [
            self.create_ocr_result("hello", 0.9, (95, 95, 105, 105)),
            self.create_ocr_result("world", 0.8, (90, 90, 110, 110)),
            self.create_ocr_result("text", 0.7, (85, 85, 115, 115))
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "")
        
    def test_single_number(self):
        """Test with single numeric result."""
        ocr_results = [
            self.create_ocr_result("42", 0.9, (95, 95, 105, 105))
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")
        
    def test_multiple_numbers_proximity_scoring(self):
        """Test proximity-based scoring with multiple numbers."""
        ocr_results = [
            # Farther from center but higher confidence
            self.create_ocr_result("25", 0.95, (200, 200, 210, 210)),  # Distance ~141
            # Closer to center
            self.create_ocr_result("42", 0.85, (95, 95, 105, 105)),    # Distance ~7
            # Very far from center
            self.create_ocr_result("99", 0.90, (300, 300, 310, 310))   # Distance ~283
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")  # Should pick closest one
        
    def test_decimal_preference(self):
        """Test decimal preference when expect_decimal=True."""
        ocr_results = [
            # Integer at moderate distance
            self.create_ocr_result("42", 0.9, (110, 110, 120, 120)),     # Distance ~14.14
            # Decimal at farther distance but gets -10 bonus
            self.create_ocr_result("39.5", 0.8, (120, 120, 130, 130))  # Distance ~35.36, but -10 bonus = 25.36
        ]
        result = extract_best_number(ocr_results, self.box_center, expect_decimal=True)
        self.assertEqual(result, "42")  # Integer still wins because decimal bonus not enough
        
    def test_decimal_preference_wins(self):
        """Test decimal preference when the bonus is enough to win."""
        ocr_results = [
            # Integer at distance ~21.21
            self.create_ocr_result("42", 0.9, (115, 115, 125, 125)),     
            # Decimal at distance ~28.28, but -10 bonus = 18.28 (wins)
            self.create_ocr_result("39.5", 0.8, (120, 120, 130, 130))  
        ]
        result = extract_best_number(ocr_results, self.box_center, expect_decimal=True)
        self.assertEqual(result, "39.5")  # Decimal should win with bonus
        
    def test_no_decimal_preference(self):
        """Test that decimal preference doesn't apply when expect_decimal=False."""
        ocr_results = [
            # Integer closer to center
            self.create_ocr_result("42", 0.9, (95, 95, 105, 105)),     # Distance ~7
            # Decimal farther from center, no bonus
            self.create_ocr_result("39.5", 0.8, (120, 120, 130, 130))  # Distance ~28
        ]
        result = extract_best_number(ocr_results, self.box_center, expect_decimal=False)
        self.assertEqual(result, "42")  # Should pick closer integer
        
    def test_positive_negative_numbers(self):
        """Test handling of positive and negative numbers."""
        ocr_results = [
            self.create_ocr_result("-15", 0.9, (95, 95, 105, 105)),
            self.create_ocr_result("+20", 0.8, (110, 110, 120, 120))
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "-15")  # Should pick closer one
        
    def test_explicit_plus_sign_handling(self):
        """Test handling of explicit + signs in text."""
        ocr_results = [
            # Text with + sign but extracted value might not include it
            self.create_ocr_result("Score: +0.82", 0.9, (95, 95, 105, 105))
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "+0.82")  # Should preserve + sign
        
    def test_pattern_matching(self):
        """Test custom pattern matching."""
        shot_id_pattern = r"#\s*(\d+)"
        ocr_results = [
            self.create_ocr_result("#15", 0.9, (95, 95, 105, 105)),
            self.create_ocr_result("42", 0.95, (90, 90, 110, 110)),  # Higher confidence but no pattern match
            self.create_ocr_result("# 23", 0.8, (120, 120, 130, 130))  # Pattern match with space
        ]
        result = extract_best_number(ocr_results, self.box_center, pattern=shot_id_pattern)
        self.assertEqual(result, "15")  # Should pick first pattern match, not highest confidence "42"
        
    def test_pattern_confidence_scoring(self):
        """Test that pattern matches use confidence scoring instead of distance."""
        shot_id_pattern = r"#\s*(\d+)"
        ocr_results = [
            # Lower confidence, closer to center
            self.create_ocr_result("#15", 0.7, (95, 95, 105, 105)),
            # Higher confidence, farther from center (should win with pattern matching)
            self.create_ocr_result("#23", 0.9, (200, 200, 210, 210))
        ]
        result = extract_best_number(ocr_results, self.box_center, pattern=shot_id_pattern)
        self.assertEqual(result, "23")  # Should pick higher confidence when using pattern
        
    def test_mixed_numeric_formats(self):
        """Test various numeric formats."""
        ocr_results = [
            self.create_ocr_result("42", 0.9, (95, 95, 105, 105)),      # Integer
            self.create_ocr_result("39.5", 0.8, (100, 100, 110, 110)),  # Decimal
            self.create_ocr_result("-0.82", 0.85, (105, 105, 115, 115)), # Negative decimal
            self.create_ocr_result("+1.23", 0.7, (110, 110, 120, 120))   # Positive decimal
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")  # Should pick closest to center
        
    def test_numbers_in_text(self):
        """Test extracting numbers from text containing other characters."""
        ocr_results = [
            self.create_ocr_result("Score: 42 pts", 0.9, (95, 95, 105, 105)),
            self.create_ocr_result("Distance 39.5 yards", 0.8, (100, 100, 110, 110)),
            self.create_ocr_result("Value: -0.82", 0.85, (105, 105, 115, 115))
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")  # Should extract and pick closest
        
    def test_no_pattern_matches(self):
        """Test pattern matching when no results match the pattern."""
        shot_id_pattern = r"#\s*(\d+)"
        ocr_results = [
            self.create_ocr_result("42", 0.9, (95, 95, 105, 105)),     # No # symbol
            self.create_ocr_result("39.5", 0.8, (100, 100, 110, 110)), # No # symbol
        ]
        result = extract_best_number(ocr_results, self.box_center, pattern=shot_id_pattern)
        self.assertEqual(result, "")  # Should return empty string
        
    def test_verbose_mode(self):
        """Test that verbose mode doesn't affect output."""
        ocr_results = [
            self.create_ocr_result("42", 0.9, (95, 95, 105, 105))
        ]
        result = extract_best_number(ocr_results, self.box_center, verbose=True)
        self.assertEqual(result, "42")
        
    def test_bbox_center_calculation(self):
        """Test that bounding box center is calculated correctly."""
        # Create OCR result with known coordinates
        ocr_results = [
            self.create_ocr_result("42", 0.9, (80, 80, 120, 120))  # Center should be (100, 100)
        ]
        # Use exact center as box_center - should have 0 distance
        result = extract_best_number(ocr_results, (100.0, 100.0))
        self.assertEqual(result, "42")
        
    def test_tie_breaking(self):
        """Test tie-breaking when scores are very close."""
        ocr_results = [
            # Same distance, different confidence (should pick first one since distance-based scoring)
            self.create_ocr_result("42", 0.8, (95, 95, 105, 105)),
            self.create_ocr_result("39", 0.9, (95, 95, 105, 105))  # Same bbox = same distance
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")  # Should pick first one with same score
        
    def test_edge_case_coordinates(self):
        """Test edge cases with coordinate calculations."""
        # Very far coordinates
        ocr_results = [
            self.create_ocr_result("42", 0.9, (1000, 1000, 1010, 1010))
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")  # Should still work with large distances
        
        # Zero coordinates
        ocr_results = [
            self.create_ocr_result("42", 0.9, (0, 0, 10, 10))
        ]
        result = extract_best_number(ocr_results, (5.0, 5.0))
        self.assertEqual(result, "42")


if __name__ == '__main__':
    unittest.main()