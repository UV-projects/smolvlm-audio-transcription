#!/bin/bash

# Complete System Launcher
# This script opens all 4 servers in separate terminal windows and then launches the GUI

echo "=========================================="
echo "  Complete System Launcher"
echo "  SmolVLM + Audio + PDF Presentation"
echo "=========================================="
echo ""
echo "This will start all components automatically:"
echo "  1. Ollama Server"
echo "  2. Web Server"
echo "  3. PDF Server (pdf_server.py)"
echo "  4. Orchestrator (orchestrator.py)"
echo "  5. Audio Server (main.py)"
echo "  6. Unified GUI Interface"
echo ""
echo "Starting in 3 seconds..."
echo "Press Ctrl+C to cancel"
echo ""
sleep 3

# Get the absolute path to the project directory (one level up from the script)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

echo "=========================================="
echo "Starting all servers in the background..."
echo "Project directory: $PROJECT_DIR"
echo "=========================================="
echo ""

# Terminal 1: Ollama Server
echo "✓ Starting Terminal 1: Ollama Server..."
(export OLLAMA_ORIGINS='*' && ollama serve) &
sleep 5

# Terminal 2: Web Server
echo "✓ Starting Terminal 2: Web Server..."
(cd "$PROJECT_DIR" && python -m http.server 8000) &
sleep 2

# Terminal 3: PDF Server
echo "✓ Starting Terminal 3: PDF Server (try.pdf)..."
(cd "$PROJECT_DIR" && echo '========================================' && echo 'PDF SERVER (Port 9002)' && echo '========================================' && echo '' && python src/presenter/pdf_server.py) &
sleep 2

# Terminal 4: Orchestrator
echo "✓ Starting Terminal 4: Orchestrator..."
(cd "$PROJECT_DIR" && echo '========================================' && echo 'ORCHESTRATOR (Port 9001)' && echo '========================================' && echo '' && python src/orchestrator/orchestrator.py) &
sleep 2

# Terminal 5: Audio Server
echo "✓ Starting Terminal 5: Audio Server (Speech-to-Text)..."
(cd "$PROJECT_DIR" && echo '========================================' && echo 'AUDIO SERVER (Port 8765)' && echo '========================================' && echo '' && python src/audio/main.py) &
sleep 3

echo ""
echo "=========================================="
echo "All servers are starting up..."
echo "Waiting 10 seconds for servers to initialize..."
echo "=========================================="
echo ""

# Wait for servers to fully start
sleep 10

# Open the unified GUI
echo "✓ Opening Unified GUI Interface..."
# The open command is for macOS, xdg-open is for Linux. This will try both.
open "http://localhost:8000/web/unified_interface.html" || xdg-open "http://localhost:8000/web/unified_interface.html"

echo ""
echo "=========================================="
echo "✅ SYSTEM LAUNCHED SUCCESSFULLY!"
echo "=========================================="
echo ""
echo "All components are now running:"
echo "  ✓ Ollama Server - Port 11434"
echo "  ✓ Web Server - Port 8000"
echo "  ✓ PDF Server - Port 9002"
echo "  ✓ Orchestrator - Port 9001"
echo "  ✓ Audio Server - Port 8765"
echo "  ✓ GUI Interface - Browser"
echo ""
echo "In the browser:"
echo "  1. Grant camera/microphone permissions"
echo "  2. Click '▶ Start System' button"
echo "  3. Say 'next' to change slides!"
echo ""
echo "Voice commands:"
echo "  • Say 'next' → Next slide"
echo "  • Say 'previous' → Previous slide"
echo "  • Say 'open presentation' → Go to first slide"
echo ""
echo "To stop the system:"
echo "  • Press Ctrl+C in each Terminal window"
echo "  • Or use: killall ollama python"
echo ""
echo "=========================================="
echo "Enjoy your presentation system! 🎉"
echo "=========================================="

