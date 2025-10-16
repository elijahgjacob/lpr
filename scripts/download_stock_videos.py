#!/usr/bin/env python3
"""
Script to download free stock videos with traffic/vehicles for ALPR testing.
"""

import os
import requests
from pathlib import Path
import time

def download_video(url, filename):
    """Download a video from URL."""
    try:
        print(f"📥 Downloading: {filename}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        video_path = Path("videos/quality") / filename
        video_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False

def download_sample_videos():
    """Download some sample traffic videos."""
    print("🎯 DOWNLOADING SAMPLE TRAFFIC VIDEOS")
    print("=" * 50)
    
    # These are example URLs - in practice, you'd find actual working URLs
    sample_videos = [
        # Placeholder URLs - these would need to be actual working video URLs
        # {
        #     'url': 'https://example.com/traffic1.mp4',
        #     'filename': 'traffic_sample_1.mp4',
        #     'description': 'Highway traffic with clear plates'
        # }
    ]
    
    if not sample_videos:
        print("ℹ️  No sample video URLs configured")
        print("   Let me try a different approach...")
        return False
    
    success_count = 0
    for video in sample_videos:
        if download_video(video['url'], video['filename']):
            success_count += 1
            print(f"   Description: {video['description']}")
    
    print(f"\n✅ Downloaded {success_count}/{len(sample_videos)} videos")
    return success_count > 0

def create_better_video():
    """Create a better video by extracting frames from existing video and upscaling."""
    print("🔧 CREATING BETTER VIDEO FROM EXISTING")
    print("=" * 50)
    
    current_video = "videos/sample_traffic.mp4"
    if not os.path.exists(current_video):
        print(f"❌ Current video not found: {current_video}")
        return False
    
    try:
        import cv2
        
        # Open current video
        cap = cv2.VideoCapture(current_video)
        
        if not cap.isOpened():
            print("❌ Cannot open current video")
            return False
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📊 Current video: {width}x{height}, {fps:.1f} fps, {frame_count} frames")
        
        # Create output video with higher resolution
        output_path = "videos/quality/enhanced_traffic.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width*2, height*2))  # 2x upscale
        
        print("🎬 Processing frames...")
        frame_num = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Upscale frame using interpolation
            upscaled = cv2.resize(frame, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
            
            # Write frame
            out.write(upscaled)
            frame_num += 1
            
            if frame_num % 50 == 0:
                print(f"   Processed {frame_num}/{frame_count} frames")
        
        cap.release()
        out.release()
        
        print(f"✅ Created enhanced video: {output_path}")
        print(f"   Resolution: {width*2}x{height*2}")
        
        return True
        
    except ImportError:
        print("❌ OpenCV not available. Install with: pip install opencv-python")
        return False
    except Exception as e:
        print(f"❌ Error creating enhanced video: {e}")
        return False

def find_free_video_sources():
    """Find actual free video sources."""
    print("🔍 FINDING FREE VIDEO SOURCES")
    print("=" * 50)
    
    sources = [
        {
            'name': 'Pexels',
            'url': 'https://www.pexels.com/search/traffic/',
            'description': 'Free stock videos - search for "traffic"'
        },
        {
            'name': 'Pixabay',
            'url': 'https://pixabay.com/videos/search/traffic/',
            'description': 'Free videos - search for "traffic surveillance"'
        },
        {
            'name': 'Videvo',
            'url': 'https://www.videvo.net/stock-video-footage/traffic/',
            'description': 'Free stock videos with traffic footage'
        },
        {
            'name': 'Unsplash Videos',
            'url': 'https://unsplash.com/s/videos/traffic',
            'description': 'Free videos from Unsplash'
        }
    ]
    
    print("📋 MANUAL DOWNLOAD SOURCES:")
    for source in sources:
        print(f"\n🎯 {source['name']}")
        print(f"   URL: {source['url']}")
        print(f"   Description: {source['description']}")
    
    print("\n📋 INSTRUCTIONS:")
    print("1. Visit each website above")
    print("2. Search for 'traffic', 'surveillance', or 'highway'")
    print("3. Look for videos with clear license plates")
    print("4. Download the highest quality available")
    print("5. Save to videos/quality/")
    
    return sources

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download stock videos for ALPR")
    parser.add_argument('--action', choices=['download', 'enhance', 'sources'], 
                       default='sources', help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'download':
        download_sample_videos()
    elif args.action == 'enhance':
        create_better_video()
    elif args.action == 'sources':
        find_free_video_sources()

if __name__ == "__main__":
    main()
