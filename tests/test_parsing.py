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
    
    def test_boundary_days(self):
        """Test boundary day values (1st and last day of months)."""
        # First day of month
        self.assertEqual(convert_date_to_yyyymmdd("JANUARY 1, 2025"), "20250101")
        # Last day of months with different day counts
        self.assertEqual(convert_date_to_yyyymmdd("JANUARY 31, 2025"), "20250131")
        self.assertEqual(convert_date_to_yyyymmdd("FEBRUARY 28, 2025"), "20250228")
        self.assertEqual(convert_date_to_yyyymmdd("APRIL 30, 2025"), "20250430")
        
    def test_leap_year_dates(self):
        """Test leap year date handling."""
        # Leap year February 29th
        self.assertEqual(convert_date_to_yyyymmdd("FEBRUARY 29, 2024"), "20240229")
        # Non-leap year February 29th (function doesn't validate, just formats)
        self.assertEqual(convert_date_to_yyyymmdd("FEBRUARY 29, 2025"), "20250229")
        
    def test_numeric_strings(self):
        """Test pure numeric strings that might be mistaken for dates."""
        self.assertEqual(convert_date_to_yyyymmdd("123456"), "")
        self.assertEqual(convert_date_to_yyyymmdd("20250701"), "")
        
    def test_special_characters(self):
        """Test input with special characters."""
        # These actually match because the regex doesn't require end-of-string
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1, 2025!"), "20250701")
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1, 2025."), "20250701")
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1st, 2025"), "")  # Ordinal numbers prevent match
        
    def test_extra_long_text(self):
        """Test very long strings with dates embedded."""
        long_text = "This is a very long string with JULY 1, 2025 embedded somewhere in the middle"
        self.assertEqual(convert_date_to_yyyymmdd(long_text), "")  # Should not match due to regex
        
    def test_partial_dates(self):
        """Test incomplete date information."""
        self.assertEqual(convert_date_to_yyyymmdd("JULY"), "")
        self.assertEqual(convert_date_to_yyyymmdd("JULY 1"), "")
        self.assertEqual(convert_date_to_yyyymmdd("1, 2025"), "")
        self.assertEqual(convert_date_to_yyyymmdd(", 2025"), "")


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
        
    def test_boundary_values(self):
        """Test boundary numeric values."""
        # Very small ranges
        result = parse_yardage_range("1-2")
        self.assertEqual(result, ("1-2", "1", "2"))
        
        # Large ranges
        result = parse_yardage_range("999-1000")
        self.assertEqual(result, ("999-1000", "999", "1000"))
        
        # Zero values (though unusual in golf)
        result = parse_yardage_range("0-10")
        self.assertEqual(result, ("0-10", "0", "10"))
        
    def test_unusual_spacing(self):
        """Test unusual spacing patterns."""
        # Tab characters
        result = parse_yardage_range("30-50\tyards")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        # Multiple spaces between range and unit
        result = parse_yardage_range("30-50    yards")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        # Leading/trailing spaces
        result = parse_yardage_range("   30-50   ")
        self.assertEqual(result, ("30-50", "30", "50"))
        
    def test_reversed_ranges(self):
        """Test ranges where to-value is smaller than from-value."""
        # Technically invalid but function should still parse the pattern
        result = parse_yardage_range("50-30")
        self.assertEqual(result, ("50-30", "50", "30"))
        
    def test_same_from_to_values(self):
        """Test ranges where from and to values are the same."""
        result = parse_yardage_range("50-50")
        self.assertEqual(result, ("50-50", "50", "50"))
        
    def test_decimal_ranges(self):
        """Test ranges with decimal values (though unusual in yardage)."""
        # Function looks for \d+-\d+ pattern, so it matches the digits after decimal
        result = parse_yardage_range("30.5-50.7")
        self.assertEqual(result, ("5-50", "5", "50"))  # Matches "5-50" from the decimal portions
        
    def test_ranges_with_punctuation(self):
        """Test ranges with surrounding punctuation."""
        result = parse_yardage_range("Range: 30-50 yards.")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        result = parse_yardage_range("(30-50 yards)")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        result = parse_yardage_range("[30-50]")
        self.assertEqual(result, ("30-50", "30", "50"))
        
    def test_alternative_units(self):
        """Test with alternative or misspelled units."""
        # Misspelled units
        result = parse_yardage_range("30-50 yeards")  # Misspelled
        self.assertEqual(result, ("30-50", "30", "50"))
        
        result = parse_yardage_range("30-50 yrds")  # Alternative abbreviation
        self.assertEqual(result, ("30-50", "30", "50"))
        
        # Other distance units (should still extract range)
        result = parse_yardage_range("30-50 meters")
        self.assertEqual(result, ("30-50", "30", "50"))
        
    def test_complex_text_scenarios(self):
        """Test complex real-world text scenarios."""
        result = parse_yardage_range("Shot distance 30-50 yards from pin")
        self.assertEqual(result, ("30-50", "30", "50"))
        
        result = parse_yardage_range("Approach shot in the 75-100 yard range")
        self.assertEqual(result, ("75-100", "75", "100"))
        
        result = parse_yardage_range("Between 50-75 yds to target")
        self.assertEqual(result, ("50-75", "50", "75"))
        
    def test_numeric_only_input(self):
        """Test purely numeric inputs without dash."""
        result = parse_yardage_range("50")
        self.assertEqual(result, ("", "", ""))
        
        result = parse_yardage_range("123456")
        self.assertEqual(result, ("", "", ""))
        
    def test_malformed_ranges(self):
        """Test additional malformed range patterns."""
        # Multiple dashes
        result = parse_yardage_range("30--50")
        self.assertEqual(result, ("", "", ""))
        
        result = parse_yardage_range("30-50-75")  # Triple range
        self.assertEqual(result, ("30-50", "30", "50"))  # Should match first valid pattern
        
        # Letters mixed with numbers
        result = parse_yardage_range("30a-50b")
        self.assertEqual(result, ("", "", ""))
        
        # Empty range components
        result = parse_yardage_range("-")
        self.assertEqual(result, ("", "", ""))
        
        result = parse_yardage_range("a-b")
        self.assertEqual(result, ("", "", ""))


if __name__ == '__main__':
    unittest.main()