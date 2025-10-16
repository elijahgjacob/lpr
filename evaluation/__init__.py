"""
Evaluation module for ALPR system.

Provides metrics and visualization for measuring system performance.
"""

from evaluation.eval import (
    compute_err,
    compute_cer,
    compute_wer,
    compute_latency_stats,
    evaluate_predictions,
)

__all__ = [
    "compute_err",
    "compute_cer",
    "compute_wer",
    "compute_latency_stats",
    "evaluate_predictions",
]


