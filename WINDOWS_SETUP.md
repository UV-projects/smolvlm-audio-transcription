# AI Director - Setup Guide for Windows with CUDA

## Prerequisites

### 1. Check CUDA Installation
```powershell
nvidia-smi
```
This should show your GPU and CUDA version. If not installed, download from [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)

### 2. Check Python Version
```powershell
python --version
```
Requires Python 3.10 or newer.

## Installation Steps

### Step 1: Create Virtual Environment
```powershell
cd e:\dev\ai-director\smolvlm-audio-transcription
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If you get execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install Dependencies
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install PyTorch with CUDA support (adjust cu121 based on your CUDA version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install moshi sentencepiece "numpy<2.0" websockets opencv-python ffmpeg-python pillow
```

### Step 3: Verify CUDA is Working
```powershell
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

Should output:
```
CUDA available: True
CUDA device: [Your GPU Name]
```

## Running the Application

### Option 1: Run with Video File

```powershell
# Make sure you're in the virtual environment
.\.venv\Scripts\Activate.ps1

# Run with a video file (replace with your video path)
python main_video.py "path\to\your\video.mp4"

# Or without audio transcription (faster)
python main_video.py "path\to\your\video.mp4" --no-audio
```

### Option 2: Download a Sample Video for Testing
```powershell
# Using curl (comes with Windows 10+)
curl -o sample_video.mp4 "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"

# Then run
python main_video.py sample_video.mp4
```

### Step 4: Open Web Interface

Once the server is running, open in your browser:
```
index_video.html
```
Or simply double-click the file.

The interface will auto-connect to `ws://localhost:8765`

## Model Configuration

### Current Models
- **Vision Model**: SmolVLM-500M (via llama.cpp)
- **STT Model**: Moshi STT 1B (English/French)

### Switching Models

Edit `main_video.py` and change the model repository:

```python
# For different STT models
model_repo="kyutai/stt-1b-en_fr"  # Current
# model_repo="kyutai/stt-2b-en_fr"  # Larger, more accurate
```

### Adding Model Selection

Create `config.json`:
```json
{
    "models": {
        "stt": {
            "small": "kyutai/stt-1b-en_fr",
            "large": "kyutai/stt-2b-en_fr"
        },
        "vlm": {
            "small": "ggml-org/SmolVLM-500M-Instruct-GGUF",
            "large": "other-model-here"
        }
    },
    "active_model": "small"
}
```

## Troubleshooting

### CUDA Out of Memory
```powershell
# Use smaller batch sizes or reduce video resolution
# Edit main_video.py and add frame resizing in VideoProcessor
```

### FFmpeg Not Found
```powershell
# Install ffmpeg via chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
# Add to PATH
```

### Port 8765 Already in Use
```powershell
# Find process using port
netstat -ano | findstr :8765

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Websocket Connection Failed
1. Make sure the Python server is running
2. Check firewall settings
3. Try accessing via `http://localhost` instead of opening file directly

## Performance Optimization

### For Better Performance:
1. Use CUDA 12.1 or newer
2. Close other GPU-intensive applications
3. Use `--no-audio` flag if you only need video analysis
4. Reduce video resolution before processing

### Monitor GPU Usage:
```powershell
# In another terminal
nvidia-smi -l 1
```

## Next Steps: n8n Integration

### Architecture Overview
```
┌──────────────┐
│   n8n        │  (Orchestrator)
│  Workflow    │
└──────┬───────┘
       │
       ├─────────────┐
       │             │
┌──────▼──────┐ ┌───▼──────────┐
│  Video      │ │   VLM/STT    │
│  Source 1   │ │   Server     │
│  (Stream)   │ │  :8765       │
└─────────────┘ └──────────────┘
```

### Prepare for n8n:
1. Install n8n: `npm install -g n8n`
2. Create REST API wrapper around WebSocket (see `api_wrapper.py` - to be created)
3. Set up webhook endpoints for n8n to consume
4. Implement stream selection logic

Would you like me to create:
1. The API wrapper for n8n integration?
2. A model configuration system for easy switching?
3. Multiple video input support?
