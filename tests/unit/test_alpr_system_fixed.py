"""Unit tests for ALPR system (with mocked dependencies) - FIXED VERSION."""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock


# Base patches that should be applied to all tests
BASE_PATCHES = [
    patch('alpr_system.YOLO'),
    patch('alpr_system.easyocr.Reader'),
    patch('alpr_system.Sort'),
    patch('alpr_system.torch.cuda.is_available', return_value=False),
    patch('alpr_system.config.USE_ROBOFLOW_API', False),
    patch('alpr_system.config.ENABLE_SUPABASE', False),
]


@pytest.fixture
def alpr_system_mocks():
    """Fixture that sets up all necessary mocks for ALPR system."""
    with patch('alpr_system.YOLO') as mock_yolo, \
         patch('alpr_system.easyocr.Reader') as mock_reader, \
         patch('alpr_system.Sort') as mock_sort, \
         patch('alpr_system.torch.cuda.is_available', return_value=False):
        
        # Setup YOLO mock
        mock_yolo_instance = Mock()
        mock_result = Mock()
        mock_result.boxes = []
        mock_yolo_instance.return_value = [mock_result]
        mock_yolo.return_value = mock_yolo_instance
        
        # Setup EasyOCR mock
        mock_reader_instance = Mock()
        mock_reader_instance.readtext.return_value = []
        mock_reader.return_value = mock_reader_instance
        
        # Setup Sort mock
        mock_sort_instance = Mock()
        mock_sort_instance.update.return_value = np.empty((0, 5))
        mock_sort.return_value = mock_sort_instance
        
        yield {
            'yolo': mock_yolo,
            'reader': mock_reader,
            'sort': mock_sort,
            'yolo_instance': mock_yolo_instance,
            'reader_instance': mock_reader_instance,
            'sort_instance': mock_sort_instance,
        }


class TestALPRSystemBasic:
    """Basic tests that the system can be imported and created."""
    
    def test_import(self):
        """Test that ALPR system can be imported."""
        from alpr_system import ALPRSystem
        assert ALPRSystem is not None
    
    def test_basic_initialization(self, alpr_system_mocks):
        """Test basic initialization with mocks."""
        with patch('alpr_system.config.USE_ROBOFLOW_API', False), \
             patch('alpr_system.config.ENABLE_SUPABASE', False):
            from alpr_system import ALPRSystem
            alpr = ALPRSystem()
            
            assert alpr is not None
            assert hasattr(alpr, 'vehicle_detector')
            assert hasattr(alpr, 'tracker')


class TestConfiguration:
    """Test configuration and validation."""
    
    def test_config_values_exist(self):
        """Test that config values are defined."""
        import config
        
        assert hasattr(config, 'VEHICLE_MODEL_PATH')
        assert hasattr(config, 'VEHICLE_CLASSES')
        assert hasattr(config, 'VEHICLE_CONFIDENCE_THRESHOLD')
    
    def test_roboflow_config_helper(self):
        """Test Roboflow config helper."""
        import config
        roboflow_config = config.get_roboflow_config()
        
        assert isinstance(roboflow_config, dict)
        assert 'api_key' in roboflow_config
        assert 'workspace' in roboflow_config
    
    def test_supabase_config_helper(self):
        """Test Supabase config helper."""
        import config
        supabase_config = config.get_supabase_config()
        
        assert isinstance(supabase_config, dict)
        assert 'url' in supabase_config
        assert 'key' in supabase_config


class TestUtilities:
    """Test utility functions."""
    
    def test_format_license_plate(self):
        """Test license plate formatting."""
        import utils
        
        result = utils.format_license_plate("ABC 123")
        assert result == "ABC123"
        
        result = utils.format_license_plate("xyz-456")
        assert result == "XYZ456"
    
    def test_validate_license_plate(self):
        """Test license plate validation."""
        import utils
        
        assert utils.validate_license_plate("ABC123") is True
        assert utils.validate_license_plate("A1") is False
        assert utils.validate_license_plate("123456") is False
        assert utils.validate_license_plate("ABCDEF") is False
    
    def test_calculate_bbox_area(self):
        """Test bbox area calculation."""
        import utils
        
        area = utils.calculate_bbox_area((0, 0, 10, 10))
        assert area == 100.0
        
        area = utils.calculate_bbox_area((10, 10, 30, 40))
        assert area == 600.0


class TestSort:
    """Test SORT tracking algorithm."""
    
    def test_sort_import(self):
        """Test SORT can be imported."""
        from sort import Sort, KalmanBoxTracker
        assert Sort is not None
        assert KalmanBoxTracker is not None
    
    def test_sort_initialization(self):
        """Test SORT tracker initialization."""
        from sort import Sort
        tracker = Sort(max_age=5, min_hits=3, iou_threshold=0.3)
        
        assert tracker.max_age == 5
        assert tracker.min_hits == 3
        assert tracker.iou_threshold == 0.3
    
    def test_iou_calculation(self):
        """Test IoU calculation."""
        from sort import iou_batch
        import numpy as np
        
        bbox1 = np.array([[0, 0, 10, 10]])
        bbox2 = np.array([[0, 0, 10, 10]])
        iou = iou_batch(bbox1, bbox2)
        
        assert np.isclose(iou[0, 0], 1.0)


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_project_structure(self):
        """Test that all main files exist."""
        import os
        
        assert os.path.exists('main.py')
        assert os.path.exists('alpr_system.py')
        assert os.path.exists('sort.py')
        assert os.path.exists('utils.py')
        assert os.path.exists('config.py')
        assert os.path.exists('requirements.txt')
        assert os.path.exists('README.md')
