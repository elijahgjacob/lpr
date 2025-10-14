# ALPR System - Automatic License Plate Recognition

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

A comprehensive Automatic License Plate Recognition system using YOLOv11, Roboflow, SORT tracking, and PaddleOCR, with Supabase integration for data storage.

## Features

- **Vehicle Detection**: Detect cars, trucks, buses, and motorbikes using YOLOv11x
- **Vehicle Tracking**: Track vehicles across frames using SORT algorithm with Kalman filtering
- **License Plate Detection**: Dual-mode detection (Roboflow API or local YOLO model)
- **OCR**: Extract text from license plates using PaddleOCR (v1.1.0+)
- **Smart Caching**: Avoid redundant plate readings for tracked vehicles
- **Data Storage**: Store detection results in Supabase with batch uploads
- **Visualization**: Real-time video visualization with annotations and progress tracking
- **Export**: Save annotated videos, CSV reports, and summary statistics
- **Version Tracking**: All detections include timestamps and version information

## What's New in v1.1.0

🎉 **PaddleOCR Migration**: Switched from EasyOCR to PaddleOCR for better accuracy and performance:
- ✅ Improved recognition of US license plates
- ✅ Zero API costs (runs completely locally)
- ✅ Faster processing with optimized C++ backend
- ✅ GPU acceleration support when available

See [CHANGELOG.md](CHANGELOG.md) for full version history.

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Linux, macOS, or Windows
- **GPU**: Optional but recommended (CUDA for NVIDIA GPUs)
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Disk Space**: ~500MB for models and dependencies

## Quick Start

### 1. Roboflow Setup

1. Create a free account at [Roboflow](https://app.roboflow.com)
2. Get your API key from your account settings
3. Note the workspace and project details

### 2. Supabase Setup

1. Create a free account at [Supabase](https://supabase.com)
2. Create a new project
3. Get your project URL and anon key from Settings > API

### 3. Installation

```bash
# Clone the repository
git clone <repository-url>
cd lpr-1

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root with your credentials:

```bash
ROBOFLOW_API_KEY=your_api_key_here
ROBOFLOW_WORKSPACE=your_workspace
ROBOFLOW_PROJECT=your_project
ROBOFLOW_VERSION=1

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
ENABLE_SUPABASE=true
```

### 5. Download Resources

The `download_resources.py` script helps you set up models and test videos:

```bash
# Interactive setup wizard (recommended for first-time setup)
python download_resources.py --setup

# Download everything automatically
python download_resources.py --all

# Download specific components
python download_resources.py --models      # YOLO models only
python download_resources.py --video       # Sample video only
```

The script will:
- Check for required dependencies
- Download YOLOv11x model (~100MB) for vehicle detection
- Optionally download sample traffic video for testing
- Guide you through Roboflow configuration

## Usage

### Basic Usage

```bash
# Process a video file
python main.py --video path/to/video.mp4 --output results/plates.csv
```

### With Visualization

```bash
# Display video with annotations in real-time
python main.py --video path/to/video.mp4 --output results/plates.csv --visualize
```

### Save Annotated Video

```bash
# Save processed video with annotations
python main.py --video path/to/video.mp4 --output results/plates.csv --save-video --report
```

### Full Options

```bash
python main.py \
  --video path/to/video.mp4 \
  --output results/plates.csv \
  --visualize \
  --save-video \
  --report \
  --use-roboflow  # Force Roboflow API mode
```

### Common Workflows

**Quick test with sample video:**
```bash
# Process sample video with visualization
python main.py --video videos/sample_traffic.mp4 --output results/test.csv --visualize
```

**Production processing (headless):**
```bash
# Process without visualization for maximum speed
python main.py --video input.mp4 --output results/output.csv --save-video --report
```

**Process every 5th frame (faster, lower accuracy):**
```bash
python main.py --video input.mp4 --output results/output.csv --skip-frames 5
```

**Local-only mode (no Roboflow or Supabase):**
```bash
python main.py --video input.mp4 --output results/output.csv --use-local --no-supabase
```

## CLI Arguments

- `--video`: Input video file path (required)
- `--output`: Output CSV file path (default: results/detected_plates.csv)
- `--visualize`: Display video with annotations in real-time
- `--save-video`: Save annotated video (default: results/annotated_video.mp4)
- `--report`: Generate summary report (default: results/summary.txt)
- `--use-roboflow`: Force use of Roboflow API
- `--use-local`: Force use of local models
- `--skip-frames`: Process every Nth frame (0 = process all frames)
- `--max-frames`: Maximum number of frames to process
- `--vehicle-model`: Path to vehicle detection model (overrides config)
- `--plate-model`: Path to plate detection model (overrides config)
- `--no-supabase`: Disable Supabase storage

## Output Format

### CSV Output

The system generates CSV files with 15 columns:

| Column | Description |
|--------|-------------|
| Frame | Frame number where detection occurred |
| Vehicle_ID | Unique tracking ID assigned by SORT |
| Plate_Text | Recognized license plate text |
| Confidence | OCR confidence score (0-1) |
| Vehicle_X1, Vehicle_Y1, Vehicle_X2, Vehicle_Y2 | Vehicle bounding box coordinates |
| Plate_X1, Plate_Y1, Plate_X2, Plate_Y2 | License plate bounding box coordinates |
| Timestamp | ISO 8601 timestamp of detection |
| Version | ALPR system version |

### Summary Report

When using `--report`, a text file is generated with:
- Total frames processed
- Total detections
- Unique vehicles tracked
- Unique license plates detected
- Average confidence score
- Detection rate
- Processing time and FPS

## Project Structure

```
lpr-1/
├── main.py                  # CLI interface
├── alpr_system.py          # Core ALPR class
├── sort.py                 # SORT tracking algorithm
├── utils.py                # Helper functions
├── config.py               # Configuration
├── download_resources.py   # Resource downloader
├── requirements.txt        # Dependencies
├── supabase_schema.sql     # Database schema
├── pytest.ini              # Test configuration
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md         # Development guidelines
├── docs/                   # Documentation
│   ├── CONFIGURATION_V1.md # Configuration guide
│   └── MIGRATION_v1.0.md   # Migration guide
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test fixtures
├── models/                 # YOLO models
│   └── yolo11x.pt          # Vehicle detection model
├── videos/                 # Input videos
└── results/                # Output (CSV, videos, reports)
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test module
pytest tests/unit/test_utils.py -v
```

## Supabase Database Schema

The system stores detection results in Supabase for analytics and historical tracking.

### Setup

1. Run the schema in your Supabase SQL editor:
   ```bash
   # Copy contents of supabase_schema.sql to Supabase SQL Editor
   ```

2. The schema includes:
   - Tables for test runs, detections, and performance metrics
   - Indexes for fast queries
   - Views for analytics
   - Helper functions for statistics

### Tables

**test_runs**: Tracks each video processing run
- `id` (uuid, primary key)
- `video_name` (text) - Name of the video file processed
- `start_time` (timestamp) - When processing started
- `end_time` (timestamp) - When processing completed
- `total_frames` (integer) - Total frames processed
- `detection_method` (text) - 'roboflow' or 'local'
- `created_at` (timestamp)

**detections**: Individual license plate detections
- `id` (uuid, primary key)
- `test_run_id` (uuid, foreign key) - Links to test_runs
- `frame_number` (integer) - Frame where detection occurred
- `vehicle_id` (integer) - SORT tracking ID
- `plate_text` (text) - Recognized license plate
- `confidence` (real) - OCR confidence (0-1)
- `bbox_x1, bbox_y1, bbox_x2, bbox_y2` (real) - Bounding box
- `timestamp` (timestamp) - Detection timestamp
- `version` (text) - ALPR system version
- `created_at` (timestamp)

**performance_metrics**: Performance statistics per run
- `id` (uuid, primary key)
- `test_run_id` (uuid, foreign key)
- `total_vehicles` (integer) - Unique vehicles detected
- `total_plates_detected` (integer) - Total plates detected
- `avg_confidence` (real) - Average OCR confidence
- `processing_fps` (real) - Processing speed
- `created_at` (timestamp)

### Views

**test_run_summary**: Aggregated statistics for each test run
**vehicle_tracking**: Vehicle tracking info with first/last frames

### Batch Upload Feature

Detections are queued in memory during processing and uploaded in a single batch transaction at the end. This improves performance and reduces API calls.

## Troubleshooting

### Installation Issues

**PaddleOCR/PaddlePaddle installation fails:**
```bash
# Try installing PaddlePaddle first
pip install paddlepaddle-gpu  # For GPU support
# or
pip install paddlepaddle      # For CPU only

# Then install PaddleOCR
pip install paddleocr
```

**OpenCV import errors:**
```bash
pip install opencv-python --upgrade
```

### Roboflow API Issues

- **Invalid API Key**: Verify your API key in `.env` file
- **Rate Limiting**: Free tier has API call limits; use `--use-local` to bypass
- **Project Not Found**: Check workspace and project names match your Roboflow account
- **Network Timeout**: Roboflow API requires internet; use local models for offline processing

### Supabase Issues

- **Connection Error**: Verify SUPABASE_URL and SUPABASE_KEY in `.env`
- **Permission Denied**: Ensure anon key has INSERT/SELECT permissions on tables
- **Table Not Found**: Run `supabase_schema.sql` in Supabase SQL Editor
- **Batch Upload Fails**: Check Supabase logs; may need to reduce batch size

### CUDA/GPU Issues

- **CUDA not available**: System will automatically fall back to CPU (slower but works)
- **Out of Memory**: GPU memory exhausted; process smaller videos or use CPU
- **Wrong CUDA version**: Ensure PyTorch CUDA version matches your GPU drivers

### Performance Issues

- **Slow processing**: 
  - Use `--skip-frames N` to process every Nth frame
  - Disable `--visualize` for faster processing
  - Use GPU if available (10-20x speedup)
  - Use local models instead of Roboflow API
- **High memory usage**: 
  - Process shorter video segments
  - Disable Supabase if not needed (`--no-supabase`)

### OCR Accuracy Issues

- **Poor plate recognition**:
  - Ensure good video quality and lighting
  - License plates should be clearly visible
  - Adjust `PLATE_CONFIDENCE_THRESHOLD` in config
  - Try preprocessing video (brightness/contrast adjustment)
- **False positives**:
  - Increase `OCR_CONFIDENCE_THRESHOLD`
  - Adjust `MIN_PLATE_LENGTH` and `MAX_PLATE_LENGTH`

## Performance Tips

- **Use GPU**: 10-20x speedup with CUDA-enabled GPU
- **Skip frames**: Use `--skip-frames` for faster processing (trade-off with accuracy)
- **Disable visualization**: Remove `--visualize` flag for headless processing
- **Local models**: Faster than Roboflow API but requires disk space
- **Batch processing**: Process multiple videos sequentially for efficiency

## FAQ

### General Questions

**Q: Do I need Roboflow for plate detection?**  
A: No, you can use local YOLO models with `--use-local`. Roboflow is optional but provides pre-trained models.

**Q: Can I run this without Supabase?**  
A: Yes! Use `--no-supabase` flag or set `ENABLE_SUPABASE=false` in `.env`. CSV output works independently.

**Q: What video formats are supported?**  
A: Any format supported by OpenCV (MP4, AVI, MOV, etc.). MP4 is recommended.

**Q: Can I process live camera streams?**  
A: Currently only pre-recorded videos are supported. Live streaming is planned for future versions.

### Technical Questions

**Q: Why is PaddleOCR better than EasyOCR?**  
A: PaddleOCR offers better accuracy for US plates, faster processing, and runs completely offline with no API costs.

**Q: How accurate is the system?**  
A: Accuracy depends on video quality, lighting, and plate visibility. Typically 85-95% for clear, well-lit plates.

**Q: Can I train my own plate detection model?**  
A: Yes! You can train a custom YOLO model and specify it with `--plate-model path/to/model.pt`.

**Q: Does it work with non-US license plates?**  
A: The OCR is optimized for English alphanumeric text. May work with other formats but not guaranteed.

**Q: What's the processing speed?**  
A: With GPU: 15-30 FPS. With CPU: 2-5 FPS. Depends on hardware and video resolution.

### Troubleshooting

**Q: Why are some plates not detected?**  
A: Common reasons: poor video quality, plate too small, extreme angles, motion blur, or occlusion.

**Q: Can I improve detection accuracy?**  
A: Yes! Adjust confidence thresholds in `.env`, use higher quality videos, ensure good lighting, and use GPU processing.

**Q: Why is processing slow?**  
A: Use GPU, skip frames, disable visualization, or use local models instead of Roboflow API.

## Configuration

The system supports extensive configuration via environment variables in `.env`:

### Detection Thresholds
- `VEHICLE_CONFIDENCE_THRESHOLD` - Minimum confidence for vehicle detection (default: 0.5)
- `PLATE_CONFIDENCE_THRESHOLD` - Minimum confidence for plate detection (default: 0.3)
- `OCR_CONFIDENCE_THRESHOLD` - Minimum confidence for OCR results (default: 0.5)

### SORT Tracking
- `SORT_MAX_AGE` - Max frames to keep alive a track without detections (default: 30)
- `SORT_MIN_HITS` - Min detections before considering a track valid (default: 3)
- `SORT_IOU_THRESHOLD` - IoU threshold for matching detections (default: 0.3)

### OCR Settings
- `MIN_PLATE_LENGTH` - Minimum valid plate length (default: 5)
- `MAX_PLATE_LENGTH` - Maximum valid plate length (default: 10)

### Processing
- `FRAME_SKIP` - Process every Nth frame, 0 = all frames (default: 0)

See [docs/CONFIGURATION_V1.md](docs/CONFIGURATION_V1.md) for detailed configuration guide.

## Documentation

- **[CHANGELOG.md](CHANGELOG.md)**: Version history and release notes
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Development guidelines and workflow
- **[docs/CONFIGURATION_V1.md](docs/CONFIGURATION_V1.md)**: Configuration guide
- **[docs/MIGRATION_v1.0.md](docs/MIGRATION_v1.0.md)**: Migration guide from older versions
- **[supabase_schema.sql](supabase_schema.sql)**: Complete database schema with examples

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Code style and standards
- Testing requirements
- Pull request process
- Development workflow

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Attribution

- YOLO models: [Ultralytics](https://github.com/ultralytics/ultralytics)
- License plate detection: [Roboflow Universe](https://universe.roboflow.com/)
- SORT tracking: [Alex Bewley](https://github.com/abewley/sort)
- OCR: [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

## Support

For issues and questions:
- 📖 Check the [FAQ](#faq) section
- 🔧 Review [Troubleshooting](#troubleshooting) guide
- 📝 Read the documentation in `docs/` directory
- 🐛 Open an issue on GitHub for bugs
- 💡 Review [Roboflow](https://docs.roboflow.com/) and [Supabase](https://supabase.com/docs) documentation

## Acknowledgments

Special thanks to:
- The open-source computer vision community
- Ultralytics for YOLO models
- Roboflow for license plate detection models
- PaddlePaddle team for PaddleOCR
- Contributors and users of this project

