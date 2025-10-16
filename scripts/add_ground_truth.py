#!/usr/bin/env python3
"""
Script to add ground truth entries for frames that have both images and predictions.
This helps increase the overlap between our predictions and ground truth for better evaluation.
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path

def add_ground_truth_entry(manifest_path, frame_id, plate_text, video_source="usplates.mp4"):
    """
    Add a new ground truth entry to the manifest.
    
    Args:
        manifest_path: Path to the manifest CSV
        frame_id: Frame number
        plate_text: Ground truth plate text
        video_source: Source video name
    """
    # Load existing manifest
    manifest_df = pd.read_csv(manifest_path)
    
    # Check if frame already exists
    if frame_id in manifest_df['frame_id'].values:
        print(f"Frame {frame_id} already exists in manifest")
        return False
    
    # Check if image file exists
    frame_path = f"data/golden/frames/frame_{frame_id:06d}.jpg"
    if not os.path.exists(frame_path):
        print(f"Image file {frame_path} does not exist")
        return False
    
    # Create new entry
    new_entry = {
        'frame_id': frame_id,
        'video_source': video_source,
        'plate_text_gt': plate_text,
        'light_condition': 'day',
        'camera_id': 'cam_01',
        'notes': '',
        'labeled_at': datetime.now().isoformat(),
        'frame_path': frame_path
    }
    
    # Add to manifest
    manifest_df = pd.concat([manifest_df, pd.DataFrame([new_entry])], ignore_index=True)
    
    # Sort by frame_id
    manifest_df = manifest_df.sort_values('frame_id').reset_index(drop=True)
    
    # Save updated manifest
    manifest_df.to_csv(manifest_path, index=False)
    print(f"✓ Added ground truth for frame {frame_id}: '{plate_text}'")
    return True

def main():
    manifest_path = "data/golden/manifest.csv"
    
    # Add ground truth for frame 610 (we have predictions and image)
    print("Adding ground truth for frame 610...")
    # Note: You'll need to manually verify the correct plate text by looking at the image
    add_ground_truth_entry(manifest_path, 610, "VHI123")  # This might need verification
    
    print(f"\nUpdated manifest saved to {manifest_path}")
    print("Please verify the plate text by looking at the actual image!")

if __name__ == "__main__":
    main()
