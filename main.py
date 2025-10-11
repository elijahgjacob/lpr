#!/usr/bin/env python3
"""
ALPR System - Main Entry Point

Command-line interface for processing videos with automatic license plate recognition.
"""

import argparse
import csv
import sys
import time
from pathlib import Path
import cv2

import config
import utils
from alpr_system import ALPRSystem


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="ALPR System - Automatic License Plate Recognition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process video with CSV output
  python main.py --video sample.mp4 --output results/plates.csv
  
  # Process with visualization
  python main.py --video sample.mp4 --output results/plates.csv --visualize
  
  # Process and save annotated video
  python main.py --video sample.mp4 --output results/plates.csv --save-video
  
  # Full pipeline with all outputs
  python main.py --video sample.mp4 --output results/plates.csv --visualize --save-video --report
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--video',
        type=str,
        required=True,
        help='Path to input video file'
    )
    
    # Output options
    parser.add_argument(
        '--output',
        type=str,
        default='results/detected_plates.csv',
        help='Path to output CSV file (default: results/detected_plates.csv)'
    )
    
    parser.add_argument(
        '--save-video',
        type=str,
        nargs='?',
        const='results/annotated_video.mp4',
        default=None,
        help='Save annotated video (default: results/annotated_video.mp4)'
    )
    
    parser.add_argument(
        '--report',
        type=str,
        nargs='?',
        const='results/summary.txt',
        default=None,
        help='Generate summary report (default: results/summary.txt)'
    )
    
    # Visualization
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Display video with annotations in real-time'
    )
    
    # Model options
    parser.add_argument(
        '--use-roboflow',
        action='store_true',
        help='Force use of Roboflow API for plate detection'
    )
    
    parser.add_argument(
        '--use-local',
        action='store_true',
        help='Force use of local models (no Roboflow)'
    )
    
    parser.add_argument(
        '--vehicle-model',
        type=str,
        help='Path to vehicle detection model (overrides config)'
    )
    
    parser.add_argument(
        '--plate-model',
        type=str,
        help='Path to plate detection model (overrides config)'
    )
    
    # Processing options
    parser.add_argument(
        '--skip-frames',
        type=int,
        default=0,
        help='Process every Nth frame (0 = process all frames)'
    )
    
    parser.add_argument(
        '--max-frames',
        type=int,
        help='Maximum number of frames to process'
    )
    
    # Supabase options
    parser.add_argument(
        '--no-supabase',
        action='store_true',
        help='Disable Supabase storage'
    )
    
    return parser.parse_args()


def validate_arguments(args):
    """Validate command-line arguments."""
    errors = []
    
    # Check video file exists
    video_path = Path(args.video)
    if not video_path.exists():
        errors.append(f"Video file not found: {args.video}")
    
    # Check model conflicts
    if args.use_roboflow and args.use_local:
        errors.append("Cannot use both --use-roboflow and --use-local")
    
    # Check skip frames
    if args.skip_frames < 0:
        errors.append("--skip-frames must be >= 0")
    
    if errors:
        print("Error: Invalid arguments", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)


def setup_output_directories(args):
    """Create output directories if they don't exist."""
    # CSV output directory
    csv_dir = Path(args.output).parent
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    # Video output directory
    if args.save_video:
        video_dir = Path(args.save_video).parent
        video_dir.mkdir(parents=True, exist_ok=True)
    
    # Report directory
    if args.report:
        report_dir = Path(args.report).parent
        report_dir.mkdir(parents=True, exist_ok=True)


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()
    validate_arguments(args)
    setup_output_directories(args)
    
    print("=" * 70)
    print("ALPR System - Automatic License Plate Recognition")
    print("=" * 70)
    print(f"Input Video: {args.video}")
    print(f"Output CSV: {args.output}")
    if args.save_video:
        print(f"Output Video: {args.save_video}")
    if args.report:
        print(f"Report: {args.report}")
    print("=" * 70)
    print()
    
    # Determine detection method
    use_roboflow = None
    if args.use_roboflow:
        use_roboflow = True
    elif args.use_local:
        use_roboflow = False
    
    # Determine Supabase usage
    enable_supabase = not args.no_supabase if args.no_supabase else None
    
    # Initialize ALPR system
    try:
        alpr = ALPRSystem(
            vehicle_model_path=args.vehicle_model,
            plate_model_path=args.plate_model,
            use_roboflow=use_roboflow,
            enable_supabase=enable_supabase
        )
    except Exception as e:
        print(f"Error: Failed to initialize ALPR system: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Open video
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"Error: Could not open video: {args.video}", file=sys.stderr)
        sys.exit(1)
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video Properties:")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Total Frames: {total_frames}")
    print()
    
    # Setup video writer if saving
    video_writer = None
    if args.save_video:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(args.save_video, fourcc, fps, (width, height))
        print(f"Video writer initialized: {args.save_video}")
    
    # Start Supabase test run
    if enable_supabase != False:
        video_name = Path(args.video).name
        alpr.start_test_run(video_name)
    
    # Open CSV file
    csv_file = open(args.output, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        'Frame',
        'Vehicle_ID',
        'Plate_Text',
        'Confidence',
        'Vehicle_X1',
        'Vehicle_Y1',
        'Vehicle_X2',
        'Vehicle_Y2',
        'Plate_X1',
        'Plate_Y1',
        'Plate_X2',
        'Plate_Y2'
    ])
    
    # Processing loop
    frame_number = 0
    processed_frames = 0
    start_time = time.time()
    all_results = []
    
    print("Processing video...")
    print("-" * 70)
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Check max frames
            if args.max_frames and processed_frames >= args.max_frames:
                break
            
            # Skip frames if requested
            if args.skip_frames > 0 and frame_number % (args.skip_frames + 1) != 0:
                frame_number += 1
                continue
            
            # Process frame
            annotated_frame, results = alpr.process_frame(
                frame,
                frame_number,
                visualize=(args.visualize or args.save_video is not None)
            )
            
            # Add frame info if visualizing
            if args.visualize or args.save_video:
                elapsed = time.time() - start_time
                processing_fps = processed_frames / elapsed if elapsed > 0 else 0
                annotated_frame = utils.add_frame_info(
                    annotated_frame,
                    frame_number,
                    processing_fps,
                    len(results)
                )
            
            # Write results to CSV
            for result in results:
                csv_writer.writerow([
                    result['frame_number'],
                    result['vehicle_id'],
                    result['plate_text'],
                    f"{result['confidence']:.4f}",
                    *result['vehicle_bbox'],
                    *result['plate_bbox']
                ])
                all_results.append(result)
            
            # Save to video
            if video_writer:
                video_writer.write(annotated_frame)
            
            # Display
            if args.visualize:
                cv2.imshow('ALPR System', annotated_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nStopped by user")
                    break
            
            # Progress update
            processed_frames += 1
            frame_number += 1
            
            if processed_frames % 30 == 0 or processed_frames == 1:
                elapsed = time.time() - start_time
                processing_fps = processed_frames / elapsed if elapsed > 0 else 0
                progress = (frame_number / total_frames) * 100 if total_frames > 0 else 0
                
                print(f"Frame {frame_number}/{total_frames} ({progress:.1f}%) | "
                      f"FPS: {processing_fps:.1f} | "
                      f"Detections: {len(all_results)}", end='\r')
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    except Exception as e:
        print(f"\n\nError during processing: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n" + "-" * 70)
        print("Cleaning up...")
        
        cap.release()
        csv_file.close()
        
        if video_writer:
            video_writer.release()
        
        if args.visualize:
            cv2.destroyAllWindows()
        
        # End Supabase test run
        if enable_supabase != False:
            alpr.end_test_run(processed_frames)
    
    # Calculate statistics
    elapsed_time = time.time() - start_time
    processing_fps = processed_frames / elapsed_time if elapsed_time > 0 else 0
    
    print("\n" + "=" * 70)
    print("Processing Complete!")
    print("=" * 70)
    print(f"Frames Processed: {processed_frames}/{total_frames}")
    print(f"Processing Time: {elapsed_time:.2f}s")
    print(f"Processing FPS: {processing_fps:.2f}")
    print(f"Detections Written: {len(all_results)}")
    
    stats = alpr.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total Vehicles Detected: {stats['vehicles_detected']}")
    print(f"  Unique Vehicles Tracked: {stats['unique_vehicles']}")
    print(f"  License Plates Detected: {stats['plates_detected']}")
    print(f"  License Plates Read: {stats['plates_read']}")
    
    # Generate report
    if args.report:
        print(f"\nGenerating summary report: {args.report}")
        summary = utils.generate_summary_report(all_results)
        summary['processing_time'] = elapsed_time
        summary['processing_fps'] = processing_fps
        utils.save_summary_to_file(summary, args.report)
        print("✓ Report saved")
    
    print("\n✓ All outputs saved successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()

