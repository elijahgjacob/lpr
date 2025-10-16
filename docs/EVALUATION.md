# ALPR System Evaluation Guide

## Overview

This document describes the evaluation methodology for measuring the performance of the ALPR system using scientifically rigorous metrics.

## Metrics

### ERR (End-to-End Read Rate)

**Definition**: The percentage of frames where the system correctly detected and read the license plate.

**Formula**: `ERR = (Correct Detections) / (Total Ground Truth Frames)`

**Interpretation**:
- `1.0` (100%) = Perfect performance
- `0.85` (85%) = Good performance
- `<0.70` (70%) = Needs improvement

**What it measures**: Overall system success rate from detection through OCR.

### CER (Character Error Rate)

**Definition**: The average character-level edit distance (Levenshtein distance) normalized by plate length.

**Formula**: `CER = (Edit Distance) / (Ground Truth Length)`

**Interpretation**:
- `0.0` (0%) = Perfect accuracy
- `0.10` (10%) = 1 character wrong per 10 characters
- `>0.20` (20%) = Poor accuracy

**What it measures**: Fine-grained OCR accuracy, catches single character errors.

### WER (Word/Plate Error Rate)

**Definition**: The percentage of plates that were not an exact match.

**Formula**: `WER = (Incorrect Plates) / (Total Plates)`

**Interpretation**:
- `0.0` (0%) = All plates perfect
- `0.15` (15%) = 15% of plates have at least one error
- `>0.30` (30%) = Concerning error rate

**What it measures**: Strict exact-match accuracy.

### Latency Metrics

**Metrics Tracked**:
- **Mean**: Average processing time per frame
- **Median** (P50): Middle value, less affected by outliers
- **P95**: 95th percentile, represents "worst case" for most frames
- **P99**: 99th percentile, represents worst case scenarios

**Target Values** (depends on hardware):
- With GPU: < 100ms mean, < 150ms P95
- With CPU: < 500ms mean, < 800ms P95

## Evaluation Workflow

### Step 1: Create Golden Dataset

Create a labeled dataset of ~80-100 frames:

```bash
# Interactive labeling
python scripts/create_golden_set.py \
  --video videos/sample_traffic.mp4 \
  --output data/golden/manifest.csv
```

See `scripts/README_GOLDEN_SET.md` for detailed instructions.

### Step 2: Run ALPR System

Process the video and generate predictions:

```bash
python main.py \
  --video videos/sample_traffic.mp4 \
  --output results/predictions.csv \
  --save-video results/annotated.mp4
```

### Step 3: Run Evaluation

Compare predictions against ground truth:

```bash
python evaluation/eval.py \
  --predictions results/predictions.csv \
  --ground-truth data/golden/manifest.csv \
  --output results/metrics/evaluation_results.json
```

**Output**:
```
EVALUATION RESULTS
======================================================================

Overall Performance:
  ERR (End-to-End Read Rate):  92.50%
  CER (Character Error Rate):  7.30%
  WER (Plate Error Rate):      8.50%
  Accuracy (Exact Match):      91.50%

Performance by Condition:
  day     : ERR=95.00%, CER=5.20%, n=60
  night   : ERR=87.50%, CER=11.80%, n=24
  dusk    : ERR=90.00%, CER=8.50%, n=16
======================================================================
```

### Step 4: Generate Visualizations

Create plots for analysis:

```bash
python evaluation/visualize.py \
  --results results/metrics/evaluation_results.json \
  --output-dir results/metrics/plots
```

**Generated plots**:
- `err_by_condition.png`: ERR across lighting conditions
- `accuracy_comparison.png`: ERR vs CER by condition
- `latency_stats.png`: Latency distribution

## Golden Dataset Format

The golden dataset CSV must have these columns:

| Column | Description | Required |
|--------|-------------|----------|
| `frame_id` | Frame number in video | Yes |
| `video_source` | Video filename | Yes |
| `plate_text_gt` | Ground truth plate text (UPPERCASE) | Yes |
| `light_condition` | day/night/dusk | Yes |
| `camera_id` | Camera identifier | Optional |
| `notes` | Additional notes | Optional |

**Example**:
```csv
frame_id,video_source,plate_text_gt,light_condition,camera_id
150,sample_traffic.mp4,ABC1234,day,cam_01
450,sample_traffic.mp4,XYZ5678,night,cam_01
780,sample_traffic.mp4,DEF9012,dusk,cam_01
```

## Predictions Format

The system outputs CSV with these columns:

| Column | Description |
|--------|-------------|
| `Frame` | Frame number |
| `Vehicle_ID` | Tracking ID |
| `Plate_Text` | Detected plate text |
| `Confidence` | OCR confidence (0-1) |
| `Timestamp` | Detection timestamp |

## Best Practices

### Labeling Guidelines

1. **Only label visible plates**: Skip frames where plate is blurred, occluded, or too small
2. **Use UPPERCASE**: Normalize all text to uppercase
3. **Include variety**: Different lighting, angles, distances
4. **Double-check**: Verify each label is correct
5. **Mark ambiguous**: Use notes field for unclear cases (O vs 0, I vs 1)

### Target Distribution

Aim for:
- 60-70% day conditions
- 20-30% night conditions
- 10-20% dusk/challenging conditions

### Sample Size

- **Minimum**: 50 labeled frames
- **Recommended**: 80-100 labeled frames
- **Comprehensive**: 200+ labeled frames

## Interpreting Results

### Good Performance

```
ERR:  > 90%
CER:  < 10%
WER:  < 15%
```

### Acceptable Performance

```
ERR:  80-90%
CER:  10-20%
WER:  15-25%
```

### Needs Improvement

```
ERR:  < 80%
CER:  > 20%
WER:  > 25%
```

## Troubleshooting

### Low ERR (< 80%)

**Possible causes**:
- Plate detector confidence threshold too high
- Poor video quality
- Extreme angles or occlusions

**Solutions**:
- Lower `PLATE_CONFIDENCE_THRESHOLD` in config
- Improve video quality/lighting
- Add preprocessing (CLAHE, normalization)

### High CER but Acceptable ERR

**Indicates**: OCR is finding plates but misreading characters

**Solutions**:
- Increase `OCR_CONFIDENCE_THRESHOLD`
- Add preprocessing for plate images
- Implement multi-frame voting
- Train better OCR model

### Day/Night Performance Delta > 20%

**Indicates**: System struggles with lighting variation

**Solutions**:
- Add CLAHE preprocessing
- Separate confidence thresholds for day/night
- Collect more night training data

## Integration with Experiments

Use evaluation metrics to compare experiments:

```bash
# Baseline
python main.py --video input.mp4 --output results/baseline.csv
python evaluation/eval.py --predictions results/baseline.csv --ground-truth data/golden/manifest.csv

# Experiment: Skip frames
python main.py --video input.mp4 --output results/skip5.csv --skip-frames 5
python evaluation/eval.py --predictions results/skip5.csv --ground-truth data/golden/manifest.csv
```

Compare ERR, CER, and latency to quantify trade-offs.

## Example Analysis

### Baseline Performance

```
ERR:  93.0%
CER:  6.5%
P95:  82 ms
FPS:  12
```

### After Skip-5 Optimization

```
ERR:  88.0%  (↓ 5%)
CER:  9.2%   (↑ 2.7%)
P95:  46 ms  (↓ 44%)
FPS:  28     (↑ 133%)
```

**Analysis**: Trading 5% accuracy for 2.3x speedup - acceptable for real-time applications.

## References

- **ERR**: Common metric in OCR evaluation
- **CER/WER**: Standard speech recognition metrics, adapted for text
- **Levenshtein Distance**: Edit distance algorithm for string comparison

## Next Steps

After establishing baseline metrics:

1. Run experiments with different configurations
2. Quantify trade-offs (accuracy vs speed)
3. Identify failure modes (lighting, angles, blur)
4. Implement improvements (preprocessing, voting)
5. Re-evaluate and measure gains

## Questions?

For issues or questions about evaluation:
- Check troubleshooting section above
- Review example workflows
- Open an issue on GitHub


