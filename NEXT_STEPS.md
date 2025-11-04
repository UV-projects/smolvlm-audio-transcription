# 🎯 GUIDA RAPIDA - Test del Sistema

## ✅ Moshi Installato Correttamente!

Il pacchetto Moshi è ora installato dalla versione corretta dal repository GitHub.

---

## 🚀 Adesso Puoi Testare!

### Opzione 1: Test Veloce (Consigliato per iniziare)

```powershell
# Esegui direttamente con un video
python main_video.py sample_bigbuck_1mb.mp4
```

**Poi apri `index_video.html` nel browser**

---

### Opzione 2: Menu Interattivo

```powershell
.\start.ps1
# Seleziona opzione 2
# Inserisci nome video
# Abilita audio: y
```

---

## 📝 Cosa Aspettarti

### Prima Esecuzione (2-5 minuti):
1. **Downloading models...** - Scarica Moshi STT da HuggingFace (~1-2GB)
2. **Loading model...** - Carica il modello sulla GPU
3. **Starting WebSocket server...** - Avvia server su porta 8765
4. **Processing video...** - Inizia elaborazione

### Durante l'Elaborazione:
- Console mostrerà: frame processati, FPS, transcription chunks
- GPU sarà al 50-80% utilizzo (puoi vedere con `nvidia-smi`)

### Nel Browser (index_video.html):
- 📹 Video frame by frame
- 🤖 Analisi visuale (cosa vede SmolVLM)
- 🎤 Trascrizione audio real-time
- 📊 Statistiche (FPS, frame count, words)

---

## 🐛 Se Qualcosa Va Storto

### "Port 8765 already in use"
```powershell
# Trova e termina processo
netstat -ano | findstr :8765
taskkill /PID <PID> /F
```

### "Out of Memory"
```powershell
# Usa solo video senza audio
python main_video.py video.mp4 --no-audio
```

### Altro
Verifica con:
```powershell
python test_system.py
```

---

## 🎬 Dopo il Test Video

### Per n8n Integration:

1. **Installa n8n**:
```powershell
npm install -g n8n
```

2. **Avvia API Server**:
```powershell
python api_server.py
# Docs: http://localhost:8000/docs
```

3. **Avvia n8n**:
```powershell
n8n start
# UI: http://localhost:5678
```

4. **Importa workflow**: `n8n-workflow-example.json`

---

## 💡 Tips

- **Prima volta**: Usa video corto (< 30 secondi)
- **Monitora GPU**: `nvidia-smi -l 1` in altro terminale
- **Test rapido**: Aggiungi `--no-audio` per skip trascrizione
- **Cambia modelli**: `python config_manager.py set-stt medium`

---

**Prova ora:**
```powershell
python main_video.py sample_bigbuck_1mb.mp4
```

Poi apri `index_video.html` e guarda la magia! ✨
