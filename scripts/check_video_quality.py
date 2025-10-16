#!/usr/bin/env python3
"""
Simple video quality checker for ALPR videos.
"""

import os
import cv2
import sys

def check_video_quality(video_path):
    """Check video quality using OpenCV."""
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return False
    
    # Get file size
    file_size = os.path.getsize(video_path)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"📁 File: {video_path}")
    print(f"📏 Size: {file_size_mb:.1f} MB")
    
    # Open video with OpenCV
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ Cannot open video file")
        return False
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    
    print(f"📺 Resolution: {width}x{height}")
    print(f"🎬 Frame Rate: {fps:.1f} fps")
    print(f"⏱️  Duration: {duration:.1f} seconds ({frame_count} frames)")
    
    # Quality assessment
    quality_score = 0
    quality_notes = []
    
    # Resolution check
    if width >= 1920 and height >= 1080:
        quality_score += 3
        quality_notes.append("✅ High resolution (1080p+)")
    elif width >= 1280 and height >= 720:
        quality_score += 2
        quality_notes.append("⚠️  Medium resolution (720p)")
    else:
        quality_notes.append("❌ Low resolution")
    
    # Frame rate check
    if fps >= 30:
        quality_score += 2
        quality_notes.append("✅ Good frame rate (30+ fps)")
    elif fps >= 15:
        quality_score += 1
        quality_notes.append("⚠️  Moderate frame rate (15-30 fps)")
    else:
        quality_notes.append("❌ Low frame rate")
    
    # Duration check
    if duration >= 300:  # 5 minutes
        quality_score += 2
        quality_notes.append("✅ Good duration (5+ minutes)")
    elif duration >= 60:  # 1 minute
        quality_score += 1
        quality_notes.append("⚠️  Short duration (1-5 minutes)")
    else:
        quality_notes.append("❌ Very short duration")
    
    # File size check (rough indicator of quality)
    if file_size_mb >= 50:
        quality_score += 1
        quality_notes.append("✅ Large file size (good quality)")
    elif file_size_mb >= 10:
        quality_notes.append("⚠️  Medium file size")
    else:
        quality_notes.append("❌ Small file size (may be low quality)")
    
    print(f"\n🎯 Quality Score: {quality_score}/8")
    
    print("\n📋 Quality Assessment:")
    for note in quality_notes:
        print(f"   {note}")
    
    # Overall recommendation
    if quality_score >= 6:
        print("\n🌟 RECOMMENDATION: Excellent for ALPR evaluation!")
    elif quality_score >= 4:
        print("\n👍 RECOMMENDATION: Good for ALPR evaluation")
    elif quality_score >= 2:
        print("\n⚠️  RECOMMENDATION: Acceptable, but consider finding better video")
    else:
        print("\n❌ RECOMMENDATION: Poor quality, find a better video")
    
    cap.release()
    return quality_score >= 4

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_video_quality.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    check_video_quality(video_path)

if __name__ == "__main__":
    main()
