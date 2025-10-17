#!/usr/bin/env python3
"""
Startup script for the license plate labeling interface.
Installs dependencies and starts the Flask server.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_frames():
    """Check if frames exist."""
    frames_dir = "../data/golden/frames"
    if not os.path.exists(frames_dir):
        print(f"❌ Frames directory not found: {frames_dir}")
        print("Please run the frame extraction script first:")
        print("python ../scripts/create_golden_dataset.py --action extract")
        return False
    
    frame_files = [f for f in os.listdir(frames_dir) if f.startswith('frame_') and f.endswith('.jpg')]
    if len(frame_files) == 0:
        print(f"❌ No frame files found in: {frames_dir}")
        print("Please run the frame extraction script first:")
        print("python ../scripts/create_golden_dataset.py --action extract")
        return False
    
    print(f"✅ Found {len(frame_files)} frames in {frames_dir}")
    return True

def main():
    print("🚗 License Plate Labeling Interface Setup")
    print("=" * 50)
    
    # Check if frames exist
    if not check_frames():
        return
    
    # Install dependencies
    if not install_requirements():
        return
    
    print("\n🎉 Setup complete! Starting the labeling interface...")
    print("=" * 50)
    print("📋 Instructions:")
    print("1. Open your browser to: http://localhost:5000")
    print("2. Click and drag to draw vehicle bounding boxes (green)")
    print("3. Click and drag to draw license plate bounding boxes (red)")
    print("4. Fill in the license plate text and other details")
    print("5. Click 'Add Vehicle' to save each vehicle")
    print("6. Use 'Next Frame' to move to the next frame")
    print("7. Click 'Save & Exit' when done")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    
    # Start the Flask app
    try:
        import app
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Happy labeling!")

if __name__ == "__main__":
    main()
