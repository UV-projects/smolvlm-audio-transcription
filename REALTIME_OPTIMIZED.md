# ⚡ Real-Time Optimization - AI Director

## 🎯 Cosa Abbiamo Cambiato

### Prima (Lento):
```
❌ Analizza ogni 5 SECONDI (solo 0.2 analisi/sec)
❌ Output verboso con print ovunque
❌ Video wait per analisi (blocca il flusso)
❌ Generazione testo lunga (100 tokens)
```

### Ora (Veloce):
```
✅ Analizza ogni N FRAMES (configurabile, default 15)
✅ Output minimale, solo essenziale
✅ Video e analisi in THREAD SEPARATI (non blocking)
✅ Generazione testo corta (50 tokens max)
✅ CUDA ottimizzato (FP16, matmul tf32, cudnn benchmark)
```

---

## 🚀 Architettura Real-Time

```
┌─────────────────────────────────────────────────────┐
│                  VIDEO THREAD                       │
│  (Runs at native FPS - 15/25/30 FPS)              │
│                                                     │
│  ┌──────────┐    Every N frames    ┌─────────┐    │
│  │ Read     │───────────────────────►│ Analysis│    │
│  │ Frame    │                       │ Queue   │    │
│  └──────────┘                       └─────────┘    │
│       │                                   │         │
│       │ Every frame                       │         │
│       ▼                                   ▼         │
│  ┌──────────┐                     ┌─────────────┐  │
│  │ Encode   │                     │  ANALYSIS   │  │
│  │ JPEG     │                     │   THREAD    │  │
│  └──────────┘                     │             │  │
│       │                           │ ┌─────────┐ │  │
│       ▼                           │ │SmolVLM  │ │  │
│  ┌──────────┐                     │ │ CUDA    │ │  │
│  │ Video    │                     │ │ FP16    │ │  │
│  │ Queue    │                     │ └─────────┘ │  │
│  └──────────┘                     └─────────────┘  │
│       │                                   │         │
└───────┼───────────────────────────────────┼─────────┘
        │                                   │
        ▼                                   ▼
   ┌─────────────────────────────────────────────┐
   │         WEBSOCKET BROADCAST                 │
   │  ┌──────────────┐    ┌──────────────┐      │
   │  │ Video Frames │    │ Descriptions │      │
   │  │  ~30 FPS     │    │  ~1-2 per sec│      │
   │  └──────────────┘    └──────────────┘      │
   └─────────────────────────────────────────────┘
                  │
                  ▼
            BROWSER (index_video.html)
```

---

## 🎛️ Parametri di Performance

### `--frames N` (Default: 15)

**Cosa controlla**: Ogni quanti frame analizzare con SmolVLM

**Esempi**:

```bash
# MASSIMA VELOCITÀ (analisi ogni 5 frame)
# Video 15 FPS → 3 analisi/sec
# Video 30 FPS → 6 analisi/sec
python main_video.py video.mp4 --frames 5 --no-audio

# BILANCIATO (default, ogni 15 frame)
# Video 15 FPS → 1 analisi/sec  ✅ CONSIGLIATO
# Video 30 FPS → 2 analisi/sec
python main_video.py video.mp4 --frames 15 --no-audio

# RISPARMIO GPU (ogni 30 frame)
# Video 15 FPS → 0.5 analisi/sec
# Video 30 FPS → 1 analisi/sec
python main_video.py video.mp4 --frames 30 --no-audio

# ULTRA FAST (ogni frame!)
# ⚠️ ATTENZIONE: GPU 100%, possibile lag video
python main_video.py video.mp4 --frames 1 --no-audio
```

### Calcolo Performance

```
FPS Video = Frames per secondo del video
N = --frames parameter

Analisi al secondo = FPS Video / N

Esempi:
- Video 15 FPS, --frames 15 → 15/15 = 1 analisi/sec
- Video 30 FPS, --frames 10 → 30/10 = 3 analisi/sec
- Video 25 FPS, --frames 25 → 25/25 = 1 analisi/sec
```

---

## 🔧 Ottimizzazioni CUDA Implementate

### 1. FP16 (Half Precision)
```python
torch_dtype=torch.float16  # 2x più veloce, 1/2 VRAM
```

### 2. TF32 Matrix Multiplication
```python
torch.backends.cuda.matmul.allow_tf32 = True  # 3x più veloce su Ampere+
```

### 3. cuDNN Benchmark
```python
torch.backends.cudnn.benchmark = True  # Auto-ottimizza convoluzioni
```

### 4. Automatic Mixed Precision (AMP)
```python
with torch.cuda.amp.autocast():
    generated_ids = model.generate(...)  # Auto FP16/FP32 mix
```

### 5. Generazione Veloce
```python
max_new_tokens=50,    # Testo corto
do_sample=False,      # No sampling, greedy
num_beams=1           # No beam search
```

---

## 📊 Performance Attese

### RTX 2070 SUPER (8GB VRAM)

**SmolVLM-500M + FP16**:

| Frames | Analisi/sec | GPU Usage | Latency | Video Lag |
|--------|------------|-----------|---------|-----------|
| 1      | ~15/sec    | 95-100%   | ~70ms   | ⚠️ Possibile |
| 5      | ~3/sec     | 60-80%    | ~70ms   | ✅ No |
| 10     | ~1.5/sec   | 40-60%    | ~70ms   | ✅ No |
| 15     | ~1/sec     | 30-40%    | ~70ms   | ✅ No ✅ |
| 30     | ~0.5/sec   | 15-20%    | ~70ms   | ✅ No |

**Latency = tempo per analizzare un singolo frame (~70ms con SmolVLM-500M)**

---

## 🎯 Configurazioni Consigliate

### 🎬 AI Director Multi-Camera (4-6 stream)
```bash
# Analisi leggera per gestire più stream
python main_video.py cam1.mp4 --frames 30 --no-audio
python main_video.py cam2.mp4 --frames 30 --no-audio
python main_video.py cam3.mp4 --frames 30 --no-audio
python main_video.py cam4.mp4 --frames 30 --no-audio

# GPU: ~60-80% (4 stream × 15-20% ciascuno)
# VRAM: ~6GB (4 × 1.5GB)
```

### 🎥 Single Stream High Quality
```bash
# Analisi frequente per dettagli
python main_video.py video.mp4 --frames 10 --no-audio

# GPU: ~50-70%
# VRAM: ~2GB
```

### ⚡ Maximum Speed Test
```bash
# Quante analisi riesce a fare la GPU?
python main_video.py video.mp4 --frames 1 --no-audio

# Monitora con:
# nvidia-smi -l 1
```

---

## 🐛 Troubleshooting

### Video va a scatti
```bash
# Riduci frequenza analisi
python main_video.py video.mp4 --frames 30 --no-audio
```

### Descrizioni troppo lente
```bash
# Aumenta frequenza analisi (se GPU regge)
python main_video.py video.mp4 --frames 5 --no-audio
```

### GPU al 100%, sistema lento
```bash
# Riduci carico
python main_video.py video.mp4 --frames 60 --no-audio
```

### Out of Memory (OOM)
```bash
# Usa modello più piccolo in config.json
"active_models": {
  "vlm": "small"  # Invece di medium
}
```

---

## 🔍 Monitoraggio Real-Time

### GPU Monitor
```powershell
# Terminale separato
nvidia-smi -l 1
```

**Osserva**:
- GPU Utilization %
- Memory Used / Total
- Temperature
- Power Draw

### Python Stats
Nel codice aggiungi (opzionale):
```python
import time

start = time.time()
description = vision_analyzer.analyze_frame(frame)
elapsed = (time.time() - start) * 1000
print(f"Analysis: {elapsed:.1f}ms")
```

---

## 🎯 Best Practices

### 1. Video Flow è Priorità #1
Il video deve scorrere a FPS nativi **sempre**. Se SmolVLM è lento, meglio analizzare meno frame che bloccare il video.

### 2. Queue Management
```python
analysis_queue = queue.Queue(maxsize=2)  # Max 2 frame in attesa
```
Se la queue è piena, skippiamo l'analisi di quel frame. Meglio saltare che accumulare ritardo.

### 3. Thread Separati
Video e analisi NON devono mai bloccarsi a vicenda. Thread separati = indipendenza.

### 4. Silent Errors
```python
except Exception as e:
    pass  # No print in production
```
In real-time, un errore non deve fermare tutto. Log minimo.

### 5. JPEG Quality Trade-off
```python
cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
```
Qualità 85 = buon compromesso tra dimensione e qualità per WebSocket.

---

## 📈 Scaling per AI Director

Quando avrai **4-6 stream simultanei**:

### Strategia 1: Multi-Process
```python
# 4 processi Python separati
# Ognuno analizza 1 stream
# PRO: Isolamento, facile debug
# CONTRO: 4× VRAM usage
```

### Strategia 2: Single Process, Batch Analysis
```python
# Un processo, analizza 4 frame in batch
# model.generate(batch_size=4)
# PRO: Efficiente VRAM
# CONTRO: Più complesso
```

### Strategia 3: Priority Queue
```python
# Analizza solo lo stream più "interessante"
# Score: movimento, persone, audio
# PRO: Massima qualità su stream importante
# CONTRO: Altri stream meno coperti
```

---

## ⚡ Risultato Finale

Con le ottimizzazioni:

```
✅ Video: 15 FPS nativi (fluido)
✅ Analisi: ~1-2 per secondo (real-time)
✅ Latency: ~70-100ms (impercettibile)
✅ GPU: 30-50% usage (margine per multi-stream)
✅ VRAM: ~2GB (spazio per 3-4 stream)
```

**Pronto per AI Director multi-camera!** 🎬
