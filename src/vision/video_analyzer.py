"""
Video File Streaming Server - Compatible with Existing Architecture
Streams video frames to browser clients (just like webcam mode)
Streams audio to Vosk STT server (localhost:8765)
The browser will send frames to the same Ollama VLM server used for webcam
No VLM processing in Python - keeps architecture consistent with colleagues' implementation
"""

import asyncio
import json
import websockets
import cv2
import time
import queue
import threading
import base64
import subprocess
import numpy as np
from pathlib import Path
from typing import Optional

# Global variables
CONNECTED_CLIENTS = set()
ORCHESTRATOR_CONNECTION: Optional[websockets.WebSocketClientProtocol] = None
MAIN_LOOP = None
video_queue = queue.Queue(maxsize=10)


async def broadcast_to_clients(message: dict):
    """Send JSON message to all connected web clients"""
    if CONNECTED_CLIENTS:
        msg_str = json.dumps(message)
        tasks = [client.send(msg_str) for client in CONNECTED_CLIENTS]
        await asyncio.gather(*tasks, return_exceptions=True)


async def connect_to_orchestrator():
    """Establish WebSocket connection to Orchestrator (optional)"""
    global ORCHESTRATOR_CONNECTION
    orchestrator_url = "ws://localhost:9001"
    
    # Try to connect once, but don't retry constantly (optional component)
    try:
        ORCHESTRATOR_CONNECTION = await websockets.connect(orchestrator_url)
        print(f"✅ Connected to Orchestrator at {orchestrator_url}")
        
        # Keep connection alive
        try:
            await ORCHESTRATOR_CONNECTION.wait_closed()
        except:
            pass
    except Exception as e:
        print(f"ℹ️  Orchestrator not available (optional - video streaming will work without it)")


async def client_handler(websocket):
    """Handle WebSocket connections from web clients"""
    print(f"✅ Client connected: {websocket.remote_address}")
    CONNECTED_CLIENTS.add(websocket)
    try:
        async for message in websocket:
            # Handle client commands if needed
            pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        print(f"❌ Client disconnected: {websocket.remote_address}")
        CONNECTED_CLIENTS.discard(websocket)


class VideoProcessor:
    """Process video files and stream frames to browser clients"""
    
    def __init__(self, video_path: str, use_native_fps: bool = True):
        self.video_path = video_path
        self.running = False
        self.cap = None
        self.use_native_fps = use_native_fps
        
    def start_processing(self):
        """Start video processing in separate thread"""
        self.running = True
        
        # Start video reading thread
        video_thread = threading.Thread(target=self._process_video)
        video_thread.daemon = True
        video_thread.start()
        
    def _process_video(self):
        """Process video file and extract frames for streaming"""
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            print(f"❌ Error: Could not open video file {self.video_path}")
            return
            
        native_fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / native_fps if native_fps > 0 else 0
        
        # Use native FPS for streaming
        streaming_fps = native_fps if self.use_native_fps else 15
        
        print(f"📹 Video Info:")
        print(f"   Native FPS: {native_fps:.1f}")
        print(f"   Total Frames: {total_frames}")
        print(f"   Duration: {duration:.1f}s")
        print(f"   Streaming at: {streaming_fps:.1f} FPS (native quality)")
        print(f"⚡ Starting playback...\n")
        
        frame_delay = 1.0 / streaming_fps
        frame_count = 0
        last_time = time.time()
        
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                # Loop video
                print("🔄 Restarting video...")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_count = 0
                continue
                
            # Send frame to browser (compressed JPEG)
            if not video_queue.full():
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_b64 = base64.b64encode(buffer).decode('utf-8')
                try:
                    video_queue.put_nowait(frame_b64)
                except queue.Full:
                    pass  # Skip frame if queue full
                
            frame_count += 1
            
            # Maintain target FPS timing
            elapsed = time.time() - last_time
            sleep_time = frame_delay - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            last_time = time.time()
            
    def stop(self):
        """Stop video processing"""
        self.running = False
        if self.cap:
            self.cap.release()


class AudioStreamer:
    """Extract audio from video file and stream to Vosk STT server"""
    
    def __init__(self, video_path: str, vosk_url: str = "ws://localhost:8765"):
        self.video_path = video_path
        self.vosk_url = vosk_url
        self.running = False
        self.vosk_connection = None
        
    async def connect_to_vosk(self):
        """Connect to Vosk STT WebSocket server"""
        try:
            # Disable ping timeout for long audio streams
            self.vosk_connection = await websockets.connect(
                self.vosk_url,
                ping_interval=None,  # Disable keepalive ping
                close_timeout=10
            )
            print(f"✅ Connected to Vosk STT at {self.vosk_url}")
            return True
        except Exception as e:
            print(f"❌ Could not connect to Vosk STT: {e}")
            print(f"ℹ️  Audio transcription disabled (Vosk server not running)")
            return False
    
    def extract_audio(self):
        """Extract PCM audio from video using ffmpeg (generator)"""
        try:
            # FFmpeg command to extract 16kHz mono PCM audio (Vosk format)
            cmd = [
                'ffmpeg',
                '-i', self.video_path,
                '-f', 's16le',      # 16-bit PCM
                '-acodec', 'pcm_s16le',
                '-ar', '16000',      # 16kHz sample rate (Vosk requirement)
                '-ac', '1',          # Mono channel
                'pipe:1'             # Output to stdout
            ]
            
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            
            # Read audio in chunks and yield
            chunk_size = 4096  # Standard chunk size for audio streaming
            while self.running:
                audio_chunk = self.ffmpeg_process.stdout.read(chunk_size)
                if not audio_chunk:
                    break
                yield audio_chunk
                    
            if self.ffmpeg_process:
                self.ffmpeg_process.terminate()
            
        except FileNotFoundError:
            print("❌ FFmpeg not found! Install FFmpeg to enable audio transcription.")
            print("   Download from: https://ffmpeg.org/download.html")
        except Exception as e:
            print(f"❌ Error extracting audio: {e}")
    
    async def receive_transcriptions(self):
        """Receive transcriptions from Vosk and broadcast to browser clients"""
        try:
            async for message in self.vosk_connection:
                if not self.running:
                    break
                    
                # Parse Vosk response
                try:
                    import json
                    msg_data = json.loads(message)
                    
                    # Handle partial results (real-time)
                    if 'partial' in msg_data:
                        partial_text = msg_data['partial']
                        if partial_text:
                            print(f"📝 Partial: {partial_text}")
                            # Send partial with special marker for real-time updates
                            await broadcast_to_clients({
                                "type": "transcription_partial", 
                                "text": partial_text
                            })
                    
                    # Handle final results
                    elif 'text' in msg_data:
                        final_text = msg_data['text']
                        if final_text:
                            print(f"📝 Final: {final_text}")
                            # Send final transcription with newline
                            await broadcast_to_clients({
                                "type": "transcription", 
                                "text": final_text + "\n"
                            })
                    
                    # Fallback for plain text
                    else:
                        text = str(msg_data)
                        print(f"📝 Text: {text}")
                        await broadcast_to_clients({
                            "type": "transcription", 
                            "text": text + "\n"
                        })
                        
                except json.JSONDecodeError:
                    # Plain text message
                    text = message
                    print(f"📝 Message: {text}")
                    await broadcast_to_clients({
                        "type": "transcription", 
                        "text": text + "\n"
                    })
                
        except Exception as e:
            print(f"❌ Transcription receive error: {e}")
    
    async def stream_audio(self):
        """Stream audio chunks to Vosk STT server and receive transcriptions"""
        if not await self.connect_to_vosk():
            return
            
        print("🎤 Streaming audio to Vosk STT...")
        
        # Start task to receive transcriptions
        transcription_task = asyncio.create_task(self.receive_transcriptions())
        
        try:
            for audio_chunk in self.extract_audio():
                if not self.running:
                    break
                    
                # Send binary audio data to Vosk
                if self.vosk_connection:
                    try:
                        await self.vosk_connection.send(audio_chunk)
                    except websockets.exceptions.ConnectionClosed:
                        print("⚠️  Vosk connection closed, reconnecting...")
                        if await self.connect_to_vosk():
                            # Restart transcription receiver
                            transcription_task.cancel()
                            transcription_task = asyncio.create_task(self.receive_transcriptions())
                            await self.vosk_connection.send(audio_chunk)
                        else:
                            break
                    
                # Small delay to prevent overwhelming the connection
                await asyncio.sleep(0.001)
                    
            # Send empty message to signal end
            if self.vosk_connection:
                try:
                    await self.vosk_connection.send('{"eof" : 1}')
                    print("✅ Audio streaming completed")
                except:
                    pass
                
        except Exception as e:
            print(f"❌ Audio streaming error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Wait for last transcriptions
            await asyncio.sleep(2)
            transcription_task.cancel()
            
            if self.vosk_connection:
                try:
                    await self.vosk_connection.close()
                except:
                    pass
        
    def stop(self):
        """Stop audio streaming"""
        self.running = False
        if hasattr(self, 'ffmpeg_process') and self.ffmpeg_process:
            self.ffmpeg_process.terminate()


async def video_broadcast_task():
    """Periodically broadcast video frames to clients"""
    while True:
        try:
            if not video_queue.empty():
                frame_b64 = video_queue.get_nowait()
                message = {"type": "video_frame", "data": frame_b64}
                await broadcast_to_clients(message)
        except Exception as e:
            pass
        await asyncio.sleep(0.033)  # ~30 FPS


async def main_async(video_path: str):
    """Main async function for video streaming server"""
    global MAIN_LOOP
    MAIN_LOOP = asyncio.get_running_loop()

    print(f"🎬 Video File Streaming Server")
    print(f"   Compatible with existing Ollama VLM architecture")
    print(f"   Video analysis will be done by browser → Ollama (same as webcam)")
    print()
    
    # Start video processor (native FPS for full quality)
    video_processor = VideoProcessor(video_path, use_native_fps=True)
    video_processor.start_processing()

    # Start audio streamer (sends audio to Vosk STT server)
    audio_streamer = AudioStreamer(video_path)
    audio_streamer.running = True
    asyncio.create_task(audio_streamer.stream_audio())

    # Start video broadcast task
    asyncio.create_task(video_broadcast_task())
    
    # Try to connect to orchestrator (optional - won't block if not available)
    asyncio.create_task(connect_to_orchestrator())

    # Start WebSocket server for web clients
    host = "0.0.0.0"
    port = 8766  # Different port from audio (8765)
    
    import socket
    local_ip = socket.gethostbyname(socket.gethostname())
    
    print(f"🌐 Video Streaming WebSocket Server:")
    print(f"   Local:  ws://localhost:{port}")
    print(f"   LAN:    ws://{local_ip}:{port}")
    print(f"   Quality: Native FPS (full quality)")
    print()
    print(f"📖 Usage:")
    print(f"   1. Open web/unified_interface.html in browser")
    print(f"   2. Select '🎬 Video File' from dropdown")
    print(f"   3. Click '▶ Start System'")
    print(f"   4. Frames will be sent to same Ollama server as webcam mode")
    print()

    try:
        async with websockets.serve(client_handler, host, port):
            await asyncio.Future()  # Run forever
    except OSError as e:
        print(f"❌ Port {port} already in use")
    finally:
        video_processor.stop()
        audio_streamer.stop()
        print("\n🛑 Video and audio streaming stopped")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_analyzer.py <video_file>")
        print("\nExamples:")
        print("  python video_analyzer.py video.mp4")
        print("\nStreams at native video FPS for full quality")
        sys.exit(1)
    
    video_file = sys.argv[1]
    
    if not Path(video_file).exists():
        print(f"❌ Video not found: {video_file}")
        sys.exit(1)
    
    try:
        asyncio.run(main_async(video_file))
    except KeyboardInterrupt:
        print("\n⏹️ Stopped")
