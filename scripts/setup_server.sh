#!/bin/bash
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
MODEL_DIR="./models/vosk-model-en-us-0.42-gigaspeech"
LLAMA_DIR="./build/bin/llama-server"
cd $PROJECT_DIR

echo "=========================================="
echo "Checking for dependencies..."
echo "=========================================="
echo ""

if [ ! -d "$MODEL_DIR" ]; then
   echo "Speech model not found, downloading now"
   echo ""
   mkdir -p models
   wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip -O vosk.zip && unzip vosk.zip -d models/
   echo "Done downloading speech model!"
fi

python vosk/asr_server.py models/vosk-model-en-us-0.42-gigaspeech/ &


if [ ! -f "$LLAMA_DIR" ]; then
   echo "Llama.cpp not found, downloading now..."
   echo ""
   wget https://github.com/ggml-org/llama.cpp/releases/download/b6804/llama-b6804-bin-ubuntu-vulkan-x64.zip -O llama.zip && unzip llama.zip
   echo "Done downloading Llama.cpp!"
fi

# Terminal 1: VLM Server (llama-server)
echo "✓ Opening Terminal 1: VLM Server (llama-server, version b6804)..."
echo '========================================'
echo 'VLM SERVER (Port 8080)'
echo '========================================'
echo ''
./build/bin/llama-server -hf lmstudio-community/InternVL3_5-4B-GGUF:Q4_K_M --host 0.0.0.0 &
sleep 5

echo "=========================================="
echo "Starting client components..."
echo "=========================================="
echo ""

# PDF Server
echo "✓ Starting PDF Server (try.pdf)..."
echo '========================================'
echo 'PDF SERVER (Port 9002)'
echo '========================================'
echo ''
python src/presenter/pdf_server.py $1 &
sleep 2

# Orchestrator
echo "✓ Starting Orchestrator..."
echo '========================================'
echo 'ORCHESTRATOR (Port 9001)'
echo '========================================'
echo ''
python src/orchestrator/orchestrator.py $1 &
sleep 2

# Audio client
echo "✓ Starting Audio Client (Speech-to-Text)..."
echo '========================================'
echo 'AUDIO SERVER (Port 2700)'
echo '========================================'
echo ''
python src/audio/audio.py $1 &
sleep 5
