#!/usr/bin/env python3
"""
Interactive tool to create golden dataset for ALPR evaluation.

Usage:
    python scripts/create_golden_set.py --video videos/sample_traffic.mp4 --output data/golden/manifest.csv
    
    # Quick extraction only (label later)
    python scripts/create_golden_set.py --video videos/sample_traffic.mp4 --extract-only
    
    # Review existing labels
    python scripts/create_golden_set.py --review data/golden/manifest.csv
"""

import argparse
import cv2
import csv
import os
import sys
from pathlib import Path
from datetime import datetime


def extract_frames_with_plates(video_path, output_dir, interval=30, max_frames=100):
    """
    Extract frames at regular intervals for manual review.
    
    Args:
        video_path: Path to video file
        output_dir: Directory to save extracted frames
        interval: Extract every Nth frame (default: 30 = ~1 frame/second at 30fps)
        max_frames: Maximum number of frames to extract
    
    Returns:
        List of (frame_number, frame_path) tuples
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        sys.exit(1)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    frame_number = 0
    extracted_frames = []
    
    print(f"Extracting frames from {video_path}...")
    print(f"Total frames: {total_frames}, FPS: {fps:.2f}")
    print(f"Interval: every {interval} frames (~{interval/fps:.1f} seconds)")
    print(f"Max frames to extract: {max_frames}")
    print("-" * 70)
    
    while cap.isOpened() and len(extracted_frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Extract every Nth frame
        if frame_number % interval == 0:
            frame_path = output_dir / f"frame_{frame_number:06d}.jpg"
            cv2.imwrite(str(frame_path), frame)
            extracted_frames.append((frame_number, str(frame_path)))
            print(f"✓ Extracted frame {frame_number} ({len(extracted_frames)}/{max_frames})")
        
        frame_number += 1
    
    cap.release()
    print("-" * 70)
    print(f"\n✓ Extracted {len(extracted_frames)} frames to {output_dir}")
    return extracted_frames


def interactive_labeling(frames, video_path, output_csv):
    """
    Interactive CLI for labeling frames.
    
    Args:
        frames: List of (frame_number, frame_path) tuples
        video_path: Original video path
        output_csv: Output CSV path
    
    Returns:
        List of label dictionaries
    """
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    labels = []
    video_name = Path(video_path).name
    
    print("\n" + "="*70)
    print("Interactive Labeling Tool")
    print("="*70)
    print("\nInstructions:")
    print("- Enter the license plate text you see (or 'skip' if none visible)")
    print("- Enter 'quit' to stop and save progress")
    print("- Enter 'back' to go back to previous frame")
    print("- Light condition: day/night/dusk")
    print("="*70 + "\n")
    
    idx = 0
    while idx < len(frames):
        frame_number, frame_path = frames[idx]
        
        print(f"\n[{idx+1}/{len(frames)}] Frame {frame_number}")
        print(f"Image: {frame_path}")
        
        # Display the frame
        img = cv2.imread(frame_path)
        if img is not None:
            # Resize for display if too large
            height, width = img.shape[:2]
            if width > 1200:
                scale = 1200 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height))
            
            cv2.imshow('Frame - Press any key in terminal to label', img)
            cv2.waitKey(100)  # Show briefly, then proceed to input
        
        # Get labels
        plate_text = input("  Plate text (or 'skip'/'quit'/'back'): ").strip().upper()
        
        if plate_text.lower() == 'quit':
            print("\nSaving progress and quitting...")
            break
        
        if plate_text.lower() == 'back':
            if idx > 0:
                idx -= 1
                # Remove last label if we're going back
                if labels and labels[-1]['frame_id'] == frames[idx][0]:
                    labels.pop()
                print("Going back to previous frame...")
                continue
            else:
                print("Already at first frame")
                continue
        
        if plate_text.lower() == 'skip' or not plate_text:
            idx += 1
            continue
        
        light_condition = input("  Light condition (day/night/dusk) [day]: ").strip().lower()
        if not light_condition:
            light_condition = "day"
        
        camera_id = input("  Camera ID [cam_01]: ").strip()
        if not camera_id:
            camera_id = "cam_01"
        
        notes = input("  Notes (optional): ").strip()
        
        labels.append({
            'frame_id': frame_number,
            'video_source': video_name,
            'plate_text_gt': plate_text,
            'light_condition': light_condition,
            'camera_id': camera_id,
            'notes': notes,
            'labeled_at': datetime.now().isoformat(),
            'frame_path': frame_path
        })
        
        print(f"  ✓ Labeled: {plate_text} ({light_condition})")
        idx += 1
    
    cv2.destroyAllWindows()
    
    # Save to CSV
    if labels:
        with open(output_csv, 'w', newline='') as f:
            fieldnames = ['frame_id', 'video_source', 'plate_text_gt', 
                         'light_condition', 'camera_id', 'notes',
                         'labeled_at', 'frame_path']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(labels)
        
        print(f"\n✓ Saved {len(labels)} labels to {output_csv}")
    else:
        print("\n⚠ No labels saved")
    
    return labels


def review_manifest(csv_path):
    """
    Load and review existing CSV.
    
    Args:
        csv_path: Path to manifest CSV
    """
    if not Path(csv_path).exists():
        print(f"Error: {csv_path} not found")
        sys.exit(1)
    
    print(f"\nReviewing {csv_path}...")
    print("-" * 70)
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Total frames labeled: {len(rows)}")
    
    # Statistics
    light_conditions = {}
    cameras = {}
    
    for row in rows:
        condition = row.get('light_condition', 'unknown')
        camera = row.get('camera_id', 'unknown')
        light_conditions[condition] = light_conditions.get(condition, 0) + 1
        cameras[camera] = cameras.get(camera, 0) + 1
    
    print("\nLight condition distribution:")
    for condition, count in sorted(light_conditions.items()):
        print(f"  {condition}: {count}")
    
    print("\nCamera distribution:")
    for camera, count in sorted(cameras.items()):
        print(f"  {camera}: {count}")
    
    print("\nSample entries:")
    print("-" * 70)
    for i, row in enumerate(rows[:10]):
        print(f"{i+1}. Frame {row['frame_id']}: {row['plate_text_gt']} ({row['light_condition']})")
    
    if len(rows) > 10:
        print(f"... and {len(rows) - 10} more")
    
    print("-" * 70)
    return rows


def create_template_csv(output_path):
    """
    Create an empty template CSV for manual editing.
    
    Args:
        output_path: Path to output CSV
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='') as f:
        fieldnames = ['frame_id', 'video_source', 'plate_text_gt', 
                     'light_condition', 'camera_id', 'notes',
                     'labeled_at', 'frame_path']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Add a sample row
        writer.writerow({
            'frame_id': '150',
            'video_source': 'sample_traffic.mp4',
            'plate_text_gt': 'ABC1234',
            'light_condition': 'day',
            'camera_id': 'cam_01',
            'notes': 'Clear view, centered',
            'labeled_at': datetime.now().isoformat(),
            'frame_path': 'data/golden/frames/frame_000150.jpg'
        })
    
    print(f"✓ Created template CSV at {output_path}")
    print("Edit this file manually to add your labels")


def main():
    parser = argparse.ArgumentParser(
        description="Create golden dataset for ALPR evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full interactive workflow
  python scripts/create_golden_set.py --video videos/sample_traffic.mp4

  # Extract frames only (label later)
  python scripts/create_golden_set.py --video videos/sample_traffic.mp4 --extract-only

  # Review existing manifest
  python scripts/create_golden_set.py --review data/golden/manifest.csv

  # Create empty template
  python scripts/create_golden_set.py --template data/golden/manifest.csv
        """
    )
    parser.add_argument(
        '--video',
        type=str,
        help='Path to video file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/golden/manifest.csv',
        help='Output CSV path (default: data/golden/manifest.csv)'
    )
    parser.add_argument(
        '--frames-dir',
        type=str,
        default='data/golden/frames',
        help='Directory to save extracted frames (default: data/golden/frames)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Extract every Nth frame (default: 30)'
    )
    parser.add_argument(
        '--max-frames',
        type=int,
        default=100,
        help='Maximum frames to extract (default: 100)'
    )
    parser.add_argument(
        '--extract-only',
        action='store_true',
        help='Only extract frames, skip interactive labeling'
    )
    parser.add_argument(
        '--review',
        type=str,
        metavar='CSV_PATH',
        help='Review existing CSV instead of creating new'
    )
    parser.add_argument(
        '--template',
        type=str,
        metavar='CSV_PATH',
        help='Create empty template CSV'
    )
    
    args = parser.parse_args()
    
    # Review mode
    if args.review:
        review_manifest(args.review)
        return
    
    # Template mode
    if args.template:
        create_template_csv(args.template)
        return
    
    # Require video for extraction
    if not args.video:
        parser.error("--video is required (unless using --review or --template)")
    
    # Extract frames
    frames = extract_frames_with_plates(
        args.video,
        args.frames_dir,
        args.interval,
        args.max_frames
    )
    
    if not frames:
        print("Error: No frames extracted")
        sys.exit(1)
    
    # Extract-only mode
    if args.extract_only:
        print("\n" + "="*70)
        print("Frames Extracted!")
        print("="*70)
        print(f"Frames saved to: {args.frames_dir}")
        print("\nNext steps:")
        print(f"1. Review frames in {args.frames_dir}")
        print(f"2. Run again without --extract-only to label")
        print(f"3. Or manually edit {args.output}")
        print("="*70)
        return
    
    # Interactive labeling
    labels = interactive_labeling(frames, args.video, args.output)
    
    print("\n" + "="*70)
    print("Golden Dataset Creation Complete!")
    print("="*70)
    print(f"Total frames labeled: {len(labels)}")
    print(f"Output file: {args.output}")
    print(f"Frames saved to: {args.frames_dir}")
    print("\nNext steps:")
    print("1. Review the CSV file for accuracy")
    print("2. Add more labels if needed (run script again)")
    print("3. Run evaluation:")
    print(f"   python evaluation/eval.py --ground-truth {args.output}")
    print("="*70)


if __name__ == "__main__":
    main()


