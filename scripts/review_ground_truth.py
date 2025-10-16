#!/usr/bin/env python3
"""
Script to help review and correct ground truth entries.
"""

import pandas as pd
import os
from pathlib import Path

def review_ground_truth(manifest_path="data/golden/manifest.csv"):
    """Review current ground truth entries."""
    gt = pd.read_csv(manifest_path)
    
    print(f"Current ground truth: {len(gt)} frames")
    print(f"Frame range: {gt['frame_id'].min()} to {gt['frame_id'].max()}")
    print(f"Unique plates: {gt['plate_text_gt'].nunique()}")
    
    print("\n=== GROUND TRUTH SUMMARY ===")
    print("Frame | Plate Text | Notes")
    print("-" * 50)
    
    for _, row in gt.iterrows():
        frame_id = row['frame_id']
        plate_text = row['plate_text_gt']
        notes = row['notes']
        
        # Check if image exists
        frame_file = f'data/golden/frames/frame_{frame_id:06d}.jpg'
        image_exists = os.path.exists(frame_file)
        
        print(f"{frame_id:5d} | {plate_text:10s} | {notes} {'[IMG ✓]' if image_exists else '[NO IMG]'}")
    
    return gt

def create_correction_template(manifest_path="data/golden/manifest.csv", output_path="ground_truth_corrections.csv"):
    """Create a template for correcting ground truth."""
    gt = pd.read_csv(manifest_path)
    
    # Create correction template
    corrections = gt[['frame_id', 'plate_text_gt', 'notes']].copy()
    corrections['corrected_plate_text'] = ''  # To be filled
    corrections['needs_correction'] = False    # Checkbox
    corrections['new_notes'] = ''             # Optional new notes
    
    corrections.to_csv(output_path, index=False)
    print(f"✓ Created correction template: {output_path}")
    print("Fill in the 'corrected_plate_text' column and set 'needs_correction' to True for entries to fix")

def apply_corrections(manifest_path="data/golden/manifest.csv", corrections_path="ground_truth_corrections.csv"):
    """Apply corrections from template."""
    gt = pd.read_csv(manifest_path)
    corrections = pd.read_csv(corrections_path)
    
    # Apply corrections
    corrected_count = 0
    for _, row in corrections.iterrows():
        if row['needs_correction'] and pd.notna(row['corrected_plate_text']):
            frame_id = row['frame_id']
            new_plate_text = row['corrected_plate_text'].strip()
            
            # Update in manifest
            mask = gt['frame_id'] == frame_id
            if mask.any():
                gt.loc[mask, 'plate_text_gt'] = new_plate_text
                if pd.notna(row['new_notes']):
                    gt.loc[mask, 'notes'] = row['new_notes']
                corrected_count += 1
                print(f"✓ Corrected frame {frame_id}: '{new_plate_text}'")
    
    if corrected_count > 0:
        gt.to_csv(manifest_path, index=False)
        print(f"\n✓ Applied {corrected_count} corrections")
    else:
        print("No corrections to apply")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Review and correct ground truth")
    parser.add_argument('--action', choices=['review', 'create-template', 'apply-corrections'], 
                       default='review', help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'review':
        review_ground_truth()
    elif args.action == 'create-template':
        create_correction_template()
    elif args.action == 'apply-corrections':
        apply_corrections()

if __name__ == "__main__":
    main()
