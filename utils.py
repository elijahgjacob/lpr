"""Utility functions for ALPR system.

This module provides helper functions for OCR text processing, image manipulation,
visualization, reporting, and Roboflow API integration.
"""

import re
import cv2
import numpy as np
from typing import Tuple, List, Dict, Optional, Any
import config


# ============================================================================
# OCR Utilities
# ============================================================================

def format_license_plate(text: str) -> str:
    """Format license plate text by removing spaces and special characters.
    
    Args:
        text: Raw OCR text
        
    Returns:
        str: Formatted license plate text (uppercase, alphanumeric only)
        
    Examples:
        >>> format_license_plate("ABC 123")
        'ABC123'
        >>> format_license_plate("xyz-456!")
        'XYZ456'
    """
    if not text:
        return ""
    
    # Remove spaces and special characters, keep only alphanumeric
    formatted = re.sub(r'[^A-Za-z0-9]', '', text)
    # Convert to uppercase
    formatted = formatted.upper()
    return formatted


def validate_license_plate(text: str) -> bool:
    """Validate license plate text.
    
    Args:
        text: License plate text to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Validation rules:
        - Length between MIN_PLATE_LENGTH and MAX_PLATE_LENGTH
        - Contains only alphanumeric characters
        - Contains at least one letter and one number
    """
    if not text:
        return False
    
    # Check length
    if len(text) < config.MIN_PLATE_LENGTH or len(text) > config.MAX_PLATE_LENGTH:
        return False
    
    # Check if alphanumeric only
    if not text.isalnum():
        return False
    
    # Must contain at least one letter and one digit
    has_letter = any(c.isalpha() for c in text)
    has_digit = any(c.isdigit() for c in text)
    
    return has_letter and has_digit


# ============================================================================
# Image Processing Utilities
# ============================================================================

def crop_license_plate(
    frame: np.ndarray,
    bbox: Tuple[float, float, float, float],
    padding: float = 0.1
) -> np.ndarray:
    """Extract license plate region from frame with padding.
    
    Args:
        frame: Input image
        bbox: Bounding box as (x1, y1, x2, y2)
        padding: Padding percentage (0.1 = 10%)
        
    Returns:
        np.ndarray: Cropped image region
    """
    x1, y1, x2, y2 = bbox
    height, width = frame.shape[:2]
    
    # Calculate padding
    box_width = x2 - x1
    box_height = y2 - y1
    pad_x = int(box_width * padding)
    pad_y = int(box_height * padding)
    
    # Apply padding with boundary checking
    x1_pad = max(0, int(x1 - pad_x))
    y1_pad = max(0, int(y1 - pad_y))
    x2_pad = min(width, int(x2 + pad_x))
    y2_pad = min(height, int(y2 + pad_y))
    
    return frame[y1_pad:y2_pad, x1_pad:x2_pad]


def calculate_bbox_area(bbox: Tuple[float, float, float, float]) -> float:
    """Calculate bounding box area.
    
    Args:
        bbox: Bounding box as (x1, y1, x2, y2)
        
    Returns:
        float: Area of bounding box
    """
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1
    return width * height


def preprocess_plate_image(image: np.ndarray) -> np.ndarray:
    """Preprocess license plate image for better OCR results.
    
    Args:
        image: License plate image
        
    Returns:
        np.ndarray: Preprocessed image
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply adaptive thresholding
    processed = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Denoise
    processed = cv2.fastNlMeansDenoising(processed, None, 10, 7, 21)
    
    return processed


# ============================================================================
# Visualization Utilities
# ============================================================================

def draw_bbox(
    frame: np.ndarray,
    bbox: Tuple[int, int, int, int],
    label: str,
    color: Tuple[int, int, int],
    thickness: int = 2
) -> np.ndarray:
    """Draw bounding box and label on frame.
    
    Args:
        frame: Input frame
        bbox: Bounding box as (x1, y1, x2, y2)
        label: Text label to display
        color: BGR color tuple
        thickness: Line thickness
        
    Returns:
        np.ndarray: Frame with drawn bbox
    """
    x1, y1, x2, y2 = map(int, bbox)
    
    # Draw rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    
    # Draw label background
    label_size, _ = cv2.getTextSize(
        label, cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SCALE, config.FONT_THICKNESS
    )
    label_width, label_height = label_size
    
    # Position label above bbox
    label_y = y1 - 10 if y1 - 10 > label_height else y1 + label_height + 10
    
    # Draw black background for text
    cv2.rectangle(
        frame,
        (x1, label_y - label_height - 5),
        (x1 + label_width + 5, label_y + 5),
        (0, 0, 0),
        -1
    )
    
    # Draw text
    cv2.putText(
        frame, label,
        (x1 + 2, label_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        config.FONT_SCALE,
        (255, 255, 255),
        config.FONT_THICKNESS
    )
    
    return frame


def write_annotations(
    frame: np.ndarray,
    vehicle_id: int,
    plate_text: Optional[str],
    vehicle_bbox: Tuple[int, int, int, int],
    plate_bbox: Optional[Tuple[int, int, int, int]] = None
) -> np.ndarray:
    """Write annotations for vehicle and plate on frame.
    
    Args:
        frame: Input frame
        vehicle_id: Vehicle tracking ID
        plate_text: Detected plate text (None if not detected)
        vehicle_bbox: Vehicle bounding box
        plate_bbox: Plate bounding box (None if not detected)
        
    Returns:
        np.ndarray: Annotated frame
    """
    # Draw vehicle box
    vehicle_color = get_color_for_id(vehicle_id)
    vehicle_label = f"Vehicle {vehicle_id}"
    frame = draw_bbox(frame, vehicle_bbox, vehicle_label, vehicle_color)
    
    # Draw plate box if detected
    if plate_bbox is not None:
        plate_label = f"Plate: {plate_text}" if plate_text else "Plate"
        frame = draw_bbox(frame, plate_bbox, plate_label, config.PLATE_BOX_COLOR)
    
    return frame


def get_color_for_id(track_id: int) -> Tuple[int, int, int]:
    """Get color for vehicle ID by cycling through palette.
    
    Args:
        track_id: Vehicle tracking ID
        
    Returns:
        Tuple[int, int, int]: BGR color tuple
    """
    color_index = track_id % len(config.COLOR_PALETTE)
    return config.COLOR_PALETTE[color_index]


def add_frame_info(
    frame: np.ndarray,
    frame_number: int,
    fps: float,
    detections_count: int
) -> np.ndarray:
    """Add frame information overlay to video.
    
    Args:
        frame: Input frame
        frame_number: Current frame number
        fps: Processing FPS
        detections_count: Number of detections in current frame
        
    Returns:
        np.ndarray: Frame with info overlay
    """
    info_text = [
        f"Frame: {frame_number}",
        f"FPS: {fps:.1f}",
        f"Detections: {detections_count}",
    ]
    
    y_offset = 30
    for i, text in enumerate(info_text):
        y_pos = y_offset + i * 30
        # Draw background
        text_size, _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
        )
        cv2.rectangle(
            frame,
            (10, y_pos - 25),
            (20 + text_size[0], y_pos + 5),
            (0, 0, 0),
            -1
        )
        # Draw text
        cv2.putText(
            frame, text,
            (15, y_pos),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
    
    return frame


# ============================================================================
# Reporting Utilities
# ============================================================================

def generate_summary_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics from detection results.
    
    Args:
        results: List of detection results
        
    Returns:
        dict: Summary statistics
    """
    if not results:
        return {
            "total_frames": 0,
            "total_detections": 0,
            "unique_vehicles": 0,
            "unique_plates": 0,
            "avg_confidence": 0.0,
            "detection_rate": 0.0,
        }
    
    unique_vehicles = set()
    unique_plates = set()
    confidences = []
    frames_with_detections = set()
    
    for result in results:
        unique_vehicles.add(result.get("vehicle_id"))
        if result.get("plate_text"):
            unique_plates.add(result.get("plate_text"))
        if result.get("confidence"):
            confidences.append(result.get("confidence"))
        frames_with_detections.add(result.get("frame_number"))
    
    total_frames = max(r.get("frame_number", 0) for r in results) + 1 if results else 0
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    detection_rate = len(frames_with_detections) / total_frames if total_frames > 0 else 0.0
    
    return {
        "total_frames": total_frames,
        "total_detections": len(results),
        "unique_vehicles": len(unique_vehicles),
        "unique_plates": len(unique_plates),
        "avg_confidence": avg_confidence,
        "detection_rate": detection_rate,
    }


def save_summary_to_file(summary: Dict[str, Any], filepath: str) -> None:
    """Save summary report to text file.
    
    Args:
        summary: Summary dictionary
        filepath: Output file path
    """
    with open(filepath, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("ALPR System - Summary Report\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Total Frames Processed: {summary['total_frames']}\n")
        f.write(f"Total Detections: {summary['total_detections']}\n")
        f.write(f"Unique Vehicles: {summary['unique_vehicles']}\n")
        f.write(f"Unique License Plates: {summary['unique_plates']}\n")
        f.write(f"Average Confidence: {summary['avg_confidence']:.2%}\n")
        f.write(f"Detection Rate: {summary['detection_rate']:.2%}\n")
        f.write("\n" + "=" * 60 + "\n")


# ============================================================================
# Roboflow Utilities
# ============================================================================

def convert_roboflow_predictions(predictions: Any) -> List[Tuple[float, float, float, float, float]]:
    """Convert Roboflow API predictions to standard bbox format.
    
    Args:
        predictions: Roboflow API prediction response
        
    Returns:
        List of bounding boxes as [(x1, y1, x2, y2, confidence), ...]
    """
    bboxes = []
    
    if not predictions:
        return bboxes
    
    # Handle different Roboflow response formats
    if hasattr(predictions, 'predictions'):
        predictions_list = predictions.predictions
    elif isinstance(predictions, dict) and 'predictions' in predictions:
        predictions_list = predictions['predictions']
    elif isinstance(predictions, list):
        predictions_list = predictions
    else:
        return bboxes
    
    for pred in predictions_list:
        # Extract bbox coordinates
        if isinstance(pred, dict):
            x = pred.get('x', 0)
            y = pred.get('y', 0)
            width = pred.get('width', 0)
            height = pred.get('height', 0)
            confidence = pred.get('confidence', 0)
        else:
            x = getattr(pred, 'x', 0)
            y = getattr(pred, 'y', 0)
            width = getattr(pred, 'width', 0)
            height = getattr(pred, 'height', 0)
            confidence = getattr(pred, 'confidence', 0)
        
        # Convert from center coordinates to corner coordinates
        x1 = x - width / 2
        y1 = y - height / 2
        x2 = x + width / 2
        y2 = y + height / 2
        
        bboxes.append((x1, y1, x2, y2, confidence))
    
    return bboxes


def validate_roboflow_config() -> Tuple[bool, Optional[str]]:
    """Validate Roboflow configuration.
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not config.USE_ROBOFLOW_API:
        return True, None
    
    if not config.ROBOFLOW_API_KEY:
        return False, "Roboflow API key not set. Set ROBOFLOW_API_KEY in .env"
    
    if not config.ROBOFLOW_WORKSPACE:
        return False, "Roboflow workspace not set"
    
    if not config.ROBOFLOW_PROJECT:
        return False, "Roboflow project not set"
    
    return True, None


# ============================================================================
# Supabase Utilities
# ============================================================================

def validate_supabase_config() -> Tuple[bool, Optional[str]]:
    """Validate Supabase configuration.
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not config.ENABLE_SUPABASE:
        return True, None
    
    if not config.SUPABASE_URL:
        return False, "Supabase URL not set. Set SUPABASE_URL in .env"
    
    if not config.SUPABASE_KEY:
        return False, "Supabase key not set. Set SUPABASE_KEY in .env"
    
    if not config.SUPABASE_URL.startswith("https://"):
        return False, "Supabase URL must start with https://"
    
    return True, None

