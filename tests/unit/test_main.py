"""Unit tests for main CLI interface."""
import pytest
from unittest.mock import Mock, patch, mock_open
import sys
from io import StringIO
import main


class TestArgumentParsing:
    """Test command-line argument parsing."""
    
    def test_parse_arguments_minimal(self):
        """Test parsing with only required arguments."""
        test_args = ['main.py', '--video', 'test.mp4']
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.video == 'test.mp4'
            assert args.output == 'results/detected_plates.csv'
            assert args.visualize is False
    
    def test_parse_arguments_all_options(self):
        """Test parsing with all options."""
        test_args = [
            'main.py',
            '--video', 'test.mp4',
            '--output', 'custom.csv',
            '--save-video', 'output.mp4',
            '--report', 'report.txt',
            '--visualize',
            '--use-roboflow',
        ]
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.video == 'test.mp4'
            assert args.output == 'custom.csv'
            assert args.save_video == 'output.mp4'
            assert args.report == 'report.txt'
            assert args.visualize is True
            assert args.use_roboflow is True
    
    def test_parse_arguments_use_local(self):
        """Test --use-local flag."""
        test_args = ['main.py', '--video', 'test.mp4', '--use-local']
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.use_local is True
    
    def test_parse_arguments_skip_frames(self):
        """Test --skip-frames option."""
        test_args = ['main.py', '--video', 'test.mp4', '--skip-frames', '5']
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.skip_frames == 5
    
    def test_parse_arguments_max_frames(self):
        """Test --max-frames option."""
        test_args = ['main.py', '--video', 'test.mp4', '--max-frames', '100']
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.max_frames == 100
    
    def test_parse_arguments_no_supabase(self):
        """Test --no-supabase flag."""
        test_args = ['main.py', '--video', 'test.mp4', '--no-supabase']
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.no_supabase is True


class TestArgumentValidation:
    """Test argument validation."""
    
    def test_validate_arguments_missing_video(self, tmp_path):
        """Test validation fails with non-existent video."""
        args = Mock()
        args.video = 'nonexistent.mp4'
        args.use_roboflow = False
        args.use_local = False
        args.skip_frames = 0
        
        with pytest.raises(SystemExit):
            main.validate_arguments(args)
    
    def test_validate_arguments_conflicting_flags(self, tmp_path):
        """Test validation fails with conflicting roboflow flags."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()
        
        args = Mock()
        args.video = str(video_file)
        args.use_roboflow = True
        args.use_local = True
        args.skip_frames = 0
        
        with pytest.raises(SystemExit):
            main.validate_arguments(args)
    
    def test_validate_arguments_negative_skip(self, tmp_path):
        """Test validation fails with negative skip frames."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()
        
        args = Mock()
        args.video = str(video_file)
        args.use_roboflow = False
        args.use_local = False
        args.skip_frames = -1
        
        with pytest.raises(SystemExit):
            main.validate_arguments(args)
    
    def test_validate_arguments_valid(self, tmp_path):
        """Test validation passes with valid arguments."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()
        
        args = Mock()
        args.video = str(video_file)
        args.use_roboflow = False
        args.use_local = False
        args.skip_frames = 0
        
        # Should not raise
        main.validate_arguments(args)


class TestOutputSetup:
    """Test output directory setup."""
    
    def test_setup_output_directories_csv(self, tmp_path):
        """Test CSV output directory creation."""
        output_csv = tmp_path / "results" / "output.csv"
        
        args = Mock()
        args.output = str(output_csv)
        args.save_video = None
        args.report = None
        
        main.setup_output_directories(args)
        
        assert output_csv.parent.exists()
    
    def test_setup_output_directories_all(self, tmp_path):
        """Test all output directories creation."""
        output_csv = tmp_path / "results" / "output.csv"
        output_video = tmp_path / "videos" / "output.mp4"
        output_report = tmp_path / "reports" / "report.txt"
        
        args = Mock()
        args.output = str(output_csv)
        args.save_video = str(output_video)
        args.report = str(output_report)
        
        main.setup_output_directories(args)
        
        assert output_csv.parent.exists()
        assert output_video.parent.exists()
        assert output_report.parent.exists()


class TestMainIntegration:
    """Integration tests for main function."""
    
    @patch('main.ALPRSystem')
    @patch('main.cv2.VideoCapture')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_basic_flow(self, mock_file, mock_video_cap, mock_alpr_class, tmp_path):
        """Test basic main function flow."""
        # Create temp video file
        video_file = tmp_path / "test.mp4"
        video_file.touch()
        output_csv = tmp_path / "output.csv"
        
        # Mock video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.side_effect = [(True, None), (False, None)]  # One frame then end
        mock_cap.get.side_effect = [100, 30.0, 640, 480]  # total_frames, fps, width, height
        mock_video_cap.return_value = mock_cap
        
        # Mock ALPR system
        mock_alpr = Mock()
        mock_alpr.process_frame.return_value = (None, [])
        mock_alpr.get_statistics.return_value = {
            'vehicles_detected': 0,
            'unique_vehicles': 0,
            'plates_detected': 0,
            'plates_read': 0,
        }
        mock_alpr_class.return_value = mock_alpr
        
        # Mock arguments
        test_args = [
            'main.py',
            '--video', str(video_file),
            '--output', str(output_csv),
        ]
        
        with patch.object(sys, 'argv', test_args):
            try:
                main.main()
            except SystemExit:
                pass  # Expected from cv2.VideoCapture
    
    @patch('main.ALPRSystem')
    def test_main_init_failure(self, mock_alpr_class, tmp_path):
        """Test main function handles ALPR init failure."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()
        output_csv = tmp_path / "output.csv"
        
        # Mock ALPR to raise error
        mock_alpr_class.side_effect = RuntimeError("Init failed")
        
        test_args = [
            'main.py',
            '--video', str(video_file),
            '--output', str(output_csv),
        ]
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main.main()


class TestDetectionMethodSelection:
    """Test detection method selection logic."""
    
    def test_use_roboflow_flag(self):
        """Test --use-roboflow sets correct flag."""
        test_args = ['main.py', '--video', 'test.mp4', '--use-roboflow']
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.use_roboflow is True
            assert args.use_local is False
    
    def test_use_local_flag(self):
        """Test --use-local sets correct flag."""
        test_args = ['main.py', '--video', 'test.mp4', '--use-local']
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.use_roboflow is False
            assert args.use_local is True
    
    def test_default_detection_method(self):
        """Test default detection method (from config)."""
        test_args = ['main.py', '--video', 'test.mp4']
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.use_roboflow is False
            assert args.use_local is False


class TestModelPathOverrides:
    """Test model path override options."""
    
    def test_vehicle_model_override(self):
        """Test --vehicle-model option."""
        test_args = [
            'main.py',
            '--video', 'test.mp4',
            '--vehicle-model', 'custom_vehicle.pt'
        ]
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.vehicle_model == 'custom_vehicle.pt'
    
    def test_plate_model_override(self):
        """Test --plate-model option."""
        test_args = [
            'main.py',
            '--video', 'test.mp4',
            '--plate-model', 'custom_plate.pt'
        ]
        with patch.object(sys, 'argv', test_args):
            args = main.parse_arguments()
            assert args.plate_model == 'custom_plate.pt'

