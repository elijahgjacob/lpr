# Configuration Guide - Version 1.0.0

## Overview

This document covers the configuration for ALPR System v1.0.0, which includes enhanced tracking with timestamp and version fields, batch Supabase uploads, and real-time progress monitoring.

---

## 🆕 What's New in v1.0.0

### Enhanced Data Tracking
- **Timestamp Field**: Every detection includes an ISO 8601 timestamp
- **Version Field**: Release version tracked for every detection
- **Batch Uploads**: Supabase detections uploaded in bulk at end of run

### Improved User Experience
- **Real-time Progress Bar**: Visual progress indicator with █ and ░
- **ETA Calculation**: Estimated time remaining
- **Live Statistics**: FPS, vehicles, plates, and detection counts
- **Performance Summary**: Pre-upload statistics display

---

## 📊 Output Format

### CSV Output Format

**New columns added in v1.0.0:**
- `Timestamp`: ISO 8601 format timestamp (e.g., `2025-10-11T18:30:45.123456`)
- `Version`: Release version (e.g., `1.0.0`)

**Complete CSV Schema:**

```csv
Frame,Vehicle_ID,Plate_Text,Confidence,Vehicle_X1,Vehicle_Y1,Vehicle_X2,Vehicle_Y2,Plate_X1,Plate_Y1,Plate_X2,Plate_Y2,Timestamp,Version
```

**Example:**
```csv
Frame,Vehicle_ID,Plate_Text,Confidence,Vehicle_X1,Vehicle_Y1,Vehicle_X2,Vehicle_Y2,Plate_X1,Plate_Y1,Plate_X2,Plate_Y2,Timestamp,Version
15,4,ABC123,0.8543,2221.79,901.07,2670.00,1286.16,2372.0,1096.0,2485.0,1131.0,2025-10-11T18:30:45.123456,1.0.0
16,4,ABC123,0.8543,2222.12,902.30,2673.21,1288.36,2372.0,1096.0,2485.0,1131.0,2025-10-11T18:30:45.223456,1.0.0
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `Frame` | Integer | Frame number in video |
| `Vehicle_ID` | Integer | Unique ID assigned by SORT tracker |
| `Plate_Text` | String | OCR-extracted license plate text |
| `Confidence` | Float | OCR confidence score (0-1) |
| `Vehicle_X1`, `Vehicle_Y1` | Float | Top-left corner of vehicle bbox |
| `Vehicle_X2`, `Vehicle_Y2` | Float | Bottom-right corner of vehicle bbox |
| `Plate_X1`, `Plate_Y1` | Float | Top-left corner of plate bbox |
| `Plate_X2`, `Plate_Y2` | Float | Bottom-right corner of plate bbox |
| `Timestamp` | String | ISO 8601 timestamp of detection |
| `Version` | String | ALPR system version |

---

## 🗄️ Supabase Configuration

### Schema Updates for v1.0.0

The `detections` table requires two new columns:

```sql
-- Add timestamp column
ALTER TABLE detections 
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ DEFAULT NOW();

-- Add version column
ALTER TABLE detections 
ADD COLUMN IF NOT EXISTS version VARCHAR(20) DEFAULT '1.0.0';

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp);
CREATE INDEX IF NOT EXISTS idx_detections_version ON detections(version);
```

### Complete Detections Table Schema

```sql
CREATE TABLE IF NOT EXISTS detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_run_id UUID REFERENCES test_runs(id) ON DELETE CASCADE,
    frame_number INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    plate_text VARCHAR(20),
    confidence FLOAT,
    bbox_x1 FLOAT,
    bbox_y1 FLOAT,
    bbox_x2 FLOAT,
    bbox_y2 FLOAT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    version VARCHAR(20) DEFAULT '1.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_detections_test_run ON detections(test_run_id);
CREATE INDEX idx_detections_vehicle ON detections(vehicle_id);
CREATE INDEX idx_detections_timestamp ON detections(timestamp);
CREATE INDEX idx_detections_version ON detections(version);
```

### Batch Upload Behavior

**v1.0.0 Change**: Detections are now uploaded in a **single batch** at the end of processing instead of individually.

**Benefits:**
- ⚡ **Faster Processing**: No API overhead during video processing
- 📊 **Better Performance**: Reduced network calls
- 💾 **Memory Efficient**: Detections queued in memory
- 🔒 **Atomic**: All detections uploaded together

**Configuration:**
```python
# Batch uploads happen automatically
# Control via enable_supabase parameter
alpr = ALPRSystem(enable_supabase=True)  # Default: uses config.ENABLE_SUPABASE

# At end of processing:
alpr.bulk_upload_detections()  # Called automatically in main.py
```

---

## ⚙️ Environment Configuration

### .env File

```bash
# Roboflow Configuration
ROBOFLOW_API_KEY=your_api_key_here
ROBOFLOW_WORKSPACE=your_workspace_name
ROBOFLOW_PROJECT=your_project_name
ROBOFLOW_VERSION=4
USE_ROBOFLOW_API=true

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
ENABLE_SUPABASE=true

# Optional: Local Model Paths
VEHICLE_MODEL_PATH=models/yolo11x.pt
PLATE_MODEL_PATH=models/license_plate_detector.pt
```

### Configuration Priority

1. **Environment Variables** (`.env` file) - Highest priority
2. **config.py** defaults - Fallback
3. **Function parameters** - Override at runtime

---

## 🚀 Usage Examples

### Basic Usage with All Features

```bash
python main.py \
  --video input_video.mp4 \
  --output results/detections.csv \
  --save-video results/annotated.mp4 \
  --report results/summary.txt \
  --visualize
```

### High-Performance Processing (0.5 FPS)

```bash
# Process every 60th frame (0.5 FPS for 30fps video)
python main.py \
  --video input_video.mp4 \
  --output results/detections.csv \
  --skip-frames 60 \
  --save-video \
  --report
```

### Process with Supabase Only (No Video Output)

```bash
python main.py \
  --video input_video.mp4 \
  --output results/detections.csv \
  --skip-frames 30
```

### Disable Supabase for Offline Processing

```bash
python main.py \
  --video input_video.mp4 \
  --output results/detections.csv \
  --no-supabase \
  --save-video
```

### Limited Frame Processing (Testing)

```bash
python main.py \
  --video input_video.mp4 \
  --output results/test.csv \
  --max-frames 100 \
  --visualize
```

---

## 📈 Progress Display

### Real-Time Progress Bar

```
Progress: |████████████████████░░░░░░░░░░░░░░░░░░░░| 50.5% Complete
Frame: 960/1920 | Speed: 2.3 FPS | ETA: 06:54 | Vehicles: 15 | Plates: 12 | Detections: 89
```

**Elements:**
- **Progress Bar**: Visual indicator (40 characters)
- **Percentage**: Completion percentage
- **Frame Counter**: Current/total frames
- **Speed**: Processing FPS
- **ETA**: Estimated time remaining (MM:SS)
- **Vehicles**: Unique vehicles tracked
- **Plates**: License plates successfully read
- **Detections**: Total detections recorded

**Updates**: Every frame for real-time feedback

---

## 🔧 Advanced Configuration

### Programmatic Usage

```python
from alpr_system import ALPRSystem

# Initialize with custom config
alpr = ALPRSystem(
    vehicle_model_path="models/yolo11x.pt",
    use_roboflow=True,
    enable_supabase=True
)

# Start tracking run
test_run_id = alpr.start_test_run("my_video.mp4")

# Process frames
for frame in video_frames:
    annotated, results = alpr.process_frame(frame, frame_num)
    
    # Results include timestamp and version
    for detection in results:
        print(f"Plate: {detection['plate_text']}")
        print(f"Time: {detection['timestamp']}")
        print(f"Version: {detection['version']}")

# Bulk upload at end
alpr.bulk_upload_detections()
alpr.end_test_run(total_frames)
```

### Custom Timestamp Format

By default, timestamps use ISO 8601 format. To customize:

```python
# In alpr_system.py
from datetime import datetime

# Modify _queue_detection method
"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
```

### Version Management

Version is automatically loaded from `__init__.py`:

```python
# __init__.py
__version__ = "1.0.0"

# To change version for a release:
# 1. Update __version__ in __init__.py
# 2. Commit with conventional commit message
# 3. Tag release: git tag v1.0.0
```

---

## 🔄 Migration from Pre-1.0

### CSV Format Migration

**Old Format (13 columns):**
```csv
Frame,Vehicle_ID,Plate_Text,Confidence,Vehicle_X1,Vehicle_Y1,Vehicle_X2,Vehicle_Y2,Plate_X1,Plate_Y1,Plate_X2,Plate_Y2
```

**New Format (15 columns):**
```csv
Frame,Vehicle_ID,Plate_Text,Confidence,Vehicle_X1,Vehicle_Y1,Vehicle_X2,Vehicle_Y2,Plate_X1,Plate_Y1,Plate_X2,Plate_Y2,Timestamp,Version
```

**Migration Script:**

```python
import csv
from datetime import datetime

# Read old CSV
with open('old_detections.csv', 'r') as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

# Write new CSV with added fields
with open('new_detections.csv', 'w', newline='') as outfile:
    fieldnames = list(rows[0].keys()) + ['Timestamp', 'Version']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in rows:
        row['Timestamp'] = datetime.now().isoformat()
        row['Version'] = 'migrated'
        writer.writerow(row)
```

### Supabase Schema Migration

```sql
-- Backup existing data
CREATE TABLE detections_backup AS SELECT * FROM detections;

-- Add new columns
ALTER TABLE detections 
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS version VARCHAR(20) DEFAULT '1.0.0';

-- Update existing rows
UPDATE detections 
SET timestamp = created_at,
    version = '0.9.0'
WHERE timestamp IS NULL;
```

---

## 🐛 Troubleshooting

### Issue: Missing Timestamp/Version in CSV

**Solution**: Ensure you're using v1.0.0+
```bash
python -c "from __init__ import __version__; print(__version__)"
```

### Issue: Supabase Upload Fails

**Cause**: Missing `timestamp` or `version` columns

**Solution**: Run schema migration:
```sql
ALTER TABLE detections 
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS version VARCHAR(20) DEFAULT '1.0.0';
```

### Issue: Progress Bar Not Displaying

**Cause**: Terminal doesn't support ANSI escape codes

**Solution**: Progress still works, just without cursor control
```bash
# Run with output redirect if needed
python main.py --video input.mp4 --output out.csv 2>&1 | tee log.txt
```

---

## 📚 Additional Resources

- **API Documentation**: See `docs/API.md`
- **Schema Reference**: See `supabase_schema.sql`
- **Migration Guide**: See `docs/MIGRATION.md`
- **Changelog**: See `CHANGELOG.md`

---

## 🎯 Best Practices

### Performance Optimization

1. **Use Frame Skipping**: `--skip-frames 60` for 0.5 FPS processing
2. **Disable Visualization**: Remove `--visualize` for faster processing
3. **Batch Processing**: Let detections queue in memory
4. **Monitor Progress**: Use ETA to estimate completion time

### Data Management

1. **Version Tracking**: Keep `__version__` updated
2. **Timestamp Accuracy**: Ensure system clock is synchronized
3. **Backup Data**: Export CSV before Supabase migration
4. **Index Strategy**: Add indexes for timestamp queries

### Production Deployment

1. **Environment Variables**: Use `.env` for configuration
2. **Error Handling**: Monitor bulk upload success
3. **Logging**: Redirect output to log files
4. **Resource Monitoring**: Track memory usage for large videos

---

**Version**: 1.0.0  
**Last Updated**: October 11, 2025  
**Maintainer**: ALPR System Contributors

