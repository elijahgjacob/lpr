#!/usr/bin/env python3
"""
Download the specific Roboflow model: license-plate-recognition-rxg4e v11
for local use without API calls.
"""

from roboflow import Roboflow
from pathlib import Path

def download_model():
    """Download model v11 from Roboflow Universe."""
    
    print("="*70)
    print("Downloading License Plate Model v11")
    print("="*70)
    print("\nProject: license-plate-recognition-rxg4e")
    print("Version: 11")
    print("Source: https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e/model/11")
    print("-"*70)
    
    # Initialize Roboflow
    API_KEY = "x4Xvvvw47esbu5nZ5XPx"
    
    print("\nInitializing Roboflow...")
    rf = Roboflow(api_key=API_KEY)
    
    # Access project
    print("Accessing project...")
    workspace = rf.workspace("roboflow-universe-projects")
    project = workspace.project("license-plate-recognition-rxg4e")
    version = project.version(11)
    
    # Download dataset with model
    print("\nDownloading YOLOv8 format...")
    print("(This includes trained weights)")
    
    dataset = version.download("yolov8", location="data/roboflow_downloads")
    
    print("\n" + "="*70)
    print("Download Complete!")
    print("="*70)
    print(f"\nDataset location: {dataset.location}")
    
    # Look for model weights
    dataset_path = Path(dataset.location)
    
    # Check common weight locations
    possible_weights = [
        dataset_path / "weights" / "best.pt",
        dataset_path / "train" / "weights" / "best.pt",
        dataset_path / "best.pt",
        dataset_path.parent / "weights" / "best.pt"
    ]
    
    weight_file = None
    for w in possible_weights:
        if w.exists():
            weight_file = w
            break
    
    if weight_file:
        # Copy to models directory
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        dest = models_dir / "license_plate_detector.pt"
        
        import shutil
        shutil.copy(weight_file, dest)
        
        print(f"\n✓ Model weights copied to: {dest}")
        print("\nYou can now run:")
        print("  python main.py --video input.mp4 --use-local")
    else:
        print("\n⚠ Model weights not found in download")
        print("You may need to train the model or export it differently")
        print("\nAlternatively, use the Roboflow API:")
        print("  python main.py --video input.mp4 --use-roboflow")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        download_model()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nNote: This downloads the dataset. The model may need to be")
        print("exported differently from Roboflow for local use.")
        print("\nFor now, use the API with version 11 (already configured in .env):")
        print("  python main.py --video input.mp4")


