#!/usr/bin/env python3
"""
Golf Photo OCR - EasyOCR Implementation
Simple, reliable OCR extraction using EasyOCR with hardcoded bounding boxes
"""

import argparse
import cv2
import easyocr
import json
import math
import os
import re
import csv
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import glob

class GolfOCR:
    """Simple OCR extractor using EasyOCR with configurable bounding boxes"""
    
    def __init__(self, verbose: bool = False, config_path: str = "config.json"):
        self.verbose = verbose
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Extract configuration data
        metrics = self.config.get("metrics", {})
        self.labels = list(metrics.keys())
        self.boxes = [tuple(metrics[label]["bbox"]) for label in self.labels]
        self.decimal_metrics = {
            label for label, config in metrics.items() 
            if config.get("expect_decimal", False)
        }
        self.pattern_metrics = {
            label: config.get("pattern") for label, config in metrics.items() 
            if config.get("pattern")
        }
        
        if self.verbose:
            print(f"Loaded configuration for {len(self.labels)} metrics")
            for i, label in enumerate(self.labels):
                print(f"  {label}: bbox={self.boxes[i]}, decimal={label in self.decimal_metrics}")
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file with validation"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        
        # Validate required sections
        if "metrics" not in config:
            raise ValueError("Configuration file must contain 'metrics' section")
        
        metrics = config["metrics"]
        required_metrics = ["DISTANCE_TO_PIN", "CARRY", "FROM_PIN", "STROKES_GAINED"]
        
        for metric in required_metrics:
            if metric not in metrics:
                raise ValueError(f"Missing required metric in configuration: {metric}")
            if "bbox" not in metrics[metric]:
                raise ValueError(f"Missing 'bbox' for metric: {metric}")
            if len(metrics[metric]["bbox"]) != 4:
                raise ValueError(f"Invalid bbox format for {metric}: must be [x, y, width, height]")
        
        if self.verbose:
            print(f"Configuration validated successfully: {config_path}")
        
        return config
    
    def convert_date_to_yyyymmdd(self, date_text: str) -> str:
        """
        Convert date text like 'JULY 1, 2025' to YYYYMMDD format like '20250701'
        
        Args:
            date_text: Date string in format 'MONTH DAY, YEAR'
            
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
                return ""
            
            month_name, day, year = match.groups()
            
            if month_name not in month_map:
                return ""
            
            month_num = month_map[month_name]
            day_num = day.zfill(2)  # Zero-pad day to 2 digits
            
            return f"{year}{month_num}{day_num}"
            
        except Exception:
            return ""
    
    def extract_best_number(self, ocr_results: List, box_center: Tuple[float, float], 
                           expect_decimal: bool = False, pattern: str = None) -> str:
        """
        Extract the best candidate from OCR results based on proximity to box center
        
        Args:
            ocr_results: List of (bbox, text, confidence) from EasyOCR
            box_center: Expected center of the bounding box
            expect_decimal: Whether to prefer decimal values
            pattern: Optional regex pattern to match (e.g., "#\\s*(\\d+)" for shot ID)
            
        Returns:
            Best candidate string found, or empty string if none found
        """
        candidates = []
        
        for bbox, text, conf in ocr_results:
            clean_text = text.strip()
            
            if self.verbose:
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
            
            if self.verbose:
                print(f"    Candidate: '{extracted_value}' (score: {score:.1f}, conf: {conf:.2f})")
        
        if not candidates:
            return ""
        
        # Sort by score (lower is better) and return best candidate
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]
    
    def extract_from_image(self, image_path: str) -> Dict[str, str]:
        """
        Extract all metrics from a golf screenshot
        
        Args:
            image_path: Path to the golf screenshot
            
        Returns:
            Dictionary with metric names as keys and extracted values as strings
        """
        if self.verbose:
            print(f"Processing: {image_path}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        results = {}
        
        # Extract each metric
        for i, (x, y, w, h) in enumerate(self.boxes):
            label = self.labels[i]
            
            if self.verbose:
                print(f"  Extracting {label}...")
            
            # Create crop
            crop = image[y:y+h, x:x+w]
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            
            # Run OCR
            ocr_results = self.reader.readtext(gray)
            
            # Extract value using unified method
            box_center = (w / 2, h / 2)
            expect_decimal = label in self.decimal_metrics
            pattern = self.pattern_metrics.get(label)  # None if no pattern defined
            
            value = self.extract_best_number(ocr_results, box_center, expect_decimal, pattern)
            
            # Special handling for DATE metric - convert to YYYYMMDD format
            if label == "DATE" and value:
                value = self.convert_date_to_yyyymmdd(value)
                if self.verbose:
                    print(f"    Converted date to: '{value}'")
            
            results[label] = value
            
            if self.verbose:
                print(f"    Result: '{value}'")
        
        # Map output keys according to PLAN.md requirements
        output_mapping = {
            "DATE": "date",
            "SHOT_ID": "shot_id",
            "DISTANCE_TO_PIN": "distance_to_pin", 
            "CARRY": "carry",
            "FROM_PIN": "from_pin",
            "STROKES_GAINED": "sg_individual"
        }
        
        mapped_results = {}
        for label, value in results.items():
            output_key = output_mapping.get(label, label.lower())
            mapped_results[output_key] = value
        
        return mapped_results
    
    def process_directory(self, input_dir: str, output_dir: str = "output") -> Dict[str, Dict[str, str]]:
        """
        Process all images in a directory
        
        Args:
            input_dir: Directory containing golf screenshots
            output_dir: Directory to save results
            
        Returns:
            Dictionary mapping filenames to their extracted metrics
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all image files
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(input_dir, ext)))
        
        if not image_files:
            print(f"No images found in {input_dir}")
            return {}
        
        print(f"Found {len(image_files)} images to process")
        
        all_results = {}
        
        # Process each image
        for image_path in sorted(image_files):
            filename = os.path.basename(image_path)
            
            try:
                results = self.extract_from_image(image_path)
                all_results[filename] = results
                
                if self.verbose:
                    print(f"✅ {filename}: {results}")
                else:
                    print(f"✅ {filename}")
                    
            except Exception as e:
                print(f"❌ {filename}: {e}")
                all_results[filename] = {"error": str(e)}
        
        # Save results
        self.save_results(all_results, output_dir)
        
        return all_results
    
    def save_results(self, results: Dict[str, Dict[str, str]], output_dir: str):
        """Save results to JSON and CSV files"""
        
        # Save JSON
        json_path = os.path.join(output_dir, "golf_ocr_results.json")
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {json_path}")
        
        # Save CSV
        csv_path = os.path.join(output_dir, "golf_ocr_results.csv")
        
        # Get all metric names for CSV headers
        all_metrics = set()
        for file_results in results.values():
            all_metrics.update(file_results.keys())
        
        # Remove 'error' from metrics if present
        all_metrics.discard('error')
        headers = ['filename'] + sorted(all_metrics)
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for filename, file_results in results.items():
                row = [filename]
                for metric in headers[1:]:  # Skip filename
                    row.append(file_results.get(metric, ''))
                writer.writerow(row)
        
        print(f"Results saved to {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Golf Photo OCR using EasyOCR")
    parser.add_argument("--input-dir", default="photos", help="Input directory containing images")
    parser.add_argument("--output-dir", default="output", help="Output directory for results")
    parser.add_argument("--single-image", help="Process single image instead of directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create OCR extractor
    ocr = GolfOCR(verbose=args.verbose)
    
    if args.single_image:
        # Process single image
        try:
            results = ocr.extract_from_image(args.single_image)
            print(f"\n=== Results for {args.single_image} ===")
            for metric, value in results.items():
                print(f"{metric}: {value}")
        except Exception as e:
            print(f"Error processing {args.single_image}: {e}")
    else:
        # Process directory
        results = ocr.process_directory(args.input_dir, args.output_dir)
        
        # Print summary
        successful = sum(1 for r in results.values() if 'error' not in r)
        total = len(results)
        print(f"\n=== Summary ===")
        print(f"Total images: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success rate: {successful/total*100:.1f}%")


if __name__ == "__main__":
    main()