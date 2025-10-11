"""
ALPR System - Automatic License Plate Recognition

A comprehensive license plate recognition system using YOLO, SORT tracking,
and EasyOCR with Roboflow and Supabase integration.
"""

__version__ = "1.0.0"
__author__ = "ALPR System Contributors"
__license__ = "MIT"

# Core modules
from alpr_system import ALPRSystem
from sort import Sort, KalmanBoxTracker

__all__ = [
    "ALPRSystem",
    "Sort",
    "KalmanBoxTracker",
]

