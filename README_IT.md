# 🎬 AI Director - Multi-Stream Video Analysis System

Sistema di analisi video in tempo reale con supporto CUDA, progettato per Windows e integrazione con n8n.

## 🎯 Caratteristiche Principali

- ✅ **Analisi Video in Tempo Reale**: Processa video locali con SmolVLM
- ✅ **Trascrizione Audio**: Estrae e trascrive l'audio dai video usando Moshi STT
- ✅ **Supporto CUDA**: Accelerazione GPU per prestazioni ottimali
- ✅ **Modelli Intercambiabili**: Cambia facilmente tra modelli di diverse dimensioni
- ✅ **API REST**: Integrazione con n8n e altri orchestrator
- ✅ **Multi-Stream**: Gestisci più flussi video contemporaneamente
- ✅ **WebSocket Real-Time**: Streaming dei risultati in tempo reale

## 📋 Requisiti di Sistema

### Hardware
- **GPU**: NVIDIA con CUDA 11.x o 12.x (consigliato)
- **VRAM**: Minimo 4GB (8GB+ consigliato per modelli più grandi)
- **RAM**: Minimo 8GB (16GB+ consigliato)
- **Storage**: 10GB+ per modelli e dipendenze

### Software
- **Windows 10/11**
- **Python 3.10+**
- **CUDA Toolkit** (se si usa GPU)
- **FFmpeg** (per elaborazione video/audio)

## 🚀 Installazione Rapida

### 1. Clona e Naviga nella Directory
```powershell
cd e:\dev\ai-director\smolvlm-audio-transcription
```

### 2. Esegui lo Script di Avvio
```powershell
.\start.ps1
```

Lo script automaticamente:
- Crea l'ambiente virtuale
- Installa le dipendenze
- Verifica la disponibilità CUDA
- Offre un menu interattivo

## 📖 Guida all'Uso

### Opzione 1: Server API (per n8n)

Avvia il server API per l'integrazione con n8n:

```powershell
.\start.ps1
# Seleziona opzione 1
```

Il server sarà disponibile su:
- API: `http://localhost:8000`
- Documentazione: `http://localhost:8000/docs`
- WebSocket: `ws://localhost:8765`

### Opzione 2: Elaborazione Video Standalone

Elabora un singolo video:

```powershell
.\start.ps1
# Seleziona opzione 2
# Inserisci il percorso del video
```

Oppure direttamente:

```powershell
.\.venv\Scripts\Activate.ps1
python main_video.py "percorso\al\video.mp4"
```

Poi apri `index_video.html` nel browser.

### Opzione 3: Configurazione Modelli

Gestisci i modelli:

```powershell
# Visualizza modelli attivi
python config_manager.py active

# Lista modelli STT disponibili
python config_manager.py list stt

# Cambia modello STT
python config_manager.py set-stt medium

# Lista modelli VLM disponibili
python config_manager.py list vlm

# Cambia modello VLM
python config_manager.py set-vlm medium

# Verifica utilizzo VRAM
python config_manager.py vram

# Suggerisci modelli per VRAM disponibile
python config_manager.py suggest 6
```

## 🔧 Configurazione

### File `config.json`

Personalizza le impostazioni del sistema:

```json
{
    "models": {
        "stt": {
            "small": {
                "repo": "kyutai/stt-1b-en_fr",
                "vram_gb": 2
            }
        }
    },
    "server": {
        "host": "localhost",
        "websocket_port": 8765,
        "http_port": 8000,
        "max_concurrent_streams": 4
    },
    "video": {
        "default_fps": 30,
        "enable_audio": true,
        "loop_video": true
    }
}
```

## 🌐 API REST Endpoints

### Stream Management

#### Crea un nuovo stream
```bash
POST /streams/create
{
    "video_path": "video.mp4",
    "enable_audio": true,
    "stream_name": "Camera 1",
    "loop": true
}
```

#### Lista streams attivi
```bash
GET /streams
```

#### Controlla stream
```bash
POST /streams/{stream_id}/control
{
    "action": "start"  # start, stop, pause, resume
}
```

#### Elimina stream
```bash
DELETE /streams/{stream_id}
```

### Analysis

#### Ottieni risultati analisi
```bash
GET /analysis/{stream_id}?limit=100
```

#### Query analisi
```bash
POST /analysis/query
{
    "stream_id": "...",
    "query": "person detected",
    "max_results": 10
}
```

### Models

#### Lista modelli
```bash
GET /models
```

#### Cambia modello
```bash
POST /models/switch
{
    "model_type": "stt",
    "size": "medium"
}
```

### System

#### Health check
```bash
GET /health
```

#### Statistiche
```bash
GET /stats
```

## 🔗 Integrazione con n8n

### 1. Installa n8n
```powershell
npm install -g n8n
```

### 2. Avvia n8n
```powershell
n8n start
```

### 3. Importa Workflow
1. Apri n8n: `http://localhost:5678`
2. Importa `n8n-workflow-example.json`
3. Configura gli endpoint API

### 4. Esempio di Utilizzo

Il workflow di esempio:
1. Riceve un webhook con i dettagli del video
2. Crea uno stream video
3. Attende l'elaborazione
4. Recupera i risultati dell'analisi
5. Invia i risultati a un webhook

**Triggera il workflow:**
```bash
curl -X POST http://localhost:5678/webhook/ai-director-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "C:\\videos\\sample.mp4",
    "enable_audio": true,
    "stream_name": "Camera 1"
  }'
```

## 🎬 Architettura AI Director

### Concetto
Un sistema che:
1. Riceve multipli feed video
2. Analizza il contenuto in tempo reale
3. Decide quali feed mostrare in base al contenuto
4. Viene orchestrato da n8n

### Componenti

```
┌─────────────────────────────────────────────────────┐
│                      n8n                             │
│                  (Orchestrator)                      │
└──────────┬──────────────────────────────────────────┘
           │
           ├────────┬────────┬────────┬────────┐
           │        │        │        │        │
    ┌──────▼──┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐
    │ Video 1 │ │Vid 2│ │Vid 3│ │Vid 4│ │Vid N│
    └────┬────┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
         │         │        │        │        │
         └─────────┴────────┴────────┴────────┘
                           │
                   ┌───────▼────────┐
                   │  AI Director   │
                   │  API Server    │
                   │   (FastAPI)    │
                   └───────┬────────┘
                           │
                   ┌───────▼────────┐
                   │   Analysis     │
                   │  VLM + STT     │
                   │   (CUDA)       │
                   └────────────────┘
```

### Logica di Selezione Stream

Esempio di criteri per scegliere quale stream mostrare:
- **Priorità contenuto**: Persone > Movimento > Statico
- **Priorità audio**: Parlato > Rumore > Silenzio
- **Eventi**: Azioni > Oggetti interessanti
- **Custom**: Regole definite dall'utente

## 🎯 Modelli Disponibili

### Speech-to-Text (STT)
| Dimensione | Modello | VRAM | Lingue | Note |
|-----------|---------|------|--------|------|
| Small | Moshi STT 1B | 2GB | EN, FR | Veloce, buona accuratezza |
| Medium | Moshi STT 2B | 4GB | EN, FR | Più accurato, più lento |

### Vision Language Model (VLM)
| Dimensione | Modello | VRAM | Note |
|-----------|---------|------|------|
| Small | SmolVLM 500M | 1GB | Veloce, real-time |
| Medium | SmolVLM 1.7B | 3GB | Più dettagliato |

## 🐛 Troubleshooting

### CUDA non disponibile
```powershell
# Verifica installazione CUDA
nvidia-smi

# Verifica PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### Errore FFmpeg
```powershell
# Installa FFmpeg
choco install ffmpeg

# Verifica installazione
ffmpeg -version
```

### Porta occupata
```powershell
# Trova processo
netstat -ano | findstr :8000

# Termina processo
taskkill /PID <PID> /F
```

### Out of Memory (VRAM)
- Usa modelli "small"
- Riduci `max_concurrent_streams` in `config.json`
- Elabora video a risoluzione ridotta

## 📊 Performance

### Benchmark Stimati (RTX 3060 12GB)

| Configurazione | FPS Video | Latenza STT | Streams Simultanei |
|----------------|-----------|-------------|-------------------|
| Small models | 30 | ~100ms | 4 |
| Medium models | 20 | ~150ms | 2 |
| Large models | 10 | ~250ms | 1 |

## 🔮 Roadmap

- [ ] Supporto per stream RTSP/HTTP in tempo reale
- [ ] Dashboard web per monitoraggio
- [ ] Rilevamento oggetti con YOLO
- [ ] Sistema di alerting basato su eventi
- [ ] Supporto per più lingue STT
- [ ] Export timeline con annotazioni
- [ ] Integrazione con sistemi di videosorveglianza

## 📝 License

Vedi file `LICENSE`

## 🤝 Contributi

Contributi benvenuti! Apri una issue o una pull request.

## 📧 Supporto

Per problemi o domande, apri una issue su GitHub.

---

**Nota**: Questo progetto è ottimizzato per uso locale su Windows con GPU CUDA. Per deployment su cloud o altri sistemi operativi, potrebbero essere necessarie modifiche.
