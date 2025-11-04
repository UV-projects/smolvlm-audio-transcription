# 🎬 SmolVLM Audio Transcription

Real-time video analysis system combining GPU-accelerated vision (Qwen3-VL) with audio transcription (Vosk STT). Streams video frames, extracts audio, analyzes visuals, and transcribes speech in real-time through a unified web interface.

## ✨ Features

- **🖼️ Vision Analysis**: Qwen3-VL-2B model via llama-server with GPU CUDA acceleration
- **🎤 Audio Transcription**: Vosk STT with real-time partial results (word-by-word typing effect)
- **📹 Video Streaming**: Server-side audio extraction using FFmpeg (no browser microphone needed)
- **⚡ GPU Support**: Full CUDA offloading for fast VLM inference
- **🌐 Web Interface**: Unified HTML interface for video + audio + vision analysis
- **🔄 Real-time**: WebSocket architecture for low-latency streaming

---

## 🛠️ Installation Guide

### Step 1: System Requirements

**Hardware:**
- **GPU**: NVIDIA GPU with CUDA support (tested on RTX 2070 SUPER, 8GB VRAM)
  - Minimum: 4GB VRAM for Qwen3-VL-2B Q4 quantization
  - Recommended: 6GB+ VRAM for smooth operation
- **RAM**: 16GB+ recommended (Vosk model loads ~7GB)
- **Storage**: ~15GB free space (models + dependencies)

**Software:**
- **Operating System**: Windows 10/11, Linux, or macOS
- **Python**: 3.10, 3.11, or 3.12
- **CUDA Toolkit**: 12.x (for NVIDIA GPU support)
- **Git**: For cloning repository

---

### Step 2: Install Dependencies

#### Windows

**2.1 Install CUDA Toolkit**
```powershell
# Download from NVIDIA
# https://developer.nvidia.com/cuda-downloads
# Install CUDA 12.6 or later

# Verify installation
nvidia-smi
nvcc --version
```

**2.2 Install FFmpeg**
```powershell
# Option 1: Using Chocolatey
choco install ffmpeg

# Option 2: Manual download
# https://ffmpeg.org/download.html
# Extract to C:\ffmpeg and add to PATH

# Verify
ffmpeg -version
```

**2.3 Install Python Dependencies**
```powershell
# Clone repository
git clone https://github.com/UV-projects/smolvlm-audio-transcription.git
cd smolvlm-audio-transcription

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python packages
pip install -r requirements.txt
```

#### Linux

**2.1 Install CUDA Toolkit**
```bash
# Ubuntu/Debian
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install cuda-toolkit-12-6

# Verify
nvidia-smi
nvcc --version
```

**2.2 Install FFmpeg**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch
sudo pacman -S ffmpeg

# Verify
ffmpeg -version
```

**2.3 Install Python Dependencies**
```bash
git clone https://github.com/UV-projects/smolvlm-audio-transcription.git
cd smolvlm-audio-transcription

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

#### macOS

**2.1 Install Dependencies**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg

# Python 3.12
brew install python@3.12
```

**Note**: macOS does not support CUDA. For GPU acceleration, you need an NVIDIA GPU on Windows or Linux.

**2.2 Install Python Dependencies**
```bash
git clone https://github.com/UV-projects/smolvlm-audio-transcription.git
cd smolvlm-audio-transcription

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Step 3: Download Models

#### 3.1 Download Vosk Speech Recognition Model

```bash
# Create Models directory
mkdir -p Models
cd Models

# Download Vosk Gigaspeech model (2.3GB)
# Option 1: Direct download
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip

# Option 2: Using curl
curl -LO https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip

# Extract
unzip vosk-model-en-us-0.42-gigaspeech.zip

# Verify structure
# Models/
#   └── vosk-model-en-us-0.42-gigaspeech/
#       ├── am/
#       ├── graph/
#       ├── ivector/
#       └── ...
```

**Alternative models** (smaller/faster):
- `vosk-model-small-en-us-0.15` (40MB) - Faster but less accurate
- `vosk-model-en-us-0.22` (1.8GB) - Good balance

#### 3.2 Download Qwen3-VL Model (llama.cpp format)

```bash
# Download from Hugging Face
# Option 1: Using huggingface-cli
pip install huggingface-hub
huggingface-cli download Qwen/Qwen3-VL-2B-Instruct-GGUF \
    Qwen3VL-2B-Instruct-Q4_K_M.gguf \
    --local-dir ./Models/Qwen3-VL

# Option 2: Manual download
# Visit: https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct-GGUF
# Download: Qwen3VL-2B-Instruct-Q4_K_M.gguf (1.05GB)
# Download: mmproj-Qwen3VL-2B-Instruct-F16.gguf (781MB)
```

**Model files needed:**
- `Qwen3VL-2B-Instruct-Q4_K_M.gguf` (1.05GB) - Main VLM model
- `mmproj-Qwen3VL-2B-Instruct-F16.gguf` (781MB) - Vision projection layer

**Note**: Update paths in `scripts/start_gpu.ps1` (line 68-69) to match your model locations.

#### 3.3 Install llama-server (llama.cpp)

**Windows:**
```powershell
# Download precompiled binary
# https://github.com/ggerganov/llama.cpp/releases
# Download: llama-b6945-bin-win-cuda-cu12.6.2-x64.zip

# Extract to C:\Tools\llama.cpp\
# Ensure llama-server.exe is in this directory

# Add CUDA DLLs to same directory:
# - cudart64_12.dll
# - cublas64_12.dll  
# - cublasLt64_12.dll
# (Copy from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\)
```

**Linux:**
```bash
# Clone and build llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build with CUDA support
mkdir build && cd build
cmake .. -DLLAMA_CUDA=ON
cmake --build . --config Release

# Binary will be at: build/bin/llama-server
```

---

### Step 4: Configuration

#### 4.1 Edit config.json

```json
{
  "vlm_endpoint": "http://localhost:8080/v1/chat/completions",
  "audio_stt_port": 8765,
  "video_port": 8766,
  "vosk_model": "Models/vosk-model-en-us-0.42-gigaspeech"
}
```

#### 4.2 Update start_gpu.ps1 Paths

Edit `scripts/start_gpu.ps1` (lines 68-70):

```powershell
$modelPath = "C:\path\to\your\Qwen3VL-2B-Instruct-Q4_K_M.gguf"
$mmprojPath = "C:\path\to\your\mmproj-Qwen3VL-2B-Instruct-F16.gguf"
$llamaExe = "C:\Tools\llama.cpp\llama-server.exe"
```

---

## 🚀 Running the System

### Method 1: Automated Start (Recommended - Windows)

```powershell
# From project root
.\scripts\start_gpu.ps1
```

**This script:**
1. Auto-detects NVIDIA GPU using `nvidia-smi`
2. Starts llama-server with Qwen3-VL + mmproj (port 8080)
3. Starts Vosk STT server (port 8765)
4. Starts Video Analyzer with ted-talk.mp4 (port 8766)

**Wait ~15-20 seconds** for all servers to initialize (Vosk model loads slowly).

### Method 2: Manual Start (All Platforms)

**Terminal 1: Vosk STT Server**
```bash
cd smolvlm-audio-transcription
python src/audio/main.py
```

Expected output:
```
Listening for audio to transcribe...
Starting WebSocket server on ws://localhost:8765
WebSocket server is now listening for connections...
```

**Terminal 2: Video Analyzer**
```bash
python src/vision/video_analyzer.py ted-talk.mp4
```

Expected output:
```
🎬 Video File Streaming Server
📹 Video Info:
   Native FPS: 25.0
   Total Frames: 18510
   Duration: 740.4s
🌐 Video Streaming WebSocket Server:
   Local:  ws://localhost:8766
✅ Connected to Vosk STT at ws://localhost:8765
🎤 Streaming audio to Vosk STT...
```

**Terminal 3: llama-server (VLM)**

**Windows:**
```powershell
cd C:\Tools\llama.cpp
.\llama-server.exe `
  --model "path\to\Qwen3VL-2B-Instruct-Q4_K_M.gguf" `
  --mmproj "path\to\mmproj-Qwen3VL-2B-Instruct-F16.gguf" `
  --port 8080 `
  --host 0.0.0.0 `
  --n-gpu-layers 99 `
  --ctx-size 8192 `
  --parallel 4
```

**Linux:**
```bash
./llama-server \
  --model /path/to/Qwen3VL-2B-Instruct-Q4_K_M.gguf \
  --mmproj /path/to/mmproj-Qwen3VL-2B-Instruct-F16.gguf \
  --port 8080 \
  --host 0.0.0.0 \
  --n-gpu-layers 99 \
  --ctx-size 8192 \
  --parallel 4
```

Expected output:
```
llama_model_load: loaded meta data with 29 key-value pairs
llama_model_load: - tensor  512: token_embd.weight     q4_K [  1024, 151936,  1,  1 ]
...
llm_load_tensors: ggml ctx size =    0.15 MiB
llm_load_tensors: offloading 29 repeating layers to GPU
llm_load_tensors: offloaded 29/29 layers to GPU
llm_load_tensors:      CUDA0 buffer size =  1799.84 MiB
```

---

### Step 5: Open Web Interface

```bash
# Open in browser
file:///path/to/smolvlm-audio-transcription/web/unified_interface.html

# Example Windows:
file:///E:/dev/ai-director/smolvlm-audio-transcription/web/unified_interface.html

# Example Linux:
file:///home/user/smolvlm-audio-transcription/web/unified_interface.html
```

**In the interface:**
1. Select **"🎬 Video File"** from dropdown (not webcam)
2. Click **"▶ Start System"**
3. Watch the magic:
   - Video frames stream at 25 FPS
   - Audio transcription appears word-by-word in **STT Response** box
   - VLM analysis appears in **VLM Response** box

---

## 📊 Architecture & Data Flow

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Browser (HTML/JS)                      │
│                 unified_interface.html                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Video Frame  │  │ STT Response │  │ VLM Response │      │
│  │   Display    │  │   Textbox    │  │   Textbox    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────┬──────────────────────┬────────────────────┬────────────┘
     │                      │                    │
     │ WebSocket 8766       │ (receives from)    │ HTTP POST
     │                      │                    │
┌────▼──────────────────────▼────────────────────▼────────────┐
│                   Video Analyzer (Python)                   │
│              src/vision/video_analyzer.py                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FFmpeg     │  │  WebSocket   │  │  WebSocket   │      │
│  │ Audio Extract│→ │  to Browser  │  │  to Vosk     │      │
│  │ 16kHz mono   │  │  (port 8766) │  │  (port 8765) │      │
│  └──────────────┘  └──────────────┘  └──────┬───────┘      │
└──────────────────────────────────────────────┼──────────────┘
                                               │
                                               │ Audio PCM data
                                               │
                          ┌────────────────────▼──────────────┐
                          │      Vosk STT (Python)            │
                          │    src/audio/main.py              │
                          │                                   │
                          │  ┌──────────────────────────┐     │
                          │  │ Vosk KaldiRecognizer     │     │
                          │  │ - Partial results        │     │
                          │  │ - Final results          │     │
                          │  └──────────────────────────┘     │
                          └────────────┬──────────────────────┘
                                       │
                                       │ Transcriptions (JSON)
                                       │
                          ┌────────────▼──────────────────────┐
                          │   Back to Video Analyzer          │
                          │   → Broadcast to Browser          │
                          └───────────────────────────────────┘

Browser also sends frames to:
                          ┌───────────────────────────────────┐
                          │   llama-server (C++)              │
                          │   Port 8080 (HTTP)                │
                          │                                   │
                          │  ┌──────────────────────────┐     │
                          │  │ Qwen3-VL-2B-Instruct     │     │
                          │  │ + mmproj (vision)        │     │
                          │  │ CUDA GPU (29/29 layers)  │     │
                          │  └──────────────────────────┘     │
                          └───────────────────────────────────┘
```

### Data Flow Details

1. **Video File Loading**:
   - User selects `ted-talk.mp4` in browser
   - Browser connects to `ws://localhost:8766` (Video Analyzer)

2. **Audio Extraction**:
   - Video Analyzer spawns FFmpeg subprocess
   - FFmpeg extracts PCM audio: `ffmpeg -i ted-talk.mp4 -f s16le -acodec pcm_s16le -ar 16000 -ac 1 pipe:1`
   - Audio chunks (4096 bytes) sent to Vosk STT via WebSocket

3. **Audio Transcription**:
   - Vosk receives PCM data
   - Processes with `KaldiRecognizer`
   - Sends partial results: `{"partial": "your cholesterol is a little"}`
   - Sends final results: `{"text": "your cholesterol is a little high"}`
   - Video Analyzer receives and forwards to browser

4. **Video Frame Streaming**:
   - Video Analyzer reads frames with OpenCV
   - Encodes as JPEG (quality 85)
   - Base64 encodes
   - Sends to browser: `{"type": "video_frame", "data": "base64..."}`

5. **VLM Analysis**:
   - Browser receives frame
   - Sends to llama-server: `POST http://localhost:8080/v1/chat/completions`
   - Payload: `{"messages": [{"role": "user", "content": [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}]}]}`
   - llama-server processes with Qwen3-VL + mmproj on GPU
   - Returns: `{"choices": [{"message": {"content": "A person is speaking at a podium..."}}]}`

---

## ⚡ Performance Benchmarks

**Test System:**
- GPU: NVIDIA GeForce RTX 2070 SUPER (8GB VRAM)
- CPU: Intel Core i7-9700K (8 cores, 16 threads)
- RAM: 32GB DDR4
- OS: Windows 11
- CUDA: 12.6

**Model Performance:**

| Component | Metric | Value |
|-----------|--------|-------|
| **Qwen3-VL-2B** | Inference Speed | ~1400 tokens/s |
| | Time per Token | ~0.70ms |
| | Image Encoding | ~400ms |
| | Total Response Time | ~2.5s (includes prompt processing) |
| | VRAM Usage | 1.8GB (1.05GB model + 0.45GB KV cache + 0.3GB compute) |
| | GPU Layers Offloaded | 29/29 (100%) |
| **Vosk STT** | Model Size | 2.3GB (gigaspeech) |
| | RAM Usage | ~7GB (loaded in memory) |
| | Latency (partial) | <0.5s |
| | Latency (final) | ~1-2s after speech ends |
| **Video Streaming** | Native FPS | 25 FPS (ted-talk.mp4) |
| | Streaming FPS | 25 FPS (native quality) |
| | Frame Size | ~50-150KB per frame (JPEG q85) |
| **FFmpeg Audio** | Sample Rate | 16000 Hz (mono) |
| | Format | PCM s16le |
| | Chunk Size | 4096 bytes |

**Note**: Performance varies based on GPU. Older/newer GPUs will see different speeds:
- **RTX 3060** (12GB): ~1800 tokens/s expected
- **RTX 4060** (8GB): ~2200 tokens/s expected  
- **GTX 1660** (6GB): ~800 tokens/s expected
- **CPU-only**: ~50-100 tokens/s (very slow, not recommended)

**VRAM Requirements by Quantization:**
- Q4_K_M (4-bit): ~1.8GB VRAM (recommended)
- Q5_K_M (5-bit): ~2.2GB VRAM
- Q8_0 (8-bit): ~3.5GB VRAM
- F16 (full precision): ~6GB VRAM

---

## 📁 Project Structure

```
smolvlm-audio-transcription/
├── src/
│   ├── audio/
│   │   ├── main.py              # Vosk STT WebSocket server
│   │   │                        # - Accepts PCM audio via WebSocket
│   │   │                        # - Returns partial + final transcriptions
│   │   │                        # - Port 8765
│   │   └── vosk_stt.py          # Vosk recognizer wrapper (legacy, not used)
│   │
│   ├── vision/
│   │   └── video_analyzer.py    # Video streaming + audio extraction
│   │                            # - Streams video frames to browser (port 8766)
│   │                            # - Extracts audio with FFmpeg
│   │                            # - Sends audio to Vosk, receives transcriptions
│   │                            # - Broadcasts transcriptions to browser
│   │
│   ├── orchestrator/            # (Optional - not used in current workflow)
│   │   └── orchestrator.py      # Coordinates multiple AI agents
│   │
│   └── presenter/               # (Optional - PDF presentation features)
│       ├── pdf_server.py        # Serves PDF slides
│       └── SlideController.py   # Controls slide navigation
│
├── web/
│   ├── unified_interface.html   # Main UI (⭐ PRIMARY INTERFACE)
│   │                            # - Video/webcam toggle
│   │                            # - Real-time transcription display
│   │                            # - VLM response display
│   │                            # - WebSocket connections to all servers
│   │
│   ├── pdf_viewer.html          # (Optional) PDF slide viewer
│   ├── test_video_connection.html # (Optional) WebSocket testing
│   └── video_interface.html     # (Optional) Old video-only interface
│
├── scripts/
│   ├── start_gpu.ps1            # ⭐ MAIN STARTUP SCRIPT (Windows)
│   │                            # - Auto GPU detection (nvidia-smi)
│   │                            # - Starts llama-server with CUDA
│   │                            # - Starts Vosk STT
│   │                            # - Starts Video Analyzer
│   │
│   ├── start_video_analyzer.ps1 # Start only video component
│   ├── start_video_analyzer.sh  # Linux version
│   ├── start_all.sh             # Linux startup (alternative)
│   └── detect_gpu.py            # Python GPU detection utility
│
├── Models/                      # ⚠️ NOT IN REPO - Download separately
│   ├── vosk-model-en-us-0.42-gigaspeech/  # Vosk STT model (2.3GB)
│   └── Qwen3-VL/                # Qwen3-VL models
│       ├── Qwen3VL-2B-Instruct-Q4_K_M.gguf      # Main model (1.05GB)
│       └── mmproj-Qwen3VL-2B-Instruct-F16.gguf  # Vision projection (781MB)
│
├── docs/                        # Documentation
│   ├── GPU_SETUP.md            # GPU setup guide
│   ├── VIDEO_AUDIO_ROUTING.md  # Architecture explanation
│   └── ...
│
├── data/                        # (Optional) Test data
│   └── try.pdf                 # Sample PDF for presentation mode
│
├── config.json                  # ⚙️ System configuration
├── requirements.txt             # 📦 Python dependencies
├── ted-talk.mp4                 # 🎬 Sample video (99MB)
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
└── README.md                    # This file
```

---

## 🎯 Usage Examples

### Example 1: Analyze Video File

```powershell
# Start system
.\scripts\start_gpu.ps1

# Open browser
# file:///E:/your/path/web/unified_interface.html

# In browser:
# 1. Select "🎬 Video File"
# 2. Click "▶ Start System"
# Result: Video plays, audio transcribed, VLM analyzes frames
```

### Example 2: Use Your Own Video

```powershell
# Start servers manually with your video
python src/audio/main.py  # Terminal 1
python src/vision/video_analyzer.py "path/to/your/video.mp4"  # Terminal 2
# Start llama-server in Terminal 3

# Open browser and start system
```

### Example 3: Use Webcam (Live)

```powershell
# Start system (llama-server + Vosk only, no video analyzer)
.\scripts\start_gpu.ps1

# In browser:
# 1. Select "📷 Webcam"  
# 2. Click "▶ Start System"
# 3. Allow camera/microphone access
# Result: Live video analyzed, live speech transcribed
```

### Example 4: Change Vosk Model (Smaller/Faster)

```bash
# Download smaller model
cd Models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip

# Edit config.json
{
  "vosk_model": "Models/vosk-model-small-en-us-0.15"
}

# Restart audio server
python src/audio/main.py
```

---

## 🔧 Troubleshooting

### 1. GPU Not Detected / Using CPU

**Symptoms:**
```
llm_load_tensors: using CUDA for GPU acceleration
llm_load_tensors: offloading 0 layers to GPU
```

**Solutions:**
```powershell
# Check CUDA installation
nvidia-smi
nvcc --version

# Check CUDA DLLs (Windows)
# Ensure these are in llama-server directory:
ls C:\Tools\llama.cpp\*.dll
# Required: cudart64_12.dll, cublas64_12.dll, cublasLt64_12.dll

# Copy DLLs if missing
copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\cudart64_12.dll" C:\Tools\llama.cpp\
copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\cublas64_12.dll" C:\Tools\llama.cpp\
copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\cublasLt64_12.dll" C:\Tools\llama.cpp\

# Verify GPU detection
cd C:\Tools\llama.cpp
.\llama-server.exe --version
```

### 2. Audio Transcription Not Working

**Symptoms:**
- STT Response box stays empty
- Console shows: "Could not connect to Vosk STT"

**Solutions:**
```powershell
# Check FFmpeg
ffmpeg -version
# If not found: choco install ffmpeg (Windows) or apt install ffmpeg (Linux)

# Check Vosk model path
ls Models/vosk-model-en-us-0.42-gigaspeech

# Check Vosk server is running
Get-NetTCPConnection -LocalPort 8765
# Should show "Listen" state

# Check audio extraction
python src/vision/video_analyzer.py ted-talk.mp4
# Look for: "✅ Connected to Vosk STT"
```

### 3. WebSocket Connection Failed

**Symptoms:**
- Browser console: "WebSocket connection failed"
- UI shows: "[Video analyzer disconnected]"

**Solutions:**
```powershell
# Check all ports are listening
Get-NetTCPConnection -LocalPort 8080,8765,8766

# Expected output:
# 8080: Listen (llama-server)
# 8765: Listen (Vosk STT)
# 8766: Listen (Video Analyzer)

# Restart servers in order:
# 1. Vosk (python src/audio/main.py)
# 2. Video Analyzer (python src/vision/video_analyzer.py ted-talk.mp4)
# 3. llama-server

# Check firewall
# Windows: Allow Python and llama-server.exe through firewall
```

### 4. Video Not Playing / Black Screen

**Symptoms:**
- Video frame display stays black
- Console: "Could not open video file"

**Solutions:**
```bash
# Check video file exists
ls ted-talk.mp4

# Check video codec
ffprobe ted-talk.mp4
# Should show: h264 video, aac audio

# Try different video
python src/vision/video_analyzer.py "path/to/other/video.mp4"

# Check OpenCV installation
python -c "import cv2; print(cv2.__version__)"
```

### 5. Out of VRAM

**Symptoms:**
```
CUDA error: out of memory
```

**Solutions:**
```powershell
# Option 1: Use smaller quantization
# Download Q4_K_M instead of Q8 or F16

# Option 2: Reduce context size
llama-server.exe --ctx-size 4096  # Instead of 8192

# Option 3: Offload fewer layers (if 4GB VRAM)
llama-server.exe --n-gpu-layers 20  # Instead of 99

# Option 4: Close other GPU applications
# Check GPU usage: nvidia-smi
```

### 6. Slow Performance / Low FPS

**Symptoms:**
- VLM takes >10s per response
- Video stutters

**Solutions:**
```powershell
# Check GPU is actually being used
nvidia-smi
# Look for "llama-server" using GPU memory

# Reduce video quality
# Edit src/vision/video_analyzer.py line 103:
# cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])  # Instead of 85

# Use smaller VLM model
# Qwen3-VL-2B Q4 is smallest, but check:
# - Qwen3-VL-1.5B (if available)
# - SmolVLM-256M (different repo)
```

### 7. Keepalive Ping Timeout (Long Videos)

**Symptoms:**
```
❌ Audio streaming error: keepalive ping timeout
```

**Solutions:**
- Already fixed in code! (`ping_interval=None` in video_analyzer.py line 161)
- If still occurs, check Vosk server is stable:
  ```powershell
  # Restart Vosk
  python src/audio/main.py
  ```

---

## 📝 Configuration Options

### config.json Fields

```json
{
  "vlm_endpoint": "http://localhost:8080/v1/chat/completions",
  "audio_stt_port": 8765,
  "video_port": 8766,
  "vosk_model": "Models/vosk-model-en-us-0.42-gigaspeech",
  
  // Optional (not currently used)
  "orchestrator_port": 9001,
  "pdf_port": 9002
}
```

### llama-server Parameters

```bash
--model <path>           # Path to GGUF model file
--mmproj <path>          # Path to vision projection file (required for VLM)
--port 8080              # HTTP server port
--host 0.0.0.0           # Listen on all interfaces (or 127.0.0.1 for localhost only)
--n-gpu-layers 99        # Offload all layers to GPU (use -1 for auto)
--ctx-size 8192          # Context window size (tokens)
--parallel 4             # Parallel requests
--threads 8              # CPU threads for non-GPU work
--flash-attn             # Use flash attention (faster)
--mlock                  # Lock model in RAM (prevent swapping)
```

### Video Analyzer Options

```python
# Edit src/vision/video_analyzer.py

# Change video FPS
VideoProcessor(video_path, use_native_fps=False)  # Use fixed 15 FPS

# Change JPEG quality
cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])  # Lower = smaller files

# Change audio chunk size
chunk_size = 8192  # Larger chunks = less frequent updates
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- **Multi-language support** (Vosk has models for 20+ languages)
- **GPU optimization** (TensorRT, quantization experiments)
- **UI enhancements** (better transcription formatting, timestamps)
- **Docker containerization**
- **Cloud deployment** (Azure, AWS, GCP)

**To contribute:**
1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📚 References & Credits

### Models & Tools
- **Qwen3-VL**: [Hugging Face](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct-GGUF) - Visual Language Model
- **llama.cpp**: [GitHub](https://github.com/ggerganov/llama.cpp) - LLM inference engine
- **Vosk**: [alphacephei.com/vosk](https://alphacephei.com/vosk/) - Offline speech recognition
- **FFmpeg**: [ffmpeg.org](https://ffmpeg.org/) - Multimedia processing
- **OpenCV**: [opencv.org](https://opencv.org/) - Computer vision library

### Documentation
- [CUDA Toolkit Docs](https://docs.nvidia.com/cuda/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.