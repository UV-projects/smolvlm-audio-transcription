#!/bin/bash
# AI Director - double-clickable launcher (Terminal visible, shows logs).
# Quit by closing this window or pressing Ctrl-C; backends are stopped automatically.

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

PY="$DIR/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"

# If the control server is already running, just open the browser.
if nc -z 127.0.0.1 8000 2>/dev/null; then
  echo "AI Director is already running. Opening browser..."
  open "http://127.0.0.1:8000"
  exit 0
fi

# Ensure a Vosk speech model exists (small 40 MB model preferred).
if [ ! -d "$DIR/models/vosk-model-small-en-us-0.15" ] && [ ! -d "$DIR/models/vosk-model-en-us-0.42-gigaspeech" ]; then
  echo "Downloading Vosk small speech model (~40 MB)..."
  mkdir -p models
  curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o /tmp/vosk-small.zip
  unzip -q /tmp/vosk-small.zip -d models/
  rm -f /tmp/vosk-small.zip
fi

trap "kill 0" EXIT

echo "Starting AI Director control server..."
"$PY" "$DIR/launcher/control_server.py" &
SERVER_PID=$!

# Wait for the control server, then open the browser.
for i in $(seq 1 60); do
  if nc -z 127.0.0.1 8000 2>/dev/null; then break; fi
  sleep 0.25
done
echo "Opening http://127.0.0.1:8000 ..."
open "http://127.0.0.1:8000"

wait $SERVER_PID
