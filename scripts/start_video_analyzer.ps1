# Start Video Analyzer Server
# This script starts the video analyzer for processing video files

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Video Analyzer Server Starter" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if video file argument is provided
if ($args.Count -eq 0) {
    Write-Host "Usage: .\start_video_analyzer.ps1 <video_file> [--frames N]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\start_video_analyzer.ps1 sample_video.mp4" -ForegroundColor White
    Write-Host "  .\start_video_analyzer.ps1 sample_video.mp4 --frames 10" -ForegroundColor White
    Write-Host ""
    exit 1
}

$videoFile = $args[0]

# Check if video file exists
if (-not (Test-Path $videoFile)) {
    Write-Host "Error: Video file not found: $videoFile" -ForegroundColor Red
    exit 1
}

Write-Host "Video file: $videoFile" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "Warning: Virtual environment not found at .venv\" -ForegroundColor Yellow
    Write-Host "Continuing with system Python..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting Video Analyzer Server..." -ForegroundColor Cyan
Write-Host "Port: 8766" -ForegroundColor White
Write-Host "Orchestrator: ws://localhost:9001" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start the video analyzer
python src\vision\video_analyzer.py $args
