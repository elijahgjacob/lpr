# License Plate Detection Model Guide

## Quick Options (Recommended for Interview Prep)

### Option 1: Download Pre-trained Model (FASTEST - 5 minutes)

```bash
# Run the download helper
python scripts/download_plate_model.py
```

This will guide you through downloading a pre-trained model from:
- Roboflow Universe
- Ultralytics Hub
- Your own Roboflow project

**Steps:**
1. Go to [Roboflow Universe](https://universe.roboflow.com/)
2. Search for "license plate detection"
3. Choose a project (e.g., `license-plate-recognition-rxg4e`)
4. Click "Export" → "YOLOv8" or "YOLOv11"
5. Download and extract
6. Copy the `.pt` file to `models/license_plate_detector.pt`

**Recommended Pre-trained Models:**
- [Car License Plate Detection](https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e)
- [Vehicle Registration Plates](https://universe.roboflow.com/vehicle-registration-plates-trudk)

### Option 2: Use Roboflow Export (10 minutes)

If you have a Roboflow account with a plate detection project:

```bash
python scripts/download_plate_model.py
# Select option 3 (Export from YOUR Roboflow project)
```

Or manually:
```python
from roboflow import Roboflow

rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("roboflow-universe").project("license-plate-recognition-rxg4e")
dataset = project.version(4).download("yolov8")
```

The model weights will be in the downloaded folder.

---

## Training Your Own Model (If You Have Time)

### Step 1: Get Training Data

**Option A: Use Existing Dataset**

Download from Roboflow:
```bash
python scripts/train_plate_model.py download \
  --api-key YOUR_KEY \
  --workspace roboflow-universe \
  --project license-plate-recognition-rxg4e \
  --version 4
```

**Option B: Create Your Own**

1. Collect 500-1000 images with license plates
2. Label using [Roboflow](https://roboflow.com/), LabelImg, or CVAT
3. Export in YOLO format

### Step 2: Check Requirements

```bash
python scripts/train_plate_model.py requirements
```

Your dataset should be organized as:
```
dataset/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

### Step 3: Train Model

```bash
# Quick training (fast, lower accuracy)
python scripts/train_plate_model.py train \
  --data plate_dataset.yaml \
  --model yolo11n \
  --epochs 50 \
  --batch 16

# Better accuracy (slower)
python scripts/train_plate_model.py train \
  --data plate_dataset.yaml \
  --model yolo11m \
  --epochs 100 \
  --batch 8
```

**Model Sizes:**
- `yolo11n` - Nano (fastest, lowest accuracy) - 5-10 min training
- `yolo11s` - Small (balanced) - 15-20 min training
- `yolo11m` - Medium (good accuracy) - 30-40 min training
- `yolo11l` - Large (high accuracy) - 1-2 hours training
- `yolo11x` - Extra Large (best accuracy) - 3-4 hours training

### Step 4: Use Trained Model

After training completes:

```bash
# Copy best model
cp runs/train/plate_detector/weights/best.pt models/license_plate_detector.pt

# Test it
python main.py \
  --video videos/sample_traffic.mp4 \
  --output results/custom_model.csv \
  --use-local
```

---

## Comparison: Pre-trained vs Training

| Aspect | Pre-trained | Train Your Own |
|--------|-------------|----------------|
| **Time** | 5-10 minutes | 1-4 hours |
| **Difficulty** | Easy | Medium |
| **Accuracy** | Good (80-90%) | Excellent (90-95%+) |
| **Customization** | Limited | Full control |
| **Data Required** | None | 500-1000 images |
| **Interview Value** | Shows efficiency | Shows ML expertise |

---

## For Interview Prep: Recommended Approach

**Timeline: 4 days to interview**

### Day 1-2: Use Pre-trained Model ✅
- Download a pre-trained model (10 minutes)
- Run baseline experiments
- Get your ERR/CER metrics
- **Focus on evaluation and metrics**

### Day 3-4 (Optional): Train If Time Allows
- Show you can train models
- Compare pre-trained vs custom
- Discuss training process in interview

**Key Point**: For the interview, having **solid evaluation metrics** (ERR, CER, trade-off analysis) is MORE IMPORTANT than training your own model.

---

## Quick Start Commands

```bash
# 1. Download a model
python scripts/download_plate_model.py

# 2. Place it at models/license_plate_detector.pt

# 3. Run ALPR with local model
python main.py \
  --video /Users/elijahgjacob/Downloads/usplates.mp4 \
  --output results/baseline_predictions.csv \
  --use-local \
  --no-supabase

# 4. Evaluate
python evaluation/eval.py \
  --predictions results/baseline_predictions.csv \
  --ground-truth data/golden/manifest.csv
```

---

## Troubleshooting

### Model Not Detecting Plates

1. **Check confidence threshold**:
   ```python
   # In .env
   PLATE_CONFIDENCE_THRESHOLD=0.2  # Lower threshold
   ```

2. **Try different model**:
   - Some models are trained on specific plate formats
   - US plates vs European plates, etc.

3. **Verify model format**:
   ```bash
   # Test model loads correctly
   python -c "from ultralytics import YOLO; model = YOLO('models/license_plate_detector.pt'); print('Model loaded OK')"
   ```

### Training Fails

1. **Check dataset format**: Run `python scripts/train_plate_model.py requirements`
2. **Reduce batch size**: Use `--batch 4` or `--batch 2`
3. **Use smaller model**: Try `yolo11n` instead of `yolo11m`

---

## Resources

- [Roboflow Universe](https://universe.roboflow.com/) - Pre-trained models
- [Ultralytics Docs](https://docs.ultralytics.com/) - YOLO training guide
- [Roboflow Docs](https://docs.roboflow.com/) - Dataset labeling and export
- [YOLO Dataset Format](https://docs.ultralytics.com/datasets/detect/) - Format specification

---

## What to Tell Your Interviewer

**If using pre-trained:**
> "I leveraged a pre-trained YOLOv11 model from Roboflow Universe, fine-tuned on 5,000+ labeled license plates. This allowed me to focus on system architecture, evaluation metrics, and trade-off analysis rather than spending time on model training."

**If you trained your own:**
> "I trained a custom YOLOv11m model on 800 labeled license plate images, achieving 94% mAP@0.5. The training process involved data augmentation, hyperparameter tuning, and early stopping. I compared it against the pre-trained baseline to demonstrate the 3% accuracy improvement."

Both are valuable - choose based on your timeline! 🚀


