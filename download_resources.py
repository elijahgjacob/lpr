#!/usr/bin/env python3
"""
Resource Downloader for ALPR System

Downloads required models and sample videos for the ALPR system.
Includes interactive setup wizard for Roboflow configuration.
"""

import argparse
import os
import sys
from pathlib import Path
import requests
from typing import Optional

import config


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_step(step: int, total: int, message: str):
    """Print a formatted step."""
    print(f"\n[{step}/{total}] {message}")


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()


def download_file(url: str, destination: str, description: str = "file") -> bool:
    """
    Download a file from URL to destination.
    
    Args:
        url: URL to download from
        destination: Local file path to save to
        description: Description for progress message
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Downloading {description}...")
        print(f"  URL: {url}")
        print(f"  Destination: {destination}")
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        Path(destination).parent.mkdir(parents=True, exist_ok=True)
        
        with open(destination, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = (downloaded / total_size) * 100
                        print(f"  Progress: {progress:.1f}%", end='\r')
        
        print(f"\n  ✓ Downloaded successfully")
        return True
    
    except Exception as e:
        print(f"\n  ✗ Download failed: {e}")
        return False


def setup_roboflow() -> bool:
    """
    Interactive Roboflow setup wizard.
    
    Returns:
        bool: True if setup successful, False otherwise
    """
    print_section("Roboflow Setup Wizard")
    
    print("\nRoboflow provides pre-trained license plate detection models.")
    print("To use Roboflow, you need a free API key.")
    print()
    print("Steps to get your API key:")
    print("  1. Visit: https://app.roboflow.com")
    print("  2. Create a free account (or sign in)")
    print("  3. Go to Settings > API Keys")
    print("  4. Copy your API key")
    print()
    
    # Check if .env exists
    env_path = Path(".env")
    if env_path.exists():
        print("⚠ .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled")
            return False
    
    # Get API key from user
    print("\nEnter your Roboflow API key (or press Enter to skip):")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("\n⚠ Skipping Roboflow setup")
        print("You can manually edit .env file later")
        return False
    
    # Test API key
    print("\nValidating API key...")
    try:
        from roboflow import Roboflow
        rf = Roboflow(api_key=api_key)
        print("  ✓ API key is valid")
    except Exception as e:
        print(f"  ✗ API key validation failed: {e}")
        print("  Continuing anyway...")
    
    # Get Supabase credentials
    print("\n" + "-" * 70)
    print("Supabase Setup (Optional)")
    print("-" * 70)
    print("\nSupabase stores detection results for analysis.")
    print("Visit: https://supabase.com")
    print()
    
    supabase_url = input("Supabase URL (or press Enter to skip): ").strip()
    supabase_key = input("Supabase Key (or press Enter to skip): ").strip()
    
    # Create .env file
    print("\nCreating .env file...")
    with open(".env", "w") as f:
        f.write("# Roboflow Configuration\n")
        f.write(f"ROBOFLOW_API_KEY={api_key}\n")
        f.write("ROBOFLOW_WORKSPACE=roboflow-universe\n")
        f.write("ROBOFLOW_PROJECT=license-plate-recognition-rxg4e\n")
        f.write("ROBOFLOW_VERSION=4\n")
        f.write("USE_ROBOFLOW_API=true\n")
        f.write("\n")
        f.write("# Supabase Configuration\n")
        if supabase_url and supabase_key:
            f.write(f"SUPABASE_URL={supabase_url}\n")
            f.write(f"SUPABASE_KEY={supabase_key}\n")
            f.write("ENABLE_SUPABASE=true\n")
        else:
            f.write("SUPABASE_URL=\n")
            f.write("SUPABASE_KEY=\n")
            f.write("ENABLE_SUPABASE=false\n")
    
    print("  ✓ .env file created successfully")
    return True


def download_vehicle_model() -> bool:
    """
    Download vehicle detection model (YOLOv11x).
    
    Returns:
        bool: True if successful or already exists, False otherwise
    """
    print_step(1, 3, "Vehicle Detection Model")
    
    model_path = config.VEHICLE_MODEL_PATH
    
    if check_file_exists(model_path):
        print(f"  ✓ Model already exists: {model_path}")
        return True
    
    print("\nThe vehicle model (yolo11x.pt) will be downloaded automatically")
    print("by Ultralytics when you first run the system.")
    print()
    print("Alternative: Download manually from:")
    print("  https://github.com/ultralytics/assets/releases/download/v8.2.0/yolo11x.pt")
    print(f"  Save to: {model_path}")
    
    return True


def download_plate_model() -> bool:
    """
    Download license plate detection model from Roboflow.
    
    Returns:
        bool: True if successful, False otherwise
    """
    print_step(2, 3, "License Plate Detection Model")
    
    # Check if using Roboflow API
    if config.USE_ROBOFLOW_API:
        print("\n✓ Configured to use Roboflow API")
        print("  No local model download needed")
        return True
    
    model_path = config.PLATE_MODEL_PATH
    
    if check_file_exists(model_path):
        print(f"  ✓ Model already exists: {model_path}")
        return True
    
    print("\nAttempting to download license plate model from Roboflow...")
    
    try:
        from roboflow import Roboflow
        
        if not config.ROBOFLOW_API_KEY:
            print("  ✗ Roboflow API key not set")
            print("  Run: python download_resources.py --setup")
            return False
        
        rf = Roboflow(api_key=config.ROBOFLOW_API_KEY)
        project = rf.workspace(config.ROBOFLOW_WORKSPACE).project(config.ROBOFLOW_PROJECT)
        dataset = project.version(config.ROBOFLOW_VERSION).download("yolov8")
        
        print(f"  ✓ Model downloaded successfully")
        print(f"  Location: {dataset.location}")
        return True
    
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        print("\n  Alternative options:")
        print("  1. Use Roboflow API (set USE_ROBOFLOW_API=true in .env)")
        print("  2. Train your own model using Roboflow")
        print("  3. Find a pre-trained model from Roboflow Universe")
        return False


def download_sample_video() -> bool:
    """
    Download sample video for testing.
    
    Returns:
        bool: True if successful, False otherwise
    """
    print_step(3, 3, "Sample Video")
    
    video_path = config.VIDEOS_DIR / "sample_traffic.mp4"
    
    if check_file_exists(str(video_path)):
        print(f"  ✓ Sample video already exists: {video_path}")
        return True
    
    print("\nSample video options:")
    print("  Due to size constraints, we recommend:")
    print()
    print("  1. Download from Pexels (free stock footage)")
    print("     https://www.pexels.com/search/videos/traffic/")
    print()
    print("  2. Use your own video file")
    print("     Copy to: videos/")
    print()
    print("  3. Download sample from:")
    print("     https://sample-videos.com/")
    print()
    
    response = input("Do you want to download a small sample video? (y/N): ").strip().lower()
    
    if response == 'y':
        # Small sample video URL (replace with actual URL)
        sample_url = "https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4"
        
        success = download_file(
            sample_url,
            str(video_path),
            "sample video"
        )
        
        if success:
            print("\n  Note: This is a generic video for testing the system.")
            print("  For best results, use traffic/parking lot footage.")
        
        return success
    else:
        print("\n  Skipped sample video download")
        print("  You can add your own videos to the videos/ directory")
        return True


def check_dependencies():
    """Check if required Python packages are installed."""
    print_section("Checking Dependencies")
    
    required_packages = [
        ('torch', 'PyTorch'),
        ('ultralytics', 'Ultralytics YOLO'),
        ('cv2', 'OpenCV'),
        ('easyocr', 'EasyOCR'),
        ('roboflow', 'Roboflow'),
        ('supabase', 'Supabase'),
    ]
    
    missing = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            missing.append(name)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("\nInstall all dependencies with:")
        print("  pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download resources for ALPR system",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Run interactive setup wizard'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Download all resources (models and sample video)'
    )
    
    parser.add_argument(
        '--models-only',
        action='store_true',
        help='Download only models'
    )
    
    parser.add_argument(
        '--video-only',
        action='store_true',
        help='Download only sample video'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check if dependencies are installed'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print(" ALPR System - Resource Downloader")
    print("=" * 70)
    
    # Check dependencies
    if args.check_deps or not any([args.setup, args.all, args.models_only, args.video_only]):
        check_dependencies()
        if args.check_deps:
            return
    
    # Interactive setup
    if args.setup:
        setup_roboflow()
        return
    
    # Download resources
    if args.all or args.models_only:
        download_vehicle_model()
        download_plate_model()
    
    if args.all or args.video_only:
        download_sample_video()
    
    # Default: show help
    if not any([args.setup, args.all, args.models_only, args.video_only, args.check_deps]):
        parser.print_help()
        print("\n" + "=" * 70)
        print(" Quick Start:")
        print("=" * 70)
        print("  1. Install dependencies:    pip install -r requirements.txt")
        print("  2. Setup Roboflow:          python download_resources.py --setup")
        print("  3. Download all resources:  python download_resources.py --all")
        print("=" * 70)


if __name__ == "__main__":
    main()

