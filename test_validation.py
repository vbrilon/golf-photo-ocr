#!/usr/bin/env python3
"""
Simple validation test for Golf Photo OCR system
Tests the system against ground truth data stored in config.json
"""

import json
import os
from main import GolfOCR

def test_ground_truth():
    """Test all ground truth images for accuracy"""
    
    # Load ground truth data from config
    with open('config.json', 'r') as f:
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
    
    for filename, expected_values in ground_truth.items():
        image_path = f"photos/{filename}"
        
        if not os.path.exists(image_path):
            print(f"⚠️  {filename}: Image not found, skipping")
            continue
        
        total += 1
        
        try:
            # Extract metrics
            results = ocr.extract_from_image(image_path)
            
            # Convert results to floats for comparison
            extracted_values = []
            for i, label in enumerate(ocr.labels):
                value_str = results[label]
                
                # Handle signs
                if '+' in value_str:
                    value = float(value_str.replace('+', ''))
                else:
                    value = float(value_str)
                    
                extracted_values.append(value)
            
            # Compare with ground truth
            all_correct = True
            for i, (extracted, expected) in enumerate(zip(extracted_values, expected_values)):
                if abs(extracted - expected) >= 0.01:  # Allow small floating point differences
                    all_correct = False
                    break
            
            if all_correct:
                print(f"✅ {filename}: PASS")
                passed += 1
            else:
                print(f"❌ {filename}: FAIL")
                print(f"   Expected: {expected_values}")
                print(f"   Got:      {extracted_values}")
                
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
    
    test_image = "photos/2025-07-01_1941_shot1.png"
    expected = [36, 35.5, 2, 0.54]
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return False
    
    ocr = GolfOCR(verbose=False)
    results = ocr.extract_from_image(test_image)
    
    print(f"Image: {test_image}")
    print(f"Results: {list(results.values())}")
    print(f"Expected: {expected}")
    
    # Quick validation
    extracted = [float(results[label].replace('+', '')) for label in ocr.labels]
    success = all(abs(e - x) < 0.01 for e, x in zip(extracted, expected))
    
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