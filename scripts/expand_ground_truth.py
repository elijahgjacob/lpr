#!/usr/bin/env python3
"""
Script to expand ground truth dataset by adding many more frames.
This helps create a comprehensive evaluation dataset.
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import argparse

def get_unlabeled_frames(manifest_path="data/golden/manifest.csv"):
    """Get frames that have images but no ground truth."""
    # Load existing manifest
    gt = pd.read_csv(manifest_path)
    gt_frames = set(gt['frame_id'].unique())
    
    # Find all frame files
    all_frame_files = set()
    for i in range(3000):  # Check up to frame 3000
        frame_file = f'data/golden/frames/frame_{i:06d}.jpg'
        if os.path.exists(frame_file):
            all_frame_files.add(i)
    
    unlabeled_frames = sorted(all_frame_files - gt_frames)
    return unlabeled_frames

def add_ground_truth_batch(manifest_path, frame_data_list, video_source="usplates.mp4"):
    """
    Add multiple ground truth entries at once.
    
    Args:
        manifest_path: Path to manifest CSV
        frame_data_list: List of (frame_id, plate_text, notes) tuples
        video_source: Source video name
    """
    # Load existing manifest
    manifest_df = pd.read_csv(manifest_path)
    
    new_entries = []
    for frame_id, plate_text, notes in frame_data_list:
        # Check if frame already exists
        if frame_id in manifest_df['frame_id'].values:
            print(f"⚠️  Frame {frame_id} already exists, skipping")
            continue
        
        # Check if image file exists
        frame_path = f"data/golden/frames/frame_{frame_id:06d}.jpg"
        if not os.path.exists(frame_path):
            print(f"⚠️  Image file {frame_path} does not exist, skipping")
            continue
        
        # Create new entry
        new_entry = {
            'frame_id': frame_id,
            'video_source': video_source,
            'plate_text_gt': plate_text,
            'light_condition': 'day',
            'camera_id': 'cam_01',
            'notes': notes,
            'labeled_at': datetime.now().isoformat(),
            'frame_path': frame_path
        }
        new_entries.append(new_entry)
        print(f"✓ Added frame {frame_id}: '{plate_text}'")
    
    if new_entries:
        # Add all new entries
        new_df = pd.DataFrame(new_entries)
        manifest_df = pd.concat([manifest_df, new_df], ignore_index=True)
        
        # Sort by frame_id
        manifest_df = manifest_df.sort_values('frame_id').reset_index(drop=True)
        
        # Save updated manifest
        manifest_df.to_csv(manifest_path, index=False)
        print(f"\n✓ Added {len(new_entries)} new ground truth entries")
        print(f"Total ground truth frames: {len(manifest_df)}")
    else:
        print("No new entries added")

def add_from_predictions(manifest_path, predictions_csv, min_confidence=0.85):
    """
    Add ground truth entries based on high-confidence predictions.
    
    Args:
        manifest_path: Path to manifest CSV
        predictions_csv: Path to predictions CSV
        min_confidence: Minimum confidence threshold
    """
    # Load predictions
    pred_df = pd.read_csv(predictions_csv)
    
    # Get high-confidence predictions
    high_conf = pred_df[pred_df['Confidence'] >= min_confidence]
    
    # Group by frame and get best prediction per frame
    frame_best = high_conf.loc[high_conf.groupby('Frame')['Confidence'].idxmax()]
    
    # Prepare data for batch addition
    frame_data = []
    for _, row in frame_best.iterrows():
        frame_id = row['Frame']
        plate_text = row['Plate_Text']
        confidence = row['Confidence']
        notes = f"Added from high-confidence prediction ({confidence:.3f})"
        frame_data.append((frame_id, plate_text, notes))
    
    print(f"Found {len(frame_data)} high-confidence predictions (>{min_confidence})")
    add_ground_truth_batch(manifest_path, frame_data)

def create_labeling_template(unlabeled_frames, output_path="ground_truth_template.csv"):
    """
    Create a CSV template for manual labeling.
    
    Args:
        unlabeled_frames: List of frame IDs to label
        output_path: Path to save template
    """
    template_data = []
    for frame_id in unlabeled_frames:
        template_data.append({
            'frame_id': frame_id,
            'plate_text_gt': '',  # To be filled manually
            'notes': ''  # Optional notes
        })
    
    template_df = pd.DataFrame(template_data)
    template_df.to_csv(output_path, index=False)
    print(f"✓ Created labeling template with {len(template_data)} frames: {output_path}")
    print("Fill in the plate_text_gt column and use add_from_template() to import")

def add_from_template(manifest_path, template_path):
    """
    Add ground truth from a filled template.
    
    Args:
        manifest_path: Path to manifest CSV
        template_path: Path to filled template CSV
    """
    template_df = pd.read_csv(template_path)
    
    # Filter out empty entries
    filled_template = template_df[template_df['plate_text_gt'].str.strip() != '']
    
    frame_data = []
    for _, row in filled_template.iterrows():
        frame_id = row['frame_id']
        plate_text = row['plate_text_gt'].strip()
        notes = row.get('notes', 'Added from template')
        frame_data.append((frame_id, plate_text, notes))
    
    print(f"Found {len(frame_data)} filled entries in template")
    add_ground_truth_batch(manifest_path, frame_data)

def main():
    parser = argparse.ArgumentParser(description="Expand ground truth dataset")
    parser.add_argument('--action', choices=['analyze', 'from-predictions', 'create-template', 'from-template'], 
                       default='analyze', help='Action to perform')
    parser.add_argument('--manifest', default='data/golden/manifest.csv', help='Path to manifest CSV')
    parser.add_argument('--predictions', default='results/usplates_final.csv', help='Path to predictions CSV')
    parser.add_argument('--template', default='ground_truth_template.csv', help='Path to template CSV')
    parser.add_argument('--min-confidence', type=float, default=0.85, help='Minimum confidence for auto-labeling')
    parser.add_argument('--max-frames', type=int, default=100, help='Maximum frames to include in template')
    
    args = parser.parse_args()
    
    if args.action == 'analyze':
        unlabeled = get_unlabeled_frames(args.manifest)
        print(f"Found {len(unlabeled)} frames with images but no ground truth")
        print(f"First 20: {unlabeled[:20]}")
        print(f"Last 20: {unlabeled[-20:]}")
        
        # Show current stats
        gt = pd.read_csv(args.manifest)
        print(f"\nCurrent ground truth: {len(gt)} frames")
        
    elif args.action == 'from-predictions':
        add_from_predictions(args.manifest, args.predictions, args.min_confidence)
        
    elif args.action == 'create-template':
        unlabeled = get_unlabeled_frames(args.manifest)
        # Take first N frames for template
        template_frames = unlabeled[:args.max_frames]
        create_labeling_template(template_frames, args.template)
        
    elif args.action == 'from-template':
        add_from_template(args.manifest, args.template)

if __name__ == "__main__":
    main()
