#!/usr/bin/env python3
"""
Script to download the UFPR-ALPR dataset.
This is one of the best academic datasets for ALPR evaluation.
"""

import os
import requests
import zipfile
from pathlib import Path
import subprocess

def download_ufpr_dataset():
    """Download the UFPR-ALPR dataset."""
    print("🎯 DOWNLOADING UFPR-ALPR DATASET")
    print("=" * 50)
    
    # Dataset information
    dataset_info = {
        'name': 'UFPR-ALPR',
        'description': '4,500 annotated images, 1920x1080 resolution',
        'size': '~2GB',
        'url': 'https://web.inf.ufpr.br/vri/databases/ufpr-alpr/',
        'license': 'Research use only'
    }
    
    print(f"📚 Dataset: {dataset_info['name']}")
    print(f"📝 Description: {dataset_info['description']}")
    print(f"📏 Size: {dataset_info['size']}")
    print(f"🔗 URL: {dataset_info['url']}")
    print(f"📄 License: {dataset_info['license']}")
    
    # Create dataset directory
    dataset_dir = Path("videos/datasets/ufpr-alpr")
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Dataset will be saved to: {dataset_dir}")
    
    # Instructions for manual download
    print("\n📋 MANUAL DOWNLOAD INSTRUCTIONS:")
    print("1. Visit: https://web.inf.ufpr.br/vri/databases/ufpr-alpr/")
    print("2. Click on 'Download Dataset' or similar link")
    print("3. Fill out any required forms (research use)")
    print("4. Download the dataset files")
    print("5. Extract to videos/datasets/ufpr-alpr/")
    
    print("\n🔄 Alternative: Try automated download...")
    
    # Try to find direct download links (these may change)
    download_urls = [
        "https://web.inf.ufpr.br/vri/databases/ufpr-alpr/UFPR-ALPR.zip",
        "https://web.inf.ufpr.br/vri/databases/ufpr-alpr/download/UFPR-ALPR.zip",
        "https://web.inf.ufpr.br/vri/databases/ufpr-alpr/dataset/UFPR-ALPR.zip"
    ]
    
    for url in download_urls:
        try:
            print(f"🔍 Trying: {url}")
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Found download link: {url}")
                print("📥 Starting download...")
                
                # Download the file
                response = requests.get(url, stream=True)
                zip_path = dataset_dir / "UFPR-ALPR.zip"
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✅ Downloaded: {zip_path}")
                
                # Extract the zip file
                print("📦 Extracting...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(dataset_dir)
                
                print("✅ Extraction complete!")
                
                # Clean up zip file
                zip_path.unlink()
                
                print(f"🎉 UFPR-ALPR dataset ready in: {dataset_dir}")
                return True
                
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    print("❌ Automated download failed")
    print("📋 Please download manually from the website")
    return False

def check_dataset():
    """Check if dataset is already downloaded."""
    dataset_dir = Path("videos/datasets/ufpr-alpr")
    
    if dataset_dir.exists() and any(dataset_dir.iterdir()):
        print("✅ UFPR-ALPR dataset already exists!")
        print(f"📁 Location: {dataset_dir}")
        
        # List contents
        files = list(dataset_dir.rglob("*"))
        print(f"📊 Files found: {len(files)}")
        
        return True
    return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download UFPR-ALPR dataset")
    parser.add_argument('--check', action='store_true', help='Check if dataset exists')
    
    args = parser.parse_args()
    
    if args.check:
        check_dataset()
    else:
        if not check_dataset():
            download_ufpr_dataset()
        else:
            print("Dataset already exists. Use --check to verify.")

if __name__ == "__main__":
    main()
