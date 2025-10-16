#!/usr/bin/env python3
"""
Quick runner for Roboflow Workflow ALPR.
Uses your specific workflow configuration.
"""

from alpr_workflow import ALPRWorkflow
import sys

def main():
    # Your Roboflow credentials
    API_KEY = "x4Xvvvw47esbu5nZ5XPx"
    WORKSPACE = "alpr-jjlrf"
    WORKFLOW_ID = "detect-and-classify-2"
    
    if len(sys.argv) < 2:
        print("Usage: python run_workflow.py <video_path> [output_csv]")
        print("\nExample:")
        print("  python run_workflow.py videos/sample_traffic.mp4")
        print("  python run_workflow.py videos/sample_traffic.mp4 results/workflow_output.csv")
        return 1
    
    video_path = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "results/workflow_predictions.csv"
    
    print(f"Video: {video_path}")
    print(f"Output: {output_csv}")
    print()
    
    # Initialize ALPR workflow
    alpr = ALPRWorkflow(
        api_key=API_KEY,
        workspace_name=WORKSPACE,
        workflow_id=WORKFLOW_ID
    )
    
    # Process video
    alpr.process_video(
        video_path=video_path,
        output_csv=output_csv,
        max_fps=30
    )
    
    # Print statistics
    stats = alpr.get_statistics()
    print("\nFinal Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return 0


if __name__ == "__main__":
    exit(main())


