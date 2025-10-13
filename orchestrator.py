"""
Orchestrator Agent - Central decision-making hub
Receives data from perception agents (Audio STT & Vision VLM)
Applies rule-based logic to recognize intent and delegate actions
"""

import asyncio
import json
import websockets
from typing import Dict, Any, Optional

# Global set to store all connected clients
CONNECTED_CLIENTS = set()
# Connection to PDF server
PDF_SERVER_CONNECTION: Optional[websockets.WebSocketClientProtocol] = None


class OrchestratorAgent:
    """
    Central orchestrator that receives perception data and delegates actions
    based on rule-based decision logic.
    """

    def __init__(self):
        self.rules = self._initialize_rules()

    def _initialize_rules(self):
        """Initialize the rule-based decision engine"""
        return {
            'audio_stt': [
                {
                    'trigger': 'open presentation',
                    'action': 'OPEN_PRESENTATION',
                    'params': {}
                },
                {
                    'trigger': 'next slide',
                    'action': 'NEXT_SLIDE',
                    'params': {}
                },
                {
                    'trigger': 'previous slide',
                    'action': 'PREVIOUS_SLIDE',
                    'params': {}
                },
            ],
            'vision_vlm': [
                {
                    'trigger': 'cardboard',
                    'action': 'ZOOM_ON_OBJECT',
                    'params': {'target': 'cardboard'}
                },
                {
                    'trigger': 'person',
                    'action': 'ZOOM_ON_OBJECT',
                    'params': {'target': 'person'}
                },
                {
                    'trigger': 'bottle',
                    'action': 'ZOOM_ON_OBJECT',
                    'params': {'target': 'bottle'}
                },
            ]
        }

    def parse_message(self, message: str) -> Dict[str, Any]:
        """Parse incoming JSON message from perception agents"""
        try:
            data = json.loads(message)
            if 'source' not in data or 'content' not in data:
                print(f"ORCHESTRATOR ERROR: Invalid message format: {message}")
                return None
            return data
        except json.JSONDecodeError as e:
            print(f"ORCHESTRATOR ERROR: Failed to parse JSON: {e}")
            return None

    def apply_rules(self, data: Dict[str, Any]):
        """
        Apply rule-based logic to determine if action is needed.
        Checks content against triggers and delegates commands.
        """
        source = data.get('source')
        content = data.get('content', '').lower()

        if not source or not content:
            return

        # Get rules for this source
        source_rules = self.rules.get(source, [])

        # Check each rule
        for rule in source_rules:
            trigger = rule['trigger'].lower()
            if trigger in content:
                action = rule['action']
                params = rule['params']

                # Delegate action (stubbed for PoC)
                self._delegate_action(source, action, params, content)

    def _delegate_action(self, source: str, action: str, params: Dict, content: str):
        """
        Delegate actions to executive agents.
        Now actually sends commands to PDF server.
        """
        print("\n" + "="*60)
        print(f"ORCHESTRATOR: Intent recognized from '{source}'")
        print(f"ORCHESTRATOR: Trigger content: {content[:50]}...")

        if params:
            param_str = ', '.join([f"{k}='{v}'" for k, v in params.items()])
            print(f"ORCHESTRATOR: Delegating command: {action}({param_str})")
        else:
            print(f"ORCHESTRATOR: Delegating command: {action}")

        print("="*60 + "\n")

        # Send command to PDF server if it's a slide action
        if action in ['OPEN_PRESENTATION', 'NEXT_SLIDE', 'PREVIOUS_SLIDE', 'GO_TO_SLIDE']:
            asyncio.create_task(send_to_pdf_server(action, params))


async def send_to_pdf_server(action: str, params: Dict):
    """Send command to PDF server"""
    global PDF_SERVER_CONNECTION

    if PDF_SERVER_CONNECTION:
        try:
            message = json.dumps({
                'action': action,
                'params': params
            })
            await PDF_SERVER_CONNECTION.send(message)
            print(f"ORCHESTRATOR: Command sent to PDF server: {action}")
        except Exception as e:
            print(f"ORCHESTRATOR ERROR: Failed to send to PDF server: {e}")
            PDF_SERVER_CONNECTION = None


async def connect_to_pdf_server():
    """Connect to the PDF server control endpoint"""
    global PDF_SERVER_CONNECTION
    pdf_server_uri = "ws://localhost:9002/control"

    try:
        PDF_SERVER_CONNECTION = await websockets.connect(pdf_server_uri)
        print(f"ORCHESTRATOR: Connected to PDF server at {pdf_server_uri}")
    except Exception as e:
        print(f"ORCHESTRATOR: Could not connect to PDF server at {pdf_server_uri}: {e}")
        print("ORCHESTRATOR: Slide control will not be available until PDF server is running.")
        PDF_SERVER_CONNECTION = None


async def connection_handler(websocket, orchestrator: OrchestratorAgent):
    """
    Handle incoming WebSocket connections from perception agents.
    """
    client_address = websocket.remote_address
    print(f"ORCHESTRATOR: New perception agent connected: {client_address}")
    CONNECTED_CLIENTS.add(websocket)

    try:
        async for message in websocket:
            # Parse the incoming message
            data = orchestrator.parse_message(message)

            if data:
                print(f"ORCHESTRATOR: Received data from '{data.get('source')}': {data.get('content')[:50]}...")

                # Apply rule-based decision logic
                orchestrator.apply_rules(data)

    except websockets.exceptions.ConnectionClosed:
        print(f"ORCHESTRATOR: Connection closed: {client_address}")
    except Exception as e:
        print(f"ORCHESTRATOR ERROR: {e}")
    finally:
        CONNECTED_CLIENTS.discard(websocket)
        print(f"ORCHESTRATOR: Agent disconnected: {client_address}")


async def main():
    """
    Main function to start the Orchestrator WebSocket server.
    """
    orchestrator = OrchestratorAgent()

    host = "localhost"
    port = 9001

    print("\n" + "="*60)
    print("ORCHESTRATOR AGENT - Starting...")
    print("="*60)
    print(f"WebSocket server: ws://{host}:{port}")
    print("Listening for perception agents (Audio STT & Vision VLM)")
    print("="*60 + "\n")

    # Print configured rules
    print("Configured Rules:")
    for source, rules in orchestrator.rules.items():
        print(f"\n  {source}:")
        for rule in rules:
            print(f"    - Trigger: '{rule['trigger']}' -> Action: {rule['action']}")
    print("\n" + "="*60 + "\n")

    # Connect to PDF server
    await connect_to_pdf_server()

    try:
        async with websockets.serve(
            lambda ws: connection_handler(ws, orchestrator),
            host,
            port
        ):
            print("ORCHESTRATOR: Ready to receive perception data...\n")
            await asyncio.Future()  # Run forever
    except OSError as e:
        print(f"ORCHESTRATOR ERROR: Failed to start server on port {port}")
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nORCHESTRATOR: Shutting down...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nORCHESTRATOR: Stopped by user.")
