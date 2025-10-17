# ALPR Model Comparison System

This system allows you to compare different license plate detection models (local YOLO and RunPod YOLO) against the golden dataset to evaluate performance, accuracy, and speed.

## Features

- **Multiple Model Support**: Compare local YOLO models and RunPod cloud-based YOLO models
- **Comprehensive Metrics**: Exact match rate, partial match rate, detection rate, confidence scores, and inference times
- **Side-by-Side Reports**: Generate markdown reports with detailed comparisons
- **Flexible Configuration**: JSON-based model registry for easy model management
- **CLI Interface**: Command-line tool for running comparisons

## Quick Start

### 1. Setup RunPod (Optional)

If you want to use RunPod models:

```bash
# Set your RunPod API key
export RUNPOD_API_KEY="your-runpod-api-key-here"

# Update model registry with your RunPod endpoints
# Edit model_registry.json and update the runpod_endpoint URLs
```

### 2. Setup Local Models (Optional)

If you want to use local YOLO models:

```bash
# Download YOLO model files to models/ directory
mkdir -p models/
# Copy your .pt model files to models/
```

### 3. Run Comparison

```bash
# Compare all models in registry
python compare_models.py --all

# Compare specific models
python compare_models.py --models yolo_baseline runpod_yolo11n runpod_yolo11x

# Use custom registry file
python compare_models.py --registry my_models.json --all

# Specify custom paths
python compare_models.py --all \
  --ground-truth my_labels.csv \
  --frames-dir my_frames/ \
  --output-dir my_results/
```

## Model Registry

The `model_registry.json` file defines all available models for comparison:

```json
{
  "models": [
    {
      "id": "yolo_baseline",
      "name": "YOLO Baseline",
      "type": "local_yolo",
      "config": {
        "model_path": "models/license_plate_detector.pt",
        "confidence_threshold": 0.25
      }
    },
    {
      "id": "runpod_yolo11n",
      "name": "RunPod YOLO11n Fast",
      "type": "runpod_yolo",
      "config": {
        "runpod_endpoint": "https://api.runpod.ai/v2/your-endpoint-id/run",
        "model_path": "/workspace/models/yolo11n.pt",
        "confidence_threshold": 0.25,
        "timeout": 15
      }
    }
  ]
}
```

## Model Types

### Local YOLO Models (`local_yolo`)
- Run YOLO models locally on your machine
- Requires local `.pt` model files
- Faster for repeated testing (no network latency)
- Limited by local hardware capabilities

**Configuration:**
- `model_path`: Path to YOLO model file
- `confidence_threshold`: Detection confidence threshold (0.0-1.0)
- `device`: Optional device specification (cpu, cuda, mps)

### RunPod YOLO Models (`runpod_yolo`)
- Run YOLO models on RunPod cloud infrastructure
- Requires RunPod API key and configured endpoints
- Can leverage powerful GPU instances
- Network latency affects inference times

**Configuration:**
- `runpod_endpoint`: RunPod API endpoint URL
- `model_path`: Path to model on RunPod instance
- `confidence_threshold`: Detection confidence threshold (0.0-1.0)
- `timeout`: Request timeout in seconds
- `api_key`: Optional API key (uses RUNPOD_API_KEY env var if not provided)

## Output Reports

The system generates comprehensive markdown reports in `results/model_comparison/`:

### Summary Table
Side-by-side comparison of all models with key metrics:

| Model | Type | Exact Match | Partial Match | No Match | Detection Rate | Avg Confidence | Avg Time (ms) |
|-------|------|-------------|---------------|----------|----------------|----------------|---------------|
| YOLO Baseline | local_yolo | 15.2% | 45.7% | 39.1% | 60.9% | 0.42 | 89.3 |
| RunPod YOLO11n | runpod_yolo | 18.6% | 52.1% | 29.3% | 70.7% | 0.38 | 245.7 |

### Best Models Section
Highlights the best-performing model for each metric:
- **Exact Match Rate**: RunPod YOLO11x (22.1%)
- **Detection Rate**: RunPod YOLO11x (78.3%)
- **Speed**: YOLO Baseline (89.3ms)
- **Confidence**: RunPod YOLO11l (0.45)

### Detailed Results
Individual model performance breakdowns with full configuration details.

## Metrics Explained

- **Exact Match Rate**: Percentage of predictions that exactly match ground truth
- **Partial Match Rate**: Percentage with significant similarity (>50% character match)
- **No Match Rate**: Percentage with no meaningful similarity
- **Detection Rate**: Percentage of successful detections (exact + partial)
- **Average Confidence**: Mean confidence score across all detections
- **Average Inference Time**: Mean time per frame in milliseconds

## CLI Options

```
python compare_models.py [OPTIONS]

Options:
  --registry PATH          Path to model registry file (default: model_registry.json)
  --models ID [ID ...]     Specific model IDs to compare
  --all                    Compare all models in registry
  --ground-truth PATH      Path to ground truth CSV (default: labeling_interface/detailed_labels_export.csv)
  --frames-dir PATH        Directory containing frame images (default: data/golden/frames)
  --output-dir PATH        Output directory for reports (default: results/model_comparison)
```

## Examples

### Compare All Models
```bash
python compare_models.py --all
```

### Compare Specific YOLO Variants
```bash
python compare_models.py --models runpod_yolo11n runpod_yolo11s runpod_yolo11m runpod_yolo11l runpod_yolo11x
```

### Compare Local vs Cloud
```bash
python compare_models.py --models yolo_baseline runpod_yolo11n runpod_yolo11x
```

### Custom Configuration
```bash
python compare_models.py \
  --registry custom_models.json \
  --models my_custom_model \
  --ground-truth my_dataset/labels.csv \
  --frames-dir my_dataset/frames/ \
  --output-dir my_results/
```

## Troubleshooting

### RunPod Issues
- **API Key**: Ensure `RUNPOD_API_KEY` environment variable is set
- **Endpoints**: Verify RunPod endpoint URLs are correct and accessible
- **Models**: Ensure YOLO models exist at specified paths on RunPod instances
- **Timeout**: Increase timeout values for slower models

### Local Model Issues
- **File Paths**: Verify model files exist at specified paths
- **Permissions**: Ensure read permissions for model files
- **Dependencies**: Install required packages (`ultralytics`, `torch`)

### General Issues
- **Memory**: Large models may require significant RAM/VRAM
- **Network**: RunPod requires stable internet connection
- **Ground Truth**: Ensure ground truth CSV has correct format and frame IDs

## Adding New Models

1. **Edit `model_registry.json`**:
   ```json
   {
     "id": "my_new_model",
     "name": "My New Model",
     "type": "local_yolo",  // or "runpod_yolo"
     "config": {
       "model_path": "path/to/model.pt",
       "confidence_threshold": 0.3
     }
   }
   ```

2. **Test the model**:
   ```bash
   python compare_models.py --models my_new_model
   ```

3. **Compare with existing models**:
   ```bash
   python compare_models.py --models my_new_model yolo_baseline
   ```

## Performance Tips

- **Local Models**: Use SSD storage and sufficient RAM for best performance
- **RunPod Models**: Choose appropriate GPU instances for your model sizes
- **Batch Processing**: Run comparisons during off-peak hours for RunPod
- **Caching**: Results are cached in output directory for faster re-runs

## Integration with Existing System

The model comparison system integrates seamlessly with the existing ALPR system:

```python
from model_configs import LocalYOLODetectorConfig, RunPodYOLODetectorConfig
from alpr_system import ALPRSystem

# Use local model
local_config = LocalYOLODetectorConfig(
    model_name="My Model",
    model_path="models/my_model.pt",
    confidence_threshold=0.3
)
alpr = ALPRSystem(plate_detector_config=local_config)

# Use RunPod model
runpod_config = RunPodYOLODetectorConfig(
    model_name="Cloud Model",
    runpod_endpoint="https://api.runpod.ai/v2/endpoint/run",
    model_path="/workspace/models/model.pt"
)
alpr = ALPRSystem(plate_detector_config=runpod_config)
```
