#!/bin/bash
# Start Video Analyzer Server
# This script starts the video analyzer for processing video files

echo "========================================"
echo "  Video Analyzer Server Starter"
echo "========================================"
echo ""

# Check if video file argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./start_video_analyzer.sh <video_file> [--frames N]"
    echo ""
    echo "Examples:"
    echo "  ./start_video_analyzer.sh sample_video.mp4"
    echo "  ./start_video_analyzer.sh sample_video.mp4 --frames 10"
    echo ""
    exit 1
fi

VIDEO_FILE="$1"

# Check if video file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo "Error: Video file not found: $VIDEO_FILE"
    exit 1
fi

echo "Video file: $VIDEO_FILE"
echo ""

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Warning: Virtual environment not found at .venv/"
    echo "Continuing with system Python..."
fi

echo ""
echo "Starting Video Analyzer Server..."
echo "Port: 8766"
echo "Orchestrator: ws://localhost:9001"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the video analyzer
python src/vision/video_analyzer.py "$@"
