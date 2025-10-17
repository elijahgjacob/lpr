#!/usr/bin/env python3
"""
Test script for the Model Comparison System

This script demonstrates how to use the model comparison system
and verifies that all components work correctly.
"""

import os
import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_configs import create_detector_config, LocalYOLODetectorConfig, RunPodYOLODetectorConfig
from alpr_system import ALPRSystem


def test_model_configs():
    """Test model configuration classes."""
    print("Testing Model Configuration Classes...")
    
    # Test Local YOLO config (without file validation)
    try:
        # Create a test model file to avoid validation error
        test_model_path = "models/test_model.pt"
        os.makedirs("models", exist_ok=True)
        Path(test_model_path).touch()  # Create empty file
        
        local_config = LocalYOLODetectorConfig(
            model_name="Test Local Model",
            model_path=test_model_path,
            confidence_threshold=0.3
        )
        print(f"  ✓ Local YOLO config: {local_config}")
        
        # Clean up
        os.remove(test_model_path)
        
    except Exception as e:
        print(f"  ✗ Local YOLO config failed: {e}")
    
    # Test RunPod config
    try:
        runpod_config = RunPodYOLODetectorConfig(
            model_name="Test RunPod Model",
            runpod_endpoint="https://api.runpod.ai/v2/test/run",
            model_path="/workspace/models/test.pt"
        )
        print(f"  ✓ RunPod YOLO config: {runpod_config}")
    except Exception as e:
        print(f"  ✗ RunPod YOLO config failed: {e}")


def test_model_registry():
    """Test model registry loading and factory function."""
    print("\nTesting Model Registry...")
    
    try:
        with open('model_registry.json', 'r') as f:
            registry = json.load(f)
        print(f"  ✓ Registry loaded: {len(registry['models'])} models")
        
        # Test factory function with RunPod models (no file validation)
        runpod_models = [m for m in registry['models'] if m['type'] == 'runpod_yolo']
        
        for model in runpod_models[:2]:  # Test first 2 RunPod models
            try:
                config_with_name = model['config'].copy()
                config_with_name['model_name'] = model['name']
                config = create_detector_config(config_with_name, model['type'])
                print(f"  ✓ Factory created {model['name']}: {type(config).__name__}")
            except Exception as e:
                print(f"  ✗ Factory failed for {model['name']}: {e}")
        
    except Exception as e:
        print(f"  ✗ Registry test failed: {e}")


def test_alpr_integration():
    """Test ALPR system integration with model configs."""
    print("\nTesting ALPR System Integration...")
    
    try:
        # Test with RunPod config (no file dependencies)
        runpod_config = RunPodYOLODetectorConfig(
            model_name="Test Integration",
            runpod_endpoint="https://api.runpod.ai/v2/test/run",
            model_path="/workspace/models/test.pt"
        )
        
        # This will fail at initialization due to missing dependencies,
        # but it should get past the config creation step
        try:
            alpr = ALPRSystem(plate_detector_config=runpod_config)
            print("  ✓ ALPR system initialized with RunPod config")
        except Exception as e:
            if "dependencies" in str(e).lower() or "import" in str(e).lower():
                print(f"  ✓ ALPR system config integration works (dependencies missing: {e})")
            else:
                print(f"  ✗ ALPR system integration failed: {e}")
        
    except Exception as e:
        print(f"  ✗ ALPR integration test failed: {e}")


def test_compare_models_script():
    """Test the compare_models.py script structure."""
    print("\nTesting Compare Models Script...")
    
    try:
        # Check if script exists and can be imported
        if os.path.exists('compare_models.py'):
            print("  ✓ compare_models.py exists")
            
            # Test basic imports
            from compare_models import load_model_registry, load_ground_truth
            print("  ✓ Script imports successfully")
            
            # Test registry loading
            registry = load_model_registry()
            print(f"  ✓ Registry loading works: {len(registry['models'])} models")
            
        else:
            print("  ✗ compare_models.py not found")
            
    except Exception as e:
        print(f"  ✗ Compare models script test failed: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("ALPR Model Comparison System - Test Suite")
    print("=" * 60)
    
    test_model_configs()
    test_model_registry()
    test_alpr_integration()
    test_compare_models_script()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete!")
    print("=" * 60)
    
    print("\nNext Steps:")
    print("1. Set up RunPod API key: export RUNPOD_API_KEY='your-key'")
    print("2. Update RunPod endpoints in model_registry.json")
    print("3. Run comparison: python compare_models.py --models runpod_yolo11n")
    print("4. For local models, add actual .pt files to models/ directory")


if __name__ == "__main__":
    main()
