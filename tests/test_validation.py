"""
Unit tests for validation utilities.

Tests the configuration and bounding box validation functions with various
valid and invalid inputs to ensure proper error handling and validation.
"""

import unittest
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validation import validate_bbox, validate_config


class TestBoundingBoxValidation(unittest.TestCase):
    """Test cases for validate_bbox function."""
    
    def test_valid_bbox(self):
        """Test valid bounding box coordinates."""
        # Standard bbox
        validate_bbox([10, 20, 100, 50], "TEST_METRIC")  # Should not raise
        
        # Zero coordinates
        validate_bbox([0, 0, 100, 100], "TEST_METRIC")  # Should not raise
        
        # Large coordinates
        validate_bbox([1000, 1000, 500, 300], "TEST_METRIC")  # Should not raise
        
    def test_invalid_bbox_format(self):
        """Test invalid bounding box formats."""
        # Not a list
        with self.assertRaises(ValueError) as context:
            validate_bbox((10, 20, 100, 50), "TEST_METRIC")
        self.assertIn("must be a list", str(context.exception))
        
        # Wrong number of elements
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 20, 100], "TEST_METRIC")
        self.assertIn("must be [x, y, width, height]", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 20, 100, 50, 60], "TEST_METRIC")
        self.assertIn("must be [x, y, width, height]", str(context.exception))
        
    def test_invalid_coordinate_types(self):
        """Test non-numeric coordinates."""
        with self.assertRaises(ValueError) as context:
            validate_bbox(["10", 20, 100, 50], "TEST_METRIC")
        self.assertIn("x must be a number", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, "20", 100, 50], "TEST_METRIC")
        self.assertIn("y must be a number", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 20, "100", 50], "TEST_METRIC")
        self.assertIn("width must be a number", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 20, 100, "50"], "TEST_METRIC")
        self.assertIn("height must be a number", str(context.exception))
        
    def test_negative_coordinates(self):
        """Test negative coordinate values."""
        with self.assertRaises(ValueError) as context:
            validate_bbox([-10, 20, 100, 50], "TEST_METRIC")
        self.assertIn("x coordinate cannot be negative", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, -20, 100, 50], "TEST_METRIC")
        self.assertIn("y coordinate cannot be negative", str(context.exception))
        
    def test_invalid_dimensions(self):
        """Test invalid width and height values."""
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 20, 0, 50], "TEST_METRIC")
        self.assertIn("width must be positive", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 20, -100, 50], "TEST_METRIC")
        self.assertIn("width must be positive", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 20, 100, 0], "TEST_METRIC")
        self.assertIn("height must be positive", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 20, 100, -50], "TEST_METRIC")
        self.assertIn("height must be positive", str(context.exception))
        
    def test_coordinates_too_large(self):
        """Test coordinates exceeding maximum bounds."""
        max_dimension = 10000
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([max_dimension + 1, 20, 100, 50], "TEST_METRIC")
        self.assertIn("x coordinate too large", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, max_dimension + 1, 100, 50], "TEST_METRIC")
        self.assertIn("y coordinate too large", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 20, max_dimension + 1, 50], "TEST_METRIC")
        self.assertIn("width too large", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 20, 100, max_dimension + 1], "TEST_METRIC")
        self.assertIn("height too large", str(context.exception))
        
    def test_bbox_extends_beyond_bounds(self):
        """Test bounding box extending beyond reasonable image bounds."""
        max_dimension = 10000
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([9990, 20, 100, 50], "TEST_METRIC")  # x + width = 10090
        self.assertIn("extends beyond reasonable image width", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            validate_bbox([10, 9990, 100, 50], "TEST_METRIC")  # y + height = 10040
        self.assertIn("extends beyond reasonable image height", str(context.exception))
        
    def test_float_coordinates(self):
        """Test that float coordinates are accepted."""
        validate_bbox([10.5, 20.3, 100.7, 50.2], "TEST_METRIC")  # Should not raise


class TestConfigValidation(unittest.TestCase):
    """Test cases for validate_config function."""
    
    def test_valid_config(self):
        """Test valid configuration."""
        valid_config = {
            "metrics": {
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
                }
            }
        }
        validate_config(valid_config)  # Should not raise
        
    def test_missing_metrics_section(self):
        """Test config missing metrics section."""
        invalid_config = {
            "other_section": {}
        }
        with self.assertRaises(ValueError) as context:
            validate_config(invalid_config)
        self.assertIn("must contain 'metrics' section", str(context.exception))
        
    def test_metrics_not_dict(self):
        """Test metrics section that is not a dictionary."""
        invalid_config = {
            "metrics": "not a dict"
        }
        with self.assertRaises(ValueError) as context:
            validate_config(invalid_config)
        self.assertIn("'metrics' section must be a dictionary", str(context.exception))
        
    def test_missing_required_metrics(self):
        """Test missing required metrics."""
        # Missing DISTANCE_TO_PIN
        invalid_config = {
            "metrics": {
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
                }
            }
        }
        with self.assertRaises(ValueError) as context:
            validate_config(invalid_config)
        self.assertIn("Missing required metric", str(context.exception))
        self.assertIn("DISTANCE_TO_PIN", str(context.exception))
        
    def test_metric_not_dict(self):
        """Test metric that is not a dictionary."""
        invalid_config = {
            "metrics": {
                "DISTANCE_TO_PIN": "not a dict",
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
                }
            }
        }
        with self.assertRaises(ValueError) as context:
            validate_config(invalid_config)
        self.assertIn("must be a dictionary", str(context.exception))
        
    def test_missing_bbox(self):
        """Test metric missing bbox."""
        invalid_config = {
            "metrics": {
                "DISTANCE_TO_PIN": {
                    "expect_decimal": False
                    # Missing bbox
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
                }
            }
        }
        with self.assertRaises(ValueError) as context:
            validate_config(invalid_config)
        self.assertIn("Missing 'bbox'", str(context.exception))
        
    def test_invalid_bbox_in_config(self):
        """Test config with invalid bounding box."""
        invalid_config = {
            "metrics": {
                "DISTANCE_TO_PIN": {
                    "bbox": [-10, 396, 175, 148],  # Negative x
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
                }
            }
        }
        with self.assertRaises(ValueError) as context:
            validate_config(invalid_config)
        self.assertIn("x coordinate cannot be negative", str(context.exception))
        
    def test_config_with_optional_metrics(self):
        """Test config with optional metrics beyond required ones."""
        valid_config = {
            "metrics": {
                # Required metrics
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
                # Optional metrics
                "DATE": {
                    "bbox": [985, 41, 301, 116],
                    "expect_decimal": False,
                    "pattern": "some_pattern"
                },
                "SHOT_ID": {
                    "bbox": [60, 175, 84, 81],
                    "expect_decimal": False,
                    "pattern": "another_pattern"
                }
            }
        }
        validate_config(valid_config)  # Should not raise
        
    def test_optional_metric_with_invalid_bbox(self):
        """Test optional metric with invalid bbox."""
        invalid_config = {
            "metrics": {
                # Required metrics (all valid)
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
                # Optional metric with invalid bbox
                "DATE": {
                    "bbox": [985, 41, 0, 116],  # Zero width
                    "expect_decimal": False
                }
            }
        }
        with self.assertRaises(ValueError) as context:
            validate_config(invalid_config)
        self.assertIn("width must be positive", str(context.exception))


if __name__ == '__main__':
    unittest.main()