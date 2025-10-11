"""Configuration module for ALPR system.

This module loads configuration from environment variables and provides
constants for the ALPR system including Roboflow and Supabase settings.
"""

import os
from pathlib import Path
from typing import Dict, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
VIDEOS_DIR = BASE_DIR / "videos"
RESULTS_DIR = BASE_DIR / "results"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Model paths
VEHICLE_MODEL_PATH = str(MODELS_DIR / "yolo11x.pt")
PLATE_MODEL_PATH = str(MODELS_DIR / "license_plate_detector.pt")

# Roboflow configuration
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_WORKSPACE = os.getenv("ROBOFLOW_WORKSPACE", "roboflow-universe")
ROBOFLOW_PROJECT = os.getenv(
    "ROBOFLOW_PROJECT", "license-plate-recognition-rxg4e"
)
ROBOFLOW_VERSION = int(os.getenv("ROBOFLOW_VERSION", "4"))
USE_ROBOFLOW_API = os.getenv("USE_ROBOFLOW_API", "true").lower() == "true"

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ENABLE_SUPABASE = os.getenv("ENABLE_SUPABASE", "true").lower() == "true"

# Vehicle detection parameters
VEHICLE_CLASSES: Dict[int, str] = {
    2: "car",
    3: "motorbike",
    5: "bus",
    7: "truck",
}

# Confidence thresholds
VEHICLE_CONFIDENCE_THRESHOLD = float(
    os.getenv("VEHICLE_CONFIDENCE_THRESHOLD", "0.5")
)
PLATE_CONFIDENCE_THRESHOLD = float(
    os.getenv("PLATE_CONFIDENCE_THRESHOLD", "0.3")
)
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.5"))

# SORT tracking parameters
SORT_MAX_AGE = int(os.getenv("SORT_MAX_AGE", "30"))
SORT_MIN_HITS = int(os.getenv("SORT_MIN_HITS", "3"))
SORT_IOU_THRESHOLD = float(os.getenv("SORT_IOU_THRESHOLD", "0.3"))

# OCR parameters
OCR_LANGUAGES = ["en"]
OCR_ALLOWLIST = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MIN_PLATE_LENGTH = int(os.getenv("MIN_PLATE_LENGTH", "5"))
MAX_PLATE_LENGTH = int(os.getenv("MAX_PLATE_LENGTH", "10"))

# Visualization colors (BGR format for OpenCV)
COLOR_PALETTE: list[Tuple[int, int, int]] = [
    (0, 255, 0),    # Green
    (255, 0, 0),    # Blue
    (0, 0, 255),    # Red
    (255, 255, 0),  # Cyan
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Yellow
    (128, 0, 128),  # Purple
    (0, 128, 128),  # Olive
]

# Visualization settings
VEHICLE_BOX_COLOR = (0, 255, 0)  # Green
PLATE_BOX_COLOR = (255, 0, 0)    # Blue
BOX_THICKNESS = 2
FONT_SCALE = 0.6
FONT_THICKNESS = 2

# Video processing
DEFAULT_FPS = 30
FRAME_SKIP = int(os.getenv("FRAME_SKIP", "0"))  # Process every Nth frame (0 = all)


def validate_config() -> tuple[bool, list[str]]:
    """Validate configuration settings.
    
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    # Check Roboflow configuration if enabled
    if USE_ROBOFLOW_API:
        if not ROBOFLOW_API_KEY:
            errors.append("ROBOFLOW_API_KEY not set in environment")
        if not ROBOFLOW_WORKSPACE:
            errors.append("ROBOFLOW_WORKSPACE not set")
        if not ROBOFLOW_PROJECT:
            errors.append("ROBOFLOW_PROJECT not set")
    
    # Check Supabase configuration if enabled
    if ENABLE_SUPABASE:
        if not SUPABASE_URL:
            errors.append("SUPABASE_URL not set in environment")
        if not SUPABASE_KEY:
            errors.append("SUPABASE_KEY not set in environment")
        if SUPABASE_URL and not SUPABASE_URL.startswith("https://"):
            errors.append("SUPABASE_URL must start with https://")
    
    # Validate thresholds
    if not 0 <= VEHICLE_CONFIDENCE_THRESHOLD <= 1:
        errors.append("VEHICLE_CONFIDENCE_THRESHOLD must be between 0 and 1")
    if not 0 <= PLATE_CONFIDENCE_THRESHOLD <= 1:
        errors.append("PLATE_CONFIDENCE_THRESHOLD must be between 0 and 1")
    if not 0 <= OCR_CONFIDENCE_THRESHOLD <= 1:
        errors.append("OCR_CONFIDENCE_THRESHOLD must be between 0 and 1")
    
    # Validate SORT parameters
    if SORT_MAX_AGE < 1:
        errors.append("SORT_MAX_AGE must be at least 1")
    if SORT_MIN_HITS < 1:
        errors.append("SORT_MIN_HITS must be at least 1")
    if not 0 <= SORT_IOU_THRESHOLD <= 1:
        errors.append("SORT_IOU_THRESHOLD must be between 0 and 1")
    
    return len(errors) == 0, errors


def get_roboflow_config() -> dict:
    """Get Roboflow configuration as dictionary.
    
    Returns:
        dict: Roboflow configuration
    """
    return {
        "api_key": ROBOFLOW_API_KEY,
        "workspace": ROBOFLOW_WORKSPACE,
        "project": ROBOFLOW_PROJECT,
        "version": ROBOFLOW_VERSION,
        "enabled": USE_ROBOFLOW_API,
    }


def get_supabase_config() -> dict:
    """Get Supabase configuration as dictionary.
    
    Returns:
        dict: Supabase configuration
    """
    return {
        "url": SUPABASE_URL,
        "key": SUPABASE_KEY,
        "enabled": ENABLE_SUPABASE,
    }


def print_config():
    """Print current configuration (without sensitive data)."""
    print("=" * 50)
    print("ALPR System Configuration")
    print("=" * 50)
    print(f"Models Directory: {MODELS_DIR}")
    print(f"Videos Directory: {VIDEOS_DIR}")
    print(f"Results Directory: {RESULTS_DIR}")
    print()
    print("Detection Settings:")
    print(f"  Vehicle Confidence: {VEHICLE_CONFIDENCE_THRESHOLD}")
    print(f"  Plate Confidence: {PLATE_CONFIDENCE_THRESHOLD}")
    print(f"  OCR Confidence: {OCR_CONFIDENCE_THRESHOLD}")
    print()
    print("Roboflow:")
    print(f"  Enabled: {USE_ROBOFLOW_API}")
    print(f"  API Key Set: {'Yes' if ROBOFLOW_API_KEY else 'No'}")
    print(f"  Workspace: {ROBOFLOW_WORKSPACE}")
    print(f"  Project: {ROBOFLOW_PROJECT}")
    print()
    print("Supabase:")
    print(f"  Enabled: {ENABLE_SUPABASE}")
    print(f"  URL Set: {'Yes' if SUPABASE_URL else 'No'}")
    print(f"  Key Set: {'Yes' if SUPABASE_KEY else 'No'}")
    print("=" * 50)


if __name__ == "__main__":
    # Print configuration when run directly
    print_config()
    
    # Validate configuration
    is_valid, errors = validate_config()
    if is_valid:
        print("\n✓ Configuration is valid")
    else:
        print("\n✗ Configuration errors:")
        for error in errors:
            print(f"  - {error}")

