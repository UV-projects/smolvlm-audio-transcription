# Video Analysis Integration Guide

## Overview

The system now supports **both webcam and video file analysis**. You can seamlessly switch between live webcam feed and pre-recorded video files while maintaining all existing features (PDF control, audio transcription, orchestrator integration).

## Architecture Integration

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser (GUI)                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Unified Interface (Toggle: Webcam/Video)        │  │
│  │  - Live Feed Display (Webcam OR Video)           │  │
│  │  - PDF Viewer                                    │  │
│  │  - Transcription                                 │  │
│  │  - Analysis Results                              │  │
│  └──────────────────────────────────────────────────┘  │
└────┬─────────────────────┬─────────────────────────────┘
     │                     │
     │ WebSocket           │ WebSocket
     │                     │
┌────▼──────────┐    ┌─────▼─────────────┐
│  Audio STT    │    │  Video Analyzer   │
│  Port: 8765   │    │  Port: 8766       │
│               │    │  (NEW!)           │
└───────┬───────┘    └─────┬─────────────┘
        │                  │
        │ JSON Messages    │ JSON Messages
        │                  │
        └──────────┬───────┘
                   │
        ┌──────────▼─────────────┐
        │  Orchestrator Agent    │
        │  Port: 9001            │
        │  - vision_video source │
        │  - vision_vlm source   │
        │  - audio_stt source    │
        └──────────┬─────────────┘
                   │
                   │ Commands
                   │
        ┌──────────▼─────────────┐
        │  PDF Server            │
        │  Port: 9002            │
        └────────────────────────┘
```

## New Components

### 1. Video Analyzer (`src/vision/video_analyzer.py`)

**Purpose**: Process video files and send analysis to orchestrator

**Key Features**:
- Reads video files frame-by-frame
- Uses SmolVLM for visual analysis
- Sends frames to web clients via WebSocket
- Sends analysis results to orchestrator
- Configurable frame analysis rate

**Port**: `ws://localhost:8766`

**Message Format** (to Orchestrator):
```json
{
  "source": "vision_video",
  "content": "description of what's in the video"
}
```

### 2. Updated Unified Interface

**Toggle**: Dropdown selector for "📹 Webcam" or "🎬 Video File"

**Behavior**:
- **Webcam Mode**: Uses existing VLM integration via llama-server
- **Video File Mode**: Connects to video_analyzer.py server
- Seamless switching (when system is stopped)
- Same PDF and audio features in both modes

### 3. Extended Orchestrator Rules

The orchestrator now recognizes `vision_video` as a source:

```python
'vision_video': [
    {
        'trigger': 'cardboard',
        'action': 'ZOOM_ON_OBJECT',
        'params': {'target': 'cardboard'}
    },
    # ... more rules
]
```

## How to Use

### Option 1: Webcam Mode (Existing Functionality)

1. Start all servers:
   ```bash
   # Terminal 1: Orchestrator
   python src/orchestrator/orchestrator.py
   
   # Terminal 2: PDF Server
   python src/presenter/pdf_server.py
   
   # Terminal 3: Audio STT
   python src/audio/main.py
   
   # Terminal 4: VLM Server (llama-server)
   llama-server --model path/to/smolvlm.gguf -ngl 99
   ```

2. Open `web/unified_interface.html`
3. Ensure "📹 Webcam" is selected
4. Click "▶ Start System"

### Option 2: Video File Mode (NEW!)

1. Start all servers:
   ```bash
   # Terminal 1: Orchestrator
   python src/orchestrator/orchestrator.py
   
   # Terminal 2: PDF Server
   python src/presenter/pdf_server.py
   
   # Terminal 3: Audio STT (optional)
   python src/audio/main.py
   
   # Terminal 4: Video Analyzer
   python src/vision/video_analyzer.py your_video.mp4
   
   # OR use the startup script:
   .\scripts\start_video_analyzer.ps1 your_video.mp4
   ```

2. Open `web/unified_interface.html`
3. Select "🎬 Video File" from the dropdown
4. Click "▶ Start System"

### Video Analyzer Script Options

**Windows (PowerShell)**:
```powershell
.\scripts\start_video_analyzer.ps1 video.mp4
.\scripts\start_video_analyzer.ps1 video.mp4 --frames 10  # Analyze every 10 frames
```

**macOS/Linux (Bash)**:
```bash
chmod +x scripts/start_video_analyzer.sh
./scripts/start_video_analyzer.sh video.mp4
./scripts/start_video_analyzer.sh video.mp4 --frames 10
```

**Direct Python**:
```bash
python src/vision/video_analyzer.py video.mp4
python src/vision/video_analyzer.py video.mp4 --frames 15  # Default: 15
```

## Configuration

### Frame Analysis Rate

Control how often frames are analyzed to balance speed vs. accuracy:

```bash
# Analyze every 5 frames (faster, less detailed)
python src/vision/video_analyzer.py video.mp4 --frames 5

# Analyze every 30 frames (slower, more efficient)
python src/vision/video_analyzer.py video.mp4 --frames 30
```

**Recommended Settings**:
- **15 FPS video**: `--frames 15` (analyze 1 frame/sec)
- **30 FPS video**: `--frames 30` (analyze 1 frame/sec)
- **60 FPS video**: `--frames 60` (analyze 1 frame/sec)
- **High detail needed**: `--frames 5` (analyze 3 times/sec at 15 FPS)

### Model Configuration

Edit `config.json` to change the vision model:

```json
{
  "active_models": {
    "vlm": "smolvlm-500m"
  },
  "models": {
    "vlm": {
      "smolvlm-500m": {
        "name": "SmolVLM2-500M-Instruct",
        "repo": "HuggingFaceTB/SmolVLM2-500M-Instruct"
      }
    }
  }
}
```

## Testing the Integration

### Test 1: Video File Analysis

1. Start orchestrator and video analyzer
2. Open unified interface, select "Video File" mode
3. Click Start
4. You should see:
   - Video frames playing in the interface
   - Analysis descriptions updating
   - Orchestrator receiving messages (check terminal)

### Test 2: Webcam Mode (Existing)

1. Start orchestrator and llama-server
2. Open unified interface, select "Webcam" mode
3. Click Start
4. Original functionality should work unchanged

### Test 3: Switch Between Modes

1. Start with webcam mode
2. Click Stop
3. Switch to video file mode
4. Click Start
5. Switch should be seamless with no errors

### Test 4: PDF + Video Integration

1. Start all servers including PDF server
2. Use video file mode
3. Say "next slide" during video playback
4. PDF should advance while video continues playing

## Troubleshooting

### Video Analyzer Connection Failed

**Error**: `[Error: Video analyzer not running]`

**Solution**:
- Ensure `video_analyzer.py` is running before clicking Start
- Check that port 8766 is not in use: `netstat -ano | findstr 8766`
- Verify video file path is correct

### No Video Frames Displayed

**Issue**: Black screen in video file mode

**Solution**:
- Check video file format (supported: MP4, AVI, MOV, MKV)
- Verify OpenCV can read the file
- Check browser console for WebSocket errors

### Analysis Not Sent to Orchestrator

**Issue**: Video plays but no analysis in orchestrator logs

**Solution**:
- Ensure orchestrator is running BEFORE video analyzer
- Check orchestrator terminal for connection messages
- Verify `vision_video` rules are in orchestrator.py

### Toggle Doesn't Work

**Issue**: Cannot switch between webcam and video

**Solution**:
- Stop the system before switching (required)
- Check that both video sources are properly initialized
- Clear browser cache and refresh page

## Performance Tips

### GPU Acceleration

Both webcam and video modes support CUDA:

```python
# Auto-detects CUDA if available
if torch.cuda.is_available():
    device = "cuda"
```

**Expected Performance**:
- **CUDA (GPU)**: ~50-100ms per frame analysis
- **CPU**: ~1-2 seconds per frame analysis

### Memory Usage

- **Video Analyzer**: ~2-3 GB VRAM (GPU) or ~4 GB RAM (CPU)
- **Webcam VLM**: ~2 GB VRAM (via llama-server)
- **Audio STT**: ~1-2 GB RAM

### Optimization Settings

**For Real-time Performance**:
```bash
# Analyze fewer frames
python src/vision/video_analyzer.py video.mp4 --frames 30
```

**For Maximum Detail**:
```bash
# Analyze more frames (slower)
python src/vision/video_analyzer.py video.mp4 --frames 5
```

## API Reference

### Video Analyzer WebSocket (Port 8766)

**Client → Server**: (None currently, bidirectional support ready)

**Server → Client**:

```json
// Video frame update
{
  "type": "video_frame",
  "data": "base64_encoded_jpeg"
}

// Vision analysis result
{
  "type": "vision_analysis",
  "description": "A person walking in a park",
  "frame": 150
}
```

### Orchestrator Messages

**From Video Analyzer**:
```json
{
  "source": "vision_video",
  "content": "description text"
}
```

## Backwards Compatibility

✅ **All existing features preserved**:
- Webcam mode works exactly as before
- PDF control unchanged
- Audio transcription unchanged
- Orchestrator rules for `vision_vlm` and `audio_stt` unchanged

✅ **New features are additive**:
- Video file mode is optional
- Original interfaces (`index.html`, `pdf_viewer.html`) still work
- No breaking changes to configuration

## Future Enhancements

Planned features:
- [ ] Video upload from browser
- [ ] Real-time video file selection in UI
- [ ] Video playback controls (pause, seek, speed)
- [ ] Multi-video support
- [ ] Video recording from webcam
- [ ] Side-by-side webcam + video comparison
- [ ] Audio extraction from video files for transcription

## Credits

- **Video Analysis**: SmolVLM2-500M-Instruct by HuggingFace
- **Integration**: Built on existing orchestrator architecture
- **Compatible with**: PDF control, audio STT, gesture detection

---

**Need Help?** Check the main README.md or existing documentation in `docs/`
