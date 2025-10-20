# Orchestrator Agent System - Implementation Guide

## Overview

This system implements an **Orchestrator-based multi-agent architecture** where independent perception agents (Audio STT and Vision VLM) send data to a central Orchestrator, which applies rule-based logic to recognize user intent and delegate actions to executive agents.

## System Architecture

```
+-------------------+      +--------------------+
| Audio Server      |      | Web Client (VLM)   |
| (main.py)         |      | (index.html)       |
+--------+----------+      +----------+---------+
         | (audio text)               | (vision text)
         |                            |
         v                            v
+--------+----------------------------+---------+
|                                              |
|         Orchestrator Agent (WebSocket)       |
|            (orchestrator.py)                 |
|                                              |
|      [ Rule-Based Decision Engine ]          |
|                                              |
+---------------------+------------------------+
                      | (Delegated Commands)
                      |
                      v
+---------------------+------------------------+
|                                              |
|   Executive Agents (Currently Log Stubs)     |
|   - SlideController.py                       |
|   - CameraController.py                      |
|                                              |
+----------------------------------------------+
```

## Components

### 1. Orchestrator Agent (`orchestrator.py`)

**Purpose**: Central decision-making hub that receives perception data and delegates actions.

**Port**: `ws://localhost:9001`

**Key Features**:
- WebSocket server listening for perception data
- JSON message parser expecting format:
  ```json
  {
    "source": "[SOURCE_AGENT_ID]",
    "content": "[DATA_PAYLOAD]"
  }
  ```
- Rule-based decision engine with configurable triggers
- Action delegation (currently stubbed with console logs)

**Pre-configured Rules**:

*Audio STT Triggers*:
- `"open presentation"` → `OPEN_PRESENTATION`
- `"next slide"` → `NEXT_SLIDE`
- `"previous slide"` → `PREVIOUS_SLIDE`

*Vision VLM Triggers*:
- `"cardboard"` → `ZOOM_ON_OBJECT(target='cardboard')`
- `"person"` → `ZOOM_ON_OBJECT(target='person')`
- `"bottle"` → `ZOOM_ON_OBJECT(target='bottle')`

### 2. Audio Server (`main.py`)

**Purpose**: Transcribes audio in real-time and forwards to Orchestrator.

**Port**: `ws://localhost:8765` (for web client connections)

**Changes Made**:
- Added `ORCHESTRATOR_CONNECTION` global variable
- Added `send_to_orchestrator()` function to forward data
- Added `connect_to_orchestrator()` function to establish connection
- Modified `process_audio()` to send JSON-formatted messages:
  ```python
  {
      "source": "audio_stt",
      "content": transcribed_text
  }
  ```

### 3. Web Client (`index.html`)

**Purpose**: Captures video, runs VLM inference, and forwards results to Orchestrator.

**Changes Made**:
- Added `orchestratorSocket` WebSocket client
- Added `setupOrchestratorWebSocket()` function
- Modified `sendData()` to forward VLM responses:
  ```javascript
  {
      source: "vision_vlm",
      content: vlm_response
  }
  ```
- Connects to Orchestrator on "Start" button click
- Disconnects on "Stop" button click

### 4. Executive Agents (Stubs)

**SlideController.py**:
- Methods: `open_presentation()`, `next_slide()`, `previous_slide()`, `go_to_slide()`
- Currently prints actions to console
- Future: Integrate with PowerPoint/Keynote APIs

**CameraController.py**:
- Methods: `zoom_on_object()`, `zoom_in()`, `zoom_out()`, `reset_zoom()`, `pan_to()`
- Currently prints actions to console
- Future: Integrate with camera control APIs

## Running the System

### Step 1: Start the Orchestrator (REQUIRED FIRST)

```bash
python orchestrator.py
```

Expected output:
```
============================================================
ORCHESTRATOR AGENT - Starting...
============================================================
WebSocket server: ws://localhost:9001
Listening for perception agents (Audio STT & Vision VLM)
============================================================

Configured Rules:
  audio_stt:
    - Trigger: 'open presentation' -> Action: OPEN_PRESENTATION
    - Trigger: 'next slide' -> Action: NEXT_SLIDE
    - Trigger: 'previous slide' -> Action: PREVIOUS_SLIDE
  vision_vlm:
    - Trigger: 'cardboard' -> Action: ZOOM_ON_OBJECT
    - Trigger: 'person' -> Action: ZOOM_ON_OBJECT
    - Trigger: 'bottle' -> Action: ZOOM_ON_OBJECT
============================================================

ORCHESTRATOR: Ready to receive perception data...
```

### Step 2: Start the Audio Server

```bash
python main.py
```

The audio server will automatically attempt to connect to the Orchestrator.

Expected output:
```
Connected to Orchestrator at ws://localhost:9001
Starting WebSocket server on ws://localhost:8765
```

### Step 3: Start the VLM Server (if not already running)

```bash
# Follow your existing llama-server setup
```

### Step 4: Open the Web Interface

Open `index.html` in a web browser and click "Start".

The browser will automatically connect to both:
- Audio server (`ws://localhost:8765`)
- Orchestrator (`ws://localhost:9001`)

## Testing the System

### Test 1: Audio Trigger

1. With all servers running, speak into your microphone: **"open presentation"**
2. Check the Orchestrator console for output:
   ```
   ============================================================
   ORCHESTRATOR: Intent recognized from 'audio_stt'
   ORCHESTRATOR: Trigger content: open presentation...
   ORCHESTRATOR: Delegating command: OPEN_PRESENTATION
   ============================================================
   ```

### Test 2: Vision Trigger

1. Hold a cardboard box in front of your camera
2. Wait for the VLM to process and respond with text containing "cardboard"
3. Check the Orchestrator console for output:
   ```
   ============================================================
   ORCHESTRATOR: Intent recognized from 'vision_vlm'
   ORCHESTRATOR: Trigger content: I see a cardboard box...
   ORCHESTRATOR: Delegating command: ZOOM_ON_OBJECT(target='cardboard')
   ============================================================
   ```

## Adding New Rules

Edit `orchestrator.py` and modify the `_initialize_rules()` method:

```python
def _initialize_rules(self):
    return {
        'audio_stt': [
            {
                'trigger': 'your trigger phrase',
                'action': 'YOUR_ACTION_NAME',
                'params': {'key': 'value'}  # optional parameters
            },
        ],
        'vision_vlm': [
            {
                'trigger': 'object name',
                'action': 'YOUR_ACTION_NAME',
                'params': {'target': 'object name'}
            },
        ]
    }
```

## Future Enhancements

### 1. Executive Agent Integration
- Modify `_delegate_action()` in `orchestrator.py` to actually call executive agents
- Example:
  ```python
  if action == "OPEN_PRESENTATION":
      self.slide_controller.open_presentation()
  elif action == "ZOOM_ON_OBJECT":
      self.camera_controller.zoom_on_object(params['target'])
  ```

### 2. Advanced Decision Logic
- Replace rule-based engine with ML-based intent recognition
- Use LLM for natural language understanding
- Implement context-aware decision making

### 3. Executive Agent WebSockets
- Create WebSocket servers for each executive agent
- Send commands via WebSocket instead of direct function calls
- Enable distributed agent deployment

### 4. Feedback Loop
- Executive agents send status updates back to Orchestrator
- Orchestrator confirms action completion
- Web UI displays action status

## Troubleshooting

**Problem**: Orchestrator connection fails
- **Solution**: Make sure `orchestrator.py` is running before starting `main.py` or opening the web page

**Problem**: No actions triggered
- **Solution**: Check that your speech/vision content exactly matches the trigger phrases (case-insensitive)

**Problem**: Port already in use
- **Solution**: Kill existing processes or change port numbers in all three files

## Message Format Specification

All messages sent to the Orchestrator MUST follow this JSON format:

```json
{
  "source": "audio_stt" | "vision_vlm",
  "content": "string containing the perception data"
}
```

The Orchestrator will reject malformed messages and log an error.

