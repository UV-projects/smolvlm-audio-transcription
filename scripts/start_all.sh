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

# Get the absolute path to the project directory (one level up from the script)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

echo "=========================================="
echo "Starting all servers in the background..."
echo "Project directory: $PROJECT_DIR"
echo "=========================================="
echo ""

# Terminal 1: VLM Server (llama-server)
echo "✓ Starting Terminal 1: VLM Server (llama-server, version b6610)..."
# Download mmproj file first using llama-server in a way that caches it
echo "Downloading vision model components..."
(cd "$PROJECT_DIR" && llama-server --hf-repo ggml-org/SmolVLM2-2.2B-Instruct-GGUF --hf-file mmproj-SmolVLM2-2.2B-Instruct-f16.gguf --version > /dev/null 2>&1 || true) &
DOWNLOAD_PID=$!
sleep 5
kill $DOWNLOAD_PID 2>/dev/null || true
wait $DOWNLOAD_PID 2>/dev/null || true

# Now start the actual server with both files
# Detect OS for correct cache path
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    MMPROJ_FILE="$HOME/Library/Caches/llama.cpp/ggml-org_SmolVLM2-2.2B-Instruct-GGUF_mmproj-SmolVLM2-2.2B-Instruct-f16.gguf"
else
    # Assume Linux-like
    MMPROJ_FILE="$HOME/.cache/llama.cpp/ggml-org_SmolVLM2-2.2B-Instruct-GGUF_mmproj-SmolVLM2-2.2B-Instruct-f16.gguf"
fi

# Check if the mmproj file exists before trying to use it
if [ ! -f "$MMPROJ_FILE" ]; then
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! ERROR: Vision model file not found! !!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Looked for mmproj file at: $MMPROJ_FILE"
    echo "The script tried to download it, but it might have failed."
    echo "Please try running this command manually to download the vision model components:"
    echo "llama-server --hf-repo ggml-org/SmolVLM2-2.2B-Instruct-GGUF --hf-file mmproj-SmolVLM2-2.2B-Instruct-f16.gguf --version"
    echo "Aborting startup."
    exit 1
fi

(cd "$PROJECT_DIR" && echo '========================================' && echo 'VLM SERVER (Port 8080)' && echo '========================================' && echo '' && llama-server --hf-repo ggml-org/SmolVLM2-2.2B-Instruct-GGUF --hf-file SmolVLM2-2.2B-Instruct-Q4_K_M.gguf --mmproj "$MMPROJ_FILE" --host 0.0.0.0) &
sleep 2

# Terminal 2: PDF Server
echo "✓ Starting Terminal 2: PDF Server (try.pdf)..."
(cd "$PROJECT_DIR" && echo '========================================' && echo 'PDF SERVER (Port 9002)' && echo '========================================' && echo '' && python src/presenter/pdf_server.py) &
sleep 2

# Terminal 3: Orchestrator
echo "✓ Starting Terminal 3: Orchestrator..."
(cd "$PROJECT_DIR" && echo '========================================' && echo 'ORCHESTRATOR (Port 9001)' && echo '========================================' && echo '' && python src/orchestrator/orchestrator.py) &
sleep 2

# Terminal 4: Audio Server
echo "✓ Starting Terminal 4: Audio Server (Speech-to-Text)..."
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
open "file://${PROJECT_DIR}/web/unified_interface.html" || xdg-open "file://${PROJECT_DIR}/web/unified_interface.html"

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
echo "  3. Say 'next' to change slides!"
echo ""
echo "Voice commands:"
echo "  • Say 'next' → Next slide"
echo "  • Say 'previous' → Previous slide"
echo "  • Say 'open presentation' → Go to first slide"
echo ""
echo "To stop the system:"
echo "  • Press Ctrl+C in each Terminal window"
echo "  • Or use: killall llama-server python"
echo ""
echo "=========================================="
echo "Enjoy your presentation system! 🎉"
echo "=========================================="

