# 🚗 License Plate Labeling Interface

A modern web-based interface for labeling vehicles and license plates in video frames with drag-and-drop bounding boxes.

## Features

- 🖱️ **Drag-and-Drop Bounding Boxes**: Draw vehicle and license plate bounding boxes by clicking and dragging
- 📝 **Detailed Annotation**: Label license plate text, vehicle type, state, confidence, and more
- 🎨 **Modern UI**: Beautiful, responsive interface with real-time feedback
- 💾 **Auto-Save**: Automatically saves your progress as you work
- 📊 **Progress Tracking**: Visual progress bar and frame counter
- ⌨️ **Keyboard Shortcuts**: Quick navigation with arrow keys
- 🔄 **Export Integration**: Seamlessly exports to CSV format compatible with the golden dataset

## Quick Start

### 1. Extract Frames First
Make sure you have extracted frames from your video:
```bash
cd /Users/elijahgjacob/lpr-1
python scripts/create_golden_dataset.py --action extract --video videos/main_video.mp4
```

### 2. Start the Labeling Interface
```bash
cd labeling_interface
python start_labeling.py
```

### 3. Open Your Browser
Navigate to: http://localhost:5000

## How to Use

### Drawing Bounding Boxes
1. **Vehicle Boxes (Green)**: Click and drag to draw a box around the entire vehicle
2. **License Plate Boxes (Red)**: Click and drag to draw a box around the license plate
3. **Multiple Vehicles**: You can label up to 5 vehicles per frame

### Filling Information
1. **License Plate Text**: Enter the exact text as it appears (e.g., "ABC1234")
2. **Vehicle Type**: Select from car, truck, motorcycle, bus, or van
3. **Plate State**: Enter the state abbreviation (e.g., "CA", "NY", "TX")
4. **Plate Clarity**: Rate from 1 (very blurry) to 5 (crystal clear)
5. **Light Condition**: Select day, night, dawn, or dusk
6. **Weather**: Select clear, rainy, cloudy, or snowy
7. **Notes**: Add any additional observations

### Navigation
- **Previous Frame**: Click "Previous" or press Left Arrow
- **Next Frame**: Click "Next" or press Right Arrow
- **Save & Exit**: Click "Save & Exit" to export all data to CSV

### Keyboard Shortcuts
- `Left Arrow`: Previous frame
- `Right Arrow`: Next frame
- `V`: Switch to vehicle mode (green boxes)
- `P`: Switch to plate mode (red boxes)

## File Structure

```
labeling_interface/
├── index.html          # Main web interface
├── app.py              # Flask backend server
├── start_labeling.py   # Setup and startup script
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── labels.json        # Auto-generated: stores your labels
└── detailed_labels_export.csv  # Auto-generated: detailed export
```

## Output Files

### 1. Updated Template CSV
The interface automatically updates `../golden_dataset_template.csv` with your labeled data.

### 2. Detailed Export CSV
Creates `detailed_labels_export.csv` with bounding box coordinates and all annotation details.

### 3. Labels JSON
Temporary storage file `labels.json` for the web interface (can be deleted after export).

## API Endpoints

The Flask server provides these endpoints:

- `GET /api/frames` - Get list of available frames
- `GET /api/frame/<frame_id>` - Serve a specific frame image
- `POST /api/save-frame` - Save labeled data for a frame
- `POST /api/export-csv` - Export all data to CSV
- `GET /api/load-frame/<frame_id>` - Load existing labels for a frame
- `GET /api/stats` - Get labeling statistics
- `POST /api/clear-labels` - Clear all labels (for testing)

## Troubleshooting

### No Frames Found
If you see "No frames found!", make sure you've extracted frames first:
```bash
python ../scripts/create_golden_dataset.py --action extract
```

### Dependencies Issues
If you get import errors, install dependencies manually:
```bash
pip install -r requirements.txt
```

### Port Already in Use
If port 5000 is busy, edit `app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

## Tips for Better Labeling

1. **Accuracy**: Be precise with bounding boxes - they should tightly fit the vehicle/plate
2. **Consistency**: Use the same conventions for vehicle types and plate states
3. **Quality**: Only label plates you can clearly read
4. **Completeness**: Fill in all available information for better training data
5. **Review**: Double-check your plate text entries for typos

## Integration with Golden Dataset

The labeling interface seamlessly integrates with the golden dataset system:

1. **Template Compatible**: Exports data in the exact format expected by the golden dataset
2. **Multi-Vehicle Support**: Handles multiple vehicles per frame (up to 5)
3. **Rich Metadata**: Includes all annotation details (confidence, weather, etc.)
4. **Bounding Box Coordinates**: Saves precise pixel coordinates for training

After labeling, you can import your data into the golden dataset:
```bash
python ../scripts/create_golden_dataset.py --action add-to-manifest --template ../golden_dataset_template.csv
```

Happy labeling! 🎯
