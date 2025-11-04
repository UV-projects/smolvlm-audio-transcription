# System Startup Guide

## Overview

This multi-agent system consists of 4 main servers that work together to provide voice-controlled presentation functionality with vision analysis. This guide will help you start the system correctly.

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  VLM Server     │     │  Audio Server   │
│  (llama-server) │     │   (main.py)     │
│  Port 8080      │     │  Port 8765      │
└─────────────────┘     └────────┬────────┘
                                 │
        ┌────────────────────────┼────────────────────┐
        │                        │                    │
        v                        v                    v
┌───────────────┐    ┌────────────────────┐   ┌──────────────┐
│  Web Client   │    │   Orchestrator     │   │  PDF Server  │
│ (index.html)  │◄───┤  (orchestrator.py) │──►│(pdf_server.py)│
│ Vision VLM    │    │    Port 9001       │   │  Port 9002   │
└───────────────┘    └────────────────────┘   └──────────────┘
```

## Prerequisites

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- torch (PyTorch)
- pyaudio (Audio capture)
- numpy<2.0
- websockets (WebSocket communication)
- PyMuPDF (PDF rendering)
- Pillow (Image processing)
- openai-whisper (Speech recognition support)

### 2. Install llama.cpp (VLM Server)

```bash
brew install llama.cpp
```

### 3. Verify Microphone Permissions

Ensure Python has microphone access:
- Go to **System Preferences** → **Security & Privacy** → **Microphone**
- Check that Terminal/Python has permission

## Starting the System

### Option 1: Automatic Startup (Recommended)

Use the provided startup script that opens all servers in separate terminal windows:

```bash
cd /Users/ciwrl/PycharmProjects/smolvlm+audio
./start_all.sh
```

This will automatically:
1. Open 4 terminal windows
2. Start all servers in the correct order
3. Open the unified GUI interface in your browser

**Wait for each server to fully initialize before the system is ready (approximately 30-60 seconds).**

---

### Option 2: Manual Startup

If you prefer more control, start each component manually in separate terminal windows **in this order**:

#### Terminal 1 - VLM Server (Vision Model) 🎥

**Start first** - this takes the longest to initialize.

```bash
cd /Users/ciwrl/PycharmProjects/smolvlm+audio
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99
```

**What it does:**
- Loads the SmolVLM-500M vision model
- First run downloads ~500MB model from HuggingFace
- Listens on port **8080**
- Provides vision analysis capabilities

**Wait for:** `"HTTP server listening"` or similar message

---

#### Terminal 2 - PDF Server 📄

```bash
cd /Users/ciwrl/PycharmProjects/smolvlm+audio
python pdf_server.py
```

**What it does:**
- Loads and serves `try.pdf` presentation
- Converts PDF pages to images
- Listens on port **9002** (WebSocket control)
- Listens on port **9003** (HTTP viewer)
- Handles slide navigation commands

**Wait for:** `"PDF Server started"` message

---

#### Terminal 3 - Orchestrator Agent 🧠

```bash
cd /Users/ciwrl/PycharmProjects/smolvlm+audio
python orchestrator.py
```

**What it does:**
- Central decision-making hub
- Listens on port **9001**
- Connects to PDF server for slide control
- Receives data from Audio and Vision agents
- Applies rule-based logic to delegate actions

**Wait for:** `"ORCHESTRATOR AGENT - Starting..."` and `"Connected to PDF server"` messages

---

#### Terminal 4 - Audio Server (Speech-to-Text) 🎤

```bash
cd /Users/ciwrl/PycharmProjects/smolvlm+audio
python main.py
```

**What it does:**
- Real-time speech-to-text using Moshi STT model
- Uses `kyutai/stt-1b-en_fr` (1B parameter model)
- First run downloads ~1GB model from HuggingFace
- Listens on port **8765** (WebSocket broadcast)
- Captures microphone audio continuously
- Connects to Orchestrator

**Wait for:** `"Listening for audio to transcribe..."` message

---

## Opening the Interface

Once all servers are running, open the interface in your browser:

### Main Interface (Vision + Audio + Slides)

```bash
open unified_interface.html
```

Or navigate to: `file:///Users/ciwrl/PycharmProjects/smolvlm+audio/unified_interface.html`

**Features:**
- Live webcam feed with vision analysis
- Real-time speech transcription
- Integrated PDF presentation viewer
- Control panel for all functions

### PDF Viewer Only

```bash
open pdf_viewer.html
```

Or navigate to: `http://localhost:9003`

**Features:**
- Full-screen presentation view
- Manual navigation controls
- Voice-controlled slide changes
- Keyboard shortcuts (arrows, space)

### Speech-to-Text Test Interface

```bash
open stt_test.html
```

**Features:**
- Simple interface to test microphone and STT
- Real-time transcription display
- Connection status indicator

---

## Voice Commands

Once the system is running and your microphone is active, you can use these voice commands:

### Slide Control
- **"next slide"** - Go to next slide
- **"previous slide"** - Go to previous slide
- **"open presentation"** - Open/reset presentation

### Vision-Based Actions
The system will detect objects via webcam and can trigger actions:
- Detects **"person"** → Zoom on person
- Detects **"cardboard"** → Zoom on cardboard
- Detects **"bottle"** → Zoom on bottle

---

## Verification Checklist

After starting all servers, verify each component:

- [ ] **VLM Server** - Check Terminal 1 shows `"HTTP server listening"` on port 8080
- [ ] **PDF Server** - Check Terminal 2 shows `"PDF Server started"` on port 9002/9003
- [ ] **Orchestrator** - Check Terminal 3 shows `"Connected to PDF server"` 
- [ ] **Audio Server** - Check Terminal 4 shows `"Listening for audio to transcribe..."`
- [ ] **GUI** - Open `unified_interface.html` and click "Start"
- [ ] **Microphone** - Speak and see transcription appear
- [ ] **Voice Control** - Say "next slide" and verify slide changes

---

## Troubleshooting

### Audio Server Issues

**Problem:** Model download fails or takes too long
- **Solution:** Check internet connection. First run downloads ~1GB from HuggingFace

**Problem:** "No audio input detected"
- **Solution:** Check microphone permissions in System Preferences → Security & Privacy → Microphone

**Problem:** PyAudio errors
- **Solution:** Reinstall: `pip uninstall pyaudio && pip install pyaudio`

### VLM Server Issues

**Problem:** Command not found: llama-server
- **Solution:** Install llama.cpp: `brew install llama.cpp`

**Problem:** Model download fails
- **Solution:** Manually download from HuggingFace: https://huggingface.co/ggml-org/SmolVLM-500M-Instruct-GGUF

### PDF Server Issues

**Problem:** PDF not loading
- **Solution:** Ensure `try.pdf` exists in project directory
- **Solution:** Check PyMuPDF is installed: `pip install PyMuPDF`

**Problem:** Port already in use
- **Solution:** Kill existing process: `lsof -ti:9002 | xargs kill -9`

### Orchestrator Issues

**Problem:** "Could not connect to PDF server"
- **Solution:** Make sure PDF server (Terminal 2) is running first
- **Solution:** Check port 9002 is not blocked by firewall

### Connection Issues

**Problem:** GUI shows "Disconnected"
- **Solution:** Verify all 4 servers are running and initialized
- **Solution:** Refresh the browser page
- **Solution:** Check browser console for WebSocket errors (F12)

---

## Stopping the System

To stop all servers:

1. In each terminal window, press **Ctrl+C**
2. Or close the terminal windows
3. Or run: `pkill -f "python main.py" && pkill -f "python orchestrator.py" && pkill -f "python pdf_server.py" && pkill -f "llama-server"`

---

## System Ports Reference

| Component | Port | Protocol | Purpose |
|-----------|------|----------|---------|
| VLM Server | 8080 | HTTP | Vision model API |
| Audio Server | 8765 | WebSocket | STT broadcast |
| Orchestrator | 9001 | WebSocket | Central hub |
| PDF Server Control | 9002 | WebSocket | Slide commands |
| PDF Server HTTP | 9003 | HTTP | Viewer interface |

---

## First-Time Setup Summary

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Install llama.cpp**: `brew install llama.cpp`
3. **Grant microphone access** to Python/Terminal
4. **Run startup script**: `./start_all.sh`
5. **Wait for initialization** (~30-60 seconds)
6. **Open GUI**: Browser should open automatically, or open `unified_interface.html`
7. **Click "Start"** in the interface
8. **Test microphone**: Say "hello" and watch transcription
9. **Test slide control**: Say "next slide"

---

## Architecture Notes

### Agent Types

**Perception Agents** (Data collectors):
- Audio Server (main.py) - Captures and transcribes speech
- Web Client (index.html) - Captures video and analyzes with VLM

**Decision Agent**:
- Orchestrator (orchestrator.py) - Rule-based decision engine

**Executive Agents** (Action executors):
- PDF Server (pdf_server.py) - Controls presentation slides
- CameraController.py - Controls camera (stub)
- SlideController.py - Alternative slide control (stub)

### Data Flow

1. **Audio** → STT → JSON → Orchestrator → PDF Server → Slide Change
2. **Video** → VLM → JSON → Orchestrator → Camera Control (future)
3. All agents communicate via WebSocket protocol
4. JSON message format: `{"source": "agent_id", "content": "data"}`

---

## Additional Resources

- **ORCHESTRATOR_GUIDE.md** - Detailed orchestrator architecture
- **PDF_SYSTEM_README.md** - PDF viewer system documentation
- **GUI_GUIDE.md** - Web interface documentation
- **README.md** - Project overview
- **SETUP_GUIDE.md** - Installation and configuration

---

**Last Updated:** October 13, 2025

