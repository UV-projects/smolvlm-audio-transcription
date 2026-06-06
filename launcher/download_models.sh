#!/bin/bash
# Download the lightweight speech model used by the demo.
# The VLM weights (SmolVLM-500M / Qwen3-VL-2B) are already in the llama.cpp cache
# and are loaded on demand by the control server.

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"
mkdir -p models

SMALL="models/vosk-model-small-en-us-0.15"
if [ -d "$SMALL" ]; then
  echo "Vosk small model already present: $SMALL"
else
  echo "Downloading Vosk small speech model (~40 MB)..."
  curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o /tmp/vosk-small.zip
  unzip -q /tmp/vosk-small.zip -d models/
  rm -f /tmp/vosk-small.zip
  echo "Done: $SMALL"
fi

echo "All set. Launch the demo with: open 'AI Director.app'  (or run launcher/start.command)"
