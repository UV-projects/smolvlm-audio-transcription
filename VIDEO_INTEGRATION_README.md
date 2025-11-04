# 🎬 Video Analysis Feature - Integration Complete!

## What's New?

The AI Director system now supports **video file analysis** in addition to the existing webcam functionality! 

### ✨ Key Features

- 🔄 **Toggle between Webcam and Video File** modes in the unified interface
- 🎥 **Process pre-recorded videos** with SmolVLM vision analysis
- 🔗 **Full integration** with existing orchestrator, PDF control, and audio systems
- ⚡ **Optimized performance** with configurable frame analysis rates
- 🌐 **WebSocket streaming** of video frames and analysis results

## Quick Start

### 1. Using Video File Mode

```powershell
# Start the orchestrator (REQUIRED FIRST)
python src\orchestrator\orchestrator.py

# Start the video analyzer with your video file
.\scripts\start_video_analyzer.ps1 your_video.mp4

# Optional: Start PDF server for slide control
python src\presenter\pdf_server.py

# Optional: Start audio STT
python src\audio\main.py
```

### 2. Open the Interface

Open `web/unified_interface.html` in your browser and:
1. Select **"🎬 Video File"** from the dropdown
2. Click **"▶ Start System"**
3. Watch your video with real-time AI analysis!

### 3. Using Webcam Mode (Original)

The original webcam functionality is **completely preserved**:
1. Select **"📹 Webcam"** from the dropdown
2. Click **"▶ Start System"**
3. Everything works as before!

## File Structure

### New Files Added

```
src/
  vision/
    video_analyzer.py          # Main video processing server (NEW!)

scripts/
  start_video_analyzer.ps1     # Windows startup script (NEW!)
  start_video_analyzer.sh      # macOS/Linux startup script (NEW!)

web/
  video_interface.html         # Standalone video interface (NEW!)

docs/
  VIDEO_INTEGRATION_GUIDE.md   # Complete documentation (NEW!)

# Helper scripts from video branch
create_test_video.py           # Generate test videos
download_sample_video.ps1      # Download sample videos
download_test_videos.ps1       # Download test video pack
```

### Modified Files

```
src/
  orchestrator/
    orchestrator.py            # Added 'vision_video' source support

web/
  unified_interface.html       # Added webcam/video toggle
```

## Configuration

### Frame Analysis Rate

Control analysis frequency for performance tuning:

```powershell
# Analyze every 15 frames (default - 1 per second at 15fps)
.\scripts\start_video_analyzer.ps1 video.mp4 --frames 15

# Analyze every 5 frames (more detailed, slower)
.\scripts\start_video_analyzer.ps1 video.mp4 --frames 5

# Analyze every 30 frames (faster, less detailed)
.\scripts\start_video_analyzer.ps1 video.mp4 --frames 30
```

## Architecture

```
┌───────────────────────────────────────┐
│    Unified Interface (Browser)        │
│  [Toggle: Webcam ⟷ Video File]      │
└─────────┬─────────────────────────────┘
          │
          ├─────── Webcam Mode ──────┐
          │                          │
          │    ┌──────────────┐      │
          │    │ VLM Server   │      │
          │    │ Port: 11434  │      │
          │    └──────────────┘      │
          │                          │
          └─────── Video Mode ───────┤
                                     │
               ┌─────────────────────┤
               │ Video Analyzer      │
               │ Port: 8766 (NEW!)   │
               └─────────┬───────────┘
                         │
          ┌──────────────▼──────────────┐
          │   Orchestrator (Port 9001)  │
          │   - vision_vlm              │
          │   - vision_video (NEW!)     │
          │   - audio_stt               │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   PDF Server (Port 9002)    │
          │   Slide Control             │
          └─────────────────────────────┘
```

## Testing the Integration

### Test Video File

Use the included scripts to get test videos:

```powershell
# Download a sample TED talk video
.\download_sample_video.ps1

# Or create a simple test video
python create_test_video.py
```

### Run the System

```powershell
# Terminal 1: Orchestrator
python src\orchestrator\orchestrator.py

# Terminal 2: Video Analyzer
.\scripts\start_video_analyzer.ps1 ted-talk.mp4

# Open web\unified_interface.html
# Select "Video File" mode
# Click "Start System"
```

### Expected Output

- ✅ Video frames display in the interface
- ✅ Real-time analysis appears in the "VLM Response" box
- ✅ Orchestrator receives messages (check terminal)
- ✅ PDF slides can be controlled via voice (if PDF server running)

## Compatibility

### ✅ Fully Backwards Compatible

- All existing webcam functionality preserved
- No breaking changes to configuration
- Original interfaces still work
- Same orchestrator rules apply

### ✅ Works With

- **PDF Control**: Voice commands work in both modes
- **Audio STT**: Transcription works in both modes
- **Gesture Detection**: Compatible with both modes
- **Orchestrator**: Handles both `vision_vlm` and `vision_video` sources

## Performance

### GPU (CUDA) Recommended

- **SmolVLM Analysis**: ~50-100ms per frame
- **Video Streaming**: ~30 FPS to browser
- **Memory Usage**: ~2-3 GB VRAM

### CPU Mode

- **SmolVLM Analysis**: ~1-2 seconds per frame
- **Recommendation**: Use `--frames 30` or higher
- **Memory Usage**: ~4 GB RAM

## Troubleshooting

### "Video analyzer not running" Error

**Solution**: Make sure to start `video_analyzer.py` BEFORE opening the web interface:

```powershell
# Start this first:
.\scripts\start_video_analyzer.ps1 your_video.mp4

# Then open web\unified_interface.html
```

### Cannot Switch Modes

**Solution**: Stop the system before switching between webcam and video file modes.

### No Video Frames

**Solution**: 
- Check video file format (MP4, AVI, MOV supported)
- Verify file path is correct
- Check browser console for errors

## Documentation

- 📖 **Complete Guide**: `docs/VIDEO_INTEGRATION_GUIDE.md`
- 📖 **Main README**: `docs/README.md`
- 📖 **Orchestrator Guide**: `docs/ORCHESTRATOR_GUIDE.md`

## Next Steps

1. ✅ **Test the integration** with your own video files
2. ✅ **Adjust frame analysis rate** for optimal performance
3. ✅ **Try voice commands** while video is playing
4. ✅ **Experiment with different videos** (TED talks, presentations, etc.)

## Future Enhancements

- [ ] Video upload from browser
- [ ] Video playback controls (pause/seek/speed)
- [ ] Audio extraction from video for transcription
- [ ] Multi-video processing
- [ ] Video recording from webcam

---

**🎉 Enjoy your enhanced AI Director system with video file support!**

For questions or issues, check the documentation in `docs/` or review the integration guide.
