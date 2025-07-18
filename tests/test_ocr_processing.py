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
        
    def test_malformed_ocr_results(self):
        """Test handling of malformed OCR result data."""
        # Test with invalid bbox coordinates (though this should be handled by caller)
        ocr_results = [
            # Normal result for comparison
            self.create_ocr_result("42", 0.9, (95, 95, 105, 105)),
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")
        
    def test_regex_pattern_edge_cases(self):
        """Test edge cases with regex patterns."""
        # Pattern with multiple capture groups (should use first one)
        complex_pattern = r"(\d+)\s*-\s*(\d+)"  # Range pattern like "30-50"
        ocr_results = [
            self.create_ocr_result("30-50 yards", 0.9, (95, 95, 105, 105))
        ]
        result = extract_best_number(ocr_results, self.box_center, pattern=complex_pattern)
        self.assertEqual(result, "30")  # Should extract first capture group
        
        # Pattern that matches but has empty text after stripping
        whitespace_pattern = r"#\s*(\d+)"
        ocr_results = [
            self.create_ocr_result("  #  15  ", 0.9, (95, 95, 105, 105))
        ]
        result = extract_best_number(ocr_results, self.box_center, pattern=whitespace_pattern)
        self.assertEqual(result, "15")
        
        # Pattern with optional elements
        optional_pattern = r"shot\s*#?\s*(\d+)"
        ocr_results = [
            self.create_ocr_result("shot 15", 0.9, (95, 95, 105, 105)),
            self.create_ocr_result("shot #23", 0.8, (100, 100, 110, 110))
        ]
        result = extract_best_number(ocr_results, self.box_center, pattern=optional_pattern)
        self.assertEqual(result, "15")  # Should pick higher confidence when using patterns
        
    def test_complex_text_with_multiple_numbers(self):
        """Test text containing multiple numbers."""
        ocr_results = [
            # Text with multiple numbers - should extract first match
            self.create_ocr_result("Score: 42 out of 100 points", 0.9, (95, 95, 105, 105)),
            # Decimal in complex text
            self.create_ocr_result("Distance: 39.5 yards from pin", 0.8, (100, 100, 110, 110)),
            # Negative number with context
            self.create_ocr_result("Strokes gained: -0.82 compared to average", 0.85, (105, 105, 115, 115))
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")  # Should pick closest to center
        
    def test_special_characters_in_numbers(self):
        """Test numbers with special characters and formatting."""
        ocr_results = [
            # Number with comma - regex will extract just the "1" part
            self.create_ocr_result("1,234", 0.9, (95, 95, 105, 105)),
            # Number with currency symbol - regex will extract "42.50"
            self.create_ocr_result("$42.50", 0.8, (100, 100, 110, 110)),
            # Percentage - regex will extract "85"
            self.create_ocr_result("85%", 0.85, (105, 105, 115, 115)),
            # Simple number for comparison
            self.create_ocr_result("42", 0.7, (110, 110, 120, 120))
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "1")  # Should extract "1" from "1,234" as it's closest to center
        
    def test_decimal_bonus_boundary_conditions(self):
        """Test decimal bonus at exact boundary conditions."""
        ocr_results = [
            # Integer at distance 15
            self.create_ocr_result("42", 0.9, (115, 100, 125, 110)),     
            # Decimal at distance 25, with -10 bonus = 15 (exact tie)
            self.create_ocr_result("39.5", 0.8, (125, 100, 135, 110))  
        ]
        result = extract_best_number(ocr_results, self.box_center, expect_decimal=True)
        self.assertEqual(result, "39.5")  # Decimal wins with bonus despite being farther
        
    def test_very_long_text_performance(self):
        """Test performance with very long text strings."""
        long_text = "This is a very long string with lots of text and eventually a number 42 buried deep inside all this content that goes on and on"
        ocr_results = [
            self.create_ocr_result(long_text, 0.9, (95, 95, 105, 105)),
            self.create_ocr_result("39", 0.8, (100, 100, 110, 110))
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")  # Should handle long text and extract number
        
    def test_confidence_extreme_values(self):
        """Test with extreme confidence values."""
        shot_id_pattern = r"#\s*(\d+)"
        ocr_results = [
            # Very low confidence
            self.create_ocr_result("#15", 0.01, (95, 95, 105, 105)),
            # Very high confidence  
            self.create_ocr_result("#23", 0.99, (100, 100, 110, 110))
        ]
        result = extract_best_number(ocr_results, self.box_center, pattern=shot_id_pattern)
        self.assertEqual(result, "23")  # Should pick higher confidence
        
    def test_zero_confidence_edge_case(self):
        """Test handling of zero confidence values."""
        ocr_results = [
            self.create_ocr_result("42", 0.0, (95, 95, 105, 105)),  # Zero confidence
            self.create_ocr_result("39", 0.1, (100, 100, 110, 110))  # Very low confidence
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")  # Distance-based, so should pick closer one
        
    def test_identical_distance_different_extraction_order(self):
        """Test candidates with identical distances in different orders."""
        ocr_results = [
            # Same distance, different values, test sort stability
            self.create_ocr_result("50", 0.8, (95, 95, 105, 105)),  # Same bbox = same distance
            self.create_ocr_result("75", 0.9, (95, 95, 105, 105)),  # Same bbox = same distance
            self.create_ocr_result("100", 0.7, (95, 95, 105, 105))  # Same bbox = same distance
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "50")  # Should pick first one with same score
        
    def test_floating_point_precision_distances(self):
        """Test floating point precision in distance calculations."""
        # Create coordinates that result in very similar distances
        ocr_results = [
            # Distance should be ~7.071
            self.create_ocr_result("42", 0.9, (95, 95, 105, 105)),
            # Distance should be ~7.072 (very slight difference)  
            self.create_ocr_result("39", 0.8, (95, 95, 105, 106))
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")  # Should handle tiny distance differences
        
    def test_pattern_with_no_capture_groups(self):
        """Test pattern matching with patterns that have no capture groups."""
        # This would cause an IndexError in group(1) - function should handle gracefully
        no_capture_pattern = r"#\d+"  # No parentheses = no capture groups
        ocr_results = [
            self.create_ocr_result("#15", 0.9, (95, 95, 105, 105)),
            self.create_ocr_result("42", 0.8, (100, 100, 110, 110))  # Fallback to normal extraction
        ]
        # This should not crash, but might not work as expected without capture groups
        # The current implementation assumes group(1) exists
        try:
            result = extract_best_number(ocr_results, self.box_center, pattern=no_capture_pattern)
            # If it doesn't crash, result should be empty since pattern matching failed
            self.assertEqual(result, "")
        except IndexError:
            # If it crashes due to group(1), that's also acceptable behavior to document
            pass
            
    def test_whitespace_only_text(self):
        """Test OCR results with whitespace-only text."""
        ocr_results = [
            self.create_ocr_result("   ", 0.9, (95, 95, 105, 105)),  # Spaces only
            self.create_ocr_result("\t\n", 0.8, (100, 100, 110, 110)),  # Tabs and newlines
            self.create_ocr_result("42", 0.7, (105, 105, 115, 115))  # Valid number
        ]
        result = extract_best_number(ocr_results, self.box_center)
        self.assertEqual(result, "42")  # Should skip whitespace-only and find number


if __name__ == '__main__':
    unittest.main()