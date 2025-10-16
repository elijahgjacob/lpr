# Interview Prep Quick Start Guide

## What's Been Implemented

✅ **Golden Dataset Creation Tool** (`scripts/create_golden_set.py`)
- Interactive frame extraction and labeling
- Manual labeling support
- CSV template generation

✅ **Evaluation Framework** (`evaluation/`)
- ERR (End-to-End Read Rate) computation
- CER (Character Error Rate) computation
- WER (Word/Plate Error Rate) computation
- Latency statistics (mean, median, p95, p99)
- Performance by lighting condition

✅ **Visualization Module** (`evaluation/visualize.py`)
- ERR by condition plots
- Accuracy comparison charts
- Latency statistics visualization

✅ **Documentation** (`docs/EVALUATION.md`)
- Complete evaluation methodology
- Metric definitions
- Best practices
- Troubleshooting guide

## Your Next Steps (In Order)

### Tonight (Tuesday) - Ground Truth Creation

**Step 1**: Create your golden dataset (~1 hour)

```bash
# Option A: Interactive labeling
python scripts/create_golden_set.py \
  --video videos/sample_traffic.mp4 \
  --output data/golden/manifest.csv \
  --max-frames 100

# Option B: Extract frames, label manually later
python scripts/create_golden_set.py \
  --video videos/sample_traffic.mp4 \
  --extract-only \
  --max-frames 100
```

**Target**: 80-100 labeled frames with:
- 60-70% day
- 20-30% night  
- 10-20% dusk/challenging

**Step 2**: Run your ALPR system on the same video

```bash
python main.py \
  --video videos/sample_traffic.mp4 \
  --output results/baseline_predictions.csv \
  --save-video results/baseline_annotated.mp4 \
  --report results/baseline_summary.txt
```

**Step 3**: Evaluate performance

```bash
python evaluation/eval.py \
  --predictions results/baseline_predictions.csv \
  --ground-truth data/golden/manifest.csv \
  --output results/metrics/baseline_eval.json
```

**Step 4**: Generate visualizations

```bash
python evaluation/visualize.py \
  --results results/metrics/baseline_eval.json \
  --output-dir results/metrics/plots
```

**Deliverable**: Know your baseline numbers (ERR, CER, latency)

---

### Wednesday - Experiments & Trade-offs

**Run 2-3 experiments**:

**Experiment 1: Baseline (already done)**
```bash
# You did this yesterday
```

**Experiment 2: Skip Frames (Speed vs Accuracy)**
```bash
python main.py \
  --video videos/sample_traffic.mp4 \
  --output results/skip5_predictions.csv \
  --skip-frames 5

python evaluation/eval.py \
  --predictions results/skip5_predictions.csv \
  --ground-truth data/golden/manifest.csv \
  --output results/metrics/skip5_eval.json
```

**Experiment 3: Confidence Threshold Sweep**
```bash
# Edit .env: PLATE_CONFIDENCE_THRESHOLD=0.5
python main.py --video videos/sample_traffic.mp4 --output results/highconf_predictions.csv

python evaluation/eval.py \
  --predictions results/highconf_predictions.csv \
  --ground-truth data/golden/manifest.csv \
  --output results/metrics/highconf_eval.json
```

**Create Trade-off Table**:

Open a spreadsheet and create:

| Variant | ERR | CER | P95 (ms) | FPS | Notes |
|---------|-----|-----|----------|-----|-------|
| Baseline | 0.93 | 0.07 | 82 | 12 | Full accuracy |
| Skip-5 | 0.88 | 0.10 | 46 | 28 | Faster, lower accuracy |
| High-Conf | 0.91 | 0.06 | 78 | 13 | Fewer false positives |

**Deliverable**: Quantified trade-offs document

---

### Thursday - Polish & Advanced Features

(These are optional but impressive - implement if time allows)

**Multi-frame voting** (improves accuracy):
```python
# In postprocessing/voting.py (not yet implemented)
# Groups detections by vehicle_id and takes most common plate_text
```

**Preprocessing enhancements** (helps with poor lighting):
```python
# In preprocessing/image_enhance.py (not yet implemented)
# CLAHE for contrast enhancement
```

---

### Friday Morning - Interview Prep

**Practice your 2-minute story**:

> "Originally, my ALPR pipeline used YOLOv11 + SORT + PaddleOCR. I re-engineered it to measure **End-to-End Read Rate, Character Error Rate, and p95 latency** on a labeled golden set of 100 frames. 
>
> Then I ran controlled experiments: baseline vs skip-frames vs high-confidence thresholds. I discovered that skip-5 trading 5% accuracy for 2.3x speedup - quantifiable trade-off.
>
> My baseline achieved 93% ERR with 82ms P95 latency. Night performance was 8% lower than day, which led me to explore preprocessing enhancements.
>
> This turned it from a working demo into a **data-driven system** where I can measure, experiment, and improve systematically."

**Be ready to discuss**:
1. How you computed ERR/CER
2. Your trade-off analysis
3. Day vs night performance delta
4. What you'd do next (multi-frame voting, drift detection)

---

## File Structure

```
lpr-1/
├── scripts/
│   ├── create_golden_set.py      # ← Use this to create golden dataset
│   └── README_GOLDEN_SET.md      # ← Instructions
├── data/
│   └── golden/
│       ├── manifest.csv          # ← Your labels go here
│       └── frames/               # ← Extracted frames
├── evaluation/
│   ├── eval.py                   # ← Core evaluation
│   └── visualize.py              # ← Plots
├── docs/
│   ├── EVALUATION.md             # ← Methodology docs
│   └── INTERVIEW_NOTES.md        # ← (You'll create this)
└── results/
    ├── metrics/
    │   ├── baseline_eval.json    # ← Evaluation results
    │   ├── skip5_eval.json
    │   └── plots/                # ← Visualizations
    └── baseline_predictions.csv  # ← ALPR outputs
```

## Commands Cheat Sheet

```bash
# 1. Create golden dataset
python scripts/create_golden_set.py --video videos/sample_traffic.mp4

# 2. Run ALPR
python main.py --video videos/sample_traffic.mp4 --output results/pred.csv

# 3. Evaluate
python evaluation/eval.py --predictions results/pred.csv --ground-truth data/golden/manifest.csv

# 4. Visualize
python evaluation/visualize.py --results results/metrics/evaluation_results.json

# 5. Review labels
python scripts/create_golden_set.py --review data/golden/manifest.csv
```

## Critical Metrics to Know

Be able to quote these for your project:

- ✅ **ERR**: ___% (your baseline)
- ✅ **CER**: ___% (your baseline)
- ✅ **P95 Latency**: ___ ms
- ✅ **Day vs Night Delta**: ___% difference
- ✅ **Trade-off**: Skip-5 is ___x faster but ___% less accurate

## Tips

1. **Label carefully**: Your metrics are only as good as your labels
2. **Document everything**: Take screenshots of plots
3. **Practice explaining**: Know why ERR/CER matter
4. **Be honest**: If something didn't work, explain why
5. **Show curiosity**: "I'd want to try X next because..."

## Ready to Start?

```bash
# Navigate to project
cd /Users/elijahgjacob/lpr-1

# Start with golden dataset creation
python scripts/create_golden_set.py --video videos/sample_traffic.mp4
```

Good luck! 🚀


