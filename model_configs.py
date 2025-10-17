"""
Model Configuration System for ALPR

This module provides pluggable configuration classes for different license plate detection models,
allowing easy comparison and evaluation of different detection approaches.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path


class PlateDetectorConfig(ABC):
    """
    Base class for plate detector configurations.
    
    This abstract base class defines the interface that all plate detector
    configurations must implement to be compatible with the ALPR system.
    """
    
    def __init__(self, model_name: str, confidence_threshold: float = 0.25):
        """
        Initialize base plate detector configuration.
        
        Args:
            model_name: Human-readable name for this model configuration
            confidence_threshold: Minimum confidence score for detections
        """
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
    
    @abstractmethod
    def get_detector(self):
        """
        Get the configured detector instance.
        
        Returns:
            Detector instance ready for use with the ALPR system
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_config_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary for serialization.
        
        Returns:
            Dictionary representation of the configuration
        """
        raise NotImplementedError
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return f"{self.__class__.__name__}(name='{self.model_name}', conf={self.confidence_threshold})"


class LocalYOLODetectorConfig(PlateDetectorConfig):
    """
    Configuration for local YOLO-based plate detector.
    
    This configuration supports local YOLO models for license plate detection,
    allowing for different model files and confidence thresholds.
    """
    
    def __init__(
        self, 
        model_name: str,
        model_path: str, 
        confidence_threshold: float = 0.25,
        device: Optional[str] = None
    ):
        """
        Initialize local YOLO detector configuration.
        
        Args:
            model_name: Human-readable name for this model
            model_path: Path to the YOLO model file (.pt)
            confidence_threshold: Minimum confidence score for detections
            device: Device to run inference on ('cpu', 'cuda', 'mps', or None for auto)
        """
        super().__init__(model_name, confidence_threshold)
        self.model_path = str(Path(model_path).resolve())
        self.device = device
        
        # Validate model path exists
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
    
    def get_detector(self):
        """
        Get configured YOLO detector instance.
        
        Returns:
            YOLO model instance configured for license plate detection
        """
        try:
            from ultralytics import YOLO
        except ImportError:
            raise RuntimeError(
                "ultralytics not installed. Run: pip install ultralytics"
            )
        
        # Load YOLO model
        detector = YOLO(self.model_path)
        
        # Set device if specified
        if self.device:
            detector.to(self.device)
        
        return detector
    
    def get_config_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "type": "local_yolo",
            "model_name": self.model_name,
            "model_path": self.model_path,
            "confidence_threshold": self.confidence_threshold,
            "device": self.device
        }
    
    def __str__(self) -> str:
        """String representation with model path."""
        return f"LocalYOLO(name='{self.model_name}', path='{self.model_path}', conf={self.confidence_threshold})"


# Future: RoboflowDetectorConfig class can be added here when Roboflow integration is needed
class RoboflowDetectorConfig(PlateDetectorConfig):
    """
    Configuration for Roboflow API-based plate detector.
    
    This configuration supports Roboflow API models for license plate detection.
    Currently not implemented but designed for future use.
    """
    
    def __init__(
        self,
        model_name: str,
        workspace: str,
        project: str,
        version: int,
        confidence_threshold: float = 0.25,
        api_key: Optional[str] = None
    ):
        """
        Initialize Roboflow detector configuration.
        
        Args:
            model_name: Human-readable name for this model
            workspace: Roboflow workspace name
            project: Roboflow project name
            version: Roboflow model version number
            confidence_threshold: Minimum confidence score for detections
            api_key: Roboflow API key (if not provided, will use environment variable)
        """
        super().__init__(model_name, confidence_threshold)
        self.workspace = workspace
        self.project = project
        self.version = version
        self.api_key = api_key
    
    def get_detector(self):
        """
        Get configured Roboflow detector instance.
        
        Returns:
            Roboflow model instance configured for license plate detection
            
        Raises:
            NotImplementedError: Roboflow integration not yet implemented
        """
        raise NotImplementedError(
            "Roboflow integration not yet implemented. "
            "Use LocalYOLODetectorConfig for now."
        )
    
    def get_config_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "type": "roboflow",
            "model_name": self.model_name,
            "workspace": self.workspace,
            "project": self.project,
            "version": self.version,
            "confidence_threshold": self.confidence_threshold,
            "api_key": self.api_key
        }


def create_detector_config(config_dict: Dict[str, Any]) -> PlateDetectorConfig:
    """
    Factory function to create detector config from dictionary.
    
    Args:
        config_dict: Dictionary containing configuration parameters
        
    Returns:
        Appropriate PlateDetectorConfig instance
        
    Raises:
        ValueError: If configuration type is not supported
        KeyError: If required configuration parameters are missing
    """
    config_type = config_dict.get("type")
    
    if config_type == "local_yolo":
        required_keys = ["model_name", "model_path"]
        missing_keys = [key for key in required_keys if key not in config_dict]
        if missing_keys:
            raise KeyError(f"Missing required keys for local_yolo config: {missing_keys}")
        
        return LocalYOLODetectorConfig(
            model_name=config_dict["model_name"],
            model_path=config_dict["model_path"],
            confidence_threshold=config_dict.get("confidence_threshold", 0.25),
            device=config_dict.get("device")
        )
    
    elif config_type == "roboflow":
        required_keys = ["model_name", "workspace", "project", "version"]
        missing_keys = [key for key in required_keys if key not in config_dict]
        if missing_keys:
            raise KeyError(f"Missing required keys for roboflow config: {missing_keys}")
        
        return RoboflowDetectorConfig(
            model_name=config_dict["model_name"],
            workspace=config_dict["workspace"],
            project=config_dict["project"],
            version=config_dict["version"],
            confidence_threshold=config_dict.get("confidence_threshold", 0.25),
            api_key=config_dict.get("api_key")
        )
    
    else:
        raise ValueError(f"Unsupported detector type: {config_type}")


# Example configurations for testing
EXAMPLE_CONFIGS = {
    "yolo_baseline": LocalYOLODetectorConfig(
        model_name="YOLO Baseline",
        model_path="models/license_plate_detector.pt",
        confidence_threshold=0.25
    ),
    "yolo_high_conf": LocalYOLODetectorConfig(
        model_name="YOLO High Confidence", 
        model_path="models/license_plate_detector.pt",
        confidence_threshold=0.5
    ),
    "yolo_low_conf": LocalYOLODetectorConfig(
        model_name="YOLO Low Confidence",
        model_path="models/license_plate_detector.pt", 
        confidence_threshold=0.1
    )
}
