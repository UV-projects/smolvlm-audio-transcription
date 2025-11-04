# 🎬 AI Director - Multi-Stream Video Analysis System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-downloads)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Sistema intelligente di analisi video multi-stream con AI, ottimizzato per Windows con GPU CUDA e orchestrazione n8n.

## 🌟 Cosa Fa Questo Progetto

**AI Director** è un sistema completo che:
- 📹 **Analizza video in tempo reale** usando SmolVLM per comprensione visiva
- 🎤 **Trascrive audio** automaticamente con Moshi STT
- 🤖 **Seleziona intelligentemente** quale stream mostrare
- 🔗 **Si integra con n8n** per orchestrazione workflow
- ⚡ **Usa accelerazione GPU** CUDA per performance ottimali
- 🎛️ **Supporta multi-stream** per gestire più video contemporaneamente

## 🚀 Quick Start (5 minuti)

### Windows con GPU NVIDIA

```powershell
# 1. Clona il repository (già fatto)
cd e:\dev\ai-director\smolvlm-audio-transcription

# 2. Esegui setup automatico
.\start.ps1

# 3. Scarica video di test
.\download_sample_video.ps1

# 4. Testa il sistema
python test_system.py

# 5. Inizia!
# Seleziona opzione 2 dallo script start.ps1
```

**Fatto!** Apri `index_video.html` nel browser e vedrai il video analizzato in tempo reale.

## 📚 Documentazione

- **[QUICKSTART.md](QUICKSTART.md)** - Guida rapida per iniziare
- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** - Setup dettagliato per Windows
- **[README_IT.md](README_IT.md)** - Documentazione completa in italiano
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architettura del sistema
- **[config.json](config.json)** - Configurazione modelli e server

## 🎯 Caratteristiche Principali

### ✅ Analisi Video
- Supporto file video (MP4, AVI, MOV, MKV)
- Loop automatico dei video
- Estrazione frame configurabile
- Analisi con SmolVLM (500M/1.7B)

### ✅ Trascrizione Audio
- Estrazione audio da video
- Trascrizione real-time con Moshi STT
- Supporto multi-lingua (EN, FR)
- Modelli da 1B a 2B parametri

### ✅ API REST per Integrazione
- FastAPI server con OpenAPI docs
- WebSocket per streaming real-time
- Gestione multi-stream
- Health check e monitoring

### ✅ Configurazione Flessibile
- Cambio modelli facile
- Ottimizzazione automatica VRAM
- Configurazione via JSON
- CLI per gestione

### ✅ Integrazione n8n
- Workflow predefiniti
- Webhook endpoints
- Stream selection logic
- Event-driven architecture

## 🏗️ Architettura

```
┌──────────────────────────────────────────────────┐
│              n8n Orchestrator                     │
│         (Workflow Management)                     │
└────────────────┬─────────────────────────────────┘
                 │ REST API
┌────────────────▼─────────────────────────────────┐
│           FastAPI Server                          │
│  - Stream management                              │
│  - Model configuration                            │
│  - Analysis aggregation                           │
└────────────────┬─────────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
┌─────▼──────┐      ┌──────▼─────┐
│  Video     │      │   Audio    │
│ Processor  │      │ Processor  │
│ (OpenCV)   │      │ (FFmpeg)   │
└─────┬──────┘      └──────┬─────┘
      │                     │
      └──────────┬──────────┘
                 │
┌────────────────▼─────────────────────────────────┐
│            AI Models (CUDA)                       │
│  - SmolVLM (Vision)                               │
│  - Moshi STT (Audio)                              │
└───────────────────────────────────────────────────┘
```

## 💻 Requisiti Sistema

### Hardware
- **GPU**: NVIDIA con CUDA 11.x o 12.x (consigliato min. 4GB VRAM)
- **RAM**: 8GB minimo (16GB consigliato)
- **Storage**: 10GB per modelli e cache

### Software
- Windows 10/11
- Python 3.10 o superiore
- CUDA Toolkit (per GPU)
- FFmpeg

## 📦 Componenti Principali

| File | Descrizione |
|------|-------------|
| `main_video.py` | Processore video con STT integrato |
| `api_server.py` | Server FastAPI per n8n integration |
| `config_manager.py` | Gestione configurazione e modelli |
| `config.json` | File di configurazione |
| `index_video.html` | Interfaccia web per visualizzazione |
| `start.ps1` | Script di avvio interattivo |
| `test_system.py` | Test di sistema completo |

## 🎮 Modi d'Uso

### 1. Standalone Video Processing
```powershell
python main_video.py "video.mp4"
# Apri index_video.html nel browser
```

### 2. API Server (per n8n)
```powershell
python api_server.py
# API disponibile su http://localhost:8000
# Docs su http://localhost:8000/docs
```

### 3. Configuration Management
```powershell
# Vedi modelli attivi
python config_manager.py active

# Cambia modello
python config_manager.py set-stt medium

# Verifica VRAM
python config_manager.py vram
```

## 🔧 Configurazione Rapida

### Cambia Modelli

Modifica `config.json`:

```json
{
    "active_models": {
        "stt": "small",  // or "medium"
        "vlm": "small"   // or "medium"
    }
}
```

Oppure via CLI:
```powershell
python config_manager.py set-stt medium
python config_manager.py set-vlm medium
```

### Ottimizza per la tua GPU

```powershell
# Suggerisce modelli ottimali per 8GB VRAM
python config_manager.py suggest 8
```

## 🌐 API Endpoints

### Stream Management
```bash
POST   /streams/create        # Crea nuovo stream
GET    /streams               # Lista streams
POST   /streams/{id}/control  # Controlla stream
DELETE /streams/{id}          # Elimina stream
```

### Analysis
```bash
GET    /analysis/{id}         # Ottieni risultati
POST   /analysis/query        # Query analisi
```

### Models
```bash
GET    /models                # Lista modelli
POST   /models/switch         # Cambia modello
```

### System
```bash
GET    /health                # Health check
GET    /stats                 # Statistiche
```

Documentazione completa: http://localhost:8000/docs

## 🔗 Integrazione n8n

### 1. Installa n8n
```powershell
npm install -g n8n
```

### 2. Importa Workflow
1. Avvia n8n: `n8n start`
2. Vai su http://localhost:5678
3. Importa `n8n-workflow-example.json`

### 3. Trigger Workflow
```bash
curl -X POST http://localhost:5678/webhook/ai-director-trigger ^
  -H "Content-Type: application/json" ^
  -d "{\"video_path\": \"video.mp4\", \"enable_audio\": true}"
```

## 📊 Performance

### Benchmark Tipici (RTX 3060 12GB)

| Config | FPS | Latenza STT | Streams |
|--------|-----|-------------|---------|
| Small  | 30  | ~100ms      | 4       |
| Medium | 20  | ~150ms      | 2       |

### Ottimizzazione VRAM

| GPU | VRAM | Config Suggerita | Max Streams |
|-----|------|------------------|-------------|
| RTX 3060 | 12GB | Medium | 2 |
| RTX 3070 | 8GB  | Small  | 2 |
| RTX 3080 | 10GB | Medium | 2 |
| RTX 3090 | 24GB | Medium | 4 |
| RTX 4090 | 24GB | Medium | 6 |

## 🐛 Troubleshooting

### CUDA non disponibile
```powershell
# Verifica
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"

# Fix: Reinstalla PyTorch con CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### FFmpeg mancante
```powershell
choco install ffmpeg
```

### Porta occupata
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Out of Memory
```powershell
# Usa modelli small
python config_manager.py set-stt small
python config_manager.py set-vlm small
```

## 🗺️ Roadmap

- [x] Video processing con CUDA
- [x] Audio transcription
- [x] API REST server
- [x] Model configuration
- [x] n8n integration examples
- [ ] Stream selection algorithm
- [ ] RTSP/HTTP live streams
- [ ] Object detection (YOLO)
- [ ] Web dashboard
- [ ] Docker deployment
- [ ] Multi-GPU support

## 🤝 Contributing

Contributi benvenuti! Apri una issue o una pull request.

## 📄 License

MIT License - vedi [LICENSE](LICENSE)

## 🙏 Credits

- [SmolVLM](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct) by HuggingFace
- [Moshi STT](https://huggingface.co/kyutai) by Kyutai
- [llama.cpp](https://github.com/ggml-org/llama.cpp) by ggml.org
- Original repo: [UV-projects/smolvlm-audio-transcription](https://github.com/UV-projects/smolvlm-audio-transcription)

## 📧 Support

Per problemi o domande:
1. Controlla [QUICKSTART.md](QUICKSTART.md)
2. Leggi [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
3. Esegui `python test_system.py`
4. Apri una issue su GitHub

---

**Made with ❤️ for the AI Director project**

> 🎬 Transform multiple video feeds into intelligent, automated director choices!
