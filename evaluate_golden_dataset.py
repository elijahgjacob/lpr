#!/usr/bin/env python3
"""
Evaluate ALPR model against golden dataset ground truth labels.
"""

import os
import sys
import json
import pandas as pd
import cv2
import numpy as np
from pathlib import Path

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpr_system import ALPRSystem

def load_ground_truth(csv_path):
    """Load ground truth labels from CSV file."""
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} ground truth entries")
    return df

def run_alpr_on_frames(frames_dir, ground_truth_df):
    """Run ALPR system on frames that have ground truth labels."""
    # Get unique frame IDs from ground truth
    frame_ids = sorted(ground_truth_df['frame_id'].unique())
    print(f"Running ALPR on {len(frame_ids)} frames: {frame_ids}")
    
    # Initialize ALPR system
    alpr = ALPRSystem()
    
    results = []
    
    for frame_id in frame_ids:
        frame_path = os.path.join(frames_dir, f"frame_{frame_id:06d}.jpg")
        
        if not os.path.exists(frame_path):
            print(f"Warning: Frame {frame_path} not found, skipping...")
            continue
            
        print(f"Processing frame {frame_id}...")
        
        # Load image
        image = cv2.imread(frame_path)
        if image is None:
            print(f"Error: Could not load image {frame_path}")
            continue
            
        # Run ALPR detection
        try:
            annotated_frame, detections = alpr.process_frame(image, frame_id, visualize=False)
            print(f"  Found {len(detections)} detections")
            
            # Store results for this frame
            for i, detection in enumerate(detections):
                result = {
                    'frame_id': frame_id,
                    'detection_id': i,
                    'plate_text': detection.get('plate_text', ''),
                    'confidence': detection.get('plate_confidence', 0.0),
                    'bbox': detection.get('vehicle_bbox', {}),
                    'plate_bbox': detection.get('plate_bbox', {})
                }
                results.append(result)
                
        except Exception as e:
            print(f"  Error processing frame {frame_id}: {e}")
            continue
    
    return results

def compare_with_ground_truth(alpr_results, ground_truth_df):
    """Compare ALPR results with ground truth labels."""
    print(f"\nComparing {len(alpr_results)} ALPR detections with {len(ground_truth_df)} ground truth labels...")
    
    # Create comparison results
    comparisons = []
    
    for _, gt_row in ground_truth_df.iterrows():
        frame_id = gt_row['frame_id']
        gt_plate_text = str(gt_row['plate_text_gt']).strip()
        
        # Find ALPR detections for this frame
        frame_detections = [r for r in alpr_results if r['frame_id'] == frame_id]
        
        # Find best match (simple text comparison for now)
        best_match = None
        best_score = 0
        
        for detection in frame_detections:
            detected_text = str(detection['plate_text']).strip()
            
            # Simple similarity score (exact match = 1.0, partial match = 0.5)
            if detected_text == gt_plate_text:
                score = 1.0
            elif detected_text and gt_plate_text and any(c in detected_text for c in gt_plate_text):
                score = 0.5
            else:
                score = 0.0
                
            if score > best_score:
                best_score = score
                best_match = detection
        
        comparison = {
            'frame_id': frame_id,
            'vehicle_number': gt_row['vehicle_number'],
            'ground_truth_text': gt_plate_text,
            'detected_text': best_match['plate_text'] if best_match else '',
            'detected_confidence': best_match['confidence'] if best_match else 0.0,
            'match_score': best_score,
            'is_correct': best_score >= 0.8,  # Consider 80%+ match as correct
            'gt_bbox': {
                'x': gt_row['vehicle_box_x'],
                'y': gt_row['vehicle_box_y'],
                'width': gt_row['vehicle_box_width'],
                'height': gt_row['vehicle_box_height']
            },
            'detected_bbox': best_match['bbox'] if best_match else {}
        }
        comparisons.append(comparison)
    
    return comparisons

def calculate_metrics(comparisons):
    """Calculate evaluation metrics."""
    total_labels = len(comparisons)
    correct_matches = sum(1 for c in comparisons if c['is_correct'])
    accuracy = correct_matches / total_labels if total_labels > 0 else 0.0
    
    # Calculate average confidence for correct matches
    correct_confidences = [c['detected_confidence'] for c in comparisons if c['is_correct']]
    avg_confidence = np.mean(correct_confidences) if correct_confidences else 0.0
    
    # Calculate text similarity distribution
    match_scores = [c['match_score'] for c in comparisons]
    exact_matches = sum(1 for score in match_scores if score >= 1.0)
    partial_matches = sum(1 for score in match_scores if 0.5 <= score < 1.0)
    no_matches = sum(1 for score in match_scores if score < 0.5)
    
    metrics = {
        'total_ground_truth_labels': total_labels,
        'correct_detections': correct_matches,
        'accuracy': accuracy,
        'average_confidence_correct': avg_confidence,
        'exact_matches': exact_matches,
        'partial_matches': partial_matches,
        'no_matches': no_matches,
        'exact_match_rate': exact_matches / total_labels if total_labels > 0 else 0.0,
        'partial_match_rate': partial_matches / total_labels if total_labels > 0 else 0.0,
        'no_match_rate': no_matches / total_labels if total_labels > 0 else 0.0
    }
    
    return metrics

def save_results(comparisons, metrics, output_dir):
    """Save evaluation results to files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save detailed comparisons
    comparisons_df = pd.DataFrame(comparisons)
    comparisons_path = os.path.join(output_dir, 'detailed_comparisons.csv')
    comparisons_df.to_csv(comparisons_path, index=False)
    print(f"Saved detailed comparisons to {comparisons_path}")
    
    # Save metrics
    metrics_path = os.path.join(output_dir, 'evaluation_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {metrics_path}")
    
    return comparisons_path, metrics_path

def print_summary(metrics):
    """Print evaluation summary."""
    print("\n" + "="*60)
    print("GOLDEN DATASET EVALUATION SUMMARY")
    print("="*60)
    print(f"Total Ground Truth Labels: {metrics['total_ground_truth_labels']}")
    print(f"Correct Detections: {metrics['correct_detections']}")
    print(f"Overall Accuracy: {metrics['accuracy']:.2%}")
    print(f"Average Confidence (Correct): {metrics['average_confidence_correct']:.2f}")
    print()
    print("Match Quality Distribution:")
    print(f"  Exact Matches: {metrics['exact_matches']} ({metrics['exact_match_rate']:.2%})")
    print(f"  Partial Matches: {metrics['partial_matches']} ({metrics['partial_match_rate']:.2%})")
    print(f"  No Matches: {metrics['no_matches']} ({metrics['no_match_rate']:.2%})")
    print("="*60)

def main():
    """Main evaluation function."""
    # File paths
    frames_dir = "data/golden/frames"
    ground_truth_csv = "labeling_interface/detailed_labels_export.csv"
    output_dir = "results/golden_evaluation"
    
    print("Starting Golden Dataset Evaluation...")
    print(f"Frames directory: {frames_dir}")
    print(f"Ground truth CSV: {ground_truth_csv}")
    print(f"Output directory: {output_dir}")
    
    # Check if files exist
    if not os.path.exists(ground_truth_csv):
        print(f"Error: Ground truth file {ground_truth_csv} not found!")
        return
    
    if not os.path.exists(frames_dir):
        print(f"Error: Frames directory {frames_dir} not found!")
        return
    
    # Load ground truth
    print("\n1. Loading ground truth labels...")
    ground_truth_df = load_ground_truth(ground_truth_csv)
    
    # Run ALPR on frames
    print("\n2. Running ALPR on frames...")
    alpr_results = run_alpr_on_frames(frames_dir, ground_truth_df)
    
    # Compare results
    print("\n3. Comparing with ground truth...")
    comparisons = compare_with_ground_truth(alpr_results, ground_truth_df)
    
    # Calculate metrics
    print("\n4. Calculating metrics...")
    metrics = calculate_metrics(comparisons)
    
    # Save results
    print("\n5. Saving results...")
    comparisons_path, metrics_path = save_results(comparisons, metrics, output_dir)
    
    # Print summary
    print_summary(metrics)
    
    print(f"\nEvaluation complete! Results saved to {output_dir}")

if __name__ == "__main__":
    main()
