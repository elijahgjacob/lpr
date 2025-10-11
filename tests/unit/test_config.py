"""Unit tests for configuration module."""
import os
import pytest
from unittest.mock import patch
import config


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_validate_config_with_all_required_vars(self):
        """Test validation passes with all required environment variables."""
        with patch.dict(os.environ, {
            "ROBOFLOW_API_KEY": "test_key",
            "ROBOFLOW_WORKSPACE": "test_workspace",
            "ROBOFLOW_PROJECT": "test_project",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test_supabase_key",
            "USE_ROBOFLOW_API": "true",
            "ENABLE_SUPABASE": "true",
        }, clear=False):
            # Reload config to pick up environment variables
            import importlib
            importlib.reload(config)
            is_valid, errors = config.validate_config()
            assert is_valid, f"Config should be valid, but got errors: {errors}"
            assert len(errors) == 0
    
    def test_validate_config_missing_roboflow_key(self):
        """Test validation fails when Roboflow API key is missing."""
        with patch.dict(os.environ, {
            "ROBOFLOW_API_KEY": "",
            "USE_ROBOFLOW_API": "true",
        }, clear=False):
            import importlib
            importlib.reload(config)
            is_valid, errors = config.validate_config()
            assert not is_valid
            assert any("ROBOFLOW_API_KEY" in error for error in errors)
    
    def test_validate_config_missing_supabase_url(self):
        """Test validation fails when Supabase URL is missing."""
        with patch.dict(os.environ, {
            "SUPABASE_URL": "",
            "ENABLE_SUPABASE": "true",
        }, clear=False):
            import importlib
            importlib.reload(config)
            is_valid, errors = config.validate_config()
            assert not is_valid
            assert any("SUPABASE_URL" in error for error in errors)
    
    def test_validate_config_invalid_supabase_url(self):
        """Test validation fails with invalid Supabase URL."""
        with patch.dict(os.environ, {
            "SUPABASE_URL": "http://invalid.url",
            "SUPABASE_KEY": "test_key",
            "ENABLE_SUPABASE": "true",
        }, clear=False):
            import importlib
            importlib.reload(config)
            is_valid, errors = config.validate_config()
            assert not is_valid
            assert any("https://" in error for error in errors)
    
    def test_validate_config_disabled_services(self):
        """Test validation passes when services are disabled."""
        with patch.dict(os.environ, {
            "USE_ROBOFLOW_API": "false",
            "ENABLE_SUPABASE": "false",
        }, clear=False):
            import importlib
            importlib.reload(config)
            is_valid, errors = config.validate_config()
            assert is_valid
            assert len(errors) == 0


class TestConfigConstants:
    """Test configuration constants."""
    
    def test_vehicle_classes_defined(self):
        """Test vehicle classes are properly defined."""
        assert isinstance(config.VEHICLE_CLASSES, dict)
        assert 2 in config.VEHICLE_CLASSES  # car
        assert 3 in config.VEHICLE_CLASSES  # motorbike
        assert 5 in config.VEHICLE_CLASSES  # bus
        assert 7 in config.VEHICLE_CLASSES  # truck
    
    def test_confidence_thresholds_in_valid_range(self):
        """Test confidence thresholds are between 0 and 1."""
        assert 0 <= config.VEHICLE_CONFIDENCE_THRESHOLD <= 1
        assert 0 <= config.PLATE_CONFIDENCE_THRESHOLD <= 1
        assert 0 <= config.OCR_CONFIDENCE_THRESHOLD <= 1
    
    def test_color_palette_defined(self):
        """Test color palette is defined with tuples."""
        assert isinstance(config.COLOR_PALETTE, list)
        assert len(config.COLOR_PALETTE) > 0
        for color in config.COLOR_PALETTE:
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)
    
    def test_directories_exist(self):
        """Test required directories are created."""
        assert config.MODELS_DIR.exists()
        assert config.VIDEOS_DIR.exists()
        assert config.RESULTS_DIR.exists()


class TestConfigHelpers:
    """Test configuration helper functions."""
    
    def test_get_roboflow_config(self):
        """Test getting Roboflow configuration."""
        roboflow_config = config.get_roboflow_config()
        assert isinstance(roboflow_config, dict)
        assert "api_key" in roboflow_config
        assert "workspace" in roboflow_config
        assert "project" in roboflow_config
        assert "version" in roboflow_config
        assert "enabled" in roboflow_config
    
    def test_get_supabase_config(self):
        """Test getting Supabase configuration."""
        supabase_config = config.get_supabase_config()
        assert isinstance(supabase_config, dict)
        assert "url" in supabase_config
        assert "key" in supabase_config
        assert "enabled" in supabase_config
    
    def test_print_config_runs_without_error(self, capsys):
        """Test print_config runs without error."""
        config.print_config()
        captured = capsys.readouterr()
        assert "ALPR System Configuration" in captured.out
        assert "Roboflow:" in captured.out
        assert "Supabase:" in captured.out


class TestThresholdValidation:
    """Test threshold parameter validation."""
    
    @pytest.mark.parametrize("threshold,value", [
        ("VEHICLE_CONFIDENCE_THRESHOLD", "1.5"),
        ("VEHICLE_CONFIDENCE_THRESHOLD", "-0.1"),
        ("PLATE_CONFIDENCE_THRESHOLD", "2.0"),
        ("OCR_CONFIDENCE_THRESHOLD", "-1.0"),
    ])
    def test_invalid_threshold_values(self, threshold, value):
        """Test that invalid threshold values are caught."""
        with patch.dict(os.environ, {threshold: value}, clear=False):
            import importlib
            importlib.reload(config)
            is_valid, errors = config.validate_config()
            assert not is_valid
            assert len(errors) > 0

