# 🎬 AI Director - Architettura Sistema Completo

## 📐 Visione d'Insieme

AI Director è un sistema di orchestrazione intelligente per flussi video multipli che:
1. Analizza contenuto video in tempo reale (VLM)
2. Trascrive audio (STT)
3. Seleziona automaticamente quale stream mostrare
4. È controllato tramite n8n per massima flessibilità

## 🏗️ Architettura Multi-Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                     Layer 1: Orchestration                       │
│                            (n8n)                                 │
│  - Workflow management                                           │
│  - Business logic                                                │
│  - Stream selection rules                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│                   Layer 2: API Gateway                           │
│                      (FastAPI - api_server.py)                   │
│  - Stream management                                             │
│  - Model configuration                                           │
│  - Analysis aggregation                                          │
│  - WebSocket broadcasting                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                  │
┌───────────▼──────────┐          ┌───────────▼──────────┐
│   Layer 3: Processing│          │  Layer 3: Processing  │
│   (main_video.py)    │          │  (main_video.py)      │
│                      │    ...   │                       │
│  Stream 1            │          │  Stream N             │
│  - Video decode      │          │  - Video decode       │
│  - Audio extract     │          │  - Audio extract      │
└──────────┬───────────┘          └───────────┬───────────┘
           │                                   │
┌──────────▼───────────────────────────────────▼──────────┐
│              Layer 4: AI Models (CUDA)                   │
│                                                           │
│  ┌─────────────────┐        ┌─────────────────┐         │
│  │   Vision Model  │        │   Audio Model   │         │
│  │   SmolVLM       │        │   Moshi STT     │         │
│  │   (500M/1.7B)   │        │   (1B/2B)       │         │
│  └─────────────────┘        └─────────────────┘         │
└───────────────────────────────────────────────────────────┘
```

## 🔄 Flusso Dati

### 1. Stream Initialization

```
n8n Workflow
    │
    └─> POST /streams/create
            │
            └─> API Server creates stream_id
                    │
                    └─> Spawn VideoProcessor instance
                            │
                            ├─> Load video file
                            ├─> Extract audio track
                            └─> Initialize models
```

### 2. Real-time Processing

```
Video Frame Loop:
┌─────────────────────┐
│  Read video frame   │
│  (OpenCV)           │
└──────────┬──────────┘
           │
           ├─> Encode frame (base64)
           │       │
           │       └─> WebSocket broadcast
           │
           └─> Queue for VLM analysis
                   │
                   └─> SmolVLM inference
                           │
                           └─> Analysis result
                                   │
                                   └─> Store + Broadcast

Audio Processing Loop:
┌─────────────────────┐
│  Audio chunk        │
│  (FFmpeg extract)   │
└──────────┬──────────┘
           │
           └─> Moshi STT inference
                   │
                   └─> Transcription
                           │
                           └─> Store + Broadcast
```

### 3. Stream Selection Logic

```
n8n Decision Workflow:

GET /analysis/{stream_1}  ──┐
GET /analysis/{stream_2}  ──┤
GET /analysis/{stream_3}  ──┼─> Aggregate results
GET /analysis/{stream_4}  ──┘
           │
           └─> Apply Rules:
                   │
                   ├─> Priority 1: Detect humans
                   ├─> Priority 2: Detect speech
                   ├─> Priority 3: Detect movement
                   ├─> Priority 4: Most recent activity
                   │
                   └─> Select stream_id
                           │
                           └─> Broadcast selection
                                   │
                                   └─> Update UI
```

## 📦 Componenti Dettagliati

### API Server (api_server.py)

**Responsabilità:**
- Gestione lifecycle streams
- Aggregazione analisi
- Configurazione modelli
- WebSocket broadcasting

**Endpoints Principali:**
- `POST /streams/create` - Crea nuovo stream
- `GET /streams` - Lista streams attivi
- `GET /analysis/{stream_id}` - Risultati analisi
- `POST /models/switch` - Cambia modello
- `GET /health` - Status sistema

### Video Processor (main_video.py)

**Responsabilità:**
- Decodifica video
- Estrazione audio
- Gestione code frame/audio
- Broadcasting real-time

**Caratteristiche:**
- Threading per video/audio separati
- Buffer management per sincronizzazione
- Supporto loop video
- Gestione errori e recovery

### Configuration Manager (config_manager.py)

**Responsabilità:**
- Gestione configurazione modelli
- Calcolo VRAM requirements
- Suggerimenti ottimizzazione
- Validazione configurazione

**Features:**
- Hot-reload configurazione
- Validazione VRAM disponibile
- Suggerimenti modelli per hardware

### n8n Integration

**Workflow Components:**

1. **Trigger Node**: Webhook per avvio
2. **Create Stream Nodes**: Uno per ogni video
3. **Analysis Nodes**: Polling risultati
4. **Decision Node**: Logica selezione
5. **Action Nodes**: Broadcast/logging/alerting

## 🧠 Logica di Selezione Stream

### Algoritmo Base

```python
def select_best_stream(analysis_results: Dict[str, List]) -> str:
    """
    Seleziona il miglior stream basato su priorità
    """
    scores = {}
    
    for stream_id, results in analysis_results.items():
        score = 0
        
        # Priority 1: Human detection (weight: 10)
        if has_humans(results):
            score += 10
        
        # Priority 2: Speech detected (weight: 8)
        if has_speech(results):
            score += 8
        
        # Priority 3: Movement (weight: 5)
        movement_level = detect_movement(results)
        score += movement_level * 5
        
        # Priority 4: Recency (weight: 3)
        recency_score = calculate_recency(results)
        score += recency_score * 3
        
        scores[stream_id] = score
    
    # Return stream with highest score
    return max(scores.items(), key=lambda x: x[1])[0]
```

### Regole Personalizzabili

```json
{
    "selection_rules": {
        "priorities": [
            {
                "type": "object_detection",
                "objects": ["person", "face"],
                "weight": 10
            },
            {
                "type": "audio_activity",
                "threshold": 0.5,
                "weight": 8
            },
            {
                "type": "motion_detection",
                "threshold": 0.3,
                "weight": 5
            }
        ],
        "cooldown_seconds": 5,
        "min_confidence": 0.6
    }
}
```

## 🔧 Configurazione per Scenari

### Scenario 1: Videosorveglianza

```json
{
    "use_case": "surveillance",
    "selection_rules": {
        "priorities": [
            {"type": "motion", "weight": 10},
            {"type": "person", "weight": 9},
            {"type": "sound", "weight": 7}
        ]
    },
    "video": {
        "fps": 15,
        "resolution": "720p"
    },
    "models": {
        "stt": "small",
        "vlm": "small"
    }
}
```

### Scenario 2: Meeting Room

```json
{
    "use_case": "meeting",
    "selection_rules": {
        "priorities": [
            {"type": "active_speaker", "weight": 10},
            {"type": "screen_sharing", "weight": 8},
            {"type": "participant_count", "weight": 5}
        ]
    },
    "video": {
        "fps": 30,
        "resolution": "1080p"
    },
    "models": {
        "stt": "medium",
        "vlm": "medium"
    }
}
```

### Scenario 3: Live Streaming

```json
{
    "use_case": "streaming",
    "selection_rules": {
        "priorities": [
            {"type": "action", "weight": 10},
            {"type": "audience_engagement", "weight": 8},
            {"type": "visual_quality", "weight": 6}
        ]
    },
    "video": {
        "fps": 60,
        "resolution": "1080p"
    },
    "models": {
        "stt": "medium",
        "vlm": "medium"
    }
}
```

## 📊 Performance Considerations

### VRAM Budget Planning

| Componente | Small | Medium | Large |
|-----------|-------|--------|-------|
| VLM Model | 1GB | 3GB | 6GB |
| STT Model | 2GB | 4GB | 8GB |
| Video Buffer | 0.5GB | 1GB | 2GB |
| **Total per stream** | **3.5GB** | **8GB** | **16GB** |

### Concurrent Streams

```python
def max_concurrent_streams(available_vram_gb: float, 
                          model_size: str = "small") -> int:
    """
    Calculate maximum concurrent streams for available VRAM
    """
    vram_per_stream = {
        "small": 3.5,
        "medium": 8.0,
        "large": 16.0
    }
    
    # Reserve 2GB for system
    usable_vram = available_vram_gb - 2.0
    
    return int(usable_vram / vram_per_stream[model_size])

# Example: RTX 3060 (12GB)
max_streams = max_concurrent_streams(12, "small")  # = 2
```

### Optimization Strategies

1. **Frame Sampling**: Analizza 1 ogni N frames
2. **Resolution Scaling**: Riduci risoluzione per VLM
3. **Batch Processing**: Processa frame in batch
4. **Model Quantization**: Usa modelli quantizzati
5. **Audio Chunking**: Bufferizza audio in chunk ottimali

## 🚀 Deployment

### Development Setup

```powershell
# Single video testing
python main_video.py test.mp4

# API server with hot reload
uvicorn api_server:app --reload
```

### Production Setup

```powershell
# API server con multiple workers
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4

# n8n in background
n8n start --tunnel
```

### Docker Deployment (Future)

```dockerfile
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip ffmpeg

# Copy application
COPY . /app
WORKDIR /app

# Install Python packages
RUN pip3 install -r requirements-windows.txt

# Expose ports
EXPOSE 8000 8765

# Start services
CMD ["python3", "api_server.py"]
```

## 🔐 Security Considerations

1. **API Authentication**: Implementare JWT tokens
2. **Input Validation**: Validare percorsi video
3. **Rate Limiting**: Limitare richieste API
4. **CORS Configuration**: Configurare origini permesse
5. **Secure WebSocket**: Usare WSS in produzione

## 📈 Monitoring & Logging

### Metrics da Tracciare

- Streams attivi
- FPS per stream
- Latenza analisi
- Utilizzo VRAM
- Utilizzo CPU
- Throughput rete
- Errori per stream

### Logging Structure

```python
{
    "timestamp": "2024-10-13T10:30:00Z",
    "level": "INFO",
    "component": "video_processor",
    "stream_id": "abc-123",
    "event": "frame_processed",
    "metrics": {
        "fps": 29.5,
        "latency_ms": 45,
        "vram_mb": 2048
    }
}
```

## 🎯 Roadmap Implementazione

### Phase 1: Core (✅ Completato)
- [x] Video processing
- [x] Audio transcription
- [x] API server
- [x] Configuration management
- [x] WebSocket streaming

### Phase 2: Intelligence (In Progress)
- [ ] Stream selection algorithm
- [ ] Object detection integration
- [ ] Custom rules engine
- [ ] Analytics dashboard

### Phase 3: Scale (Future)
- [ ] Multiple GPU support
- [ ] Distributed processing
- [ ] Redis caching
- [ ] Database integration

### Phase 4: Production (Future)
- [ ] Docker containers
- [ ] Kubernetes deployment
- [ ] Monitoring stack
- [ ] Auto-scaling

## 📚 Resources

- **PyTorch CUDA**: https://pytorch.org/get-started/locally/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **n8n Docs**: https://docs.n8n.io/
- **OpenCV**: https://opencv.org/
- **FFmpeg**: https://ffmpeg.org/

---

**Nota**: Questa architettura è progettata per essere modulare e scalabile. 
Ogni componente può essere sviluppato e testato indipendentemente.
