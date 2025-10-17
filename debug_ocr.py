#!/usr/bin/env python3
"""
Debug OCR results to understand the data structure.
"""

import os
import sys
import cv2
import numpy as np

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from paddleocr import PaddleOCR
import utils

def debug_ocr():
    """Debug OCR on a license plate crop."""
    print("Initializing PaddleOCR...")
    ocr_reader = PaddleOCR(use_angle_cls=True, lang='en')
    
    # Load a test frame and crop a license plate area
    frame_path = "data/golden/frames/frame_000000.jpg"
    image = cv2.imread(frame_path)
    
    # Crop around one of the license plates (based on ground truth)
    # From ground truth: frame 0, vehicle 1 has plate at (211, 398) with size (63, 17)
    x, y, w, h = 211, 398, 63, 17
    
    # Expand the crop a bit
    margin = 10
    x1 = max(0, x - margin)
    y1 = max(0, y - margin)
    x2 = min(image.shape[1], x + w + margin)
    y2 = min(image.shape[0], y + h + margin)
    
    plate_crop = image[y1:y2, x1:x2]
    
    print(f"Cropped plate shape: {plate_crop.shape}")
    
    # Save the crop for inspection
    cv2.imwrite("debug_plate_crop.jpg", plate_crop)
    print("Saved plate crop to debug_plate_crop.jpg")
    
    # Process the image
    processed = utils.preprocess_plate_image(plate_crop)
    
    # Convert back to 3D for PaddleOCR
    if len(processed.shape) == 2:
        processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
    
    cv2.imwrite("debug_processed.jpg", processed)
    print("Saved processed plate to debug_processed.jpg")
    
    # Run OCR
    print("Running OCR...")
    results = ocr_reader.ocr(processed)
    
    print(f"OCR results type: {type(results)}")
    print(f"OCR results: {results}")
    
    if results and results[0]:
        print(f"Number of lines: {len(results[0])}")
        for i, line in enumerate(results[0]):
            print(f"Line {i}: {line}")
            print(f"  Type: {type(line)}")
            if line:
                print(f"  Length: {len(line)}")
                for j, item in enumerate(line):
                    print(f"    Item {j}: {item} (type: {type(item)})")

if __name__ == "__main__":
    debug_ocr()
