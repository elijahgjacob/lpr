#!/usr/bin/env python3
"""
Model Comparison Script for ALPR System

Compare different license plate detection models against the golden dataset
and generate side-by-side comparison reports.
"""

import os
import sys
import json
import argparse
import time
import pandas as pd
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpr_system import ALPRSystem
from model_configs import create_detector_config


def load_model_registry(registry_path: str = "model_registry.json") -> Dict[str, Any]:
    """
    Load model registry from JSON file.
    
    Args:
        registry_path: Path to the model registry JSON file
        
    Returns:
        Dictionary containing model configurations
        
    Raises:
        FileNotFoundError: If registry file doesn't exist
        json.JSONDecodeError: If registry file is malformed
    """
    if not os.path.exists(registry_path):
        raise FileNotFoundError(f"Model registry not found: {registry_path}")
    
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    print(f"Loaded model registry with {len(registry['models'])} models")
    return registry


def load_ground_truth(csv_path: str) -> pd.DataFrame:
    """
    Load ground truth labels from CSV file.
    
    Args:
        csv_path: Path to the ground truth CSV file
        
    Returns:
        DataFrame with ground truth labels
    """
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} ground truth entries")
    return df


def run_model_evaluation(
    model_config: Dict[str, Any],
    frames_dir: str,
    ground_truth_df: pd.DataFrame,
    model_id: str
) -> Dict[str, Any]:
    """
    Run evaluation for a single model configuration.
    
    Args:
        model_config: Model configuration dictionary
        frames_dir: Directory containing frame images
        ground_truth_df: Ground truth DataFrame
        model_id: Model identifier
        
    Returns:
        Dictionary containing evaluation results and metrics
    """
    print(f"\n{'='*60}")
    print(f"Evaluating Model: {model_config['name']} ({model_id})")
    print(f"{'='*60}")
    
    try:
        # Create detector configuration
        # Add model_name to config for factory function
        config_with_name = model_config['config'].copy()
        config_with_name['model_name'] = model_config['name']
        detector_config = create_detector_config(config_with_name, model_config['type'])
        print(f"Created detector config: {detector_config}")
        
        # Initialize ALPR system with the detector config
        alpr = ALPRSystem(plate_detector_config=detector_config)
        
        # Get unique frame IDs from ground truth
        frame_ids = sorted(ground_truth_df['frame_id'].unique())
        print(f"Processing {len(frame_ids)} frames...")
        
        results = []
        total_inference_time = 0
        successful_detections = 0
        
        for i, frame_id in enumerate(frame_ids):
            frame_path = os.path.join(frames_dir, f"frame_{frame_id:06d}.jpg")
            
            if not os.path.exists(frame_path):
                print(f"Warning: Frame {frame_path} not found, skipping...")
                continue
            
            print(f"  Frame {frame_id} ({i+1}/{len(frame_ids)})...")
            
            # Load image
            image = cv2.imread(frame_path)
            if image is None:
                print(f"Error: Could not load image {frame_path}")
                continue
            
            # Get ground truth for this frame
            frame_gt = ground_truth_df[ground_truth_df['frame_id'] == frame_id]
            
            # Run ALPR on the frame
            start_time = time.time()
            predictions = alpr.process_frame(image)
            inference_time = time.time() - start_time
            total_inference_time += inference_time
            
            # Compare predictions with ground truth
            frame_results = compare_predictions_with_ground_truth(
                predictions, frame_gt, frame_id, inference_time
            )
            
            results.extend(frame_results)
            successful_detections += len([r for r in frame_results if r['status'] != 'error'])
            
            print(f"    Found {len(predictions)} predictions, {len(frame_results)} comparisons")
        
        # Calculate overall metrics
        if results:
            metrics = calculate_model_metrics(results, total_inference_time, len(frame_ids))
        else:
            metrics = {
                'total_frames': len(frame_ids),
                'successful_detections': 0,
                'exact_match_rate': 0.0,
                'partial_match_rate': 0.0,
                'no_match_rate': 1.0,
                'detection_rate': 0.0,
                'avg_confidence': 0.0,
                'avg_inference_time_ms': 0.0,
                'total_inference_time': total_inference_time
            }
        
        print(f"\nResults for {model_config['name']}:")
        print(f"  Exact Match Rate: {metrics['exact_match_rate']:.1%}")
        print(f"  Partial Match Rate: {metrics['partial_match_rate']:.1%}")
        print(f"  Detection Rate: {metrics['detection_rate']:.1%}")
        print(f"  Avg Inference Time: {metrics['avg_inference_time_ms']:.1f}ms")
        
        return {
            'model_id': model_id,
            'model_name': model_config['name'],
            'model_type': model_config['type'],
            'config': model_config['config'],
            'results': results,
            'metrics': metrics,
            'success': True,
            'error': None
        }
        
    except Exception as e:
        print(f"Error evaluating model {model_id}: {e}")
        return {
            'model_id': model_id,
            'model_name': model_config.get('name', 'Unknown'),
            'model_type': model_config.get('type', 'unknown'),
            'config': model_config.get('config', {}),
            'results': [],
            'metrics': {},
            'success': False,
            'error': str(e)
        }


def compare_predictions_with_ground_truth(
    predictions: List[Dict[str, Any]],
    ground_truth: pd.DataFrame,
    frame_id: int,
    inference_time: float
) -> List[Dict[str, Any]]:
    """
    Compare ALPR predictions with ground truth labels.
    
    Args:
        predictions: List of ALPR predictions
        ground_truth: DataFrame with ground truth for this frame
        frame_id: Frame identifier
        inference_time: Time taken for inference
        
    Returns:
        List of comparison results
    """
    comparisons = []
    
    for _, gt_row in ground_truth.iterrows():
        gt_plate = str(gt_row['plate_text_gt']).strip().upper()
        if gt_plate == 'nan' or gt_plate == '':
            continue
        
        # Find best matching prediction
        best_match = None
        best_score = 0
        
        for pred in predictions:
            pred_plate = str(pred.get('plate_text', '')).strip().upper()
            if not pred_plate:
                continue
            
            # Calculate similarity score
            score = calculate_plate_similarity(gt_plate, pred_plate)
            if score > best_score:
                best_score = score
                best_match = pred
        
        # Determine match status
        if best_match is None:
            status = 'no_match'
            confidence = 0.0
        elif best_score >= 0.9:  # 90% similarity threshold for exact match
            status = 'exact_match'
            confidence = best_match.get('confidence', 0.0)
        elif best_score >= 0.5:  # 50% similarity threshold for partial match
            status = 'partial_match'
            confidence = best_match.get('confidence', 0.0)
        else:
            status = 'no_match'
            confidence = best_match.get('confidence', 0.0) if best_match else 0.0
        
        comparisons.append({
            'frame_id': frame_id,
            'vehicle_number': gt_row['vehicle_number'],
            'ground_truth_plate': gt_plate,
            'predicted_plate': best_match.get('plate_text', '') if best_match else '',
            'confidence': confidence,
            'similarity_score': best_score,
            'status': status,
            'inference_time': inference_time
        })
    
    return comparisons


def calculate_plate_similarity(gt_plate: str, pred_plate: str) -> float:
    """
    Calculate similarity score between ground truth and predicted plate text.
    
    Args:
        gt_plate: Ground truth plate text
        pred_plate: Predicted plate text
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not gt_plate or not pred_plate:
        return 0.0
    
    # Simple character-level similarity
    # This could be enhanced with more sophisticated string matching
    matches = sum(1 for a, b in zip(gt_plate, pred_plate) if a == b)
    max_len = max(len(gt_plate), len(pred_plate))
    
    if max_len == 0:
        return 0.0
    
    return matches / max_len


def calculate_model_metrics(results: List[Dict[str, Any]], total_inference_time: float, total_frames: int) -> Dict[str, Any]:
    """
    Calculate overall metrics for a model.
    
    Args:
        results: List of comparison results
        total_inference_time: Total time spent on inference
        total_frames: Total number of frames processed
        
    Returns:
        Dictionary containing calculated metrics
    """
    if not results:
        return {
            'total_frames': total_frames,
            'successful_detections': 0,
            'exact_match_rate': 0.0,
            'partial_match_rate': 0.0,
            'no_match_rate': 1.0,
            'detection_rate': 0.0,
            'avg_confidence': 0.0,
            'avg_inference_time_ms': 0.0,
            'total_inference_time': total_inference_time
        }
    
    total_comparisons = len(results)
    exact_matches = sum(1 for r in results if r['status'] == 'exact_match')
    partial_matches = sum(1 for r in results if r['status'] == 'partial_match')
    no_matches = sum(1 for r in results if r['status'] == 'no_match')
    
    # Calculate rates
    exact_match_rate = exact_matches / total_comparisons
    partial_match_rate = partial_matches / total_comparisons
    no_match_rate = no_matches / total_comparisons
    detection_rate = (exact_matches + partial_matches) / total_comparisons
    
    # Calculate average confidence (only for successful detections)
    confidences = [r['confidence'] for r in results if r['confidence'] > 0]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    
    # Calculate average inference time
    avg_inference_time_ms = (total_inference_time / total_frames) * 1000 if total_frames > 0 else 0.0
    
    return {
        'total_frames': total_frames,
        'total_comparisons': total_comparisons,
        'successful_detections': exact_matches + partial_matches,
        'exact_match_rate': exact_match_rate,
        'partial_match_rate': partial_match_rate,
        'no_match_rate': no_match_rate,
        'detection_rate': detection_rate,
        'avg_confidence': avg_confidence,
        'avg_inference_time_ms': avg_inference_time_ms,
        'total_inference_time': total_inference_time
    }


def generate_comparison_report(
    evaluation_results: List[Dict[str, Any]],
    output_dir: str = "results/model_comparison"
) -> str:
    """
    Generate markdown comparison report.
    
    Args:
        evaluation_results: List of model evaluation results
        output_dir: Output directory for the report
        
    Returns:
        Path to the generated report file
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter successful evaluations
    successful_results = [r for r in evaluation_results if r['success']]
    
    if not successful_results:
        print("No successful evaluations to report")
        return None
    
    # Generate report content
    report_content = generate_report_content(successful_results)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(output_dir, f"comparison_report_{timestamp}.md")
    
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    print(f"Comparison report saved to: {report_path}")
    return report_path


def generate_report_content(results: List[Dict[str, Any]]) -> str:
    """
    Generate markdown report content.
    
    Args:
        results: List of successful evaluation results
        
    Returns:
        Markdown report content as string
    """
    content = []
    
    # Header
    content.append("# ALPR Model Comparison Report")
    content.append("")
    content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")
    content.append("## Summary Table")
    content.append("")
    
    # Summary table
    content.append("| Model | Type | Exact Match | Partial Match | No Match | Detection Rate | Avg Confidence | Avg Time (ms) |")
    content.append("|-------|------|-------------|---------------|----------|----------------|----------------|---------------|")
    
    for result in results:
        metrics = result['metrics']
        content.append(
            f"| {result['model_name']} | {result['model_type']} | "
            f"{metrics['exact_match_rate']:.1%} | {metrics['partial_match_rate']:.1%} | "
            f"{metrics['no_match_rate']:.1%} | {metrics['detection_rate']:.1%} | "
            f"{metrics['avg_confidence']:.2f} | {metrics['avg_inference_time_ms']:.1f} |"
        )
    
    content.append("")
    
    # Best models section
    content.append("## Best Models by Metric")
    content.append("")
    
    # Find best models for each metric
    best_exact = max(results, key=lambda r: r['metrics']['exact_match_rate'])
    best_detection = max(results, key=lambda r: r['metrics']['detection_rate'])
    best_speed = min(results, key=lambda r: r['metrics']['avg_inference_time_ms'])
    best_confidence = max(results, key=lambda r: r['metrics']['avg_confidence'])
    
    content.append(f"- **Exact Match Rate**: {best_exact['model_name']} ({best_exact['metrics']['exact_match_rate']:.1%})")
    content.append(f"- **Detection Rate**: {best_detection['model_name']} ({best_detection['metrics']['detection_rate']:.1%})")
    content.append(f"- **Speed**: {best_speed['model_name']} ({best_speed['metrics']['avg_inference_time_ms']:.1f}ms)")
    content.append(f"- **Confidence**: {best_confidence['model_name']} ({best_confidence['metrics']['avg_confidence']:.2f})")
    content.append("")
    
    # Detailed results
    content.append("## Detailed Results")
    content.append("")
    
    for result in results:
        content.append(f"### {result['model_name']}")
        content.append("")
        content.append(f"- **Model ID**: {result['model_id']}")
        content.append(f"- **Type**: {result['model_type']}")
        content.append(f"- **Configuration**: {json.dumps(result['config'], indent=2)}")
        content.append("")
        
        metrics = result['metrics']
        content.append("**Metrics:**")
        content.append(f"- Total Frames: {metrics['total_frames']}")
        content.append(f"- Total Comparisons: {metrics['total_comparisons']}")
        content.append(f"- Successful Detections: {metrics['successful_detections']}")
        content.append(f"- Exact Match Rate: {metrics['exact_match_rate']:.1%}")
        content.append(f"- Partial Match Rate: {metrics['partial_match_rate']:.1%}")
        content.append(f"- No Match Rate: {metrics['no_match_rate']:.1%}")
        content.append(f"- Detection Rate: {metrics['detection_rate']:.1%}")
        content.append(f"- Average Confidence: {metrics['avg_confidence']:.3f}")
        content.append(f"- Average Inference Time: {metrics['avg_inference_time_ms']:.1f}ms")
        content.append(f"- Total Inference Time: {metrics['total_inference_time']:.2f}s")
        content.append("")
    
    return "\n".join(content)


def main():
    """Main function for model comparison."""
    parser = argparse.ArgumentParser(description="Compare ALPR models against golden dataset")
    parser.add_argument("--registry", default="model_registry.json", help="Path to model registry file")
    parser.add_argument("--models", nargs="+", help="Specific model IDs to compare")
    parser.add_argument("--all", action="store_true", help="Compare all models in registry")
    parser.add_argument("--ground-truth", default="labeling_interface/detailed_labels_export.csv", help="Path to ground truth CSV")
    parser.add_argument("--frames-dir", default="data/golden/frames", help="Directory containing frame images")
    parser.add_argument("--output-dir", default="results/model_comparison", help="Output directory for reports")
    
    args = parser.parse_args()
    
    # Load model registry
    try:
        registry = load_model_registry(args.registry)
    except Exception as e:
        print(f"Error loading model registry: {e}")
        return 1
    
    # Determine which models to compare
    if args.all:
        model_ids = [model['id'] for model in registry['models']]
    elif args.models:
        model_ids = args.models
    else:
        print("Please specify --all or --models")
        return 1
    
    # Filter models
    models_to_compare = [model for model in registry['models'] if model['id'] in model_ids]
    
    if not models_to_compare:
        print(f"No models found matching IDs: {model_ids}")
        return 1
    
    print(f"Will compare {len(models_to_compare)} models: {[m['name'] for m in models_to_compare]}")
    
    # Load ground truth
    try:
        ground_truth = load_ground_truth(args.ground_truth)
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return 1
    
    # Run evaluations
    evaluation_results = []
    
    for model in models_to_compare:
        result = run_model_evaluation(
            model, args.frames_dir, ground_truth, model['id']
        )
        evaluation_results.append(result)
    
    # Generate report
    try:
        report_path = generate_comparison_report(evaluation_results, args.output_dir)
        if report_path:
            print(f"\nComparison complete! Report saved to: {report_path}")
        else:
            print("\nComparison complete, but no report generated.")
    except Exception as e:
        print(f"Error generating report: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
