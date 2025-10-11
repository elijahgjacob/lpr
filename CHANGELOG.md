# Changelog

All notable changes to the ALPR System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-11

### Added

#### Core Features
- **Vehicle Detection**: YOLOv11x-based vehicle detection for cars, trucks, buses, and motorbikes
- **Vehicle Tracking**: SORT algorithm implementation with Kalman filtering for consistent vehicle tracking
- **License Plate Detection**: Dual-mode plate detection (Roboflow API or local YOLO model)
- **OCR**: EasyOCR integration for license plate text recognition with validation
- **Result Caching**: Smart caching to avoid redundant plate readings for tracked vehicles

#### Integrations
- **Roboflow Integration**: 
  - API-based license plate detection
  - Model download from Roboflow Universe
  - Configurable workspace, project, and version
- **Supabase Integration**:
  - Store test runs with metadata
  - Track individual detections
  - Performance metrics storage
  - Database schema with views and functions

#### CLI Interface (`main.py`)
- Comprehensive argument parsing
- Video input processing
- Multiple output formats (CSV, annotated video, summary report)
- Real-time visualization option
- Progress tracking and statistics
- Configurable frame skipping and max frames

#### Configuration System (`config.py`)
- Environment variable loading via `python-dotenv`
- Comprehensive validation
- Support for Roboflow and Supabase settings
- Configurable thresholds and parameters
- Helper functions for config access

#### Utilities (`utils.py`)
- OCR text formatting and validation
- Image processing (cropping, preprocessing)
- Visualization (bounding boxes, annotations, frame info)
- Reporting (summary generation, CSV export)
- Roboflow prediction conversion
- Supabase configuration validation

#### Resource Management
- **Download Script** (`download_resources.py`):
  - Interactive Roboflow setup wizard
  - Model download automation
  - Sample video download
  - Dependency checking
- **.env Configuration**: Template for API keys and settings

#### Documentation
- Comprehensive README with:
  - Quick start guide
  - Installation instructions
  - Usage examples for all features
  - Supabase database schema
  - Troubleshooting section
- **LICENSE**: MIT License with third-party attributions
- **CONTRIBUTING.md**: Development guidelines and workflow
- **Supabase Schema** (`supabase_schema.sql`):
  - Complete database schema
  - Views for analytics
  - Helper functions
  - Sample queries

#### Testing
- Comprehensive unit tests for all modules
- Mocked external dependencies (YOLO, Roboflow, Supabase)
- Test coverage > 80%
- Integration test framework
- pytest configuration

#### Development Infrastructure
- `.gitignore`: Comprehensive ignore rules
- `pytest.ini`: Test configuration
- `.coveragerc`: Coverage settings
- `.env.example`: Configuration template
- Project directory structure

### Technical Details

#### Architecture
- Modular design with clear separation of concerns
- Dependency injection for flexibility
- Mock-friendly architecture for testing
- Type hints throughout codebase

#### Performance
- Frame-by-frame processing with configurable skip
- GPU acceleration support (CUDA)
- Smart caching to reduce redundant computations
- Efficient tracking with SORT algorithm

#### Models
- **Vehicle Detection**: YOLOv11x (auto-download from Ultralytics)
- **License Plate Detection**: 
  - Roboflow API (license-plate-recognition-rxg4e/4)
  - Local YOLO model support
- **OCR**: EasyOCR with English language support

#### Git Workflow
- Proper branching strategy (GitHub Flow)
- Conventional commit messages
- Feature branches with PRs
- Clean commit history

### Known Limitations
- OCR accuracy varies with lighting and plate condition
- Tracking may struggle with long occlusions
- Requires good quality video for best results
- Roboflow API has rate limits on free tier

### Future Enhancements
- Multi-language OCR support
- Real-time video streaming
- Web interface
- Advanced analytics dashboard
- Model training scripts
- DeepSORT for better tracking
- GPU batch processing optimization

---

## [Unreleased]

### Planned
- CI/CD pipeline with GitHub Actions
- Docker containerization
- REST API endpoint
- Real-time alerts system
- Multi-camera support
- Historical data analysis tools

---

## Version History

- **v1.0.0** (2025-01-11): Initial release with full ALPR pipeline, Roboflow & Supabase integration

