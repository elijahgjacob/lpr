#!/usr/bin/env python3
"""
Quick launcher for the license plate labeling interface.
"""

import subprocess
import sys
import webbrowser
import time
import os

def main():
    print("🚗 License Plate Labeling Interface")
    print("=" * 50)
    
    # Check if frames exist
    frames_dir = "data/golden/frames"
    if not os.path.exists(frames_dir):
        print(f"❌ Frames directory not found: {frames_dir}")
        print("Please run the frame extraction script first:")
        print("python scripts/create_golden_dataset.py --action extract")
        return
    
    frame_files = [f for f in os.listdir(frames_dir) if f.startswith('frame_') and f.endswith('.jpg')]
    if len(frame_files) == 0:
        print(f"❌ No frame files found in: {frames_dir}")
        print("Please run the frame extraction script first:")
        print("python scripts/create_golden_dataset.py --action extract")
        return
    
    print(f"✅ Found {len(frame_files)} frames ready for labeling")
    print("\n🚀 Starting labeling interface...")
    print("=" * 50)
    print("📋 Instructions:")
    print("1. Your browser will open automatically to: http://localhost:5001")
    print("2. Click and drag to draw vehicle bounding boxes (green)")
    print("3. Click and drag to draw license plate bounding boxes (red)")
    print("4. Fill in the license plate text and other details")
    print("5. Click 'Add Vehicle' to save each vehicle")
    print("6. Use 'Next Frame' to move to the next frame")
    print("7. Click 'Save & Exit' when done")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start the Flask server
        os.chdir('labeling_interface')
        process = subprocess.Popen([sys.executable, 'app.py'])
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        webbrowser.open('http://localhost:5001')
        
        # Wait for process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Happy labeling!")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    main()
