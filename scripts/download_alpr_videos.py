#!/usr/bin/env python3
"""
Script to download high-quality ALPR videos from various sources.
"""

import os
import subprocess
import requests
import json
from pathlib import Path
import time

def create_directories():
    """Create necessary directories."""
    Path("videos/quality").mkdir(parents=True, exist_ok=True)
    Path("videos/datasets").mkdir(parents=True, exist_ok=True)
    print("✓ Created video directories")

def download_youtube_video(url, output_name):
    """Download YouTube video using yt-dlp."""
    try:
        cmd = [
            'yt-dlp',
            '-f', 'best[height>=1080]',  # Best quality 1080p or higher
            '-o', f'videos/quality/{output_name}.%(ext)s',
            url
        ]
        
        print(f"📥 Downloading: {output_name}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Downloaded: {output_name}")
            return True
        else:
            print(f"❌ Failed to download {output_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error downloading {output_name}: {e}")
        return False

def download_dataset_info():
    """Get information about academic datasets."""
    datasets = [
        {
            'name': 'UFPR-ALPR',
            'url': 'https://web.inf.ufpr.br/vri/databases/ufpr-alpr/',
            'description': '4,500 annotated images, 1920x1080 resolution',
            'size': '~2GB',
            'license': 'Research use'
        },
        {
            'name': 'AI City Challenge',
            'url': 'https://www.aicitychallenge.org/',
            'description': '3 hours of synchronized videos, 960p+ resolution',
            'size': '~50GB',
            'license': 'Research use'
        },
        {
            'name': 'CCPD Dataset',
            'url': 'https://github.com/detectRecog/CCPD',
            'description': '290k+ Chinese license plate images',
            'size': '~10GB',
            'license': 'Research use'
        }
    ]
    
    print("📚 ACADEMIC DATASETS:")
    for dataset in datasets:
        print(f"\n🎯 {dataset['name']}")
        print(f"   Description: {dataset['description']}")
        print(f"   Size: {dataset['size']}")
        print(f"   License: {dataset['license']}")
        print(f"   URL: {dataset['url']}")
    
    return datasets

def find_youtube_videos():
    """Find specific YouTube videos good for ALPR."""
    # These are example searches - you'll need to find actual URLs
    search_terms = [
        "traffic surveillance 4K high quality",
        "highway traffic camera HD license plates",
        "traffic intersection 1080p clear plates",
        "vehicle surveillance camera clear",
        "road traffic monitoring HD"
    ]
    
    print("🔍 YOUTUBE SEARCH TERMS:")
    for term in search_terms:
        print(f"   - {term}")
    
    print("\n📋 MANUAL SEARCH INSTRUCTIONS:")
    print("1. Go to YouTube")
    print("2. Search for each term above")
    print("3. Look for videos with:")
    print("   - 1080p or 4K resolution")
    print("   - Clear license plates visible")
    print("   - Good lighting conditions")
    print("   - 5+ minutes duration")
    print("4. Copy the URL and run:")
    print("   python scripts/download_alpr_videos.py --download-youtube [URL]")

def download_sample_videos():
    """Download some sample videos if URLs are provided."""
    # Placeholder for actual video URLs
    sample_videos = [
        # Add actual YouTube URLs here when found
        # {
        #     'url': 'https://www.youtube.com/watch?v=EXAMPLE1',
        #     'name': 'traffic_surveillance_sample1'
        # },
        # {
        #     'url': 'https://www.youtube.com/watch?v=EXAMPLE2', 
        #     'name': 'highway_camera_sample1'
        # }
    ]
    
    if sample_videos:
        print("📥 DOWNLOADING SAMPLE VIDEOS:")
        for video in sample_videos:
            download_youtube_video(video['url'], video['name'])
    else:
        print("ℹ️  No sample video URLs configured yet")
        print("   Please find YouTube URLs manually and add them to the script")

def create_download_guide():
    """Create a comprehensive download guide."""
    guide = """
# ALPR Video Download Guide

## Quick Start (YouTube)
1. Search YouTube for these terms:
   - "traffic surveillance 4K"
   - "highway traffic camera HD"
   - "traffic intersection 1080p"
   - "vehicle surveillance clear plates"

2. Download with yt-dlp:
   ```bash
   yt-dlp -f "best[height>=1080]" -o "videos/quality/%(title)s.%(ext)s" [YOUTUBE_URL]
   ```

## Academic Datasets (Best Quality)

### UFPR-ALPR Dataset
- **URL**: https://web.inf.ufpr.br/vri/databases/ufpr-alpr/
- **Size**: ~2GB
- **Quality**: 1920x1080, 4500 images
- **License**: Research use

### AI City Challenge
- **URL**: https://www.aicitychallenge.org/
- **Size**: ~50GB  
- **Quality**: 960p+, 3 hours of video
- **License**: Research use

### CCPD Dataset
- **URL**: https://github.com/detectRecog/CCPD
- **Size**: ~10GB
- **Quality**: 290k+ images
- **License**: Research use

## Video Quality Checklist
- ✅ Resolution: 1080p or higher
- ✅ Duration: 5+ minutes
- ✅ File Size: 50MB+ (indicates good quality)
- ✅ Clear License Plates: Visible to human eye
- ✅ Good Lighting: Well-lit conditions
- ✅ Multiple Vehicles: Variety of plate types

## After Download
```bash
# Check video quality
python scripts/check_video_quality.py videos/quality/your_video.mp4

# Target: Quality Score 6+/8
```
"""
    
    with open('ALPR_Video_Download_Guide.md', 'w') as f:
        f.write(guide)
    
    print("✓ Created ALPR_Video_Download_Guide.md")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download ALPR videos")
    parser.add_argument('--action', choices=['guide', 'datasets', 'youtube', 'download-youtube'], 
                       default='guide', help='Action to perform')
    parser.add_argument('--url', type=str, help='YouTube URL to download')
    parser.add_argument('--name', type=str, help='Output name for video')
    
    args = parser.parse_args()
    
    create_directories()
    
    if args.action == 'guide':
        create_download_guide()
        find_youtube_videos()
        download_dataset_info()
    elif args.action == 'datasets':
        download_dataset_info()
    elif args.action == 'youtube':
        find_youtube_videos()
    elif args.action == 'download-youtube':
        if args.url and args.name:
            download_youtube_video(args.url, args.name)
        else:
            print("❌ Please provide --url and --name for YouTube download")

if __name__ == "__main__":
    main()
