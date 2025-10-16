#!/usr/bin/env python3
"""
Script to create a golden dataset for vehicle and license plate labeling.
This extracts frames from videos and creates a template for manual annotation.
"""

import cv2
import pandas as pd
import os
import json
from pathlib import Path
from datetime import datetime
import argparse

def get_video_info(video_path):
    """Get basic information about the video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    
    info = {
        'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
    }
    cap.release()
    return info

def extract_frames_for_labeling(video_path, output_dir, frame_interval=50, max_frames=200):
    """
    Extract frames from video at regular intervals for labeling.
    
    Args:
        video_path: Path to input video
        output_dir: Directory to save extracted frames
        frame_interval: Extract every Nth frame
        max_frames: Maximum number of frames to extract
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video info
    info = get_video_info(video_path)
    if not info:
        print(f"Error: Could not open video {video_path}")
        return []
    
    print(f"Video: {video_path}")
    print(f"Resolution: {info['width']}x{info['height']}")
    print(f"Total frames: {info['total_frames']}")
    print(f"FPS: {info['fps']:.2f}")
    print(f"Duration: {info['duration']:.2f} seconds")
    print(f"Extracting every {frame_interval} frames (max {max_frames} frames)...")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    extracted_frames = []
    frame_id = 0
    extracted_count = 0
    
    while extracted_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Extract frame at intervals
        if frame_id % frame_interval == 0:
            # Save frame
            frame_filename = f"frame_{frame_id:06d}.jpg"
            frame_path = os.path.join(output_dir, frame_filename)
            cv2.imwrite(frame_path, frame)
            extracted_frames.append(frame_id)
            extracted_count += 1
            print(f"Extracted frame {frame_id} ({extracted_count}/{max_frames})")
        
        frame_id += 1
    
    cap.release()
    print(f"✓ Extracted {len(extracted_frames)} frames")
    return extracted_frames, info

def create_labeling_template(extracted_frames, video_info, video_source, output_path):
    """
    Create a comprehensive CSV template for manual labeling.
    Each frame gets multiple rows - one for each vehicle/plate combination.
    
    Args:
        extracted_frames: List of frame IDs that were extracted
        video_info: Video information dictionary
        video_source: Name of the source video
        output_path: Path to save the template CSV
    """
    template_data = []
    for frame_id in extracted_frames:
        # Create 5 rows per frame to allow for multiple vehicles/plates
        for vehicle_num in range(1, 6):  # Up to 5 vehicles per frame
            template_data.append({
                'frame_id': frame_id,
                'vehicle_number': vehicle_num,  # 1, 2, 3, 4, 5 for vehicles in this frame
                'video_source': video_source,
                'frame_path': f"data/golden/frames/frame_{frame_id:06d}.jpg",
                'has_vehicle': '',  # Y/N - Is this vehicle row used?
                'vehicle_type': '',  # car/truck/motorcycle/bus/van
                'plate_text_gt': '',  # License plate text (if visible)
                'plate_confidence': '',  # 1-5 scale for plate visibility
                'plate_state': '',  # US state code if visible
                'plate_type': '',  # standard/vanity/commercial/temporary
                'light_condition': 'day',  # day/night/dawn/dusk
                'weather': 'clear',  # clear/rainy/cloudy/snowy
                'vehicle_notes': '',  # Notes specific to this vehicle
                'frame_notes': '',  # Notes about the overall frame (only fill for vehicle_number=1)
                'labeled_at': '',  # Will be filled when imported
                'labeled_by': ''  # Who labeled this frame
            })
    
    template_df = pd.DataFrame(template_data)
    template_df.to_csv(output_path, index=False)
    
    # Create metadata file
    metadata = {
        'video_source': video_source,
        'video_info': video_info,
        'extraction_date': datetime.now().isoformat(),
        'total_frames_extracted': len(extracted_frames),
        'frame_interval_used': '50',  # This should match the actual interval used
        'template_columns': list(template_df.columns),
        'instructions': {
            'vehicle_number': '1-5, indicating which vehicle in the frame this row represents',
            'has_vehicle': 'Y if this vehicle row is used (vehicle visible), N if unused',
            'vehicle_type': 'car/truck/motorcycle/bus/van for the specific vehicle',
            'plate_text_gt': 'License plate text exactly as it appears (e.g., ABC1234)',
            'plate_confidence': '1=very blurry/unclear, 5=crystal clear for this plate',
            'plate_state': 'US state abbreviation if visible (e.g., CA, NY, TX)',
            'plate_type': 'standard/vanity/commercial/temporary for this plate',
            'light_condition': 'day/night/dawn/dusk (fill for vehicle_number=1 only)',
            'weather': 'clear/rainy/cloudy/snowy (fill for vehicle_number=1 only)',
            'vehicle_notes': 'Notes specific to this individual vehicle',
            'frame_notes': 'Notes about the overall frame (fill for vehicle_number=1 only)',
            'usage': 'Each frame has 5 rows. Use only the rows needed for vehicles in that frame.'
        }
    }
    
    metadata_path = output_path.replace('.csv', '_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Created labeling template: {output_path}")
    print(f"✓ Created metadata file: {metadata_path}")
    print(f"Template contains {len(extracted_frames)} frames with {len(template_data)} total rows (5 rows per frame)")
    print("\nLabeling Instructions:")
    print("- Each frame has 5 rows (vehicle_number 1-5)")
    print("- Fill in 'has_vehicle' with Y for vehicles present, N for unused rows")
    print("- Fill in 'plate_text_gt' exactly as it appears for each vehicle")
    print("- Use 1-5 scale for 'plate_confidence' (1=blurry, 5=clear)")
    print("- Fill 'light_condition' and 'weather' only for vehicle_number=1 per frame")
    print("- Fill 'frame_notes' only for vehicle_number=1 per frame")
    print("- Leave unused vehicle rows empty or mark 'has_vehicle' as N")

def add_to_golden_manifest(manifest_path, template_path):
    """
    Add filled template entries to the golden dataset manifest.
    Handles multiple vehicles per frame.
    
    Args:
        manifest_path: Path to the golden dataset manifest
        template_path: Path to the filled template CSV
    """
    # Load existing manifest
    if os.path.exists(manifest_path):
        manifest_df = pd.read_csv(manifest_path)
    else:
        # Create new manifest if it doesn't exist
        manifest_df = pd.DataFrame(columns=[
            'frame_id', 'video_source', 'plate_text_gt', 'light_condition', 
            'camera_id', 'notes', 'labeled_at', 'frame_path'
        ])
    
    # Load template
    template_df = pd.read_csv(template_path)
    
    # Filter out entries without vehicles or with empty plate text
    vehicle_frames = template_df[
        (template_df['has_vehicle'].str.upper() == 'Y') & 
        (template_df['plate_text_gt'].str.strip() != '')
    ]
    
    new_entries = []
    for _, row in vehicle_frames.iterrows():
        frame_id = row['frame_id']
        vehicle_num = row['vehicle_number']
        plate_text = row['plate_text_gt'].strip()
        
        # Create unique identifier for this vehicle in this frame
        vehicle_id = f"{frame_id}_{vehicle_num}"
        
        # Check if this specific vehicle already exists (using a combination of frame_id and vehicle details)
        existing = manifest_df[
            (manifest_df['frame_id'] == frame_id) & 
            (manifest_df['plate_text_gt'] == plate_text)
        ]
        if not existing.empty:
            print(f"⚠️  Vehicle {vehicle_id} already exists in manifest, skipping")
            continue
        
        # Create comprehensive notes
        notes_parts = []
        notes_parts.append(f"Vehicle #{vehicle_num}")
        if row.get('plate_confidence'):
            notes_parts.append(f"Confidence: {row['plate_confidence']}/5")
        if row.get('vehicle_type'):
            notes_parts.append(f"Type: {row['vehicle_type']}")
        if row.get('plate_state'):
            notes_parts.append(f"State: {row['plate_state']}")
        if row.get('plate_type'):
            notes_parts.append(f"Plate type: {row['plate_type']}")
        if row.get('vehicle_notes'):
            notes_parts.append(f"Vehicle notes: {row['vehicle_notes']}")
        if row.get('frame_notes') and vehicle_num == 1:  # Only add frame notes once per frame
            notes_parts.append(f"Frame notes: {row['frame_notes']}")
        if row.get('weather') and vehicle_num == 1:
            notes_parts.append(f"Weather: {row['weather']}")
        
        notes = "; ".join(notes_parts) if notes_parts else ""
        
        # Create new entry
        new_entry = {
            'frame_id': frame_id,
            'video_source': row['video_source'],
            'plate_text_gt': plate_text,
            'light_condition': row.get('light_condition', 'day'),
            'camera_id': 'cam_01',
            'notes': notes,
            'labeled_at': datetime.now().isoformat(),
            'frame_path': row['frame_path']
        }
        new_entries.append(new_entry)
        print(f"✓ Added vehicle {vehicle_id}: '{plate_text}'")
    
    if new_entries:
        # Add all new entries
        new_df = pd.DataFrame(new_entries)
        manifest_df = pd.concat([manifest_df, new_df], ignore_index=True)
        
        # Sort by frame_id
        manifest_df = manifest_df.sort_values('frame_id').reset_index(drop=True)
        
        # Save updated manifest
        manifest_df.to_csv(manifest_path, index=False)
        print(f"\n✓ Added {len(new_entries)} new ground truth entries")
        print(f"Total ground truth entries: {len(manifest_df)}")
    else:
        print("No new entries added")

def main():
    parser = argparse.ArgumentParser(description="Create golden dataset for vehicle and license plate labeling")
    parser.add_argument('--action', choices=['extract', 'create-template', 'add-to-manifest'], 
                       default='extract', help='Action to perform')
    parser.add_argument('--video', default='videos/main_video.mp4', help='Path to video file')
    parser.add_argument('--output-dir', default='data/golden/frames', help='Directory for extracted frames')
    parser.add_argument('--template', default='golden_dataset_template.csv', help='Template CSV path')
    parser.add_argument('--manifest', default='data/golden/manifest.csv', help='Manifest CSV path')
    parser.add_argument('--interval', type=int, default=50, help='Frame extraction interval')
    parser.add_argument('--max-frames', type=int, default=200, help='Maximum frames to extract')
    
    args = parser.parse_args()
    
    if args.action == 'extract':
        # Extract frames from video
        extracted_frames, video_info = extract_frames_for_labeling(
            args.video, 
            args.output_dir, 
            args.interval,
            args.max_frames
        )
        
        if extracted_frames:
            # Create template
            create_labeling_template(
                extracted_frames,
                video_info,
                'main_video.mp4',
                args.template
            )
            
            print(f"\nNext steps:")
            print(f"1. Open {args.template} in a spreadsheet editor")
            print(f"2. Fill in the template with vehicle and license plate information")
            print(f"3. Run: python {__file__} --action add-to-manifest --template {args.template}")
    
    elif args.action == 'create-template':
        # Just create template (if frames already extracted)
        frame_files = [f for f in os.listdir(args.output_dir) if f.startswith('frame_') and f.endswith('.jpg')]
        extracted_frames = [int(f.split('_')[1].split('.')[0]) for f in frame_files]
        extracted_frames.sort()
        
        # Get video info for template
        video_info = get_video_info(args.video)
        
        create_labeling_template(
            extracted_frames,
            video_info,
            'main_video.mp4',
            args.template
        )
    
    elif args.action == 'add-to-manifest':
        # Add filled template to manifest
        add_to_golden_manifest(args.manifest, args.template)

if __name__ == "__main__":
    main()
