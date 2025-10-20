"""
Real-time Speech-to-Text using Vosk STT model with microphone input
MODIFIED TO RUN AS A WEBSOCKET SERVER
"""

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
    # IMPORTANT: You need to download a Vosk model and place it in the `Models` directory.
    # Download from: https://alphacephei.com/vosk/models
    # For example, download 'vosk-model-small-en-us-0.15' and unzip it to 'Models/vosk-model-small-en-us-0.15'
    model_path = "Models/vosk-model-en-us-0.42-gigaspeech"

    try:
        stt = VoskSTT(model_path=model_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please make sure the Vosk model is in the correct path.")
        return

    # Start microphone capture and transcription in a separate thread
    # so it doesn't block the async event loop
    mic_thread = threading.Thread(target=stt.process_audio, args=(on_transcription,))
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