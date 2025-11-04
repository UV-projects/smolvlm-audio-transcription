# AI Director - Startup Script for Windows
# This script starts all necessary services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AI Director - Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "Virtual environment created." -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$pipList = pip list
if ($pipList -notmatch "torch") {
    Write-Host "Installing dependencies (this may take a while)..." -ForegroundColor Yellow
    pip install -r requirements-windows.txt
}

# Check CUDA availability
Write-Host ""
Write-Host "Checking CUDA availability..." -ForegroundColor Yellow
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}') if torch.cuda.is_available() else print('Running on CPU')"

# Check for video files
Write-Host ""
Write-Host "Available video files:" -ForegroundColor Yellow
Get-ChildItem -Path . -Filter *.mp4 | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Choose an option:" -ForegroundColor Cyan
Write-Host "1) Start API Server (for n8n integration)" -ForegroundColor White
Write-Host "2) Process a video file (standalone)" -ForegroundColor White
Write-Host "3) Configure models" -ForegroundColor White
Write-Host "4) Check system requirements" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting API Server..." -ForegroundColor Green
        Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Yellow
        Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
        Write-Host ""
        python api_server.py
    }
    "2" {
        Write-Host ""
        $videoPath = Read-Host "Enter video file path (or press Enter for sample.mp4)"
        if ([string]::IsNullOrWhiteSpace($videoPath)) {
            $videoPath = "sample.mp4"
        }
        
        if (-not (Test-Path $videoPath)) {
            Write-Host "Video file not found: $videoPath" -ForegroundColor Red
            Write-Host "Please provide a valid video file path." -ForegroundColor Yellow
            exit
        }
        
        $useAudio = Read-Host "Enable audio transcription? (y/n, default: y)"
        $audioFlag = if ($useAudio -eq "n") { "--no-audio" } else { "" }
        
        Write-Host ""
        Write-Host "Starting video processing..." -ForegroundColor Green
        Write-Host "Server will be available at: ws://localhost:8765" -ForegroundColor Yellow
        Write-Host "Open index_video.html in your browser" -ForegroundColor Yellow
        Write-Host ""
        
        if ($audioFlag) {
            python main_video.py "$videoPath" $audioFlag
        } else {
            python main_video.py "$videoPath"
        }
    }
    "3" {
        Write-Host ""
        Write-Host "Model Configuration" -ForegroundColor Green
        Write-Host "===================" -ForegroundColor Green
        Write-Host ""
        
        python config_manager.py active
        
        Write-Host ""
        Write-Host "Available commands:" -ForegroundColor Yellow
        Write-Host "  python config_manager.py list stt       - List STT models" -ForegroundColor Gray
        Write-Host "  python config_manager.py list vlm       - List VLM models" -ForegroundColor Gray
        Write-Host "  python config_manager.py set-stt small  - Set STT model" -ForegroundColor Gray
        Write-Host "  python config_manager.py set-vlm small  - Set VLM model" -ForegroundColor Gray
        Write-Host ""
        
        $configCmd = Read-Host "Enter command (or press Enter to exit)"
        if (-not [string]::IsNullOrWhiteSpace($configCmd)) {
            Invoke-Expression "python config_manager.py $configCmd"
        }
    }
    "4" {
        Write-Host ""
        Write-Host "System Requirements Check" -ForegroundColor Green
        Write-Host "=========================" -ForegroundColor Green
        Write-Host ""
        
        # Check CUDA
        Write-Host "CUDA Status:" -ForegroundColor Yellow
        python -c "import torch; print(f'  CUDA Available: {torch.cuda.is_available()}'); print(f'  CUDA Version: {torch.version.cuda}') if torch.cuda.is_available() else None; print(f'  GPU: {torch.cuda.get_device_name(0)}') if torch.cuda.is_available() else print('  Using CPU')"
        
        Write-Host ""
        Write-Host "VRAM Requirements:" -ForegroundColor Yellow
        python config_manager.py vram
        
        Write-Host ""
        Write-Host "FFmpeg Status:" -ForegroundColor Yellow
        try {
            $ffmpegVersion = ffmpeg -version 2>&1 | Select-String "ffmpeg version"
            Write-Host "  $ffmpegVersion" -ForegroundColor Green
        } catch {
            Write-Host "  FFmpeg not found. Install with: choco install ffmpeg" -ForegroundColor Red
        }
        
        Write-Host ""
        Read-Host "Press Enter to continue"
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service stopped. Thank you!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
