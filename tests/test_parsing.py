"""
Unit tests for parsing utilities.

Tests the date conversion and yardage range parsing functions with various inputs
including valid data, edge cases, malformed input, and error conditions.
"""

import unittest
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parsing import convert_date_to_yyyymmdd, parse_yardage_range


class TestDateConversion(unittest.TestCase):
    """Test cases for convert_date_to_yyyymmdd function."""
    
    def test_valid_dates(self):
        """Test conversion of valid date formats."""
        # Standard format
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1, 2025"), "20250701")
        self.assertEqual(convert_date_to_yyyymmdd("JANUARY 15, 2024"), "20240115")
        self.assertEqual(convert_date_to_yyyymmdd("DECEMBER 31, 2023"), "20231231")
        
        # All months
        self.assertEqual(convert_date_to_yyyymmdd("FEBRUARY 5, 2025"), "20250205")
        self.assertEqual(convert_date_to_yyyymmdd("MARCH 10, 2025"), "20250310")
        self.assertEqual(convert_date_to_yyyymmdd("APRIL 20, 2025"), "20250420")
        self.assertEqual(convert_date_to_yyyymmdd("MAY 3, 2025"), "20250503")
        self.assertEqual(convert_date_to_yyyymmdd("JUNE 18, 2025"), "20250618")
        self.assertEqual(convert_date_to_yyyymmdd("AUGUST 9, 2025"), "20250809")
        self.assertEqual(convert_date_to_yyyymmdd("SEPTEMBER 25, 2025"), "20250925")
        self.assertEqual(convert_date_to_yyyymmdd("OCTOBER 7, 2025"), "20251007")
        self.assertEqual(convert_date_to_yyyymmdd("NOVEMBER 12, 2025"), "20251112")
        
    def test_spacing_variations(self):
        """Test different spacing patterns."""
        # No space after comma
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1,2025"), "20250701")
        # Multiple spaces
        self.assertEqual(convert_date_to_yyyymmdd("JULY  1,  2025"), "20250701")
        # Extra whitespace around - current regex doesn't handle leading/trailing whitespace
        self.assertEqual(convert_date_to_yyyymmdd("  JULY 1, 2025  "), "")  # Known limitation
        
    def test_case_variations(self):
        """Test different case inputs (should handle uppercase)."""
        # Lowercase - should work since we convert to uppercase
        self.assertEqual(convert_date_to_yyyymmdd("july 1, 2025"), "20250701")
        # Mixed case
        self.assertEqual(convert_date_to_yyyymmdd("July 1, 2025"), "20250701")
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1, 2025"), "20250701")
        
    def test_single_digit_days(self):
        """Test single digit days get zero-padded."""
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1, 2025"), "20250701")
        self.assertEqual(convert_date_to_yyyymmdd("JULY 9, 2025"), "20250709")
        
    def test_two_digit_days(self):
        """Test two digit days work correctly."""
        self.assertEqual(convert_date_to_yyyymmdd("JULY 10, 2025"), "20250710")
        self.assertEqual(convert_date_to_yyyymmdd("JULY 31, 2025"), "20250731")
        
    def test_invalid_inputs(self):
        """Test invalid inputs return empty string."""
        # Empty string
        self.assertEqual(convert_date_to_yyyymmdd(""), "")
        
        # None input (will cause AttributeError but should be handled)
        self.assertEqual(convert_date_to_yyyymmdd(None), "")
        
        # Invalid month names
        self.assertEqual(convert_date_to_yyyymmdd("INVALIDMONTH 1, 2025"), "")
        self.assertEqual(convert_date_to_yyyymmdd("JUL 1, 2025"), "")  # Abbreviated month
        
        # Invalid format
        self.assertEqual(convert_date_to_yyyymmdd("2025-07-01"), "")  # Wrong format
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1 2025"), "")  # Missing comma
        self.assertEqual(convert_date_to_yyyymmdd("1 JULY, 2025"), "")  # Wrong order
        
        # Invalid day values
        self.assertEqual(convert_date_to_yyyymmdd("JULY 32, 2025"), "20250732")  # Note: function doesn't validate day ranges
        self.assertEqual(convert_date_to_yyyymmdd("JULY 0, 2025"), "20250700")  # Note: function doesn't validate day ranges
        
        # Invalid year
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1, 25"), "")  # Two digit year
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1, ABCD"), "")  # Non-numeric year
        
        # Malformed strings
        self.assertEqual(convert_date_to_yyyymmdd("random text"), "")
        self.assertEqual(convert_date_to_yyyymmdd("JULY"), "")
        self.assertEqual(convert_date_to_yyyymmdd("1, 2025"), "")
        
    def test_verbose_mode(self):
        """Test that verbose mode doesn't affect output (just adds logging)."""
        # Valid date should work the same with verbose
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1, 2025", verbose=True), "20250701")
        
        # Invalid date should still return empty string with verbose
        self.assertEqual(convert_date_to_yyyymmdd("invalid", verbose=True), "")


class TestYardageRangeParsing(unittest.TestCase):
    """Test cases for parse_yardage_range function."""
    
    def test_valid_ranges(self):
        """Test parsing of valid yardage ranges."""
        # Basic range
        result = parse_yardage_range("30-50")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        # Range with yards
        result = parse_yardage_range("30-50 yards")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        # Range with yds
        result = parse_yardage_range("30-50 yds")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        # Range with yard (singular)
        result = parse_yardage_range("30-50 yard")
        self.assertEqual(result, ("30-50", "30", "50"))
        
    def test_different_range_values(self):
        """Test various numeric range values."""
        # Different ranges
        result = parse_yardage_range("50-75")
        self.assertEqual(result, ("50-75", "50", "75"))
        
        result = parse_yardage_range("75-100")
        self.assertEqual(result, ("75-100", "75", "100"))
        
        result = parse_yardage_range("100-125")
        self.assertEqual(result, ("100-125", "100", "125"))
        
        # Single digit ranges
        result = parse_yardage_range("5-10")
        self.assertEqual(result, ("5-10", "5", "10"))
        
        # Three digit ranges
        result = parse_yardage_range("150-200")
        self.assertEqual(result, ("150-200", "150", "200"))
        
    def test_spacing_variations(self):
        """Test different spacing around ranges."""
        # Extra spaces around text (should work since we search within text)
        result = parse_yardage_range("  30-50  yards  ")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        # Spaces around dash - current regex looks for \d+-\d+ pattern without spaces
        result = parse_yardage_range("30 - 50 yards")
        self.assertEqual(result, ("", "", ""))  # Known limitation - spaces around dash not supported
        
    def test_case_variations(self):
        """Test different case variations for yard/yards."""
        result = parse_yardage_range("30-50 YARDS")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        result = parse_yardage_range("30-50 Yards")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        result = parse_yardage_range("30-50 YDS")
        self.assertEqual(result, ("30-50", "30", "50"))
        
    def test_invalid_inputs(self):
        """Test invalid inputs return empty strings."""
        # Empty string
        result = parse_yardage_range("")
        self.assertEqual(result, ("", "", ""))
        
        # None input
        result = parse_yardage_range(None)
        self.assertEqual(result, ("", "", ""))
        
        # No range pattern
        result = parse_yardage_range("just text")
        self.assertEqual(result, ("", "", ""))
        
        result = parse_yardage_range("30 yards")  # No dash
        self.assertEqual(result, ("", "", ""))
        
        result = parse_yardage_range("yards 30-50")  # Range at end might not match
        self.assertEqual(result, ("30-50", "30", "50"))  # Actually this should work
        
        # Invalid range format
        result = parse_yardage_range("30-")
        self.assertEqual(result, ("", "", ""))
        
        result = parse_yardage_range("-50")
        self.assertEqual(result, ("", "", ""))
        
        result = parse_yardage_range("30--50")  # Double dash
        self.assertEqual(result, ("", "", ""))
        
        # Non-numeric ranges
        result = parse_yardage_range("abc-def")
        self.assertEqual(result, ("", "", ""))
        
        result = parse_yardage_range("30-xyz")
        self.assertEqual(result, ("", "", ""))
        
    def test_embedded_ranges(self):
        """Test ranges embedded in longer text."""
        result = parse_yardage_range("The range is 30-50 yards for this shot")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        result = parse_yardage_range("Shot from 75-100 yds")
        self.assertEqual(result, ("75-100", "75", "100"))
        
    def test_multiple_ranges(self):
        """Test text with multiple ranges (should pick first one)."""
        result = parse_yardage_range("30-50 or 75-100 yards")
        self.assertEqual(result, ("30-50", "30", "50"))  # Should get first match
        
    def test_verbose_mode(self):
        """Test that verbose mode doesn't affect output."""
        # Valid range should work the same with verbose
        result = parse_yardage_range("30-50 yards", verbose=True)
        self.assertEqual(result, ("30-50", "30", "50"))
        
        # Invalid range should still return empty strings with verbose
        result = parse_yardage_range("invalid", verbose=True)
        self.assertEqual(result, ("", "", ""))


if __name__ == '__main__':
    unittest.main()