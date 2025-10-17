"""
ALPR System - Automatic License Plate Recognition

This module provides the main ALPRSystem class that integrates:
- Vehicle detection (YOLO)
- License plate detection (Roboflow API or local YOLO)
- OCR (EasyOCR)
- Vehicle tracking (SORT)
- Data storage (Supabase)
"""

import cv2
import numpy as np
import torch
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import uuid

# Version info
try:
    from __init__ import __version__
except ImportError:
    __version__ = "1.0.0"

# Core dependencies
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

try:
    from roboflow import Roboflow
except ImportError:
    Roboflow = None

try:
    from supabase import create_client, Client
except ImportError:
    Client = None

# Local imports
import config
import utils
from sort import Sort
from model_configs import PlateDetectorConfig


class ALPRSystem:
    """
    Main ALPR system class that coordinates vehicle detection, tracking,
    license plate detection, and OCR.
    """
    
    def __init__(
        self,
        vehicle_model_path: Optional[str] = None,
        plate_model_path: Optional[str] = None,
        use_roboflow: Optional[bool] = None,
        enable_supabase: Optional[bool] = None,
        plate_detector_config: Optional[PlateDetectorConfig] = None
    ):
        """
        Initialize the ALPR system.
        
        Args:
            vehicle_model_path: Path to vehicle detection YOLO model
            plate_model_path: Path to license plate YOLO model (if not using Roboflow)
            use_roboflow: Override config to use Roboflow API
            enable_supabase: Override config to enable Supabase storage
            plate_detector_config: Optional PlateDetectorConfig for pluggable plate detection
            
        Raises:
            RuntimeError: If required dependencies are not installed
            ValueError: If configuration is invalid
        """
        print("=" * 60)
        print("Initializing ALPR System...")
        print("=" * 60)
        
        # Configuration (set these FIRST before checking dependencies)
        self.use_roboflow = use_roboflow if use_roboflow is not None else config.USE_ROBOFLOW_API
        self.enable_supabase = enable_supabase if enable_supabase is not None else config.ENABLE_SUPABASE
        
        # Check dependencies
        self._check_dependencies()
        
        # Validate configurations
        self._validate_configurations()
        
        # Initialize vehicle detector (always local YOLO)
        print(f"Loading vehicle detection model: {vehicle_model_path or config.VEHICLE_MODEL_PATH}")
        self.vehicle_detector = YOLO(vehicle_model_path or config.VEHICLE_MODEL_PATH)
        
        # Initialize license plate detector
        self.plate_detector_config = plate_detector_config
        self._init_plate_detector(plate_model_path)
        
        # Initialize OCR
        print("Initializing PaddleOCR...")
        gpu_available = torch.cuda.is_available()
        print(f"  GPU Available: {gpu_available}")
        # PaddleOCR will automatically use GPU if available
        self.ocr_reader = PaddleOCR(
            use_angle_cls=True,
            lang='en'
        )
        
        # Initialize SORT tracker
        print("Initializing SORT tracker...")
        self.tracker = Sort(
            max_age=config.SORT_MAX_AGE,
            min_hits=config.SORT_MIN_HITS,
            iou_threshold=config.SORT_IOU_THRESHOLD
        )
        
        # Cache for vehicle plates
        self.vehicle_plates: Dict[int, Dict[str, Any]] = {}
        
        # Initialize Supabase if enabled
        self.supabase_client: Optional[Client] = None
        self.current_test_run_id: Optional[str] = None
        self.pending_detections: List[Dict[str, Any]] = []  # Batch storage for Supabase
        if self.enable_supabase:
            print("Initializing Supabase connection...")
            self._init_supabase()
        
        # Statistics
        self.stats = {
            "total_frames": 0,
            "vehicles_detected": 0,
            "plates_detected": 0,
            "plates_read": 0,
        }
        
        print("✓ ALPR System initialized successfully!")
        print("=" * 60)
    
    def _check_dependencies(self):
        """Check if required dependencies are installed."""
        if YOLO is None:
            raise RuntimeError("ultralytics not installed. Run: pip install ultralytics")
        if PaddleOCR is None:
            raise RuntimeError("paddleocr not installed. Run: pip install paddleocr")
        if self.use_roboflow and Roboflow is None:
            raise RuntimeError("roboflow not installed. Run: pip install roboflow")
        if self.enable_supabase and Client is None:
            raise RuntimeError("supabase not installed. Run: pip install supabase")
    
    def _validate_configurations(self):
        """Validate Roboflow and Supabase configurations."""
        if self.use_roboflow:
            is_valid, error = utils.validate_roboflow_config()
            if not is_valid:
                raise ValueError(f"Invalid Roboflow configuration: {error}")
        
        if self.enable_supabase:
            is_valid, error = utils.validate_supabase_config()
            if not is_valid:
                raise ValueError(f"Invalid Supabase configuration: {error}")
    
    def _init_plate_detector(self, plate_model_path: Optional[str] = None):
        """
        Initialize license plate detector using either config-based or legacy approach.
        
        Args:
            plate_model_path: Path to plate model (used for legacy initialization)
        """
        if self.plate_detector_config is not None:
            # Use pluggable configuration
            print(f"Initializing plate detector from config: {self.plate_detector_config}")
            self.plate_detector = self.plate_detector_config.get_detector()
            print(f"  Plate detector loaded: {self.plate_detector_config.model_name}")
        else:
            # Use legacy initialization for backward compatibility
            if self.use_roboflow:
                print("Initializing Roboflow for license plate detection...")
                self._init_roboflow_detector()
            else:
                print(f"Loading local plate detection model: {plate_model_path or config.PLATE_MODEL_PATH}")
                self.plate_detector = YOLO(plate_model_path or config.PLATE_MODEL_PATH)
    
    def _init_roboflow_detector(self):
        """Initialize Roboflow license plate detector."""
        try:
            rf = Roboflow(api_key=config.ROBOFLOW_API_KEY)
            project = rf.workspace(config.ROBOFLOW_WORKSPACE).project(config.ROBOFLOW_PROJECT)
            self.plate_detector = project.version(config.ROBOFLOW_VERSION).model
            print(f"  ✓ Roboflow model loaded: {config.ROBOFLOW_PROJECT} v{config.ROBOFLOW_VERSION}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Roboflow: {e}")
    
    def _init_supabase(self):
        """Initialize Supabase client."""
        try:
            self.supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            print(f"  ✓ Supabase connected: {config.SUPABASE_URL}")
        except Exception as e:
            print(f"  ⚠ Supabase initialization failed: {e}")
            print(f"  Continuing without Supabase...")
            self.enable_supabase = False
    
    def start_test_run(self, video_name: str) -> Optional[str]:
        """
        Start a new test run in Supabase.
        
        Args:
            video_name: Name of the video being processed
            
        Returns:
            str: Test run ID if Supabase enabled, None otherwise
        """
        if not self.enable_supabase or not self.supabase_client:
            return None
        
        try:
            test_run_id = str(uuid.uuid4())
            data = {
                "id": test_run_id,
                "video_name": video_name,
                "start_time": datetime.utcnow().isoformat(),
                "detection_method": "roboflow" if self.use_roboflow else "local",
            }
            self.supabase_client.table("test_runs").insert(data).execute()
            self.current_test_run_id = test_run_id
            print(f"✓ Started test run: {test_run_id}")
            return test_run_id
        except Exception as e:
            print(f"⚠ Failed to start test run in Supabase: {e}")
            return None
    
    def end_test_run(self, total_frames: int):
        """
        End the current test run in Supabase.
        
        Args:
            total_frames: Total number of frames processed
        """
        if not self.enable_supabase or not self.supabase_client or not self.current_test_run_id:
            return
        
        try:
            # Update test run
            data = {
                "end_time": datetime.utcnow().isoformat(),
                "total_frames": total_frames,
            }
            self.supabase_client.table("test_runs").update(data).eq(
                "id", self.current_test_run_id
            ).execute()
            
            # Insert performance metrics
            metrics = {
                "test_run_id": self.current_test_run_id,
                "total_vehicles": self.stats["vehicles_detected"],
                "total_plates_detected": self.stats["plates_detected"],
                "avg_confidence": 0.0,  # Calculate from cached plates
                "processing_fps": 0.0,  # Will be calculated by caller
            }
            
            if self.vehicle_plates:
                confidences = [
                    p["confidence"] for p in self.vehicle_plates.values() 
                    if p.get("confidence")
                ]
                if confidences:
                    metrics["avg_confidence"] = sum(confidences) / len(confidences)
            
            self.supabase_client.table("performance_metrics").insert(metrics).execute()
            print(f"✓ Test run completed: {self.current_test_run_id}")
        except Exception as e:
            print(f"⚠ Failed to end test run: {e}")
    
    def detect_vehicles(self, frame: np.ndarray) -> np.ndarray:
        """
        Detect vehicles in frame using YOLO.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            numpy array: Detections as [[x1, y1, x2, y2, confidence], ...]
        """
        results = self.vehicle_detector(frame, verbose=False)[0]
        
        detections = []
        for box in results.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            # Filter by vehicle classes and confidence
            if class_id in config.VEHICLE_CLASSES and confidence >= config.VEHICLE_CONFIDENCE_THRESHOLD:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                detections.append([x1, y1, x2, y2, confidence])
        
        return np.array(detections) if detections else np.empty((0, 5))
    
    def detect_license_plates(
        self, 
        frame: np.ndarray, 
        vehicle_bbox: Tuple[float, float, float, float]
    ) -> List[Tuple[float, float, float, float, float]]:
        """
        Detect license plates within a vehicle bounding box.
        
        Args:
            frame: Full frame
            vehicle_bbox: Vehicle bounding box (x1, y1, x2, y2)
            
        Returns:
            List of plate bboxes as [(x1, y1, x2, y2, confidence), ...]
        """
        # Crop vehicle region
        x1, y1, x2, y2 = map(int, vehicle_bbox)
        vehicle_crop = frame[y1:y2, x1:x2]
        
        if vehicle_crop.size == 0:
            return []
        
        plates = []
        
        if self.use_roboflow:
            # Use Roboflow API
            try:
                # Use config threshold if available, otherwise use global config
                threshold = (self.plate_detector_config.confidence_threshold 
                           if self.plate_detector_config else config.PLATE_CONFIDENCE_THRESHOLD)
                predictions = self.plate_detector.predict(
                    vehicle_crop, 
                    confidence=int(threshold * 100)
                ).json()
                
                # Convert Roboflow predictions
                plate_bboxes = utils.convert_roboflow_predictions(predictions)
                
                # Convert coordinates from crop to full frame
                for px1, py1, px2, py2, conf in plate_bboxes:
                    plates.append((
                        x1 + px1,
                        y1 + py1,
                        x1 + px2,
                        y1 + py2,
                        conf
                    ))
            except Exception as e:
                print(f"⚠ Roboflow detection failed: {e}")
        else:
            # Use local YOLO model
            results = self.plate_detector(vehicle_crop, verbose=False)[0]
            
            # Use config threshold if available, otherwise use global config
            threshold = (self.plate_detector_config.confidence_threshold 
                       if self.plate_detector_config else config.PLATE_CONFIDENCE_THRESHOLD)
            
            for box in results.boxes:
                confidence = float(box.conf[0])
                if confidence >= threshold:
                    px1, py1, px2, py2 = box.xyxy[0].cpu().numpy()
                    # Convert to full frame coordinates
                    plates.append((
                        x1 + px1,
                        y1 + py1,
                        x1 + px2,
                        y1 + py2,
                        confidence
                    ))
        
        return plates
    
    def read_license_plate(
        self,
        frame: np.ndarray,
        plate_bbox: Tuple[float, float, float, float]
    ) -> Tuple[Optional[str], float]:
        """
        Read text from license plate using OCR.
        
        Args:
            frame: Full frame
            plate_bbox: Plate bounding box (x1, y1, x2, y2)
            
        Returns:
            Tuple[Optional[str], float]: (plate_text, confidence) or (None, 0.0)
        """
        # Crop plate with padding
        plate_crop = utils.crop_license_plate(frame, plate_bbox, padding=0.1)
        
        if plate_crop.size == 0:
            return None, 0.0
        
        # Preprocess image
        processed = utils.preprocess_plate_image(plate_crop)
        
        # Convert back to 3D for PaddleOCR
        if len(processed.shape) == 2:
            processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
        
        # Run OCR with PaddleOCR
        try:
            # PaddleOCR returns: [[[bbox], (text, confidence)], ...]
            results = self.ocr_reader.ocr(processed)
            
            if not results or not isinstance(results, list) or not results[0]:
                return None, 0.0
            
            # Handle new PaddleOCR format (dictionary)
            if isinstance(results[0], dict):
                rec_texts = results[0].get('rec_texts', [])
                rec_scores = results[0].get('rec_scores', [])
                
                if not rec_texts:
                    return None, 0.0
                
                # Combine all texts and get average confidence
                texts = []
                confidences = []
                
                for text, conf in zip(rec_texts, rec_scores):
                    # Filter with allowlist
                    filtered_text = ''.join(
                        c for c in text if c in config.OCR_ALLOWLIST
                    )
                    
                    if filtered_text:
                        texts.append(filtered_text)
                        confidences.append(conf)
                        
            else:
                # Handle old format (list of lists)
                texts = []
                confidences = []
                
                for line in results[0]:
                    if line and len(line) >= 2:
                        text = line[1][0] if len(line[1]) > 0 else ""
                        conf = line[1][1] if len(line[1]) > 1 else 0.0
                        
                        # Filter with allowlist
                        filtered_text = ''.join(
                            c for c in text if c in config.OCR_ALLOWLIST
                        )
                        
                        if filtered_text:
                            texts.append(filtered_text)
                            confidences.append(conf)
            
            if not texts:
                return None, 0.0
            
            # Combine results
            final_text = ''.join(texts).strip()
            avg_confidence = sum(confidences) / len(confidences)
            
            # Format and validate
            formatted_text = utils.format_license_plate(final_text)
            
            if avg_confidence >= config.OCR_CONFIDENCE_THRESHOLD and utils.validate_license_plate(formatted_text):
                return formatted_text, avg_confidence
            
        except Exception as e:
            print(f"⚠ OCR failed: {e}")
        
        return None, 0.0
    
    def process_frame(
        self,
        frame: np.ndarray,
        frame_number: int,
        visualize: bool = False
    ) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Process a single frame: detect vehicles, track them, detect and read plates.
        
        Args:
            frame: Input frame
            frame_number: Current frame number
            visualize: Whether to draw annotations on frame
            
        Returns:
            Tuple[np.ndarray, List[Dict]]: (annotated_frame, detection_results)
        """
        self.stats["total_frames"] += 1
        results = []
        
        # Detect vehicles
        vehicle_detections = self.detect_vehicles(frame)
        
        # Update tracker
        tracked_vehicles = self.tracker.update(vehicle_detections)
        
        # Process each tracked vehicle
        for vehicle in tracked_vehicles:
            vehicle_id = int(vehicle[4])
            vehicle_bbox = tuple(vehicle[:4])
            
            self.stats["vehicles_detected"] += 1
            
            # Check if we've already read this vehicle's plate
            if vehicle_id not in self.vehicle_plates:
                # Detect license plates
                plate_bboxes = self.detect_license_plates(frame, vehicle_bbox)
                
                if plate_bboxes:
                    self.stats["plates_detected"] += 1
                    
                    # Read the first detected plate
                    plate_bbox = plate_bboxes[0][:4]
                    plate_text, confidence = self.read_license_plate(frame, plate_bbox)
                    
                    if plate_text:
                        self.stats["plates_read"] += 1
                        
                        # Cache the result
                        self.vehicle_plates[vehicle_id] = {
                            "text": plate_text,
                            "confidence": confidence,
                            "bbox": plate_bbox,
                            "first_seen": frame_number,
                        }
                        
                        # Queue detection for batch Supabase upload
                        if self.enable_supabase and self.current_test_run_id:
                            self._queue_detection(frame_number, vehicle_id, plate_text, confidence, plate_bbox)
            
            # Add to results
            cached_plate = self.vehicle_plates.get(vehicle_id)
            if cached_plate:
                results.append({
                    "frame_number": frame_number,
                    "vehicle_id": vehicle_id,
                    "vehicle_bbox": vehicle_bbox,
                    "plate_text": cached_plate["text"],
                    "plate_bbox": cached_plate["bbox"],
                    "confidence": cached_plate["confidence"],
                    "timestamp": datetime.now().isoformat(),
                    "version": __version__,
                })
            
            # Visualize if requested
            if visualize:
                plate_text = cached_plate["text"] if cached_plate else None
                plate_bbox = cached_plate["bbox"] if cached_plate else None
                frame = utils.write_annotations(
                    frame, vehicle_id, plate_text, vehicle_bbox, plate_bbox
                )
        
        return frame, results
    
    def _queue_detection(
        self,
        frame_number: int,
        vehicle_id: int,
        plate_text: str,
        confidence: float,
        bbox: Tuple[float, float, float, float]
    ):
        """Queue detection for batch upload to Supabase."""
        if not self.current_test_run_id:
            return
        
        data = {
            "test_run_id": self.current_test_run_id,
            "frame_number": frame_number,
            "vehicle_id": vehicle_id,
            "plate_text": plate_text,
            "confidence": confidence,
            "bbox_x1": bbox[0],
            "bbox_y1": bbox[1],
            "bbox_x2": bbox[2],
            "bbox_y2": bbox[3],
            "timestamp": datetime.now().isoformat(),
            "version": __version__,
        }
        self.pending_detections.append(data)
    
    def bulk_upload_detections(self):
        """
        Upload all pending detections to Supabase in one batch.
        Call this at the end of processing.
        """
        if not self.enable_supabase or not self.supabase_client or not self.pending_detections:
            return
        
        try:
            print(f"\n📤 Uploading {len(self.pending_detections)} detections to Supabase...")
            # Supabase supports batch inserts
            self.supabase_client.table("detections").insert(self.pending_detections).execute()
            print(f"  ✓ Successfully uploaded {len(self.pending_detections)} detections")
            self.pending_detections.clear()
        except Exception as e:
            print(f"  ⚠ Failed to bulk upload detections: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current processing statistics.
        
        Returns:
            dict: Statistics dictionary
        """
        return {
            **self.stats,
            "unique_vehicles": len(self.vehicle_plates),
            "cache_size": len(self.vehicle_plates),
        }
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self.stats = {
            "total_frames": 0,
            "vehicles_detected": 0,
            "plates_detected": 0,
            "plates_read": 0,
        }
        self.vehicle_plates.clear()

