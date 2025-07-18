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
import cv2

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
        
    @patch('easyocr.Reader')
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    def test_image_cropping_and_preprocessing(self, mock_cvtColor, mock_imread, mock_easyocr):
        """Test image cropping and grayscale conversion."""
        # Mock image loading
        mock_image = np.zeros((1000, 2000, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        
        # Mock grayscale conversion
        mock_gray = np.zeros((116, 301), dtype=np.uint8)
        mock_cvtColor.return_value = mock_gray
        
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        mock_reader.readtext.return_value = [
            self.create_mock_ocr_result("42", 0.9, (10, 10, 50, 50))
        ]
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Extract from mock image
        result = ocr.extract_from_image("fake_image.png")
        
        # Verify cvtColor was called for each metric (7 times)
        self.assertEqual(mock_cvtColor.call_count, 7)
        
        # Verify that each call was with correct parameters
        for call in mock_cvtColor.call_args_list:
            args, kwargs = call
            self.assertEqual(len(args), 2)  # Should have crop and color conversion constant
            self.assertEqual(args[1], cv2.COLOR_BGR2GRAY)
            
    @patch('easyocr.Reader')
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    def test_box_center_calculation(self, mock_cvtColor, mock_imread, mock_easyocr):
        """Test that box center is calculated correctly for different bbox sizes."""
        # Mock image loading
        mock_image = np.zeros((1000, 2000, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = np.zeros((100, 100), dtype=np.uint8)
        
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        mock_reader.readtext.return_value = [
            self.create_mock_ocr_result("42", 0.9, (10, 10, 50, 50))
        ]
        
        # Create custom config with known bbox dimensions
        test_config = {
            "metrics": {
                "TEST_METRIC": {
                    "bbox": [100, 100, 200, 150],  # w=200, h=150
                    "expect_decimal": False
                },
                # Add required metrics to pass validation
                "DISTANCE_TO_PIN": {"bbox": [184, 396, 175, 148], "expect_decimal": False},
                "CARRY": {"bbox": [147, 705, 252, 145], "expect_decimal": True},
                "FROM_PIN": {"bbox": [188, 982, 170, 136], "expect_decimal": False},
                "STROKES_GAINED": {"bbox": [94, 1249, 323, 149], "expect_decimal": True}
            }
        }
        
        temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(test_config, temp_config)
        temp_config.close()
        
        try:
            ocr = GolfOCR(verbose=False, config_path=temp_config.name)
            result = ocr.extract_from_image("fake_image.png")
            
            # Verify result
            self.assertEqual(result["test_metric"], "42")
        finally:
            os.unlink(temp_config.name)
            
    @patch('easyocr.Reader')
    @patch('glob.glob')
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    @patch('os.makedirs')
    def test_directory_processing_success(self, mock_makedirs, mock_cvtColor, mock_imread, mock_glob, mock_easyocr):
        """Test successful directory processing workflow."""
        # Mock file discovery
        mock_glob.return_value = ["test1.png", "test2.png", "test3.png"]
        
        # Mock image loading
        mock_image = np.zeros((1000, 2000, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = np.zeros((116, 301), dtype=np.uint8)
        
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        mock_reader.readtext.return_value = [
            self.create_mock_ocr_result("42", 0.9, (10, 10, 50, 50))
        ]
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Mock save_results to avoid file system operations
        with patch.object(ocr, 'save_results') as mock_save:
            results = ocr.process_directory("fake_input_dir", "fake_output_dir")
            
            # Verify results
            self.assertEqual(len(results), 3)
            self.assertIn("test1.png", results)
            self.assertIn("test2.png", results)
            self.assertIn("test3.png", results)
            
            # Verify save_results was called
            mock_save.assert_called_once()
            
            # Verify directory creation
            mock_makedirs.assert_called_once_with("fake_output_dir", exist_ok=True)
            
    @patch('easyocr.Reader')
    @patch('glob.glob')
    def test_directory_processing_no_images(self, mock_glob, mock_easyocr):
        """Test directory processing when no images are found."""
        # Mock no files found
        mock_glob.return_value = []
        
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Mock save_results to avoid file system operations
        with patch.object(ocr, 'save_results') as mock_save:
            results = ocr.process_directory("empty_dir", "output_dir")
            
            # Verify empty results
            self.assertEqual(results, {})
            
            # Verify save_results was not called
            mock_save.assert_not_called()
            
    @patch('easyocr.Reader')
    @patch('glob.glob')
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    def test_directory_processing_mixed_results(self, mock_cvtColor, mock_imread, mock_glob, mock_easyocr):
        """Test directory processing with mixed success/failure."""
        # Mock file discovery
        mock_glob.return_value = ["good.png", "bad.png", "ugly.png"]
        
        # Mock image loading - some succeed, some fail
        def mock_imread_side_effect(path):
            if "bad.png" in path:
                return None  # Simulate loading failure
            return np.zeros((1000, 2000, 3), dtype=np.uint8)
        
        mock_imread.side_effect = mock_imread_side_effect
        mock_cvtColor.return_value = np.zeros((116, 301), dtype=np.uint8)
        
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        mock_reader.readtext.return_value = [
            self.create_mock_ocr_result("42", 0.9, (10, 10, 50, 50))
        ]
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Mock save_results to avoid file system operations
        with patch.object(ocr, 'save_results') as mock_save:
            results = ocr.process_directory("mixed_dir", "output_dir")
            
            # Verify results
            self.assertEqual(len(results), 3)
            
            # Verify successful extractions
            self.assertIn("good.png", results)
            self.assertIn("ugly.png", results)
            self.assertNotIn("error", results["good.png"])
            self.assertNotIn("error", results["ugly.png"])
            
            # Verify failed extraction
            self.assertIn("bad.png", results)
            self.assertIn("error", results["bad.png"])
            self.assertIn("Could not load image", results["bad.png"]["error"])
            
    @patch('easyocr.Reader') 
    def test_save_results_json_csv(self, mock_easyocr):
        """Test save_results method creates both JSON and CSV files."""
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Test data
        test_results = {
            "test1.png": {
                "date": "20250701",
                "shot_id": "1",
                "carry": "42.5"
            },
            "test2.png": {
                "date": "20250701",
                "shot_id": "2", 
                "carry": "39.0"
            }
        }
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save results
            ocr.save_results(test_results, temp_dir)
            
            # Verify JSON file exists and has correct content
            json_path = os.path.join(temp_dir, "golf_ocr_results.json")
            self.assertTrue(os.path.exists(json_path))
            
            with open(json_path, 'r') as f:
                saved_json = json.load(f)
            self.assertEqual(saved_json, test_results)
            
            # Verify CSV file exists and has correct content
            csv_path = os.path.join(temp_dir, "golf_ocr_results.csv")
            self.assertTrue(os.path.exists(csv_path))
            
            with open(csv_path, 'r') as f:
                csv_content = f.read()
            
            # Check CSV headers and data
            self.assertIn("filename", csv_content)
            self.assertIn("carry", csv_content)
            self.assertIn("date", csv_content)
            self.assertIn("shot_id", csv_content)
            self.assertIn("test1.png", csv_content)
            self.assertIn("test2.png", csv_content)
            self.assertIn("42.5", csv_content)
            self.assertIn("39.0", csv_content)
            
    @patch('easyocr.Reader')
    def test_save_results_with_errors(self, mock_easyocr):
        """Test save_results handles results with errors correctly."""
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        # Test data with errors
        test_results = {
            "good.png": {
                "date": "20250701",
                "shot_id": "1"
            },
            "bad.png": {
                "error": "Could not load image"
            }
        }
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save results
            ocr.save_results(test_results, temp_dir)
            
            # Verify CSV excludes error entries from data rows
            csv_path = os.path.join(temp_dir, "golf_ocr_results.csv")
            with open(csv_path, 'r') as f:
                csv_content = f.read()
            
            # Error should not be in headers
            self.assertNotIn("error", csv_content.split('\n')[0])
            
            # But filenames should still be present
            self.assertIn("good.png", csv_content)
            self.assertIn("bad.png", csv_content)
            
    @patch('easyocr.Reader')
    def test_save_results_io_error(self, mock_easyocr):
        """Test save_results handles IO errors gracefully."""
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        
        # Create GolfOCR instance
        ocr = GolfOCR(verbose=False, config_path=self.temp_config_file.name)
        
        test_results = {"test.png": {"metric": "value"}}
        
        # Test with invalid directory (should raise ValueError)
        with self.assertRaises(ValueError) as context:
            ocr.save_results(test_results, "/nonexistent/readonly/path")
        
        self.assertIn("Failed to save JSON results", str(context.exception))
        
    @patch('easyocr.Reader')
    @patch('cv2.imread')
    @patch('cv2.cvtColor') 
    def test_verbose_mode_output(self, mock_cvtColor, mock_imread, mock_easyocr):
        """Test verbose mode provides detailed output during extraction."""
        # Mock image loading
        mock_image = np.zeros((1000, 2000, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = np.zeros((116, 301), dtype=np.uint8)
        
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        mock_reader.readtext.return_value = [
            self.create_mock_ocr_result("JULY 1, 2025", 0.9, (10, 10, 50, 50))
        ]
        
        # Create GolfOCR instance in verbose mode
        ocr = GolfOCR(verbose=True, config_path=self.temp_config_file.name)
        
        # Capture stdout to verify verbose output
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            result = ocr.extract_from_image("test.png")
            
            # Restore stdout
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            # Verify verbose output contains expected messages
            self.assertIn("Processing: test.png", output)
            self.assertIn("Extracting DATE", output)
            self.assertIn("Converted date to", output)
            self.assertIn("Result:", output)
            
        finally:
            sys.stdout = sys.__stdout__
            
    @patch('easyocr.Reader')
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    def test_extraction_with_boundary_coordinates(self, mock_cvtColor, mock_imread, mock_easyocr):
        """Test extraction with boundary bbox coordinates."""
        # Mock image loading
        mock_image = np.zeros((1000, 2000, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = np.zeros((1, 1), dtype=np.uint8)
        
        # Mock EasyOCR reader
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        mock_reader.readtext.return_value = [
            self.create_mock_ocr_result("42", 0.9, (0, 0, 1, 1))
        ]
        
        # Create config with boundary coordinates
        boundary_config = {
            "metrics": {
                "BOUNDARY_TEST": {
                    "bbox": [0, 0, 1, 1],  # Minimal bbox
                    "expect_decimal": False
                },
                # Add required metrics to pass validation
                "DISTANCE_TO_PIN": {"bbox": [184, 396, 175, 148], "expect_decimal": False},
                "CARRY": {"bbox": [147, 705, 252, 145], "expect_decimal": True},
                "FROM_PIN": {"bbox": [188, 982, 170, 136], "expect_decimal": False},
                "STROKES_GAINED": {"bbox": [94, 1249, 323, 149], "expect_decimal": True}
            }
        }
        
        temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(boundary_config, temp_config)
        temp_config.close()
        
        try:
            ocr = GolfOCR(verbose=False, config_path=temp_config.name)
            result = ocr.extract_from_image("test.png")
            
            # Should handle boundary coordinates without error
            self.assertEqual(result["boundary_test"], "42")
        finally:
            os.unlink(temp_config.name)
            
    @patch('easyocr.Reader')
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    def test_multiple_pattern_matches(self, mock_cvtColor, mock_imread, mock_easyocr):
        """Test handling of multiple pattern matches in OCR results."""
        # Mock image loading
        mock_image = np.zeros((1000, 2000, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        mock_cvtColor.return_value = np.zeros((100, 100), dtype=np.uint8)
        
        # Mock EasyOCR reader with multiple matches
        mock_reader = Mock()
        mock_easyocr.return_value = mock_reader
        mock_reader.readtext.return_value = [
            self.create_mock_ocr_result("#1 Shot #2", 0.9, (10, 10, 50, 50)),
            self.create_mock_ocr_result("#3", 0.8, (60, 60, 100, 100))
        ]
        
        # Create config with shot ID pattern
        pattern_config = {
            "metrics": {
                "SHOT_ID": {
                    "bbox": [0, 0, 100, 100],
                    "expect_decimal": False,
                    "pattern": "#\\s*(\\d+)"
                },
                # Add required metrics to pass validation
                "DISTANCE_TO_PIN": {"bbox": [184, 396, 175, 148], "expect_decimal": False},
                "CARRY": {"bbox": [147, 705, 252, 145], "expect_decimal": True},
                "FROM_PIN": {"bbox": [188, 982, 170, 136], "expect_decimal": False},
                "STROKES_GAINED": {"bbox": [94, 1249, 323, 149], "expect_decimal": True}
            }
        }
        
        temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(pattern_config, temp_config)
        temp_config.close()
        
        try:
            ocr = GolfOCR(verbose=False, config_path=temp_config.name)
            result = ocr.extract_from_image("test.png")
            
            # Should extract based on confidence scoring
            self.assertIn(result["shot_id"], ["1", "3"])  # Should pick one based on confidence
        finally:
            os.unlink(temp_config.name)


if __name__ == '__main__':
    unittest.main()