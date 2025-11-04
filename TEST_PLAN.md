# 🧪 Test Plan - Video Integration

## Sistema di Test

### 1. ✅ Video Analyzer (Completato)
**Stato**: FUNZIONA! 
- Server WebSocket attivo su porta 8766
- Streaming video ted-talk.mp4 a 15 FPS
- Compatibile con architettura Ollama
- Orchestrator opzionale (non richiesto)

### 2. 🔄 Interfaccia Web (In Test)
**File**: `web/unified_interface.html`

**Test da eseguire**:

#### Test A: Verifica Toggle Video
1. Apri `web/unified_interface.html` in browser
2. Verifica presenza dropdown con opzioni:
   - 📹 Webcam
   - 🎬 Video File
3. Seleziona "🎬 Video File"
4. Verifica che l'elemento video cambi a immagine

#### Test B: Connessione Video Analyzer
1. Con "Video File" selezionato, clicca "▶ Start System"
2. Verifica nella console browser:
   - Connessione a `ws://localhost:8766`
   - Ricezione frame video
3. Verifica visivamente:
   - Frame del video visualizzati nell'interfaccia
   - Aggiornamento continuo (~15 FPS)

#### Test C: Integrazione Ollama (Se Disponibile)
1. Verifica che Ollama sia in esecuzione:
   ```powershell
   # Controlla se Ollama è attivo
   curl http://localhost:11434/api/tags
   ```
2. Con video in streaming, i frame dovrebbero essere analizzati da Ollama
3. Risultati analisi dovrebbero apparire in "VLM Response"

#### Test D: Modalità Webcam (Backward Compatibility)
1. Seleziona "📹 Webcam" dal dropdown
2. Clicca "▶ Start System"
3. Verifica che webcam funzioni come prima
4. Nessuna regressione nelle funzionalità esistenti

### 3. ⏳ PDF Server (Opzionale)
Se vuoi testare anche il controllo PDF vocale:
```powershell
python src\presenter\pdf_server.py
```

### 4. ⏳ Orchestrator (Opzionale)
Se vuoi testare comandi orchestrati:
```powershell
python src\orchestrator\orchestrator.py
```

## Checklist Test Completa

### Funzionalità Core
- [ ] Video analyzer serve frames
- [ ] Browser riceve frames via WebSocket
- [ ] Frames visualizzati nell'interfaccia
- [ ] Toggle webcam/video funziona
- [ ] Nessun errore console browser

### Integrazione Ollama
- [ ] Browser invia frames a Ollama (se disponibile)
- [ ] Ollama restituisce analisi
- [ ] Analisi visualizzata in interfaccia

### Backward Compatibility
- [ ] Modalità webcam funziona normalmente
- [ ] PDF viewer funziona (se server attivo)
- [ ] Audio STT funziona (se server attivo)
- [ ] Nessuna breaking change

## Problemi Noti

### Da Risolvere
1. **Ollama non testato**: Verificare se Ollama è installato e configurato
2. **VLM model**: Confermare quale modello usano i colleghi (qwen3-vl:2b-instruct?)

### Deprecation Warnings (Non Critici)
- `websockets.WebSocketClientProtocol` deprecated - funziona comunque

## Prossimi Passi

Se tutti i test passano:
1. ✅ Aggiornare documentazione
2. ✅ Committare modifiche
3. ✅ Push al branch main
4. ✅ Creare PR o merge diretto

Se ci sono problemi:
1. ❌ Documentare errori
2. ❌ Fix necessari
3. ❌ Re-test

---

**Eseguito da**: AI Assistant
**Data**: 2025-11-04
**Commit Target**: main branch
