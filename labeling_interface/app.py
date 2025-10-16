#!/usr/bin/env python3
"""
Flask backend for the license plate labeling interface.
Serves frames and handles API endpoints for saving labels.
"""

import os
import json
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import glob

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES_DIR = os.path.join(BASE_DIR, 'data', 'golden', 'frames')
TEMPLATE_CSV = os.path.join(BASE_DIR, 'golden_dataset_template.csv')
LABELS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'labels.json')

# Initialize labels storage
def init_labels():
    """Initialize the labels storage file."""
    if not os.path.exists(LABELS_JSON):
        with open(LABELS_JSON, 'w') as f:
            json.dump({}, f)

@app.route('/')
def index():
    """Serve the main labeling interface."""
    return send_file('index.html')

@app.route('/api/frames')
def get_frames():
    """Get list of all available frames."""
    try:
        print(f"DEBUG: FRAMES_DIR = {FRAMES_DIR}")
        print(f"DEBUG: TEMPLATE_CSV = {TEMPLATE_CSV}")
        print(f"DEBUG: FRAMES_DIR exists: {os.path.exists(FRAMES_DIR)}")
        print(f"DEBUG: TEMPLATE_CSV exists: {os.path.exists(TEMPLATE_CSV)}")
        
        # Read the template CSV to get frame information
        if os.path.exists(TEMPLATE_CSV):
            df = pd.read_csv(TEMPLATE_CSV)
            # Get unique frame IDs
            frame_ids = sorted(df['frame_id'].unique())
            print(f"DEBUG: Found {len(frame_ids)} frames in template CSV")
        else:
            # Fallback: get frames from directory
            frame_files = glob.glob(os.path.join(FRAMES_DIR, 'frame_*.jpg'))
            print(f"DEBUG: Found {len(frame_files)} frame files in directory")
            frame_ids = []
            for frame_file in frame_files:
                # Extract frame ID from filename
                filename = os.path.basename(frame_file)
                frame_id = int(filename.split('_')[1].split('.')[0])
                frame_ids.append(frame_id)
            frame_ids.sort()

        frames = [{'frame_id': int(frame_id)} for frame_id in frame_ids]
        return jsonify(frames)
    except Exception as e:
        print(f"DEBUG: Error in get_frames: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/frame/<int:frame_id>')
def get_frame(frame_id):
    """Serve a specific frame image."""
    try:
        frame_filename = f'frame_{frame_id:06d}.jpg'
        return send_from_directory(FRAMES_DIR, frame_filename)
    except Exception as e:
        return jsonify({'error': f'Frame {frame_id} not found'}), 404

@app.route('/api/save-frame', methods=['POST'])
def save_frame():
    """Save labeled data for a specific frame."""
    try:
        data = request.json
        frame_id = data['frame_id']
        vehicles = data['vehicles']

        # Load existing labels
        init_labels()
        with open(LABELS_JSON, 'r') as f:
            labels = json.load(f)

        # Save frame data
        labels[str(frame_id)] = {
            'frame_id': frame_id,
            'vehicles': vehicles,
            'saved_at': datetime.now().isoformat()
        }

        # Write back to file
        with open(LABELS_JSON, 'w') as f:
            json.dump(labels, f, indent=2)

        return jsonify({'success': True, 'message': f'Saved {len(vehicles)} vehicles for frame {frame_id}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-csv', methods=['POST'])
def export_csv():
    """Export all labeled data to CSV format compatible with the template."""
    try:
        init_labels()
        with open(LABELS_JSON, 'r') as f:
            labels = json.load(f)

        # Read the original template
        if os.path.exists(TEMPLATE_CSV):
            template_df = pd.read_csv(TEMPLATE_CSV)
        else:
            # Create empty template if it doesn't exist
            template_df = pd.DataFrame(columns=[
                'frame_id', 'vehicle_number', 'video_source', 'frame_path',
                'has_vehicle', 'vehicle_type', 'plate_text_gt', 'plate_confidence',
                'plate_state', 'plate_type', 'light_condition', 'weather',
                'vehicle_notes', 'frame_notes', 'labeled_at', 'labeled_by'
            ])

        # Update template with labeled data
        for frame_id_str, frame_data in labels.items():
            frame_id = int(frame_id_str)
            vehicles = frame_data['vehicles']

            for vehicle in vehicles:
                # Find the corresponding row in template
                mask = (template_df['frame_id'] == frame_id) & (template_df['vehicle_number'] == vehicle['vehicle_number'])
                
                if mask.any():
                    # Update existing row
                    template_df.loc[mask, 'has_vehicle'] = 'Y'
                    template_df.loc[mask, 'vehicle_type'] = vehicle['vehicle_type']
                    template_df.loc[mask, 'plate_text_gt'] = vehicle['plate_text']
                    template_df.loc[mask, 'plate_confidence'] = vehicle['plate_confidence']
                    template_df.loc[mask, 'plate_state'] = vehicle['plate_state']
                    template_df.loc[mask, 'light_condition'] = vehicle['light_condition']
                    template_df.loc[mask, 'weather'] = vehicle['weather']
                    template_df.loc[mask, 'vehicle_notes'] = vehicle['vehicle_notes']
                    template_df.loc[mask, 'labeled_at'] = frame_data['saved_at']
                    template_df.loc[mask, 'labeled_by'] = 'web_interface'

        # Save updated template
        template_df.to_csv(TEMPLATE_CSV, index=False)

        # Also create a detailed export with bounding box information
        detailed_export = []
        for frame_id_str, frame_data in labels.items():
            frame_id = int(frame_id_str)
            for vehicle in frame_data['vehicles']:
                detailed_export.append({
                    'frame_id': int(frame_id),
                    'vehicle_number': int(vehicle['vehicle_number']),
                    'plate_text_gt': str(vehicle['plate_text']),
                    'vehicle_type': str(vehicle['vehicle_type']) if vehicle['vehicle_type'] else '',
                    'plate_state': str(vehicle['plate_state']) if vehicle['plate_state'] else '',
                    'plate_confidence': int(vehicle['plate_confidence']) if vehicle['plate_confidence'] else None,
                    'light_condition': str(vehicle['light_condition']),
                    'weather': str(vehicle['weather']),
                    'vehicle_notes': str(vehicle['vehicle_notes']) if vehicle['vehicle_notes'] else '',
                    'vehicle_box_x': int(vehicle['vehicle_box']['x']),
                    'vehicle_box_y': int(vehicle['vehicle_box']['y']),
                    'vehicle_box_width': int(vehicle['vehicle_box']['width']),
                    'vehicle_box_height': int(vehicle['vehicle_box']['height']),
                    'plate_box_x': int(vehicle['plate_box']['x']),
                    'plate_box_y': int(vehicle['plate_box']['y']),
                    'plate_box_width': int(vehicle['plate_box']['width']),
                    'plate_box_height': int(vehicle['plate_box']['height']),
                    'labeled_at': str(frame_data['saved_at']),
                    'labeled_by': 'web_interface'
                })

        # Save detailed export
        detailed_df = pd.DataFrame(detailed_export)
        detailed_df.to_csv('detailed_labels_export.csv', index=False)

        return jsonify({
            'success': True,
            'message': f'Exported {len(detailed_export)} vehicle labels',
            'files': {
                'template_csv': TEMPLATE_CSV,
                'detailed_export': 'detailed_labels_export.csv'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/load-frame/<int:frame_id>')
def load_frame_data(frame_id):
    """Load existing labeled data for a specific frame."""
    try:
        init_labels()
        with open(LABELS_JSON, 'r') as f:
            labels = json.load(f)

        frame_data = labels.get(str(frame_id), {'vehicles': []})
        return jsonify(frame_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get labeling statistics."""
    try:
        init_labels()
        with open(LABELS_JSON, 'r') as f:
            labels = json.load(f)

        total_frames_labeled = len(labels)
        total_vehicles = sum(len(frame_data['vehicles']) for frame_data in labels.values())
        
        return jsonify({
            'total_frames_labeled': total_frames_labeled,
            'total_vehicles': total_vehicles,
            'frames': list(labels.keys())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-labels', methods=['POST'])
def clear_labels():
    """Clear all labels (for testing/reset)."""
    try:
        with open(LABELS_JSON, 'w') as f:
            json.dump({}, f)
        return jsonify({'success': True, 'message': 'All labels cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(os.path.abspath(FRAMES_DIR)), exist_ok=True)
    
    print("🚗 License Plate Labeling Interface")
    print("=" * 40)
    print(f"Frames directory: {FRAMES_DIR}")
    print(f"Template CSV: {TEMPLATE_CSV}")
    print("=" * 40)
    print("Starting server...")
    print("Open your browser to: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
