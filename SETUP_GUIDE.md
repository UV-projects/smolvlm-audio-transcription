# Setup and Run Guide for VLM + Audio Transcription App

## Prerequisites

### 1. Install System Dependencies (macOS)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PortAudio (required for PyAudio)
brew install portaudio

# Install llama.cpp
brew install llama.cpp
```

### 2. Create and Activate Virtual Environment

```bash
cd /Users/ciwrl/PycharmProjects/smolvlm+audio

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install torch sentencepiece numpy websockets
pip install pyaudio
pip install moshi
```

## Running the Application

### Step 1: Start the VLM Server (Terminal 1)

```bash
# Run llama.cpp server with SmolVLM model
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99
```

The VLM server should start on `http://localhost:8080`

### Step 2: Start the Audio Transcription Server (Terminal 2)

```bash
cd /Users/ciwrl/PycharmProjects/smolvlm+audio
source .venv/bin/activate
python main.py
```

The audio server will:
- Download the Moshi STT model (first run only)
- Start WebSocket server on `ws://localhost:8765`
- Begin listening to your microphone

### Step 3: Open the Web Interface

```bash
# Open in your default browser
open index.html
```

Or simply drag `index.html` into your browser.

### Step 4: Use the Application

1. **Grant Permissions**: Allow camera and microphone access when prompted
2. **Click "Start"**: This will activate both:
   - Video capture → VLM analysis
   - Audio capture → Real-time transcription
3. **View Results**:
   - "Response (VLM)" shows what the AI sees in your camera
   - "Audio Transcription (STT)" shows live speech-to-text
4. **Click "Stop"** when done

## Troubleshooting

### PyAudio Installation Issues
```bash
# If pip install pyaudio fails:
brew install portaudio
pip install pyaudio
```

### Port Already in Use
If port 8765 is busy:
```bash
# Find and kill the process
lsof -ti:8765 | xargs kill -9
```

### MPS (Apple Silicon GPU) Issues
The app will automatically use MPS if available, otherwise falls back to CPU.

## Quick Start (One-liner per terminal)

**Terminal 1 (VLM):**
```bash
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99
```

**Terminal 2 (Audio):**
```bash
cd /Users/ciwrl/PycharmProjects/smolvlm+audio && source .venv/bin/activate && python main.py
```

**Browser:**
Open `index.html` and click Start!

