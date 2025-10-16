#!/usr/bin/env python3
"""
Script to help find and download good YouTube videos for ALPR.
"""

import subprocess
import json
from pathlib import Path

def search_youtube_videos():
    """Search for YouTube videos using yt-dlp."""
    search_terms = [
        "traffic surveillance 4K",
        "highway traffic camera HD", 
        "traffic intersection 1080p",
        "vehicle surveillance camera",
        "road traffic monitoring HD",
        "license plate recognition test",
        "traffic camera feed HD"
    ]
    
    print("🔍 SEARCHING YOUTUBE FOR ALPR VIDEOS")
    print("=" * 50)
    
    for term in search_terms:
        print(f"\n🎯 Searching: '{term}'")
        try:
            # Use yt-dlp to search (this is a simplified approach)
            cmd = ['yt-dlp', '--get-url', f'ytsearch10:{term}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                urls = result.stdout.strip().split('\n')
                print(f"   Found {len(urls)} videos")
                for i, url in enumerate(urls[:3], 1):  # Show first 3
                    print(f"   {i}. {url}")
            else:
                print(f"   ❌ Search failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Search timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def download_specific_videos():
    """Download specific videos that are known to be good for ALPR."""
    # These are example URLs - you'll need to find actual good ones
    good_videos = [
        # Add actual YouTube URLs here when you find them
        # {
        #     'url': 'https://www.youtube.com/watch?v=EXAMPLE1',
        #     'name': 'traffic_surveillance_1',
        #     'description': 'Highway traffic with clear plates'
        # }
    ]
    
    print("📥 DOWNLOADING SPECIFIC VIDEOS")
    print("=" * 50)
    
    if not good_videos:
        print("ℹ️  No specific video URLs configured")
        print("   Please find YouTube URLs manually and add them to the script")
        return
    
    for video in good_videos:
        print(f"\n🎬 {video['name']}")
        print(f"   Description: {video['description']}")
        
        try:
            cmd = [
                'yt-dlp',
                '-f', 'best[height>=1080]',
                '-o', f'videos/quality/{video["name"]}.%(ext)s',
                video['url']
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Downloaded successfully")
            else:
                print(f"   ❌ Download failed: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def create_video_finder():
    """Create a simple video finder interface."""
    print("🎯 YOUTUBE VIDEO FINDER FOR ALPR")
    print("=" * 50)
    
    print("\n📋 STEP-BY-STEP INSTRUCTIONS:")
    print("1. Open YouTube in your browser")
    print("2. Search for these terms one by one:")
    
    search_terms = [
        "traffic surveillance 4K high quality",
        "highway traffic camera HD license plates",
        "traffic intersection 1080p clear plates",
        "vehicle surveillance camera clear",
        "road traffic monitoring HD",
        "license plate recognition test video",
        "traffic camera feed HD clear"
    ]
    
    for i, term in enumerate(search_terms, 1):
        print(f"   {i}. '{term}'")
    
    print("\n3. Look for videos with these characteristics:")
    print("   ✅ Resolution: 1080p or 4K")
    print("   ✅ Duration: 5+ minutes")
    print("   ✅ Clear license plates visible")
    print("   ✅ Good lighting conditions")
    print("   ✅ Multiple vehicles")
    
    print("\n4. When you find a good video:")
    print("   a. Copy the YouTube URL")
    print("   b. Run this command:")
    print("      yt-dlp -f 'best[height>=1080]' -o 'videos/quality/%(title)s.%(ext)s' [URL]")
    
    print("\n5. Check video quality:")
    print("   python scripts/check_video_quality.py videos/quality/your_video.mp4")
    
    print("\n🎯 TARGET: Quality Score 6+/8")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Find YouTube videos for ALPR")
    parser.add_argument('--action', choices=['search', 'download', 'guide'], 
                       default='guide', help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'search':
        search_youtube_videos()
    elif args.action == 'download':
        download_specific_videos()
    elif args.action == 'guide':
        create_video_finder()

if __name__ == "__main__":
    main()
