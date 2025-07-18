#!/usr/bin/env python3
"""
Golf Photo OCR - EasyOCR Implementation
Simple, reliable OCR extraction using EasyOCR with hardcoded bounding boxes
"""

import argparse
import cv2
import easyocr
import json
import os
import csv
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import glob

from utils import (
    validate_config, 
    convert_date_to_yyyymmdd, 
    parse_yardage_range, 
    extract_best_number
)

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
        
        # Validate the loaded configuration
        validate_config(config)
        
        if self.verbose:
            print(f"Configuration validated successfully: {config_path}")
        
        return config
    
    
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
            raise ValueError(f"Could not load image: {image_path}. Check that the file exists and is a valid image format.")
        
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
            
            value = extract_best_number(ocr_results, box_center, expect_decimal, pattern, self.verbose)
            
            # Special handling for DATE metric - convert to YYYYMMDD format
            if label == "DATE" and value:
                value = convert_date_to_yyyymmdd(value, self.verbose)
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
            "STROKES_GAINED": "sg_individual",
            "YARDAGE_RANGE": "yardage_range"
        }
        
        mapped_results = {}
        for label, value in results.items():
            output_key = output_mapping.get(label, label.lower())
            mapped_results[output_key] = value
        
        # Special handling for yardage range - parse into 3 separate metrics
        if "YARDAGE_RANGE" in results:
            yardage_range_text = results["YARDAGE_RANGE"]
            yardage_range, yardage_from, yardage_to = parse_yardage_range(yardage_range_text, self.verbose)
            
            mapped_results["yardage_range"] = yardage_range
            mapped_results["yardage_from"] = yardage_from
            mapped_results["yardage_to"] = yardage_to
        
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
                    
            except ValueError as e:
                print(f"❌ {filename}: {e}")
                all_results[filename] = {"error": str(e)}
            except Exception as e:
                error_msg = f"Unexpected error processing {filename}: {e}"
                print(f"❌ {error_msg}")
                all_results[filename] = {"error": error_msg}
        
        # Save results
        self.save_results(all_results, output_dir)
        
        return all_results
    
    def save_results(self, results: Dict[str, Dict[str, str]], output_dir: str):
        """Save results to JSON and CSV files"""
        
        try:
            # Save JSON
            json_path = os.path.join(output_dir, "golf_ocr_results.json")
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {json_path}")
            
        except (IOError, OSError) as e:
            raise ValueError(f"Failed to save JSON results to {json_path}: {e}")
        
        try:
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
            
        except (IOError, OSError) as e:
            raise ValueError(f"Failed to save CSV results to {csv_path}: {e}")


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
        except ValueError as e:
            print(f"Error processing {args.single_image}: {e}")
        except Exception as e:
            print(f"Unexpected error processing {args.single_image}: {e}")
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