# Video File Audio Routing Solution

## Problem
- Current system: Audio STT only listens to **microphone**
- When "Video File" is selected, video frames are displayed but **audio is not processed**
- Need: Route video file audio to Vosk STT when Video File mode is active

## Architecture Options

### Option 1: Browser-based (RECOMMENDED)
**Pros:**
- No Python audio extraction needed
- Works with existing WebSocket architecture
- Browser natively handles video/audio sync

**Implementation:**
1. Add hidden `<video>` element that plays video file
2. Use Web Audio API to capture audio from video element
3. Send audio chunks to Vosk via WebSocket (same as microphone)
4. Switch between microphone and video audio based on `currentVideoSource`

### Option 2: Python-based (Complex)
Extract audio in `video_analyzer.py` using FFmpeg/PyDub and stream separately.

**Cons:**
- Requires FFmpeg installation
- Complex synchronization with video frames
- Higher server load

## Solution: Browser Web Audio API

### Changes Required

#### 1. `unified_interface.html`
```javascript
let audioContext;
let microphoneStream;
let videoElement; // Hidden video element for audio playback
let audioSourceNode;

// Setup audio from video file
function setupVideoAudio() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    // Create hidden video element
    if (!videoElement) {
        videoElement = document.createElement('video');
        videoElement.src = 'ted-talk.mp4'; // Match video file in video_analyzer.py
        videoElement.muted = true; // Mute DOM playback (we capture via Web Audio)
        document.body.appendChild(videoElement);
    }
    
    // Create audio source from video
    audioSourceNode = audioContext.createMediaElementSource(videoElement);
    const processor = audioContext.createScriptProcessor(4096, 1, 1);
    
    processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        // Convert Float32Array to Int16Array for Vosk
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
            pcmData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
        }
        // Send to Vosk
        if (sttSocket && sttSocket.readyState === WebSocket.OPEN) {
            sttSocket.send(pcmData.buffer);
        }
    };
    
    audioSourceNode.connect(processor);
    processor.connect(audioContext.destination);
    
    // Start playing
    videoElement.play();
}

// Modified handleStart()
function handleStart() {
    // ... existing code ...
    
    if (currentVideoSource === 'webcam') {
        // Use microphone (existing code)
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                microphoneStream = stream;
                // Send mic audio to Vosk
            });
    } else {
        // Use video file audio
        setupVideoAudio();
    }
}
```

#### 2. Alternative: Server-side Audio Streaming
If browser approach doesn't work, modify `video_analyzer.py`:

```python
import subprocess
import numpy as np

class VideoProcessor:
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.audio_process = None
    
    def start_audio_stream(self):
        """Extract audio using FFmpeg and stream to Vosk"""
        # FFmpeg command to extract PCM audio
        cmd = [
            'ffmpeg',
            '-i', self.video_path,
            '-f', 's16le',  # 16-bit PCM
            '-acodec', 'pcm_s16le',
            '-ar', '16000',  # 16kHz for Vosk
            '-ac', '1',  # Mono
            'pipe:1'
        ]
        
        self.audio_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        
        # Read and send audio chunks
        chunk_size = 4096
        while self.running:
            audio_chunk = self.audio_process.stdout.read(chunk_size)
            if not audio_chunk:
                break
            # Send to Vosk WebSocket at localhost:8765
            asyncio.create_task(self.send_audio_to_vosk(audio_chunk))
```

## Recommended Approach
**Use Browser Web Audio API (Option 1)** because:
1. Simpler implementation
2. No FFmpeg dependency
3. Better sync with video frames
4. Lower server load

## Testing
1. Select "Video File" from dropdown
2. Click "Start System"
3. Verify:
   - Video frames display
   - Audio transcription appears in STT Response box
   - Transcription matches video audio (not microphone)
4. Switch to "Webcam"
5. Verify:
   - Webcam video shows
   - Microphone audio transcription works

## Known Limitations
- Video file must be accessible to browser (served via HTTP or file://)
- CORS may block video loading from different origin
- Solution: Serve video from `serve_html.py` or copy to `web/` folder
