"""
Integration tests for the main GolfOCR class.

Tests the GolfOCR class workflow with mocked EasyOCR reader to verify
proper orchestration of utility functions and image processing.
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, mock_open
import numpy as np

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import GolfOCR


class TestGolfOCR(unittest.TestCase):
    """Integration tests for GolfOCR class."""
    
    def setUp(self):
        """Set up test configuration and mock data."""
        self.test_config = {
            "metrics": {
                "DATE": {
                    "bbox": [985, 41, 301, 116],
                    "expect_decimal": False,
                    "pattern": "((?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\\s+\\d{1,2},\\s*\\d{4})"
                },
                "SHOT_ID": {
                    "bbox": [60, 175, 84, 81],
                    "expect_decimal": False,
                    "pattern": "#\\s*(\\d+)"
                },
                "DISTANCE_TO_PIN": {
                    "bbox": [184, 396, 175, 148],
                    "expect_decimal": False
                },
                "CARRY": {
                    "bbox": [147, 705, 252, 145],
                    "expect_decimal": True
                },
                "FROM_PIN": {
                    "bbox": [188, 982, 170, 136],
                    "expect_decimal": False
                },
                "STROKES_GAINED": {
                    "bbox": [94, 1249, 323, 149],
                    "expect_decimal": True
                },
                "YARDAGE_RANGE": {
                    "bbox": [1783, 525, 150, 60],
                    "expect_decimal": False,
                    "pattern": "(\\d+-\\d+)\\s*(?:yards?|yds?)?"
                }
            }
        }
        
        # Create temporary config file
        self.temp_config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_config, self.temp_config_file)
        self.temp_config_file.close()
        
    def tearDown(self):
        """Clean up temporary files."""
        os.unlink(self.temp_config_file.name)
        
    def create_mock_ocr_result(self, text: str, confidence: float, bbox_coords: tuple) -> tuple:
        """Helper to create mock OCR result."""
        x1, y1, x2, y2 = bbox_coords
        bbox = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        return (bbox, text, confidence)
        
    @patch('easyocr.Reader')
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    def test_successful_extraction(self, mock_cvtColor, mock_imread, mock_easyocr):
        """Test successful metric extraction from image."""
        # Mock image loading
        mock_image = np.zeros((1000, 2000, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = np.zeros((116, 301), dtype=np.uint8)  # Mock grayscale
        
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        
        # Define mock OCR responses for each metric
        mock_reader.readtext.side_effect = [
            # DATE
            [self.create_mock_ocr_result("JULY 1, 2025", 0.9, (10, 10, 100, 50))],
            # SHOT_ID  
            [self.create_mock_ocr_result("#15", 0.95, (5, 5, 50, 30))],
            # DISTANCE_TO_PIN
            [self.create_mock_ocr_result("42", 0.85, (20, 20, 80, 60))],
            # CARRY
            [self.create_mock_ocr_result("39.5", 0.88, (30, 30, 90, 70))],
            # FROM_PIN
            [self.create_mock_ocr_result("6", 0.92, (25, 25, 75, 65))],
            # STROKES_GAINED
            [self.create_mock_ocr_result("+0.22", 0.87, (35, 35, 95, 75))],
            # YARDAGE_RANGE
            [self.create_mock_ocr_result("30-50 yds", 0.90, (40, 10, 120, 40))]
        ]
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Extract from mock image
        result = ocr.extract_from_image("fake_image.png")
        
        # Verify results
        expected = {
            "date": "20250701",
            "shot_id": "15", 
            "distance_to_pin": "42",
            "carry": "39.5",
            "from_pin": "6",
            "sg_individual": "+0.22",
            "yardage_range": "30-50",
            "yardage_from": "30",
            "yardage_to": "50"
        }
        
        self.assertEqual(result, expected)
        
        # Verify EasyOCR was called for each metric
        self.assertEqual(mock_reader.readtext.call_count, 7)
        
    @patch('easyocr.Reader')
    @patch('cv2.imread')
    def test_image_loading_error(self, mock_imread, mock_easyocr):
        """Test error handling when image cannot be loaded."""
        # Mock image loading failure
        mock_imread.return_value = None
        
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Should raise ValueError for invalid image
        with self.assertRaises(ValueError) as context:
            ocr.extract_from_image("nonexistent.png")
            
        self.assertIn("Could not load image", str(context.exception))
        
    def test_invalid_config_file(self):
        """Test error handling for invalid config file."""
        with self.assertRaises(FileNotFoundError):
            GolfOCR(config_path="nonexistent_config.json")
            
    def test_invalid_config_structure(self):
        """Test error handling for invalid config structure."""
        # Create invalid config (missing metrics section)
        invalid_config = {"invalid": "config"}
        
        temp_invalid_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(invalid_config, temp_invalid_config)
        temp_invalid_config.close()
        
        try:
            with self.assertRaises(ValueError) as context:
                GolfOCR(config_path=temp_invalid_config.name)
            self.assertIn("metrics", str(context.exception))
        finally:
            os.unlink(temp_invalid_config.name)
            
    @patch('easyocr.Reader')
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    def test_empty_ocr_results(self, mock_cvtColor, mock_imread, mock_easyocr):
        """Test handling when OCR returns no results."""
        # Mock image loading
        mock_image = np.zeros((1000, 2000, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = np.zeros((116, 301), dtype=np.uint8)
        
        # Mock EasyOCR reader with empty results
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        mock_reader.readtext.return_value = []  # No OCR results
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Extract from mock image
        result = ocr.extract_from_image("fake_image.png")
        
        # All metrics should be empty strings
        expected = {
            "date": "",
            "shot_id": "",
            "distance_to_pin": "",
            "carry": "",
            "from_pin": "",
            "sg_individual": "",
            "yardage_range": "",
            "yardage_from": "",
            "yardage_to": ""
        }
        
        self.assertEqual(result, expected)
        
    @patch('easyocr.Reader')
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    def test_partial_extraction(self, mock_cvtColor, mock_imread, mock_easyocr):
        """Test when only some metrics can be extracted."""
        # Mock image loading
        mock_image = np.zeros((1000, 2000, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = np.zeros((116, 301), dtype=np.uint8)
        
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        
        # Mixed results - some successful, some empty
        mock_reader.readtext.side_effect = [
            # DATE - successful
            [self.create_mock_ocr_result("JULY 1, 2025", 0.9, (10, 10, 100, 50))],
            # SHOT_ID - no match
            [self.create_mock_ocr_result("some text", 0.8, (5, 5, 50, 30))],
            # DISTANCE_TO_PIN - successful
            [self.create_mock_ocr_result("42", 0.85, (20, 20, 80, 60))],
            # CARRY - empty
            [],
            # FROM_PIN - successful
            [self.create_mock_ocr_result("6", 0.92, (25, 25, 75, 65))],
            # STROKES_GAINED - successful
            [self.create_mock_ocr_result("-0.82", 0.87, (35, 35, 95, 75))],
            # YARDAGE_RANGE - no pattern match
            [self.create_mock_ocr_result("some yards", 0.90, (40, 10, 120, 40))]
        ]
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Extract from mock image
        result = ocr.extract_from_image("fake_image.png")
        
        # Verify partial results
        expected = {
            "date": "20250701",     # Successful
            "shot_id": "",          # No pattern match
            "distance_to_pin": "42", # Successful
            "carry": "",            # Empty OCR result
            "from_pin": "6",        # Successful
            "sg_individual": "-0.82", # Successful
            "yardage_range": "",    # No pattern match
            "yardage_from": "",     # Derived from yardage_range
            "yardage_to": ""        # Derived from yardage_range
        }
        
        self.assertEqual(result, expected)
        
    @patch('easyocr.Reader')
    def test_initialization_with_verbose(self, mock_easyocr):
        """Test initialization with verbose mode."""
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        
        # Should not raise any errors
        ocr = GolfOCR(verbose=True, config_path=self.temp_config_file.name)
        
        # Verify configuration loaded correctly
        self.assertEqual(len(ocr.labels), 7)
        self.assertEqual(len(ocr.boxes), 7)
        self.assertIn("CARRY", ocr.decimal_metrics)
        self.assertIn("STROKES_GAINED", ocr.decimal_metrics)
        
    @patch('easyocr.Reader')
    def test_pattern_metrics_loading(self, mock_easyocr):
        """Test that pattern metrics are loaded correctly."""
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Verify pattern metrics
        self.assertIn("DATE", ocr.pattern_metrics)
        self.assertIn("SHOT_ID", ocr.pattern_metrics)
        self.assertIn("YARDAGE_RANGE", ocr.pattern_metrics)
        
        # Verify non-pattern metrics don't have patterns
        self.assertIsNone(ocr.pattern_metrics.get("DISTANCE_TO_PIN"))
        self.assertIsNone(ocr.pattern_metrics.get("CARRY"))


if __name__ == '__main__':
    unittest.main()