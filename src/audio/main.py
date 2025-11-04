"""
Real-time Speech-to-Text using Vosk STT model with microphone input
MODIFIED TO RUN AS A WEBSOCKET SERVER
"""

import os
import threading
import asyncio
import websockets
import json
from vosk_stt import VoskSTT

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
    print(f"New audio client connected: {websocket.remote_address}")
    CONNECTED_CLIENTS.add(websocket)
    
    # Create Vosk recognizer for this connection
    import vosk
    model_path = "Models/vosk-model-en-us-0.42-gigaspeech"
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, 16000)
    recognizer.SetWords(True)
    
    # Track last partial text to avoid duplicates
    last_partial = ""
    
    try:
        # Process incoming audio data
        async for message in websocket:
            if isinstance(message, bytes):
                # Binary audio data
                if recognizer.AcceptWaveform(message):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '')
                    if text:
                        print(f"📝 Final: {text}")
                        await websocket.send(json.dumps({"text": text}))
                        on_transcription(text)
                    last_partial = ""  # Reset partial
                else:
                    # Send partial results for real-time feedback
                    partial_result = json.loads(recognizer.PartialResult())
                    partial_text = partial_result.get('partial', '')
                    
                    # Only send if changed and has content
                    if partial_text and partial_text != last_partial:
                        print(f"📝 Partial: {partial_text}")
                        await websocket.send(json.dumps({"partial": partial_text}))
                        last_partial = partial_text
            elif isinstance(message, str):
                # Handle control messages (like EOF)
                msg_data = json.loads(message)
                if msg_data.get('eof'):
                    # End of audio stream
                    final_result = json.loads(recognizer.FinalResult())
                    final_text = final_result.get('text', '')
                    if final_text:
                        print(f"📝 Final: {final_text}")
                        on_transcription(final_text)
                    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        print(f"Audio client disconnected: {websocket.remote_address}")
        CONNECTED_CLIENTS.discard(websocket)


def on_transcription(text: str):
    """
    Callback function to handle transcribed text.
    This function is called from a different thread, so we use
    asyncio.run_coroutine_threadsafe to interact with the event loop.
    """
    if text and MAIN_LOOP:
        # Send text via WebSocket to all connected clients
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

async def main_async():
    """
    Main asynchronous function to set up STT and run the WebSocket server.
    """
    global MAIN_LOOP
    MAIN_LOOP = asyncio.get_running_loop()

    # --- VOSK MODEL CONFIGURATION ---
    # Model will be loaded per-connection when audio arrives
    model_path = "Models/vosk-model-en-us-0.42-gigaspeech"
    
    if not os.path.exists(model_path):
        print(f"Error: Vosk model not found at {model_path}")
        print("Please download a model from: https://alphacephei.com/vosk/models")
        return

    # No need for microphone thread - we accept audio via WebSocket
    print("\nListening for audio to transcribe... (Press Ctrl+C in console to stop server)")
    print("-" * 50)

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