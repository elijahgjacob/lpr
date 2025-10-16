#!/usr/bin/env python3
"""
ALPR System using Roboflow Workflows with InferencePipeline.

This module provides an alternative ALPR implementation using Roboflow's
workflow API for combined detection and classification.
"""

import csv
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import cv2
import numpy as np

from inference import InferencePipeline

# Version info
try:
    from __init__ import __version__
except ImportError:
    __version__ = "1.1.0"

import config
from sort import Sort


class ALPRWorkflow:
    """
    ALPR system using Roboflow Workflows.
    
    This implementation uses Roboflow's InferencePipeline with a custom workflow
    that combines detection and OCR in a single API call.
    """
    
    def __init__(
        self,
        api_key: str,
        workspace_name: str,
        workflow_id: str,
    ):
        """
        Initialize ALPR Workflow system.
        
        Args:
            api_key: Roboflow API key
            workspace_name: Roboflow workspace name
            workflow_id: Workflow ID from Roboflow
        """
        print("=" * 60)
        print("Initializing ALPR Workflow System...")
        print("=" * 60)
        
        self.api_key = api_key
        self.workspace_name = workspace_name
        self.workflow_id = workflow_id
        
        # Initialize SORT tracker
        print("Initializing SORT tracker...")
        self.tracker = Sort(
            max_age=config.SORT_MAX_AGE,
            min_hits=config.SORT_MIN_HITS,
            iou_threshold=config.SORT_IOU_THRESHOLD
        )
        
        # Cache for vehicle plates
        self.vehicle_plates: Dict[int, Dict[str, Any]] = {}
        
        # Statistics
        self.stats = {
            "total_frames": 0,
            "vehicles_detected": 0,
            "plates_detected": 0,
            "plates_read": 0,
        }
        
        # Storage for results
        self.all_results: List[Dict[str, Any]] = []
        self.current_frame_number = 0
        
        print("✓ ALPR Workflow System initialized successfully!")
        print("=" * 60)
    
    def prediction_sink(self, result: Dict, video_frame: np.ndarray):
        """
        Callback function for processing workflow predictions.
        
        This is called by InferencePipeline for each frame.
        
        Args:
            result: Workflow prediction result
            video_frame: Current video frame
        """
        self.stats["total_frames"] += 1
        frame_results = []
        
        # Extract predictions from workflow result
        # The structure depends on your workflow configuration
        predictions = result.get("predictions", {})
        
        # Process vehicle detections if available
        vehicle_detections = predictions.get("vehicle_detection", [])
        
        if not vehicle_detections:
            # Try alternative keys
            vehicle_detections = predictions.get("detections", [])
        
        # Convert to numpy array for SORT
        detections_array = []
        for det in vehicle_detections:
            # Extract bounding box and confidence
            if "x" in det and "y" in det:
                # Center format (x, y, width, height)
                x, y = det["x"], det["y"]
                w, h = det["width"], det["height"]
                x1 = x - w / 2
                y1 = y - h / 2
                x2 = x + w / 2
                y2 = y + h / 2
            else:
                # Corner format
                x1, y1 = det.get("x1", 0), det.get("y1", 0)
                x2, y2 = det.get("x2", 0), det.get("y2", 0)
            
            confidence = det.get("confidence", 0.0)
            detections_array.append([x1, y1, x2, y2, confidence])
        
        # Update tracker
        if detections_array:
            detections_np = np.array(detections_array)
            tracked_vehicles = self.tracker.update(detections_np)
        else:
            tracked_vehicles = np.empty((0, 5))
        
        # Process tracked vehicles
        for vehicle in tracked_vehicles:
            vehicle_id = int(vehicle[4])
            vehicle_bbox = tuple(vehicle[:4])
            
            self.stats["vehicles_detected"] += 1
            
            # Check if we already have a plate for this vehicle
            if vehicle_id not in self.vehicle_plates:
                # Look for plate in workflow results
                plate_text = None
                plate_confidence = 0.0
                plate_bbox = vehicle_bbox  # Default to vehicle bbox
                
                # Extract OCR results from workflow
                ocr_results = predictions.get("ocr", [])
                if not ocr_results:
                    ocr_results = predictions.get("plate_text", [])
                
                # Find plate associated with this detection
                if ocr_results:
                    # Take first OCR result (workflow should associate correctly)
                    for ocr in ocr_results:
                        text = ocr.get("text", "").strip().upper()
                        conf = ocr.get("confidence", 0.0)
                        
                        if text and conf >= config.OCR_CONFIDENCE_THRESHOLD:
                            plate_text = text
                            plate_confidence = conf
                            
                            # Get plate bbox if available
                            if "x" in ocr:
                                px, py = ocr["x"], ocr["y"]
                                pw, ph = ocr["width"], ocr["height"]
                                plate_bbox = (
                                    px - pw/2,
                                    py - ph/2,
                                    px + pw/2,
                                    py + ph/2
                                )
                            break
                
                if plate_text:
                    self.stats["plates_detected"] += 1
                    self.stats["plates_read"] += 1
                    
                    # Cache the result
                    self.vehicle_plates[vehicle_id] = {
                        "text": plate_text,
                        "confidence": plate_confidence,
                        "bbox": plate_bbox,
                        "first_seen": self.current_frame_number,
                    }
            
            # Add to results
            cached_plate = self.vehicle_plates.get(vehicle_id)
            if cached_plate:
                frame_results.append({
                    "frame_number": self.current_frame_number,
                    "vehicle_id": vehicle_id,
                    "vehicle_bbox": vehicle_bbox,
                    "plate_text": cached_plate["text"],
                    "plate_bbox": cached_plate["bbox"],
                    "confidence": cached_plate["confidence"],
                    "timestamp": datetime.now().isoformat(),
                    "version": __version__,
                })
        
        self.all_results.extend(frame_results)
        self.current_frame_number += 1
    
    def process_video(
        self,
        video_path: str,
        output_csv: str,
        max_fps: int = 30,
        visualize: bool = False
    ):
        """
        Process video using Roboflow workflow.
        
        Args:
            video_path: Path to input video
            output_csv: Path to output CSV
            max_fps: Maximum FPS for processing
            visualize: Whether to show video during processing
        """
        print(f"\nProcessing video: {video_path}")
        print("-" * 60)
        
        # Reset state
        self.all_results = []
        self.current_frame_number = 0
        self.vehicle_plates.clear()
        self.tracker = Sort(
            max_age=config.SORT_MAX_AGE,
            min_hits=config.SORT_MIN_HITS,
            iou_threshold=config.SORT_IOU_THRESHOLD
        )
        
        # Get video info
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        print(f"Total frames: {total_frames}")
        print(f"Video FPS: {fps:.2f}")
        print(f"Processing max FPS: {max_fps}")
        print("-" * 60)
        
        # Initialize pipeline
        start_time = time.time()
        
        pipeline = InferencePipeline.init_with_workflow(
            api_key=self.api_key,
            workspace_name=self.workspace_name,
            workflow_id=self.workflow_id,
            video_reference=video_path,
            max_fps=max_fps,
            on_prediction=self.prediction_sink
        )
        
        # Start processing
        print("\nProcessing...")
        pipeline.start()
        pipeline.join()
        
        elapsed_time = time.time() - start_time
        processing_fps = self.stats["total_frames"] / elapsed_time if elapsed_time > 0 else 0
        
        # Save results to CSV
        self._save_to_csv(output_csv)
        
        print("\n" + "=" * 60)
        print("Processing Complete!")
        print("=" * 60)
        print(f"Frames Processed: {self.stats['total_frames']}/{total_frames}")
        print(f"Processing Time: {elapsed_time:.2f}s")
        print(f"Processing FPS: {processing_fps:.2f}")
        print(f"Detections: {len(self.all_results)}")
        print(f"\nStatistics:")
        print(f"  Vehicles Detected: {self.stats['vehicles_detected']}")
        print(f"  Unique Vehicles: {len(self.vehicle_plates)}")
        print(f"  Plates Detected: {self.stats['plates_detected']}")
        print(f"  Plates Read: {self.stats['plates_read']}")
        print("=" * 60)
    
    def _save_to_csv(self, output_path: str):
        """Save results to CSV file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Frame',
                'Vehicle_ID',
                'Plate_Text',
                'Confidence',
                'Vehicle_X1',
                'Vehicle_Y1',
                'Vehicle_X2',
                'Vehicle_Y2',
                'Plate_X1',
                'Plate_Y1',
                'Plate_X2',
                'Plate_Y2',
                'Timestamp',
                'Version'
            ])
            
            for result in self.all_results:
                writer.writerow([
                    result['frame_number'],
                    result['vehicle_id'],
                    result['plate_text'],
                    f"{result['confidence']:.4f}",
                    *result['vehicle_bbox'],
                    *result['plate_bbox'],
                    result['timestamp'],
                    result['version']
                ])
        
        print(f"\n✓ Results saved to: {output_path}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return {
            **self.stats,
            "unique_vehicles": len(self.vehicle_plates),
            "total_detections": len(self.all_results),
        }


def main():
    """CLI interface for workflow-based ALPR."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ALPR System using Roboflow Workflows"
    )
    parser.add_argument('--video', type=str, required=True, help='Input video path')
    parser.add_argument('--output', type=str, default='results/workflow_predictions.csv',
                       help='Output CSV path')
    parser.add_argument('--api-key', type=str, help='Roboflow API key')
    parser.add_argument('--workspace', type=str, help='Roboflow workspace name')
    parser.add_argument('--workflow-id', type=str, help='Roboflow workflow ID')
    parser.add_argument('--max-fps', type=int, default=30, help='Maximum FPS')
    parser.add_argument('--visualize', action='store_true', help='Show video during processing')
    
    args = parser.parse_args()
    
    # Get credentials from args or config
    api_key = args.api_key or config.ROBOFLOW_API_KEY
    workspace = args.workspace or "alpr-jjlrf"
    workflow_id = args.workflow_id or "detect-and-classify-2"
    
    if not api_key:
        print("Error: Roboflow API key required")
        return 1
    
    # Initialize and run
    alpr = ALPRWorkflow(
        api_key=api_key,
        workspace_name=workspace,
        workflow_id=workflow_id
    )
    
    alpr.process_video(
        video_path=args.video,
        output_csv=args.output,
        max_fps=args.max_fps,
        visualize=args.visualize
    )
    
    return 0


if __name__ == "__main__":
    exit(main())


