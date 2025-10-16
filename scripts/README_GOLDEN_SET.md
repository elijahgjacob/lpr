# Golden Dataset Creation Guide

## Quick Start

### Option 1: Extract frames then label interactively

```bash
# Extract frames from your video
python scripts/create_golden_set.py \
  --video videos/sample_traffic.mp4 \
  --output data/golden/manifest.csv \
  --interval 30 \
  --max-frames 100
```

This will:
1. Extract 100 frames (every 30th frame)
2. Show each frame in a window
3. Prompt you to enter the plate text
4. Save labels to `data/golden/manifest.csv`

### Option 2: Extract only (label later manually)

```bash
# Just extract frames
python scripts/create_golden_set.py \
  --video videos/sample_traffic.mp4 \
  --extract-only \
  --interval 30 \
  --max-frames 100
```

Then edit `data/golden/manifest.csv` manually in Excel/Google Sheets.

### Option 3: Create empty template

```bash
# Create template CSV
python scripts/create_golden_set.py \
  --template data/golden/manifest.csv
```

## During Interactive Labeling

- Type the plate text you see (e.g., `ABC1234`)
- Press Enter to confirm
- Enter light condition: `day`, `night`, or `dusk`
- Enter camera ID (default: `cam_01`)
- Type `skip` if no plate is visible
- Type `back` to go to previous frame
- Type `quit` to save and exit

## Review Your Labels

```bash
python scripts/create_golden_set.py --review data/golden/manifest.csv
```

## Tips

- Aim for 80-100 well-labeled frames
- Include variety: different lighting, angles, distances
- Only label plates that are clearly visible
- Double-check spelling (use UPPERCASE)
- Mark ambiguous cases in notes field

## Output Format

The CSV will have these columns:
- `frame_id`: Frame number
- `video_source`: Video filename
- `plate_text_gt`: Ground truth plate text (what you labeled)
- `light_condition`: day/night/dusk
- `camera_id`: Camera identifier
- `notes`: Optional notes
- `labeled_at`: Timestamp
- `frame_path`: Path to saved frame image

## Next Steps

Once you have your golden dataset:
```bash
# Run evaluation
python evaluation/eval.py \
  --predictions results/output.csv \
  --ground-truth data/golden/manifest.csv
```


