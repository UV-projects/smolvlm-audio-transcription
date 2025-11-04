# Quick Start Guide - AI Director

## 🚀 Setup Veloce (5 minuti)

### 1. Installazione Base

```powershell
# Apri PowerShell nella directory del progetto
cd e:\dev\ai-director\smolvlm-audio-transcription

# Esegui lo script di avvio
.\start.ps1
```

### 2. Scarica un Video di Test

```powershell
# Scarica un video di esempio
.\download_sample_video.ps1

# Seleziona l'opzione 1 per un video piccolo (1MB)
```

### 3. Primo Test

```powershell
# Avvia l'elaborazione video
.\start.ps1
# Seleziona opzione 2
# Inserisci: sample_bigbuck_1mb.mp4
# Abilita audio: y

# Apri nel browser: index_video.html
```

## ✅ Verifica Installazione

```powershell
# Verifica CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Verifica configurazione
python config_manager.py active

# Verifica VRAM
python config_manager.py vram
```

## 🎯 Casi d'Uso Comuni

### Caso 1: Analisi Singolo Video

```powershell
# Attiva ambiente
.\.venv\Scripts\Activate.ps1

# Elabora video
python main_video.py "mio_video.mp4"

# Apri index_video.html nel browser
```

### Caso 2: API Server per n8n

```powershell
# Avvia API server
python api_server.py

# Accedi a: http://localhost:8000/docs

# Crea stream via API
curl -X POST http://localhost:8000/streams/create ^
  -H "Content-Type: application/json" ^
  -d "{\"video_path\": \"video.mp4\", \"enable_audio\": true}"
```

### Caso 3: Cambia Modelli

```powershell
# Visualizza modelli disponibili
python config_manager.py list stt

# Cambia a modello più grande (migliore qualità)
python config_manager.py set-stt medium

# Visualizza modelli attivi
python config_manager.py active
```

## 🔧 Comandi Utili

### Gestione Ambiente

```powershell
# Attiva ambiente virtuale
.\.venv\Scripts\Activate.ps1

# Disattiva ambiente
deactivate

# Aggiorna dipendenze
pip install -r requirements-windows.txt --upgrade
```

### Monitoraggio GPU

```powershell
# Monitoraggio continuo GPU
nvidia-smi -l 1

# Utilizzo VRAM
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

### Test Connettività

```powershell
# Test WebSocket
# Apri index_video.html e verifica connessione

# Test API Server
curl http://localhost:8000/health
```

## 🐛 Problemi Comuni e Soluzioni

### Problema: "CUDA not available"

**Soluzione:**
```powershell
# Verifica driver NVIDIA
nvidia-smi

# Reinstalla PyTorch con CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Problema: "FFmpeg not found"

**Soluzione:**
```powershell
# Installa FFmpeg
choco install ffmpeg

# Verifica
ffmpeg -version
```

### Problema: "Port already in use"

**Soluzione:**
```powershell
# Trova processo su porta 8000
netstat -ano | findstr :8000

# Termina processo (sostituisci PID)
taskkill /PID <PID> /F
```

### Problema: "Out of Memory"

**Soluzione:**
```powershell
# Usa modelli più piccoli
python config_manager.py set-stt small
python config_manager.py set-vlm small

# Verifica VRAM richiesta
python config_manager.py vram
```

## 📊 Ottimizzazione Performance

### Per GPU con 4-6GB VRAM

```json
// config.json
{
    "active_models": {
        "stt": "small",
        "vlm": "small"
    },
    "server": {
        "max_concurrent_streams": 2
    }
}
```

### Per GPU con 8-12GB VRAM

```json
// config.json
{
    "active_models": {
        "stt": "medium",
        "vlm": "medium"
    },
    "server": {
        "max_concurrent_streams": 4
    }
}
```

### Per GPU con 12GB+ VRAM

```json
// config.json
{
    "active_models": {
        "stt": "medium",
        "vlm": "medium"
    },
    "server": {
        "max_concurrent_streams": 6
    }
}
```

## 🎬 Workflow Completo

### 1. Setup Iniziale (una volta)

```powershell
# Clona repo (già fatto)
# Esegui setup
.\start.ps1

# Scarica video test
.\download_sample_video.ps1
```

### 2. Sviluppo e Test

```powershell
# Test singolo video
python main_video.py sample_bigbuck_1mb.mp4

# Apri browser: index_video.html
```

### 3. Integrazione n8n

```powershell
# Terminal 1: Avvia API server
python api_server.py

# Terminal 2: Avvia n8n
n8n start

# Browser: http://localhost:5678
# Importa: n8n-workflow-example.json
```

### 4. Produzione

```powershell
# Configura modelli ottimali
python config_manager.py suggest 8  # 8GB VRAM disponibile

# Avvia servizio
python api_server.py
```

## 📝 Checklist Pre-Produzione

- [ ] CUDA funzionante (`python -c "import torch; print(torch.cuda.is_available())"`)
- [ ] FFmpeg installato (`ffmpeg -version`)
- [ ] Modelli configurati (`python config_manager.py active`)
- [ ] VRAM sufficiente (`python config_manager.py vram`)
- [ ] Test con video campione
- [ ] API server raggiungibile
- [ ] n8n configurato (se usato)
- [ ] Firewall configurato per porte 8000, 8765

## 🔗 Link Utili

- **API Docs**: http://localhost:8000/docs
- **n8n**: http://localhost:5678
- **WebSocket Test**: index_video.html

## 🆘 Supporto

Se hai problemi:

1. Verifica i requisiti di sistema
2. Controlla i log per errori
3. Consulta README_IT.md per dettagli
4. Verifica CUDA e dipendenze

## 🎉 Prossimi Passi

Una volta che tutto funziona:

1. **Testa con i tuoi video**
2. **Configura n8n workflows**
3. **Implementa logica di selezione stream**
4. **Ottimizza per il tuo hardware**
5. **Crea dashboard personalizzate**

Buon divertimento con AI Director! 🎬
