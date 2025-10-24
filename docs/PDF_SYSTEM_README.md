# PDF Presentation Control System - Complete Guide

## Overview

This system allows you to control a PDF presentation (`try.pdf`) using voice commands. When you say trigger phrases like "next slide", the system automatically advances the presentation.

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  Audio Server   │     │  Web Client     │
│   (main.py)     │     │  (index.html)   │
│  Port 8765      │     │  Vision VLM     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │ Audio transcription   │ Vision analysis
         │                       │
         v                       v
┌────────────────────────────────────────┐
│        Orchestrator Agent              │
│       (orchestrator.py)                │
│          Port 9001                     │
│  [Rule-Based Decision Engine]          │
└────────────────┬───────────────────────┘
                 │
                 │ Slide commands
                 v
┌────────────────────────────────────────┐
│         PDF Server                     │
│       (pdf_server.py)                  │
│          Port 9002                     │
│  - Serves PDF slides as images         │
│  - Handles navigation commands         │
└────────────────────────────────────────┘
                 │
                 │ Slide updates
                 v
┌────────────────────────────────────────┐
│       PDF Viewer (Browser)             │
│      (pdf_viewer.html)                 │
│  Displays current slide                │
└────────────────────────────────────────┘
```

## Files Created

### New Components

1. **pdf_server.py** - PDF presentation server
   - Loads and serves `try.pdf`
   - Converts PDF pages to images
   - Handles slide navigation commands from Orchestrator
   - Broadcasts slide updates to all connected viewers

2. **pdf_viewer.html** - Web-based presentation viewer
   - Full-screen slide display
   - Navigation controls (Previous/Next buttons)
   - Keyboard shortcuts (Arrow keys, Space bar)
   - Real-time slide synchronization
   - Connection status indicator

3. **start_system.sh** - Complete system startup script

### Updated Components

4. **orchestrator.py** - Enhanced with PDF server integration
   - Connects to PDF server on startup
   - Sends slide control commands when voice triggers detected
   - Configured rules for "next slide", "previous slide", "open presentation"

5. **requirements.txt** - Added PDF dependencies
   - PyMuPDF (fitz) - PDF rendering
   - Pillow - Image processing

## Installation

Install the new dependencies:

```bash
pip install PyMuPDF Pillow
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

## Running the System

### Method 1: Manual Startup (Recommended for Testing)

Open **4 separate terminal windows** and run these commands in order:

**Terminal 1 - PDF Server (FIRST):**
```bash
python pdf_server.py
```

**Terminal 2 - Orchestrator (SECOND):**
```bash
python orchestrator.py
```

**Terminal 3 - Audio STT Server (THIRD):**
```bash
python main.py
```

**Terminal 4 - VLM Server (if not already running):**
```bash
# Your llama-server command here
```

Then open in your web browser:
- `pdf_viewer.html` - For the presentation display
- `index.html` - For VLM and audio control interface

### Method 2: Using the Startup Script

```bash
./start_system.sh
```

This will guide you through the startup process and start the PDF server. You'll need to manually start the other components in separate terminals.

## Using the System

### 1. PDF Viewer Controls

**Mouse Controls:**
- Click "Previous" / "Next" buttons to navigate

**Keyboard Controls:**
- `Right Arrow` or `Space` - Next slide
- `Left Arrow` - Previous slide

**Status Indicators:**
- Green "Connected" badge - Server is running
- Red "Disconnected" badge - Server is not available
- Slide counter shows current position (e.g., "3 / 10")

### 2. Voice Commands

With the audio server running and microphone active, speak these commands:

- **"next slide"** - Advances to the next slide
- **"previous slide"** - Goes back to the previous slide
- **"open presentation"** - Resets to the first slide

### 3. Vision Integration

The vision system (VLM) is already integrated but doesn't have slide control triggers by default. You can add rules in `orchestrator.py` if needed.

## Testing the System

### Test 1: Manual Navigation

1. Start the PDF server and open `pdf_viewer.html`
2. You should see the first slide of `try.pdf`
3. Click "Next" button or press Right Arrow
4. Slide should advance

### Test 2: Voice Control

1. Start all 4 servers
2. Open `pdf_viewer.html` in one browser window
3. Open `index.html` in another browser window
4. Click "Start" in the audio interface
5. Say **"next slide"** into your microphone
6. Watch the PDF viewer automatically advance

**Expected Console Output:**

**Orchestrator Terminal:**
```
============================================================
ORCHESTRATOR: Intent recognized from 'audio_stt'
ORCHESTRATOR: Trigger content: next slide...
ORCHESTRATOR: Delegating command: NEXT_SLIDE
============================================================

ORCHESTRATOR: Command sent to PDF server: NEXT_SLIDE
```

**PDF Server Terminal:**
```
PDF Server: Received command - NEXT_SLIDE
PDF Controller: Next slide -> 2/10
```

### Test 3: Multiple Viewers

1. Open `pdf_viewer.html` in multiple browser tabs/windows
2. Say "next slide" or click navigation in one viewer
3. All viewers should update simultaneously

## Troubleshooting

### Problem: "PDF file not found: try.pdf"
**Solution:** Make sure `try.pdf` is in the same directory as `pdf_server.py`

### Problem: PDF Viewer shows "Disconnected"
**Solution:** Start `pdf_server.py` before opening the viewer

### Problem: Voice commands don't control slides
**Solution:** 
1. Check that the orchestrator is running and connected to PDF server
2. Look for this message in orchestrator terminal: "Connected to PDF server at ws://localhost:9002/control"
3. Make sure audio server is running and transcribing correctly

### Problem: "Port already in use"
**Solution:** 
- Port 9002: PDF server is already running
- Port 9001: Orchestrator is already running
- Kill existing processes or change ports in the code

### Problem: Slides don't load / blank screen
**Solution:**
1. Check PDF server terminal for errors
2. Make sure PyMuPDF is installed: `pip install PyMuPDF`
3. Try a different PDF file if `try.pdf` is corrupted

## Adding More Voice Commands

Edit `orchestrator.py` and add rules to the `_initialize_rules()` method:

```python
'audio_stt': [
    {
        'trigger': 'go to slide five',
        'action': 'GO_TO_SLIDE',
        'params': {'slide_number': 4}  # 0-indexed
    },
    {
        'trigger': 'first slide',
        'action': 'GO_TO_SLIDE',
        'params': {'slide_number': 0}
    },
    # ... more rules
]
```

## Technical Details

### PDF Rendering
- Each slide is rendered at 2x resolution for high quality
- Slides are converted to PNG format
- Images are base64-encoded for WebSocket transmission

### Slide Synchronization
- All viewers are synchronized through the PDF server
- Server maintains single source of truth for current slide
- Updates are broadcast to all connected clients instantly

### WebSocket Endpoints

**PDF Server (Port 9002):**
- `/viewer` - For web browsers displaying slides
- `/control` - For orchestrator sending commands

**Orchestrator (Port 9001):**
- Main endpoint - For perception agents (audio/vision)

**Audio Server (Port 8765):**
- Main endpoint - For web client receiving transcriptions

## Future Enhancements

1**AI Summary** - Generate slide summaries with VLM
2**Smart Navigation** - "Go to the slide about X" using semantic search

## Port Reference

| Component | Port | Protocol |
|-----------|------|----------|
| PDF Server | 9002 | WebSocket |
| Orchestrator | 9001 | WebSocket |
| Audio Server | 8765 | WebSocket |
| VLM Server | 8080 | HTTP |

## File Structure

```
.
├── try.pdf                  # Your PDF presentation
├── pdf_server.py            # PDF server (NEW)
├── pdf_viewer.html          # Presentation viewer (NEW)
├── orchestrator.py          # Enhanced orchestrator
├── main.py                  # Audio STT server
├── index.html               # VLM + Audio interface
├── SlideController.py       # (Now deprecated, use pdf_server)
├── CameraController.py      # Camera stub
├── start_system.sh          # Startup helper (NEW)
├── requirements.txt         # Updated with PDF deps
└── ORCHESTRATOR_GUIDE.md    # System documentation
```

## Credits

Built with:
- PyMuPDF (fitz) - PDF rendering
- Pillow - Image processing
- websockets - Real-time communication
- Moshi - Speech-to-text

