#!/usr/bin/env python3
"""
Simple validation test for Golf Photo OCR system
Tests the system against ground truth data stored in config.json
"""

import json
import os
import sys

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import GolfOCR

def test_ground_truth():
    """Test all ground truth images for accuracy"""
    
    # Load ground truth data from config
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    ground_truth = config['ground_truth']['test_images']
    
    print("=== Golf OCR Ground Truth Validation ===")
    print(f"Testing {len(ground_truth)} images...\n")
    print("Ground truth images:")
    for filename in ground_truth.keys():
        print(f"  - {filename}")
    print()
    
    # Initialize OCR system
    ocr = GolfOCR(verbose=False)
    
    passed = 0
    total = 0
    
    for filename, expected_dict in ground_truth.items():
        image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'photos', filename)
        
        if not os.path.exists(image_path):
            print(f"⚠️  {filename}: Image not found, skipping")
            continue
        
        total += 1
        
        try:
            # Extract metrics
            results = ocr.extract_from_image(image_path)
            
            # Compare each metric individually
            all_correct = True
            extracted_dict = {}
            
            for metric_key, expected_value in expected_dict.items():
                if metric_key not in results:
                    print(f"❌ {filename}: Missing metric '{metric_key}'")
                    all_correct = False
                    continue
                
                value_str = results[metric_key]
                
                # Normalize expected value to match system output type
                if metric_key == "shot_id":
                    # Shot ID: convert both to int
                    try:
                        extracted_value = int(value_str) if value_str else None
                        expected_norm = int(expected_value) if expected_value else None
                    except ValueError:
                        print(f"❌ {filename}: Invalid shot_id '{value_str}' or expected '{expected_value}'")
                        all_correct = False
                        continue
                elif metric_key in ["date", "yardage_range"]:
                    # String metrics: compare as strings
                    extracted_value = value_str
                    expected_norm = expected_value
                else:
                    # Numeric metrics: convert both to float, handle signs and empty values
                    if not value_str or value_str.strip() == "":
                        extracted_value = None
                    else:
                        try:
                            if '+' in value_str:
                                extracted_value = float(value_str.replace('+', ''))
                            else:
                                extracted_value = float(value_str)
                        except ValueError:
                            print(f"❌ {filename}: Invalid numeric value '{value_str}' for {metric_key}")
                            all_correct = False
                            continue
                    
                    # Normalize expected value
                    if not expected_value or expected_value.strip() == "":
                        expected_norm = None
                    else:
                        try:
                            if '+' in expected_value:
                                expected_norm = float(expected_value.replace('+', ''))
                            else:
                                expected_norm = float(expected_value)
                        except ValueError:
                            print(f"❌ {filename}: Invalid expected numeric value '{expected_value}' for {metric_key}")
                            all_correct = False
                            continue
                
                extracted_dict[metric_key] = extracted_value
                
                # Compare normalized values
                if metric_key == "shot_id":
                    if extracted_value != expected_norm:
                        all_correct = False
                elif metric_key in ["date", "yardage_range"]:
                    if extracted_value != expected_norm:
                        all_correct = False
                else:
                    # Numeric comparison with tolerance
                    if expected_norm is None:
                        if extracted_value is not None:
                            all_correct = False
                    elif extracted_value is None:
                        all_correct = False
                    else:
                        if abs(extracted_value - expected_norm) >= 0.01:
                            all_correct = False
            
            if all_correct:
                print(f"✅ {filename}: PASS")
                passed += 1
            else:
                print(f"❌ {filename}: FAIL")
                print(f"   Expected: {expected_dict}")
                print(f"   Got:      {extracted_dict}")
                
        except Exception as e:
            print(f"❌ {filename}: ERROR - {e}")
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%" if total > 0 else "No tests run")
    
    if passed == total and total > 0:
        print("🎉 All tests passed! System is working perfectly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the results above.")
        return False

def quick_test():
    """Quick test with a single image"""
    print("=== Quick Validation Test ===")
    
    test_image = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'photos', '2025-07-01_1941_shot1.png')
    expected = {"shot_id": 14, "distance_to_pin": 36, "carry": 35.5, "from_pin": 2, "sg_individual": 0.54}
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return False
    
    ocr = GolfOCR(verbose=False)
    results = ocr.extract_from_image(test_image)
    
    print(f"Image: {test_image}")
    print(f"Results: {results}")
    print(f"Expected: {expected}")
    
    # Quick validation
    success = True
    for metric_key, expected_value in expected.items():
        if metric_key not in results:
            success = False
            break
        
        value_str = results[metric_key]
        
        if metric_key == "shot_id":
            try:
                extracted_value = int(value_str)
                if extracted_value != expected_value:
                    success = False
                    break
            except ValueError:
                success = False
                break
        else:
            try:
                if '+' in value_str:
                    extracted_value = float(value_str.replace('+', ''))
                else:
                    extracted_value = float(value_str)
                if abs(extracted_value - expected_value) >= 0.01:
                    success = False
                    break
            except ValueError:
                success = False
                break
    
    if success:
        print("✅ Quick test PASSED")
        return True
    else:
        print("❌ Quick test FAILED")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = quick_test()
    else:
        success = test_ground_truth()
    
    sys.exit(0 if success else 1)