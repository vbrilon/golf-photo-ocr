"""
OCR result processing utilities for extracting and ranking text candidates.
"""

import math
import re
from typing import List, Tuple


def extract_best_number(ocr_results: List, box_center: Tuple[float, float], 
                       expect_decimal: bool = False, pattern: str = None, 
                       verbose: bool = False) -> str:
    """
    Extract the best candidate from OCR results based on proximity to box center
    
    Args:
        ocr_results: List of (bbox, text, confidence) from EasyOCR
        box_center: Expected center of the bounding box
        expect_decimal: Whether to prefer decimal values
        pattern: Optional regex pattern to match (e.g., "#\\s*(\\d+)" for shot ID)
        verbose: Whether to print debug information
        
    Returns:
        Best candidate string found, or empty string if none found
    """
    candidates = []
    
    for bbox, text, conf in ocr_results:
        clean_text = text.strip()
        
        if verbose:
            print(f"    Checking text: '{clean_text}'")
        
        # Use custom pattern if provided, otherwise use default numeric pattern
        if pattern:
            match = re.search(pattern, clean_text)
            if not match:
                continue
            extracted_value = match.group(1)  # Extract from capture group
        else:
            # Skip if no digits found
            if not re.search(r'\d', clean_text):
                continue
            
            # Extract number with optional sign
            match = re.search(r'[+-]?\d+\.?\d*', clean_text)
            if not match:
                continue
            
            extracted_value = match.group(0)
            
            # Handle explicit + sign in original text
            if '+' in clean_text and not extracted_value.startswith('+'):
                extracted_value = '+' + extracted_value.lstrip('+-')
        
        # Calculate distance from expected center (for pattern matches, distance is less important)
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        text_center = (sum(x_coords) / 4, sum(y_coords) / 4)
        
        distance = math.hypot(text_center[0] - box_center[0], text_center[1] - box_center[1])
        
        # Apply decimal preference bonus (only for numeric extraction)
        decimal_bonus = -10.0 if not pattern and expect_decimal and '.' in extracted_value else 0.0
        
        # For pattern matches, prioritize by confidence rather than distance
        score = distance + decimal_bonus if not pattern else -conf * 100
        
        candidates.append((score, extracted_value, conf))
        
        if verbose:
            print(f"    Candidate: '{extracted_value}' (score: {score:.1f}, conf: {conf:.2f})")
    
    if not candidates:
        return ""
    
    # Sort by score (lower is better) and return best candidate
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]