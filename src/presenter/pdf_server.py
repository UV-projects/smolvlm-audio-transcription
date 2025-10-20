"""
PDF Presentation Server
Serves PDF slides and receives control commands from Orchestrator
"""

import asyncio
import json
import base64
import websockets
from pathlib import Path
import fitz  # PyMuPDF
from io import BytesIO
from PIL import Image

# Global state
CURRENT_SLIDE = 0
PDF_DOCUMENT = None
TOTAL_SLIDES = 0
CONNECTED_CLIENTS = set()

def load_pdf(pdf_path):
    """Load the PDF document"""
    global PDF_DOCUMENT, TOTAL_SLIDES
    try:
        PDF_DOCUMENT = fitz.open(pdf_path)
        TOTAL_SLIDES = len(PDF_DOCUMENT)
        print(f"PDF loaded: {pdf_path}")
        print(f"Total slides: {TOTAL_SLIDES}")
        return True
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return False

def get_slide_image(slide_number):
    """
    Render a specific slide as a base64-encoded image
    """
    global PDF_DOCUMENT

    if PDF_DOCUMENT is None or slide_number < 0 or slide_number >= TOTAL_SLIDES:
        return None

    try:
        page = PDF_DOCUMENT[slide_number]
        # Render page to pixmap (higher resolution)
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
        pix = page.get_pixmap(matrix=mat)

        # Convert to PNG bytes
        img_data = pix.tobytes("png")

        # Convert to base64
        img_base64 = base64.b64encode(img_data).decode('utf-8')

        return img_base64
    except Exception as e:
        print(f"Error rendering slide {slide_number}: {e}")
        return None

async def broadcast_slide_update():
    """Send current slide to all connected clients"""
    if not CONNECTED_CLIENTS:
        return

    slide_image = get_slide_image(CURRENT_SLIDE)
    if slide_image:
        message = json.dumps({
            'type': 'slide_update',
            'slide_number': CURRENT_SLIDE,
            'total_slides': TOTAL_SLIDES,
            'image': slide_image
        })

        # Send to all clients
        tasks = [client.send(message) for client in CONNECTED_CLIENTS]
        await asyncio.gather(*tasks, return_exceptions=True)

def next_slide():
    """Move to next slide"""
    global CURRENT_SLIDE
    if CURRENT_SLIDE < TOTAL_SLIDES - 1:
        CURRENT_SLIDE += 1
        print(f"PDF Controller: Next slide -> {CURRENT_SLIDE + 1}/{TOTAL_SLIDES}")
        return True
    else:
        print(f"PDF Controller: Already on last slide")
        return False

def previous_slide():
    """Move to previous slide"""
    global CURRENT_SLIDE
    if CURRENT_SLIDE > 0:
        CURRENT_SLIDE -= 1
        print(f"PDF Controller: Previous slide -> {CURRENT_SLIDE + 1}/{TOTAL_SLIDES}")
        return True
    else:
        print(f"PDF Controller: Already on first slide")
        return False

def go_to_slide(slide_number):
    """Go to specific slide (0-indexed)"""
    global CURRENT_SLIDE
    if 0 <= slide_number < TOTAL_SLIDES:
        CURRENT_SLIDE = slide_number
        print(f"PDF Controller: Go to slide -> {CURRENT_SLIDE + 1}/{TOTAL_SLIDES}")
        return True
    else:
        print(f"PDF Controller: Invalid slide number {slide_number}")
        return False

async def handle_viewer_client(websocket):
    """Handle connections from the PDF viewer (browser)"""
    client_address = websocket.remote_address
    print(f"PDF Server: Viewer connected: {client_address}")
    CONNECTED_CLIENTS.add(websocket)

    try:
        # Send initial slide
        await broadcast_slide_update()

        # Listen for client messages
        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get('command')

                if command == 'next':
                    if next_slide():
                        await broadcast_slide_update()
                elif command == 'previous':
                    if previous_slide():
                        await broadcast_slide_update()
                elif command == 'goto':
                    slide_num = data.get('slide_number', 0)
                    if go_to_slide(slide_num):
                        await broadcast_slide_update()
                elif command == 'refresh':
                    await broadcast_slide_update()

            except json.JSONDecodeError:
                print(f"PDF Server: Invalid JSON from client")

    except websockets.exceptions.ConnectionClosed:
        print(f"PDF Server: Viewer disconnected: {client_address}")
    finally:
        CONNECTED_CLIENTS.discard(websocket)

async def handle_orchestrator_commands(websocket):
    """Handle commands from the Orchestrator"""
    client_address = websocket.remote_address
    print(f"PDF Server: Orchestrator connected: {client_address}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get('action')
                params = data.get('params', {})

                print(f"PDF Server: Received command - {action}")

                if action == 'NEXT_SLIDE':
                    if next_slide():
                        await broadcast_slide_update()
                elif action == 'PREVIOUS_SLIDE':
                    if previous_slide():
                        await broadcast_slide_update()
                elif action == 'GO_TO_SLIDE':
                    slide_num = params.get('slide_number', 0)
                    if go_to_slide(slide_num):
                        await broadcast_slide_update()
                elif action == 'OPEN_PRESENTATION':
                    # Reload PDF or reset to first slide
                    go_to_slide(0)
                    await broadcast_slide_update()

            except json.JSONDecodeError:
                print(f"PDF Server: Invalid JSON from orchestrator")

    except websockets.exceptions.ConnectionClosed:
        print(f"PDF Server: Orchestrator disconnected: {client_address}")

async def route_connection(websocket):
    """Route connections based on path"""
    # In websockets 15.x, use request.path instead
    try:
        path = websocket.request.path
    except AttributeError:
        # Fallback for older versions
        path = getattr(websocket, 'path', '/')

    print(f"PDF Server: Connection received for path: {path}")

    if path == "/viewer":
        await handle_viewer_client(websocket)
    elif path == "/control":
        await handle_orchestrator_commands(websocket)
    else:
        print(f"PDF Server: Unknown path: {path}")
        await websocket.close()

async def main():
    """Start the PDF server"""
    pdf_path = Path(__file__).parent.parent.parent / "data" / "try.pdf"

    if not pdf_path.exists():
        print(f"ERROR: PDF file not found: {pdf_path}")
        return

    if not load_pdf(pdf_path):
        print("ERROR: Failed to load PDF")
        return

    host = "localhost"
    port = 9002

    print("\n" + "="*60)
    print("PDF PRESENTATION SERVER - Starting...")
    print("="*60)
    print(f"WebSocket server: ws://{host}:{port}")
    print(f"Viewer endpoint: ws://{host}:{port}/viewer")
    print(f"Control endpoint: ws://{host}:{port}/control")
    print(f"PDF loaded: {pdf_path}")
    print(f"Total slides: {TOTAL_SLIDES}")
    print("="*60 + "\n")

    try:
        async with websockets.serve(route_connection, host, port):
            print("PDF Server: Ready to serve slides...\n")
            await asyncio.Future()  # Run forever
    except OSError as e:
        print(f"PDF Server ERROR: Failed to start server on port {port}")
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nPDF Server: Shutting down...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPDF Server: Stopped by user.")
