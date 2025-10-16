#!/usr/bin/env python3
"""
Script to help find and download good ALPR videos.
"""

import os
import subprocess
import requests
from pathlib import Path

def check_video_quality(video_path):
    """Check basic video quality metrics."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if video_stream:
                width = video_stream.get('width', 0)
                height = video_stream.get('height', 0)
                fps = eval(video_stream.get('r_frame_rate', '0/1'))
                
                print(f"Video: {width}x{height}, {fps:.1f} fps")
                return {
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'quality_score': (width * height * fps) / 1000000  # Simple quality score
                }
    except Exception as e:
        print(f"Error checking video quality: {e}")
    
    return None

def suggest_video_sources():
    """Suggest good sources for ALPR videos."""
    sources = [
        {
            'name': 'OpenALPR Benchmark Dataset',
            'url': 'https://github.com/openalpr/benchmarks',
            'description': 'Academic dataset with ground truth annotations',
            'quality': 'High - Academic grade',
            'license': 'Research use'
        },
        {
            'name': 'CCPD Dataset',
            'url': 'https://github.com/detectRecog/CCPD',
            'description': 'Chinese City Parking Dataset with license plates',
            'quality': 'High - 290k+ images',
            'license': 'Research use'
        },
        {
            'name': 'UFPR-ALPR Dataset',
            'url': 'https://web.inf.ufpr.br/vri/databases/ufpr-alpr/',
            'description': 'Brazilian license plate dataset',
            'quality': 'High - Academic dataset',
            'license': 'Research use'
        },
        {
            'name': 'YouTube Traffic Videos',
            'description': 'Search for: "traffic surveillance 4K", "highway traffic camera"',
            'quality': 'Variable - Manual selection needed',
            'license': 'Check individual videos'
        },
        {
            'name': 'Traffic Cameras (Public)',
            'description': 'Many cities have public traffic camera feeds',
            'quality': 'Variable - Often low resolution',
            'license': 'Public domain'
        }
    ]
    
    print("=== RECOMMENDED ALPR VIDEO SOURCES ===")
    for i, source in enumerate(sources, 1):
        print(f"\n{i}. {source['name']}")
        print(f"   Description: {source['description']}")
        print(f"   Quality: {source['quality']}")
        print(f"   License: {source['license']}")
        if 'url' in source:
            print(f"   URL: {source['url']}")

def create_video_requirements():
    """Create a requirements document for good ALPR videos."""
    requirements = """
# ALPR Video Requirements

## Minimum Requirements:
- Resolution: 1080p (1920x1080) minimum
- Frame Rate: 30fps minimum
- Duration: 5-15 minutes
- Format: MP4, AVI, or MOV

## Quality Criteria:
- License plates clearly visible to human eye
- Minimal motion blur
- Good lighting conditions
- Multiple vehicle types and plate formats
- Various viewing angles (front, rear, side)

## What to Look For:
✅ High contrast between plate and background
✅ Plates fill reasonable portion of frame
✅ Minimal occlusions (no objects blocking plates)
✅ Variety in plate colors and formats
✅ Different lighting conditions

## What to Avoid:
❌ Low resolution videos (< 720p)
❌ Excessive motion blur
❌ Poor lighting or shadows
❌ Plates too small in frame
❌ Heavy compression artifacts
"""
    
    with open('ALPR_Video_Requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✓ Created ALPR_Video_Requirements.txt")

def download_sample_video():
    """Download a sample high-quality traffic video."""
    print("Looking for sample traffic videos...")
    
    # This would be a placeholder - in practice you'd download from a specific source
    sample_urls = [
        "https://example.com/sample-traffic-video.mp4",  # Placeholder
        # Add real URLs here when found
    ]
    
    print("To download sample videos:")
    print("1. Visit traffic camera websites")
    print("2. Use tools like yt-dlp for YouTube videos")
    print("3. Check academic dataset repositories")
    
    return sample_urls

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Find and analyze ALPR videos")
    parser.add_argument('--action', choices=['sources', 'requirements', 'analyze', 'download'], 
                       default='sources', help='Action to perform')
    parser.add_argument('--video', type=str, help='Path to video file for analysis')
    
    args = parser.parse_args()
    
    if args.action == 'sources':
        suggest_video_sources()
    elif args.action == 'requirements':
        create_video_requirements()
    elif args.action == 'analyze' and args.video:
        check_video_quality(args.video)
    elif args.action == 'download':
        download_sample_video()
    else:
        suggest_video_sources()

if __name__ == "__main__":
    main()
