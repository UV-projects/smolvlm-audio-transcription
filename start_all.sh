#!/bin/bash

# Complete System Launcher
# This script opens all 4 servers in separate terminal windows and then launches the GUI

echo "=========================================="
echo "  Complete System Launcher"
echo "  SmolVLM + Audio + PDF Presentation"
echo "=========================================="
echo ""
echo "This will start all components automatically:"
echo "  1. VLM Server (llama-server)"
echo "  2. PDF Server (pdf_server.py)"
echo "  3. Orchestrator (orchestrator.py)"
echo "  4. Audio Server (main.py)"
echo "  5. Unified GUI Interface"
echo ""
echo "Starting in 3 seconds..."
echo "Press Ctrl+C to cancel"
echo ""
sleep 3

# Get the absolute path to the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "Starting all servers..."
echo "=========================================="
echo ""

# Terminal 1: VLM Server (llama-server)
echo "✓ Opening Terminal 1: VLM Server (llama-server)..."
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && echo '========================================' && echo 'VLM SERVER (Port 8080)' && echo '========================================' && echo '' && llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99\""
sleep 2

# Terminal 2: PDF Server
echo "✓ Opening Terminal 2: PDF Server (try.pdf)..."
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && echo '========================================' && echo 'PDF SERVER (Port 9002)' && echo '========================================' && echo '' && python pdf_server.py\""
sleep 2

# Terminal 3: Orchestrator
echo "✓ Opening Terminal 3: Orchestrator..."
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && echo '========================================' && echo 'ORCHESTRATOR (Port 9001)' && echo '========================================' && echo '' && python orchestrator.py\""
sleep 2

# Terminal 4: Audio Server
echo "✓ Opening Terminal 4: Audio Server (Speech-to-Text)..."
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && echo '========================================' && echo 'AUDIO SERVER (Port 8765)' && echo '========================================' && echo '' && python main.py\""
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
open "file://${PROJECT_DIR}/unified_interface.html"

echo ""
echo "=========================================="
echo "✅ SYSTEM LAUNCHED SUCCESSFULLY!"
echo "=========================================="
echo ""
echo "All components are now running:"
echo "  ✓ VLM Server - Port 8080"
echo "  ✓ PDF Server - Port 9002"
echo "  ✓ Orchestrator - Port 9001"
echo "  ✓ Audio Server - Port 8765"
echo "  ✓ GUI Interface - Browser"
echo ""
echo "In the browser:"
echo "  1. Grant camera/microphone permissions"
echo "  2. Click '▶ Start System' button"
echo "  3. Say 'next slide' to test!"
echo ""
echo "To stop the system:"
echo "  • Press Ctrl+C in each Terminal window"
echo "  • Or use: killall llama-server python"
echo ""
echo "=========================================="
echo "Enjoy your presentation system! 🎉"
echo "=========================================="

