"""
Real-time Video Analysis + Audio Transcription using SmolVLM and Moshi STT
Adapted for Windows with CUDA support
Supports VIDEO FILES instead of webcam
"""

from dataclasses import dataclass
import time
import queue
import threading
import numpy as np
import sentencepiece
import torch
import asyncio
import websockets
import cv2
import json
from pathlib import Path
from typing import Optional
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq

from moshi.models import loaders, MimiModel, LMGen

# Global sets and queues
CONNECTED_CLIENTS = set()
MAIN_LOOP = None
video_queue = queue.Queue(maxsize=10)
analysis_queue = queue.Queue(maxsize=5)  # For video descriptions

async def broadcast_message(message: dict):
    """Send JSON message to all connected clients"""
    if CONNECTED_CLIENTS:
        msg_str = json.dumps(message)
        tasks = [client.send(msg_str) for client in CONNECTED_CLIENTS]
        await asyncio.gather(*tasks, return_exceptions=True)

async def connection_handler(websocket):
    """Handle WebSocket connections"""
    print(f"New client connected: {websocket.remote_address}")
    CONNECTED_CLIENTS.add(websocket)
    try:
        async for message in websocket:
            # Handle client messages if needed
            pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        print(f"Client disconnected: {websocket.remote_address}")
        CONNECTED_CLIENTS.discard(websocket)


@dataclass
class InferenceState:
    mimi: MimiModel
    text_tokenizer: sentencepiece.SentencePieceProcessor
    lm_gen: LMGen

    def __post_init__(self):
        """Initialize streaming context after dataclass initialization"""
        self.streaming_context = self.lm_gen.streaming(batch_size=1)
        self.streaming_context.__enter__()

    def process_chunk(self, chunk: torch.Tensor, first_frame: bool = False):
        """Process a single audio chunk and return transcribed text"""
        codes = self.mimi.encode(chunk)

        if first_frame:
            tokens = self.lm_gen.step(codes)

        tokens = self.lm_gen.step(codes)

        if tokens is None:
            return None

        assert tokens.shape[1] == 1
        one_text = tokens[0, 0].cpu()

        if one_text.item() not in [0, 3]:
            text = self.text_tokenizer.id_to_piece(one_text.item())
            text = text.replace("▁", " ")
            return text

        return None

    def cleanup(self):
        """Clean up streaming context"""
        if hasattr(self, 'streaming_context'):
            self.streaming_context.__exit__(None, None, None)


class VisionAnalyzer:
    """Analyze video frames using SmolVLM - optimized for speed"""
    
    def __init__(self, model_name: str, device="cuda"):
        self.device = device
        self.model_name = model_name
        
        # Load SmolVLM model and processor
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModelForVision2Seq.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map=device,
            low_cpu_mem_usage=True
        )
        self.model.eval()
        
        # Enable optimizations for speed
        if device == "cuda":
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
        
    def analyze_frame(self, frame: np.ndarray, prompt: str = "What's happening? Be brief.") -> str:
        """Analyze a single frame and return description - optimized for speed"""
        try:
            # Convert BGR (OpenCV) to RGB (PIL)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            
            # Prepare inputs (minimal prompt for speed and brevity)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            prompt_text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
            inputs = self.processor(text=prompt_text, images=[image], return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate description - faster settings
            with torch.no_grad(), torch.cuda.amp.autocast():
                generated_ids = self.model.generate(
                    **inputs, 
                    max_new_tokens=25,   # Even shorter = faster + more concise
                    do_sample=False,     # Greedy decoding = faster
                    num_beams=1          # No beam search = faster
                )
                generated_texts = self.processor.batch_decode(
                    generated_ids,
                    skip_special_tokens=True
                )
            
            # Extract only the assistant's response
            response = generated_texts[0]
            if "Assistant:" in response:
                response = response.split("Assistant:")[-1].strip()
            
            # Trim to first sentence if too long
            if '. ' in response:
                response = response.split('. ')[0] + '.'
            
            return response
            
        except Exception as e:
            return None  # Silent fail for speed


class VideoProcessor:
    """Process video files and extract audio for transcription"""
    
    def __init__(self, video_path: str, vision_analyzer: VisionAnalyzer, analyze_every_n_frames: int = 30, device="cuda"):
        self.video_path = video_path
        self.device = device
        self.running = False
        self.cap = None
        self.vision_analyzer = vision_analyzer
        self.analyze_every_n_frames = analyze_every_n_frames  # Analyze every N frames
        self.frame_count = 0
        self.analysis_queue = queue.Queue(maxsize=2)  # Small queue to avoid lag
        
    def start_processing(self):
        """Start video processing in separate thread"""
        self.running = True
        
        # Start video reading thread
        video_thread = threading.Thread(target=self._process_video)
        video_thread.daemon = True
        video_thread.start()
        
        # Start analysis thread (runs independently)
        analysis_thread = threading.Thread(target=self._analysis_worker)
        analysis_thread.daemon = True
        analysis_thread.start()
        
    def _analysis_worker(self):
        """Worker thread that processes frames for analysis"""
        while self.running:
            try:
                frame_data = self.analysis_queue.get(timeout=0.1)
                frame, frame_num = frame_data
                
                # Analyze with SmolVLM
                description = self.vision_analyzer.analyze_frame(
                    frame, 
                    prompt="Describe what's happening."
                )
                
                if description and MAIN_LOOP:
                    message = {
                        "type": "vision_analysis",
                        "description": description,
                        "frame": frame_num
                    }
                    asyncio.run_coroutine_threadsafe(broadcast_message(message), MAIN_LOOP)
                    
            except queue.Empty:
                continue
            except Exception as e:
                pass  # Silent error handling for max speed
        
    def _process_video(self):
        """Process video file and extract frames - runs at native FPS"""
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            print(f"❌ Error: Could not open video file {self.video_path}")
            return
            
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"📹 Video: {fps:.1f} FPS, {total_frames} frames")
        print(f"🔍 Analyzing every {self.analyze_every_n_frames} frames")
        print(f"⚡ Starting real-time processing...\n")
        
        frame_delay = 1.0 / fps
        last_time = time.time()
        
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                # Loop video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.frame_count = 0
                continue
            
            # Send every Nth frame for analysis (non-blocking)
            if self.frame_count % self.analyze_every_n_frames == 0:
                if not self.analysis_queue.full():
                    # Make a copy for analysis thread
                    frame_copy = frame.copy()
                    try:
                        self.analysis_queue.put_nowait((frame_copy, self.frame_count))
                    except queue.Full:
                        pass  # Skip this analysis if queue full
                
            # Send frame to browser (compressed)
            if not video_queue.full():
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                import base64
                frame_b64 = base64.b64encode(buffer).decode('utf-8')
                try:
                    video_queue.put_nowait(frame_b64)
                except queue.Full:
                    pass  # Skip frame if queue full
                
            self.frame_count += 1
            
            # Maintain native FPS timing
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


class AudioSTT:
    """Real-time Speech-to-Text from video audio track"""
    
    def __init__(self, video_path: str, device="cuda", model_repo="kyutai/stt-1b-en_fr"):
        print(f"Loading STT model from {model_repo} on {device}...")
        self.device = device
        self.video_path = video_path
        
        # Disable PyTorch compilation and CUDA graphs to avoid compatibility issues
        import torch._dynamo
        import os
        torch._dynamo.config.suppress_errors = True
        torch._dynamo.config.disable = True
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
        
        # Disable CUDA graphs
        torch.cuda.set_stream(torch.cuda.Stream())

        checkpoint_info = loaders.CheckpointInfo.from_hf_repo(model_repo)
        self.mimi = checkpoint_info.get_mimi(device=device)
        self.text_tokenizer = checkpoint_info.get_text_tokenizer()
        lm = checkpoint_info.get_moshi(device=device)
        lm_gen = LMGen(lm, temp=0.8, temp_text=0.7, top_k=250)

        self.state = InferenceState(
            mimi=self.mimi,
            text_tokenizer=self.text_tokenizer,
            lm_gen=lm_gen
        )

        self.sample_rate = int(self.mimi.sample_rate)
        self.chunk_duration = 1.0 / self.mimi.frame_rate
        self.chunk_samples = int(self.sample_rate * self.chunk_duration)

        self.audio_queue = queue.Queue()
        self.running = False
        self.first_frame = True
        self.audio_buffer = np.array([], dtype=np.float32)

        print(f"STT Model loaded. Sample rate: {self.sample_rate}Hz")

    def extract_audio_stream(self):
        """Extract audio from video file using OpenCV"""
        cap = cv2.VideoCapture(self.video_path)
        
        # Note: OpenCV doesn't support audio extraction directly
        # We'll use ffmpeg-python for this
        import ffmpeg
        
        try:
            out, _ = (
                ffmpeg
                .input(self.video_path)
                .output('pipe:', format='f32le', acodec='pcm_f32le', ac=1, ar=self.sample_rate)
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            audio_data = np.frombuffer(out, dtype=np.float32)
            
            # Split into chunks and put in queue
            for i in range(0, len(audio_data), self.chunk_samples):
                chunk = audio_data[i:i + self.chunk_samples]
                if len(chunk) == self.chunk_samples:
                    self.audio_queue.put(chunk)
                    
        except ffmpeg.Error as e:
            print(f"Error extracting audio: {e.stderr.decode()}")

    def process_audio(self):
        """Process audio from queue and broadcast transcription"""
        print("\nProcessing audio for transcription...")
        print("-" * 50)

        while self.running:
            try:
                audio_chunk = self.audio_queue.get(timeout=0.1)
                self.audio_buffer = np.concatenate([self.audio_buffer, audio_chunk])

                while len(self.audio_buffer) >= self.chunk_samples:
                    chunk = self.audio_buffer[:self.chunk_samples]
                    self.audio_buffer = self.audio_buffer[self.chunk_samples:]

                    try:
                        chunk_tensor = torch.from_numpy(np.ascontiguousarray(chunk)).float()
                        chunk_tensor = chunk_tensor.to(device=self.device).unsqueeze(0).unsqueeze(0)

                        text = self.state.process_chunk(chunk_tensor, self.first_frame)
                        self.first_frame = False

                        if text and MAIN_LOOP:
                            message = {"type": "transcription", "text": text}
                            asyncio.run_coroutine_threadsafe(broadcast_message(message), MAIN_LOOP)

                    except Exception as tensor_error:
                        print(f"\nTensor conversion error: {tensor_error}")
                        continue
            except queue.Empty:
                continue
            except Exception as e:
                print(f"\nError processing audio: {e}")

    def start(self):
        """Start audio extraction and processing"""
        self.running = True
        
        # Extract audio in separate thread
        extract_thread = threading.Thread(target=self.extract_audio_stream)
        extract_thread.daemon = True
        extract_thread.start()
        
        # Process audio in separate thread
        process_thread = threading.Thread(target=self.process_audio)
        process_thread.daemon = True
        process_thread.start()

    def stop(self):
        """Stop audio processing"""
        self.running = False


async def video_broadcast_task():
    """Periodically broadcast video frames to clients"""
    while True:
        try:
            if not video_queue.empty():
                frame_b64 = video_queue.get_nowait()
                message = {"type": "video_frame", "data": frame_b64}
                await broadcast_message(message)
        except Exception as e:
            print(f"Error broadcasting video: {e}")
        await asyncio.sleep(0.033)  # ~30 FPS


async def main_async(video_path: str, use_audio: bool = True, analyze_every_n_frames: int = 15):
    """
    Main asynchronous function to set up video processing and WebSocket server
    """
    global MAIN_LOOP
    MAIN_LOOP = asyncio.get_running_loop()

    # Load configuration
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    active_vlm = config['active_models']['vlm']
    active_stt = config['active_models']['stt']
    
    # Get model repo names from config (nested dict structure)
    vlm_model_name = config['models']['vlm'][active_vlm]['repo']
    stt_model_name = config['models']['stt'][active_stt]['repo']

    # Determine device (CUDA or CPU)
    if torch.cuda.is_available():
        device = "cuda"
        print(f"🚀 GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB)")
    else:
        device = "cpu"
        print("⚠️ CPU mode")

    # Initialize Vision Analyzer (SmolVLM)
    print(f"🔍 Loading {config['models']['vlm'][active_vlm]['name']}...")
    
    vision_analyzer = VisionAnalyzer(vlm_model_name, device=device)
    print(f"✅ Model loaded\n")
    
    # Start video processor with vision analyzer
    video_processor = VideoProcessor(
        video_path, 
        vision_analyzer=vision_analyzer,
        analyze_every_n_frames=analyze_every_n_frames,
        device=device
    )
    video_processor.start_processing()

    # Start audio transcription if enabled
    stt = None
    if use_audio:
        try:
            print(f"\n🎤 Initializing Audio Transcription...")
            stt = AudioSTT(video_path, device=device, model_repo=stt_model_name)
            stt.start()
        except Exception as e:
            print(f"Could not start audio processing: {e}")
            print("Continuing with video only...")

    # Start video broadcast task
    asyncio.create_task(video_broadcast_task())

    # Start WebSocket server
    host = "0.0.0.0"  # Listen on all network interfaces (LAN access)
    port = 8765
    
    # Get local IP for display
    import socket
    local_ip = socket.gethostbyname(socket.gethostname())
    
    print(f"🌐 WebSocket Server:")
    print(f"   Local:  ws://localhost:{port}")
    print(f"   LAN:    ws://{local_ip}:{port}")
    print(f"📂 Open index_video.html and connect to the address above\n")

    try:
        async with websockets.serve(connection_handler, host, port):
            await asyncio.Future()  # Run forever
    except OSError as e:
        print(f"❌ Port {port} in use")
    finally:
        video_processor.stop()
        if stt:
            stt.stop()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python main_video.py <video_file> [--frames N] [--no-audio]")
        print("\nExamples:")
        print("  python main_video.py video.mp4")
        print("  python main_video.py video.mp4 --frames 10  # Analyze every 10 frames")
        print("  python main_video.py video.mp4 --no-audio")
        sys.exit(1)
    
    video_file = sys.argv[1]
    use_audio = "--no-audio" not in sys.argv
    
    # Parse --frames argument
    analyze_frames = 15  # Default: analyze every 15 frames (1 sec at 15fps)
    if "--frames" in sys.argv:
        try:
            idx = sys.argv.index("--frames")
            analyze_frames = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("⚠️ Invalid --frames value, using default (15)")
    
    if not Path(video_file).exists():
        print(f"❌ Video not found: {video_file}")
        sys.exit(1)
    
    try:
        asyncio.run(main_async(video_file, use_audio=use_audio, analyze_every_n_frames=analyze_frames))
    except KeyboardInterrupt:
        print("\n⏹️ Stopped")
