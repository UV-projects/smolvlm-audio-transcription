# 🎬 Sistema AI Director Completo

## 📋 Cosa fa il Sistema

Il tuo sistema è un **REGISTA AI** che analizza video in tempo reale combinando due AI:

### 1. 🔍 **SmolVLM** (Vision Language Model)
- **Cosa fa**: Guarda i frame video e li descrive in linguaggio naturale
- **Quando**: Analizza un frame ogni 5 secondi (configurabile)
- **Output**: "A bunny is sitting in the grass looking at something"
- **Modelli disponibili**: 
  - `small` (500M parametri, 2GB VRAM)
  - `medium` (1.7B parametri, 4GB VRAM)

### 2. 🎤 **Moshi STT** (Speech-to-Text)
- **Cosa fa**: Trascrive l'audio del video in tempo reale
- **Quando**: Continuamente, analizzando l'audio estratto dal video
- **Output**: "Hello, how are you today?"
- **Modelli disponibili**:
  - `small` (1B parametri, 1GB VRAM)
  - `medium` (2B parametri, 2GB VRAM)

---

## 🎯 Il Tuo Obiettivo: AI Director Multi-Camera

### Scenario Ideale
Immagina 4-6 telecamere che riprendono diverse zone di una stanza:
```
Camera 1: Porta d'ingresso
Camera 2: Area conversazione
Camera 3: Scrivania
Camera 4: Zona cucina
```

### Cosa Farà il Sistema
1. **Analizza ogni feed** in parallelo (SmolVLM + Moshi)
2. **Rileva eventi interessanti**:
   - 🚶 Persona entra nella stanza
   - 🗣️ Qualcuno inizia a parlare
   - 👋 Movimento/gesto importante
   - 📦 Nuovo oggetto appare
3. **Sceglie automaticamente** quale camera mostrare
4. **Switch intelligente** tra le diverse inquadrature

### Come Funzionerà con n8n
```
Video Feed 1 → API Endpoint → Analisi AI → Score di Importanza
Video Feed 2 → API Endpoint → Analisi AI → Score di Importanza
Video Feed 3 → API Endpoint → Analisi AI → Score di Importanza
Video Feed 4 → API Endpoint → Analisi AI → Score di Importanza
                                           ↓
                                    n8n Workflow
                                           ↓
                        Seleziona il feed più interessante
                                           ↓
                                    Output Stream
```

---

## 🔧 Come Funziona Attualmente

### File Principali

#### `main_video.py` (Appena Aggiornato!)
```python
# 1. VisionAnalyzer - Usa SmolVLM per descrivere frame
vision_analyzer = VisionAnalyzer("HuggingFaceTB/SmolVLM-500M-Instruct")

# 2. VideoProcessor - Legge video e invia frame per analisi
video_processor = VideoProcessor(
    video_path="video.mp4",
    vision_analyzer=vision_analyzer,
    analyze_interval=5.0  # Analizza ogni 5 secondi
)

# 3. AudioSTT - Trascrive audio
stt = AudioSTT(video_path="video.mp4", model_repo="kyutai/stt-1b-en_fr")

# 4. WebSocket Server - Invia tutto al browser
# Messaggi inviati:
# - {"type": "video_frame", "data": "base64_image"}
# - {"type": "vision_analysis", "description": "...", "frame": 123, "timestamp": 5.2}
# - {"type": "transcription", "text": "Hello"}
```

#### `index_video.html` (Appena Aggiornato!)
Ora ha **DUE BOX**:
1. **Vision Analysis (SmolVLM)** - Verde acqua, mostra descrizioni video
2. **Audio Transcription (Moshi)** - Viola, mostra trascrizioni audio

#### `api_server.py` (Per n8n)
REST API con endpoint:
- `POST /streams/create` - Crea nuovo stream video
- `GET /streams` - Lista stream attivi
- `GET /analysis/{stream_id}` - Ottieni analisi
- `POST /models/switch` - Cambia modello
- `GET /health` - Stato sistema

---

## 📊 Cosa Significa "FPS Received"

**FPS Received** = Frames Per Second ricevuti dal browser via WebSocket

- **Origine**: Quanti frame/secondo arrivano dal server Python al browser
- **Normale**: 15-30 FPS per video fluido
- **Basso (<10 FPS)**: GPU occupata con analisi, normale
- **Alto (>30 FPS)**: Spreco di banda, puoi ridurre

**Non confondere con**:
- FPS del video originale (es: 25 FPS)
- FPS di analisi SmolVLM (0.2 FPS = ogni 5 secondi)
- FPS della trascrizione audio (continua)

---

## 🚀 Come Testare Ora

### 1. Test Base (Appena fixato!)
```powershell
cd e:\dev\ai-director\smolvlm-audio-transcription
.\.venv\Scripts\Activate.ps1
python main_video.py sample_bigbuck_1mb.mp4
```

**Cosa vedrai**:
```
🚀 Using CUDA GPU: NVIDIA GeForce RTX 2070 SUPER
   VRAM Available: 8.0 GB

🔍 Loading SmolVLM model: HuggingFaceTB/SmolVLM-500M-Instruct on cuda...
✅ SmolVLM loaded successfully!

🎤 Initializing Audio Transcription...
Loading STT model from kyutai/stt-1b-en_fr on cuda...

Video loaded: sample_bigbuck_1mb.mp4
FPS: 25, Total frames: 215

🔍 Analyzing frame 0...
📝 Description: A small bunny is sitting in grass surrounded by flowers...

🔍 Analyzing frame 125...
📝 Description: The bunny is looking up at a butterfly flying above...
```

### 2. Apri Browser
Apri `index_video.html` nel browser:
- Vedrai i frame video in tempo reale
- Vedrai le descrizioni SmolVLM ogni 5 secondi
- Vedrai trascrizioni audio (se il video ha audio)

### 3. Personalizza Intervallo Analisi
Nel comando puoi cambiare quanto spesso analizzare:

```python
# In main_video.py, funzione main():
asyncio.run(main_async(
    video_path=sys.argv[1],
    use_audio=True,
    analyze_interval=3.0  # Ogni 3 secondi invece di 5
))
```

O modifica direttamente:
```powershell
# Analisi ogni 2 secondi (più intensivo, ma più dettagliato)
python main_video.py sample_bigbuck_1mb.mp4 --interval 2.0
```

---

## 🎮 Prossimi Passi per AI Director

### Fase 1: Test Singolo Stream ✅ (Ora)
- [x] Carica video
- [x] Analizza con SmolVLM
- [x] Trascrive con Moshi
- [x] Mostra risultati nel browser

### Fase 2: Sistema Multi-Stream (Prossimo)
Bisogna creare:
1. **Stream Manager** - Gestisce 4-6 feed video simultanei
2. **Priority Scorer** - Calcola quale stream è più interessante
3. **Auto-Switcher** - Cambia automaticamente tra stream

### Fase 3: Integrazione n8n
1. Installa n8n: `npm install -g n8n`
2. Avvia API server: `python api_server.py`
3. Crea workflow che:
   - Riceve notifiche quando succede qualcosa di interessante
   - Decide quale camera mostrare
   - Trigghera azioni (notifiche, registrazioni, etc)

---

## 🐛 Cosa Era Sbagliato Prima

### Problema 1: Nessuna Descrizione Video
**Prima**: Il codice leggeva i frame ma NON li analizzava con SmolVLM
**Ora**: Ogni 5 secondi analizza un frame e invia la descrizione

### Problema 2: Audio Non Funzionante
**Prima**: Big Buck Bunny non ha dialoghi quindi silenzio
**Ora**: Se usi un video con audio (parlato), vedrai la trascrizione in tempo reale

### Problema 3: Interfaccia Confusa
**Prima**: Una sola box "transcription" poco chiara
**Ora**: Due box separate:
- 🔍 Verde = Descrizioni video (SmolVLM)
- 🎤 Viola = Trascrizioni audio (Moshi)

---

## 💡 Consigli per Video di Test

### Video Ideali per Testare
1. **Con Dialogo**: Film, interviste, presentazioni
2. **Con Azione**: Sport, animali in movimento
3. **Multi-Persona**: Riunioni, conferenze

### Scaricare Video di Test YouTube
```powershell
# Installa yt-dlp se non ce l'hai
pip install yt-dlp

# Scarica un video breve (es: TED talk)
yt-dlp -f "best[height<=720]" --output "test_video.mp4" "URL_YOUTUBE"
```

### Esempi di Video Utili
- TED Talks (persona che parla + slide)
- Video sportivi (azione + commento)
- Tutorial cucina (azione + spiegazione)
- News (presentatore + eventi)

---

## 🎛️ Configurazione Modelli

Modifica `config.json` per scegliere i modelli:

```json
{
  "active_models": {
    "vlm": "small",    // o "medium" per analisi migliore (4GB VRAM)
    "stt": "small"     // o "medium" per trascrizione migliore (2GB VRAM)
  },
  "analysis": {
    "vision_interval": 5.0,    // Secondi tra analisi frame
    "min_confidence": 0.5       // Score minimo per eventi
  }
}
```

### Per RTX 2070 SUPER (8GB)
Configurazioni consigliate:

**Qualità Massima** (7GB usati):
- VLM: medium (4GB)
- STT: medium (2GB)
- Streams: 1

**Bilanciato** (5GB usati):
- VLM: medium (4GB)
- STT: small (1GB)
- Streams: 1

**Multi-Stream** (6GB usati):
- VLM: small (2GB)
- STT: small (1GB)
- Streams: 2-3

---

## ❓ FAQ

**Q: Perché non vedo descrizioni?**
A: Aspetta 5 secondi, è l'intervallo di analisi. La prima analisi scarica anche il modello.

**Q: Posso analizzare più velocemente?**
A: Sì, ma consuma più GPU. Cambia `analyze_interval` in `main_video.py`.

**Q: Posso usare webcam invece di video?**
A: Sì, cambia `cv2.VideoCapture(0)` invece del percorso file.

**Q: Come aggiungo più stream?**
A: Prossimo step! Creeremo un `stream_manager.py` che gestisce multipli VideoProcessor.

**Q: n8n può controllare quale camera scegliere?**
A: Sì! Useremo l'API REST per comunicare con n8n e decidere lo switch.

---

## 🎉 Recap

Hai ora un sistema che:
✅ Legge video da file
✅ Descrive cosa vede (SmolVLM)
✅ Trascrive audio (Moshi)  
✅ Mostra tutto in tempo reale nel browser
✅ Usa CUDA per accelerazione GPU
✅ Ha API REST per integrazione n8n

**Prossimo Goal**: Multi-stream con switching automatico! 🚀
