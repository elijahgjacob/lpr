#!/usr/bin/env python3
"""
Test ALPR on a single frame to debug issues.
"""

import os
import sys
import cv2
import numpy as np

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpr_system import ALPRSystem

def test_single_frame():
    """Test ALPR on a single frame."""
    # Initialize ALPR system
    print("Initializing ALPR System...")
    alpr = ALPRSystem()
    
    # Load a test frame
    frame_path = "data/golden/frames/frame_000000.jpg"
    print(f"Loading frame: {frame_path}")
    
    image = cv2.imread(frame_path)
    if image is None:
        print("Error: Could not load image")
        return
    
    print(f"Image shape: {image.shape}")
    
    # Test vehicle detection separately
    print("\nTesting vehicle detection...")
    try:
        vehicles = alpr.detect_vehicles(image)
        print(f"Found {len(vehicles)} vehicles")
        for i, vehicle in enumerate(vehicles):
            print(f"  Vehicle {i}: {vehicle}")
    except Exception as e:
        print(f"Vehicle detection error: {e}")
    
    # Test full processing
    print("\nTesting full ALPR processing...")
    try:
        annotated_frame, detections = alpr.process_frame(image, 0, visualize=True)
        print(f"Found {len(detections)} detections")
        for i, detection in enumerate(detections):
            print(f"  Detection {i}: {detection}")
    except Exception as e:
        print(f"Full processing error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_frame()

