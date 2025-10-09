# SmolVLM + Audio Transcription Real-time Demo

![demo](./demo.png)

This project combines **real-time vision analysis** with **live audio transcription** to create an interactive multimodal AI system. It demonstrates how to use:

- **SmolVLM (500M)** for visual understanding of your webcam feed
- **Moshi STT** for real-time speech-to-text transcription
- A simple web interface to interact with both models simultaneously

## What This Project Does

### 🎥 Real-time Vision (VLM)
- Captures video from your webcam at configurable intervals (100ms to 2s)
- Sends frames to SmolVLM for visual analysis
- You can ask questions like "What do you see?", "Count the objects", "Describe in JSON format", etc.
- Displays AI responses in real-time

### 🎤 Real-time Audio Transcription (STT)
- Continuously listens to your microphone
- Transcribes speech to text in real-time using Moshi STT model
- Displays live transcription as you speak
- Works independently of the vision model

### 🌐 Web Interface
- Simple, clean interface to view both outputs simultaneously
- Controls for starting/stopping capture
- Adjustable frame capture intervals
- Camera and microphone permission management

## Architecture

```
┌─────────────────┐
│   Web Browser   │  (index.html)
│  - Video Feed   │
│  - Transcription│
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│  VLM  │ │  Audio  │
│Server │ │ Server  │
│:8080  │ │  :8765  │
└───────┘ └─────────┘
llama.cpp  Python+WS
SmolVLM    Moshi STT
```

## Setup Instructions

### Prerequisites

- macOS (tested on Apple Silicon and Intel)
- Python 3.12+
- Homebrew (for installing llama.cpp)
- Webcam and microphone

### Step 1: Install System Dependencies

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install llama.cpp for VLM server
brew install llama.cpp

# Install PortAudio for microphone support
brew install portaudio
```

### Step 2: Set Up Python Environment

```bash
# Navigate to project directory
cd /path/to/smolvlm+audio

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install "numpy<2.0"  # Important: NumPy 1.x required for PyTorch compatibility
pip install torch sentencepiece websockets pyaudio moshi
```

### Step 3: Start the Servers

You need to run **two servers** simultaneously:

#### Terminal 1: VLM Server (Vision)
```bash
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99
```

**Notes:** 
- First run will download the SmolVLM model (~500MB)
- `-ngl 99` enables GPU acceleration (works with Apple Silicon, NVIDIA, AMD, Intel GPUs)
- Server runs on `http://localhost:8080`

#### Terminal 2: Audio Transcription Server
```bash
cd /path/to/smolvlm+audio
source .venv/bin/activate
python main.py
```

**Notes:**
- First run will download the Moshi STT model (~1-2GB)
- Automatically uses Apple Silicon GPU (MPS) if available, otherwise CPU
- WebSocket server runs on `ws://localhost:8765`

### Step 4: Open the Web Interface

```bash
open index.html
```

Or simply drag `index.html` into your browser.

### Step 5: Use the Application

1. **Grant Permissions**: 
   - Allow camera access when prompted
   - Allow microphone access when prompted

2. **Click "Start"**: Both vision and audio capture will begin

3. **Interact**:
   - **Instruction field**: Customize what you want the VLM to analyze (e.g., "What objects are on my desk?", "Count the people", "Describe the scene in JSON")
   - **Interval selector**: Choose how often to capture frames (100ms to 2s)
   - **Response (VLM)**: See what the AI sees in your camera
   - **Audio Transcription**: See your speech transcribed in real-time

4. **Click "Stop"**: Stop both captures

## Configuration Options

### VLM Server
- Change the base URL in the web interface if running on a different host/port
- Try different models from [llama.cpp multimodal models](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md)

### Audio Server
- Edit `main.py` to change:
  - Model: `model_repo="kyutai/stt-1b-en_fr"` (supports English and French)
  - Device: Force CPU or GPU usage
  - Port: Change WebSocket port from 8765

### Web Interface
- Edit `index.html` to customize:
  - Video resolution
  - UI styling
  - Default instruction
  - Capture intervals

## Troubleshooting

### NumPy/PyTorch Compatibility Error
```bash
# Ensure you're using NumPy 1.x
pip install "numpy<2.0"
```

### PyAudio Installation Issues
```bash
# Make sure PortAudio is installed first
brew install portaudio
pip install pyaudio
```

### Port Already in Use
```bash
# Kill process on port 8765 (audio server)
lsof -ti:8765 | xargs kill -9

# Kill process on port 8080 (VLM server)
lsof -ti:8080 | xargs kill -9
```

### Camera/Microphone Not Working
- Ensure you're accessing via `localhost` or `https://` (required for browser permissions)
- Check System Preferences → Privacy & Security → Camera/Microphone
- Restart the browser after granting permissions

### VLM Server Not Responding
- Wait for model download to complete (first run only)
- Check terminal for errors
- Ensure port 8080 is not blocked by firewall

## Use Cases

- 🤖 **Accessibility**: Visual assistance with voice queries
- 📹 **Real-time video analysis**: Security, monitoring, object detection
- 🎓 **Education**: Interactive learning with multimodal AI
- 🎮 **Gaming**: Voice-controlled visual game analysis
- 🔬 **Research**: Multimodal AI experimentation
- 💼 **Presentations**: Live demo of AI capabilities

## Technical Details

- **VLM Model**: SmolVLM-500M-Instruct (GGUF format)
- **STT Model**: Moshi STT 1B (English/French)
- **Frameworks**: llama.cpp, PyTorch, WebSockets
- **Frontend**: Vanilla JavaScript (no frameworks required)
- **Backend**: Python asyncio + WebSocket server

## Credits

- [SmolVLM](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct) by HuggingFace
- [Moshi STT](https://huggingface.co/kyutai) by Kyutai
- [llama.cpp](https://github.com/ggml-org/llama.cpp) by ggml.org

## License

See [LICENSE](LICENSE) file for details.
# smolvlm-audio-transcription
