#!/usr/bin/env python3
"""
Train a YOLOv11 model for license plate detection.

This script shows how to train your own model if you have labeled data.
"""

import argparse
from pathlib import Path
from ultralytics import YOLO
import yaml


def create_dataset_yaml(data_dir: str, output_path: str = "plate_dataset.yaml"):
    """Create dataset configuration file for YOLO training."""
    
    data_dir = Path(data_dir)
    
    # Create YAML configuration
    config = {
        'path': str(data_dir.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',  # optional
        'names': {
            0: 'license_plate'
        },
        'nc': 1  # number of classes
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"✓ Created dataset config: {output_path}")
    return output_path


def train_model(
    data_yaml: str,
    model_size: str = 'yolo11n',
    epochs: int = 100,
    img_size: int = 640,
    batch_size: int = 16,
    name: str = 'plate_detector'
):
    """
    Train YOLO model for license plate detection.
    
    Args:
        data_yaml: Path to dataset YAML configuration
        model_size: Model size (yolo11n, yolo11s, yolo11m, yolo11l, yolo11x)
        epochs: Number of training epochs
        img_size: Image size for training
        batch_size: Batch size
        name: Name for this training run
    """
    
    print("="*70)
    print(f"Training {model_size} for License Plate Detection")
    print("="*70)
    
    # Load model
    print(f"\nLoading {model_size} model...")
    model = YOLO(f"{model_size}.pt")
    
    # Train
    print(f"\nStarting training...")
    print(f"  Epochs: {epochs}")
    print(f"  Image size: {img_size}")
    print(f"  Batch size: {batch_size}")
    print("-"*70)
    
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        name=name,
        patience=50,  # Early stopping patience
        save=True,
        device='mps',  # Use Apple Silicon GPU (change to 'cpu' or '0' for CUDA)
        workers=4,
        project='runs/train',
        exist_ok=True,
        pretrained=True,
        optimizer='auto',
        verbose=True,
        seed=42,
        deterministic=True,
        single_cls=True,  # Single class detection
        rect=False,
        cos_lr=False,
        close_mosaic=10,
        amp=True,
        fraction=1.0,
        profile=False,
        freeze=None,
        lr0=0.01,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        pose=12.0,
        kobj=1.0,
        label_smoothing=0.0,
        nbs=64,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.0,
        copy_paste=0.0,
    )
    
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    
    # Get best model path
    best_model = Path(results.save_dir) / 'weights' / 'best.pt'
    
    print(f"\nBest model saved to: {best_model}")
    print(f"\nTo use this model:")
    print(f"  cp {best_model} models/license_plate_detector.pt")
    print(f"  python main.py --video input.mp4 --use-local")
    
    return best_model


def prepare_roboflow_dataset(api_key: str, workspace: str, project: str, version: int):
    """Download and prepare dataset from Roboflow."""
    
    print("="*70)
    print("Downloading Dataset from Roboflow")
    print("="*70)
    
    try:
        from roboflow import Roboflow
        
        rf = Roboflow(api_key=api_key)
        proj = rf.workspace(workspace).project(project)
        dataset = proj.version(version).download("yolov8")
        
        print(f"\n✓ Dataset downloaded to: {dataset.location}")
        
        # Create dataset YAML
        yaml_path = create_dataset_yaml(dataset.location)
        
        return yaml_path
        
    except Exception as e:
        print(f"\n✗ Error downloading dataset: {e}")
        return None


def show_dataset_requirements():
    """Show what's needed for training."""
    
    print("="*70)
    print("Dataset Requirements for Training")
    print("="*70)
    
    print("\nYour dataset should be organized like this:")
    print("""
    dataset/
    ├── images/
    │   ├── train/
    │   │   ├── img1.jpg
    │   │   ├── img2.jpg
    │   │   └── ...
    │   ├── val/
    │   │   ├── img1.jpg
    │   │   └── ...
    │   └── test/  (optional)
    └── labels/
        ├── train/
        │   ├── img1.txt  (YOLO format annotations)
        │   ├── img2.txt
        │   └── ...
        └── val/
            ├── img1.txt
            └── ...
    """)
    
    print("\nYOLO Label Format (one line per object):")
    print("  <class_id> <x_center> <y_center> <width> <height>")
    print("\nExample: 0 0.5 0.5 0.2 0.1")
    print("  - class_id: 0 (license_plate)")
    print("  - x_center, y_center: normalized (0-1)")
    print("  - width, height: normalized (0-1)")
    
    print("\n" + "="*70)
    print("Options to get training data:")
    print("="*70)
    print("\n1. Use Roboflow:")
    print("   - Go to https://universe.roboflow.com/")
    print("   - Search for 'license plate' datasets")
    print("   - Export in YOLOv8 format")
    
    print("\n2. Label your own:")
    print("   - Use tools like LabelImg, CVAT, or Roboflow")
    print("   - Label 500-1000 images for good results")
    print("   - Export in YOLO format")
    
    print("\n3. Use existing dataset:")
    print("   - Find datasets on Kaggle, GitHub, etc.")
    print("   - Convert to YOLO format if needed")


def main():
    parser = argparse.ArgumentParser(
        description="Train YOLOv11 for license plate detection"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train model')
    train_parser.add_argument('--data', required=True, help='Path to dataset YAML')
    train_parser.add_argument('--model', default='yolo11n', help='Model size (n/s/m/l/x)')
    train_parser.add_argument('--epochs', type=int, default=100, help='Training epochs')
    train_parser.add_argument('--batch', type=int, default=16, help='Batch size')
    train_parser.add_argument('--img-size', type=int, default=640, help='Image size')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download dataset from Roboflow')
    download_parser.add_argument('--api-key', required=True, help='Roboflow API key')
    download_parser.add_argument('--workspace', required=True, help='Workspace name')
    download_parser.add_argument('--project', required=True, help='Project name')
    download_parser.add_argument('--version', type=int, required=True, help='Version number')
    
    # Requirements command
    subparsers.add_parser('requirements', help='Show dataset requirements')
    
    args = parser.parse_args()
    
    if args.command == 'train':
        train_model(
            data_yaml=args.data,
            model_size=args.model,
            epochs=args.epochs,
            batch_size=args.batch,
            img_size=args.img_size
        )
    
    elif args.command == 'download':
        yaml_path = prepare_roboflow_dataset(
            api_key=args.api_key,
            workspace=args.workspace,
            project=args.project,
            version=args.version
        )
        
        if yaml_path:
            print(f"\nReady to train! Run:")
            print(f"  python scripts/train_plate_model.py train --data {yaml_path}")
    
    elif args.command == 'requirements':
        show_dataset_requirements()
    
    else:
        parser.print_help()
        print("\nExamples:")
        print("\n  # Show requirements")
        print("  python scripts/train_plate_model.py requirements")
        print("\n  # Download dataset from Roboflow")
        print("  python scripts/train_plate_model.py download \\")
        print("    --api-key YOUR_KEY \\")
        print("    --workspace roboflow-universe \\")
        print("    --project license-plate-recognition-rxg4e \\")
        print("    --version 4")
        print("\n  # Train model")
        print("  python scripts/train_plate_model.py train \\")
        print("    --data plate_dataset.yaml \\")
        print("    --model yolo11n \\")
        print("    --epochs 100")


if __name__ == "__main__":
    main()


