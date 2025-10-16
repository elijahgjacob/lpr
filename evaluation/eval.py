#!/usr/bin/env python3
"""
Simple evaluation module for ALPR system.

Computes basic accuracy metrics:
- Accuracy: % of correct predictions
- Simple comparison between predictions and ground truth
"""

import argparse
import pandas as pd
from typing import Dict, Optional
from pathlib import Path
import json


def simple_accuracy(predictions_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> float:
    """
    Compute simple accuracy: % of correct predictions.
    
    Args:
        predictions_df: DataFrame with predictions
        ground_truth_df: DataFrame with ground truth
        
    Returns:
        float: Accuracy (0.0 to 1.0, higher is better)
    """
    # Merge predictions with ground truth
    merged = ground_truth_df.merge(
        predictions_df,
        left_on='frame_id',
        right_on='Frame',
        how='left'
    )
    
    # Count correct detections (exact match)
    merged['correct'] = merged.apply(
        lambda row: str(row.get('Plate_Text', '')).strip().upper() == 
                   str(row['plate_text_gt']).strip().upper(),
        axis=1
    )
    
    total_frames = len(ground_truth_df)
    correct_frames = merged['correct'].sum()
    
    return correct_frames / total_frames if total_frames > 0 else 0.0


def evaluate_predictions(
    predictions_csv: str,
    ground_truth_csv: str,
    output_json: Optional[str] = None
) -> Dict:
    """
    Simple evaluation of predictions against ground truth.
    
    Args:
        predictions_csv: Path to predictions CSV (from ALPR system)
        ground_truth_csv: Path to golden dataset CSV
        output_json: Optional path to save results JSON
        
    Returns:
        dict: Simple evaluation results
    """
    # Load data
    print(f"Loading predictions from {predictions_csv}")
    predictions_df = pd.read_csv(predictions_csv)
    
    print(f"Loading ground truth from {ground_truth_csv}")
    ground_truth_df = pd.read_csv(ground_truth_csv)
    
    print(f"\nDataset info:")
    print(f"  Predictions: {len(predictions_df)} rows")
    print(f"  Ground truth: {len(ground_truth_df)} frames")
    
    # Compute simple accuracy
    print("\nComputing accuracy...")
    accuracy = simple_accuracy(predictions_df, ground_truth_df)
    
    # Compile results
    results = {
        'accuracy': float(accuracy),
        'total_gt_frames': len(ground_truth_df),
        'total_predictions': len(predictions_df),
    }
    
    # Print summary
    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    print(f"\nAccuracy: {accuracy:.2%}")
    print(f"Total ground truth frames: {len(ground_truth_df)}")
    print(f"Total predictions: {len(predictions_df)}")
    print("="*50)
    
    # Save to JSON if requested
    if output_json:
        output_path = Path(output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to {output_json}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate ALPR predictions against golden dataset"
    )
    parser.add_argument(
        '--predictions',
        type=str,
        required=True,
        help='Path to predictions CSV (from ALPR system)'
    )
    parser.add_argument(
        '--ground-truth',
        type=str,
        required=True,
        help='Path to golden dataset CSV'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='results/metrics/evaluation_results.json',
        help='Path to save results JSON'
    )
    
    args = parser.parse_args()
    
    evaluate_predictions(
        predictions_csv=args.predictions,
        ground_truth_csv=args.ground_truth,
        output_json=args.output
    )


if __name__ == "__main__":
    main()


