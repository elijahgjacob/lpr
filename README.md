# ALPR System - Automatic License Plate Recognition

A comprehensive Automatic License Plate Recognition system using YOLOv11, Roboflow, SORT tracking, and PaddleOCR, with Supabase integration for data storage.

## Features

- **Vehicle Detection**: Detect cars, trucks, buses, and motorbikes using YOLOv11
- **Vehicle Tracking**: Track vehicles across frames using SORT algorithm
- **License Plate Detection**: Detect license plates using Roboflow's pre-trained models
- **OCR**: Extract text from license plates using PaddleOCR
- **Data Storage**: Store detection results in Supabase for analytics
- **Visualization**: Real-time video visualization with annotations
- **Export**: Save annotated videos and CSV reports

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

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 4. Configure Environment

Edit `.env` file with your credentials:

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

```bash
# Download models and sample video
python download_resources.py --setup  # Interactive setup
python download_resources.py --all    # Download everything
```

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

## CLI Arguments

- `--video`: Input video file path (required)
- `--output`: Output CSV file path (default: results/detected_plates.csv)
- `--visualize`: Display video with annotations in real-time
- `--save-video`: Save annotated video (default: results/annotated_video.mp4)
- `--report`: Generate summary report (default: results/summary.txt)
- `--use-roboflow`: Force use of Roboflow API
- `--use-local`: Force use of local models

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
├── tests/                  # Test suite
├── models/                 # YOLO models
├── videos/                 # Input/output videos
└── results/                # CSV reports
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

The system stores the following data in Supabase:

### Tables

**test_runs**: Tracks each video processing run
- id (uuid, primary key)
- video_name (text)
- start_time (timestamp)
- end_time (timestamp)
- total_frames (integer)
- detection_method (text: 'roboflow' or 'local')
- created_at (timestamp)

**detections**: Individual license plate detections
- id (uuid, primary key)
- test_run_id (uuid, foreign key)
- frame_number (integer)
- vehicle_id (integer)
- plate_text (text)
- confidence (float)
- bbox_x1, bbox_y1, bbox_x2, bbox_y2 (float)
- created_at (timestamp)

**performance_metrics**: Performance statistics per run
- id (uuid, primary key)
- test_run_id (uuid, foreign key)
- total_vehicles (integer)
- total_plates_detected (integer)
- avg_confidence (float)
- processing_fps (float)
- created_at (timestamp)

## Troubleshooting

### Roboflow API Issues

- **Invalid API Key**: Verify your API key in `.env` file
- **Rate Limiting**: Free tier has API call limits; consider using local models
- **Project Not Found**: Check workspace and project names

### Supabase Issues

- **Connection Error**: Verify SUPABASE_URL and SUPABASE_KEY
- **Permission Denied**: Ensure anon key has proper table permissions
- **Table Not Found**: Run the database schema setup scripts

### CUDA/GPU Issues

- **CUDA not available**: System will automatically fall back to CPU
- **Out of Memory**: Reduce batch size or use smaller model

### Model Download Failures

- **Network Issues**: Check internet connection
- **Disk Space**: Ensure sufficient disk space for models (~100MB+)

## Performance Tips

- Use GPU for faster processing (10-20x speedup)
- Roboflow API is slower but requires no local storage
- Local models are faster but require more disk space
- Disable visualization for faster processing
- Use lower resolution videos for real-time processing

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Attribution

- YOLO models: [Ultralytics](https://github.com/ultralytics/ultralytics)
- License plate detection: [Roboflow Universe](https://universe.roboflow.com/)
- SORT tracking: [Alex Bewley](https://github.com/abewley/sort)
- OCR: [EasyOCR](https://github.com/JaidedAI/EasyOCR)

## Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review Roboflow and Supabase documentation

