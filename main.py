"""
Real-time Speech-to-Text using Moshi STT model with microphone input
Adapted for macOS with PyCharm
MODIFIED TO RUN AS A WEBSOCKET SERVER
"""

from dataclasses import dataclass
import time
import queue
import threading
import numpy as np
import sentencepiece
import torch
import pyaudio
import asyncio
import websockets
import json

from moshi.models import loaders, MimiModel, LMGen

# Global set to store all connected WebSocket clients
CONNECTED_CLIENTS = set()
# Global event loop reference
MAIN_LOOP = None
# WebSocket connection to Orchestrator
ORCHESTRATOR_CONNECTION = None

async def broadcast_text(text: str):
    """
    Send a text message to all connected clients asynchronously.
    """
    if CONNECTED_CLIENTS:
        # Create list of send tasks, one per client
        tasks = [client.send(text) for client in CONNECTED_CLIENTS]
        # Execute all send tasks in parallel
        await asyncio.gather(*tasks, return_exceptions=True)

async def send_to_orchestrator(message: str):
    """
    Send a message to the Orchestrator agent.
    """
    global ORCHESTRATOR_CONNECTION

    if ORCHESTRATOR_CONNECTION:
        try:
            await ORCHESTRATOR_CONNECTION.send(message)
        except Exception as e:
            print(f"Error sending to orchestrator: {e}")
            ORCHESTRATOR_CONNECTION = None

async def connect_to_orchestrator():
    """
    Establish connection to the Orchestrator agent.
    """
    global ORCHESTRATOR_CONNECTION
    orchestrator_uri = "ws://localhost:9001"

    try:
        ORCHESTRATOR_CONNECTION = await websockets.connect(orchestrator_uri)
        print(f"Connected to Orchestrator at {orchestrator_uri}")
    except Exception as e:
        print(f"Could not connect to Orchestrator at {orchestrator_uri}: {e}")
        print("Audio STT will continue without orchestrator integration.")
        ORCHESTRATOR_CONNECTION = None

async def connection_handler(websocket):
    """
    Handle a new WebSocket connection, adding it to the global set
    and removing it when the connection closes.
    """
    print(f"New client connected: {websocket.remote_address}")
    CONNECTED_CLIENTS.add(websocket)
    try:
        # Keep connection alive until client disconnects
        async for message in websocket:
            # Echo back any messages (optional)
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


class RealtimeSTT:
    def __init__(self, device="cpu", model_repo="kyutai/stt-1b-en_fr"):
        """
        Initialize real-time STT system

        Args:
            device: "cpu" for Intel Mac, "mps" for Apple Silicon
            model_repo: HuggingFace model repository
        """
        print(f"Loading model from {model_repo}...")
        self.device = device

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

        print(f"Model loaded. Sample rate: {self.sample_rate}Hz")
        print(f"Chunk size: {self.chunk_samples} samples ({self.chunk_duration * 1000:.1f}ms)")

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for PyAudio stream"""
        if status:
            print(f"Audio status: {status}")
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        self.audio_queue.put(audio_data)
        return (in_data, pyaudio.paContinue)

    def process_audio(self):
        """
        Process audio from the queue and broadcast transcription via WebSocket.
        This function runs in a separate thread.
        """
        print("\nListening for audio to transcribe... (Press Ctrl+C in console to stop server)")
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
                            # Send text via WebSocket in a thread-safe manner
                            asyncio.run_coroutine_threadsafe(broadcast_text(text), MAIN_LOOP)

                            # Send text to orchestrator with proper JSON format
                            orchestrator_payload = json.dumps({
                                "source": "audio_stt",
                                "content": text
                            })
                            asyncio.run_coroutine_threadsafe(
                                send_to_orchestrator(orchestrator_payload),
                                MAIN_LOOP
                            )

                    except Exception as tensor_error:
                        print(f"\nTensor conversion error: {tensor_error}")
                        continue
            except queue.Empty:
                continue
            except Exception as e:
                print(f"\nError processing audio: {e}")

    def start_microphone_stream(self):
        """
        Starts the PyAudio stream to capture microphone input.
        This method will block until stop() is called.
        """
        self.running = True

        # Start the audio processing thread
        process_thread = threading.Thread(target=self.process_audio)
        process_thread.daemon = True
        process_thread.start()

        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_samples,
            stream_callback=self.audio_callback
        )
        stream.start_stream()

        try:
            while self.running and stream.is_active():
                time.sleep(0.1)
        finally:
            print("Stopping microphone stream...")
            stream.stop_stream()
            stream.close()
            p.terminate()
            # No need to join the process_thread here because it's a daemon

    def stop(self):
        """Stop transcription"""
        self.running = False


async def main_async():
    """
    Main asynchronous function to set up STT and run the WebSocket server.
    """
    global MAIN_LOOP
    MAIN_LOOP = asyncio.get_running_loop()

    if torch.backends.mps.is_available():
        device = "mps"
        print("Using Apple Silicon GPU (MPS)")
    else:
        device = "cpu"
        print("Using CPU")

    stt = RealtimeSTT(device=device, model_repo="kyutai/stt-1b-en_fr")

    # Start microphone capture in a separate thread
    # so it doesn't block the async event loop
    mic_thread = threading.Thread(target=stt.start_microphone_stream)
    mic_thread.daemon = True
    mic_thread.start()

    # Start the WebSocket server
    host = "localhost"
    port = 8765
    print(f"Starting WebSocket server on ws://{host}:{port}")

    # Connect to Orchestrator
    await connect_to_orchestrator()

    try:
        async with websockets.serve(connection_handler, host, port):
            print("WebSocket server is now listening for connections...")
            await asyncio.Future()  # Run forever
    except OSError as e:
        print(f"Failed to start server, maybe the port {port} is already in use?")
        print(e)


if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nServer stopped by user.")