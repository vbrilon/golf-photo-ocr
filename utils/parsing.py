"""
Text parsing utilities for extracting structured data from OCR results.
"""

import re
from typing import Tuple


def convert_date_to_yyyymmdd(date_text: str, verbose: bool = False) -> str:
    """
    Convert date text like 'JULY 1, 2025' to YYYYMMDD format like '20250701'
    
    Args:
        date_text: Date string in format 'MONTH DAY, YEAR'
        verbose: Whether to print debug information
        
    Returns:
        Date in YYYYMMDD format, or empty string if parsing fails
    """
    if not date_text:
        return ""
    
    month_map = {
        'JANUARY': '01', 'FEBRUARY': '02', 'MARCH': '03', 'APRIL': '04',
        'MAY': '05', 'JUNE': '06', 'JULY': '07', 'AUGUST': '08',
        'SEPTEMBER': '09', 'OCTOBER': '10', 'NOVEMBER': '11', 'DECEMBER': '12'
    }
    
    try:
        # Parse format like "JULY 1, 2025" or "JULY 1,2025"
        match = re.match(r'([A-Z]+)\s+(\d{1,2}),\s*(\d{4})', date_text.upper())
        if not match:
            if verbose:
                print(f"    Date parsing: No match found for pattern in '{date_text}'")
            return ""
        
        month_name, day, year = match.groups()
        
        if month_name not in month_map:
            if verbose:
                print(f"    Date parsing: Unknown month '{month_name}' in '{date_text}'")
            return ""
        
        month_num = month_map[month_name]
        day_num = day.zfill(2)  # Zero-pad day to 2 digits
        
        return f"{year}{month_num}{day_num}"
        
    except (AttributeError, ValueError, IndexError) as e:
        if verbose:
            print(f"    Date parsing error for '{date_text}': {e}")
        return ""
    except Exception as e:
        if verbose:
            print(f"    Unexpected date parsing error for '{date_text}': {e}")
        return ""


def parse_yardage_range(range_text: str, verbose: bool = False) -> Tuple[str, str, str]:
    """
    Parse yardage range text like '30-50' into components
    
    Args:
        range_text: Range string like '30-50' or '30-50 yards'
        verbose: Whether to print debug information
        
    Returns:
        Tuple of (yardage_range, yardage_from, yardage_to) or empty strings if parsing fails
    """
    if not range_text:
        return "", "", ""
    
    try:
        # Extract just the range portion (e.g., "30-50" from "30-50 yards")
        range_match = re.search(r'(\d+-\d+)', range_text)
        if not range_match:
            if verbose:
                print(f"    Yardage range parsing: No range pattern found in '{range_text}'")
            return "", "", ""
        
        range_part = range_match.group(1)
        
        # Split the range into from/to components
        if '-' in range_part:
            parts = range_part.split('-')
            if len(parts) == 2:
                yardage_from = parts[0].strip()
                yardage_to = parts[1].strip()
                return range_part, yardage_from, yardage_to
        
        if verbose:
            print(f"    Yardage range parsing: Could not split range '{range_part}'")
        return "", "", ""
        
    except (AttributeError, ValueError, IndexError) as e:
        if verbose:
            print(f"    Yardage range parsing error for '{range_text}': {e}")
        return "", "", ""
    except Exception as e:
        if verbose:
            print(f"    Unexpected yardage range parsing error for '{range_text}': {e}")
        return "", "", ""