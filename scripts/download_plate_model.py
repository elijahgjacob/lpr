#!/usr/bin/env python3
"""
Download pre-trained license plate detection model.

This script helps you download a YOLOv8/v11 model trained on license plates.
"""

import os
import sys
from pathlib import Path
import requests
from tqdm import tqdm


def download_file(url: str, destination: str):
    """Download file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    with open(destination, 'wb') as file, tqdm(
        desc=destination.name,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)
    
    print(f"✓ Downloaded to: {destination}")


def download_from_roboflow():
    """Download model from Roboflow Universe."""
    print("\n" + "="*70)
    print("Download from Roboflow")
    print("="*70)
    print("\nOption 1: Use Roboflow CLI to download trained model")
    print("\nSteps:")
    print("1. Go to: https://universe.roboflow.com/")
    print("2. Search for 'license plate detection'")
    print("3. Find a project with YOLO format")
    print("4. Click 'Export' → Choose 'YOLOv8' or 'YOLOv11'")
    print("5. Download the dataset + weights")
    print("6. Extract and copy the .pt file to models/license_plate_detector.pt")
    print("\nRecommended projects:")
    print("  - license-plate-recognition-rxg4e")
    print("  - car-license-plate-detection")
    print("  - vehicle-registration-plates-trudk")


def download_from_ultralytics():
    """Provide instructions for Ultralytics models."""
    print("\n" + "="*70)
    print("Download from Ultralytics Hub")
    print("="*70)
    print("\nSteps:")
    print("1. Go to: https://hub.ultralytics.com/")
    print("2. Browse models trained on license plates")
    print("3. Download the model weights (.pt file)")
    print("4. Place in: models/license_plate_detector.pt")


def download_sample_model():
    """Download a sample pre-trained model."""
    print("\n" + "="*70)
    print("Quick Option: Use a Generic Object Detection Model")
    print("="*70)
    print("\nFor quick testing, we can use a general YOLOv11 model")
    print("that detects objects. While not perfect for plates,")
    print("it can work for initial testing.")
    print("\nDownloading YOLOv11n (nano, fast)...")
    
    try:
        from ultralytics import YOLO
        
        # Download YOLOv11n
        model = YOLO("yolo11n.pt")
        
        print("\n✓ Downloaded yolo11n.pt")
        print("\nNote: This is a general object detector.")
        print("For best results, use a model specifically trained on license plates.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("Install ultralytics: pip install ultralytics")


def export_roboflow_model():
    """Help user export model from their Roboflow project."""
    print("\n" + "="*70)
    print("Export from YOUR Roboflow Project")
    print("="*70)
    
    api_key = input("\nEnter your Roboflow API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("\nManual export steps:")
        print("1. Go to: https://app.roboflow.com/")
        print("2. Open your project: roboflow-universe/license-plate-recognition-rxg4e")
        print("3. Go to 'Versions' tab")
        print("4. Click version 4")
        print("5. Click 'Export' → 'YOLOv11' format")
        print("6. Choose 'Show download code' and copy the snippet")
        return
    
    print("\nAttempting to download your model...")
    
    try:
        from roboflow import Roboflow
        
        rf = Roboflow(api_key=api_key)
        
        workspace = input("Workspace name [roboflow-universe]: ").strip() or "roboflow-universe"
        project = input("Project name [license-plate-recognition-rxg4e]: ").strip() or "license-plate-recognition-rxg4e"
        version = input("Version [4]: ").strip() or "4"
        
        print(f"\nDownloading {workspace}/{project} version {version}...")
        
        proj = rf.workspace(workspace).project(project)
        dataset = proj.version(int(version)).download("yolov8")
        
        print(f"\n✓ Dataset downloaded to: {dataset.location}")
        print("\nLook for a .pt file in the downloaded folder")
        print("Copy it to: models/license_plate_detector.pt")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTry manual export instead.")


def main():
    print("="*70)
    print("License Plate Detection Model Downloader")
    print("="*70)
    
    print("\nOptions:")
    print("1. Download from Roboflow Universe (recommended)")
    print("2. Download from Ultralytics Hub")
    print("3. Export from YOUR Roboflow project")
    print("4. Download sample model for testing")
    print("5. Show training instructions")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        download_from_roboflow()
    elif choice == "2":
        download_from_ultralytics()
    elif choice == "3":
        export_roboflow_model()
    elif choice == "4":
        download_sample_model()
    elif choice == "5":
        print("\nSee: scripts/train_plate_model.py")
    else:
        print("Invalid choice")
    
    print("\n" + "="*70)
    print("After downloading, place the model at:")
    print("  models/license_plate_detector.pt")
    print("\nThen run:")
    print("  python main.py --video input.mp4 --use-local")
    print("="*70)


if __name__ == "__main__":
    main()


