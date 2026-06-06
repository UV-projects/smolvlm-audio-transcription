# AI Director — Demo Launcher

A lightweight, macOS-first version of the demo. One click starts everything; the
whole thing is controlled from the browser. No command line needed.

## Start

- Double-click **`AI Director.app`** (in the project root).
  - It starts the control server and opens your browser at `http://127.0.0.1:8000`.
  - If macOS blocks it the first time: right-click the app, choose **Open**, confirm once.
- Alternative (shows logs in Terminal): double-click **`launcher/start.command`**.

## Use

In the page:

1. Pick a **Source**: *Webcam* or *Video file*.
2. Pick a **Vision model** (default: Qwen3-VL 2B — the paper's model).
3. Press **Start**. The model loads, then the camera feed, VLM responses, and live
   transcription appear.
4. **Stop** ends capture and unloads the model to free memory. **Restart** reloads.

The first time you use the webcam/microphone, the browser asks for permission. Grant it.

## Stop everything

- Quit **`AI Director.app`** (Cmd-Q from the Dock), or close the `start.command`
  Terminal window. Backends are stopped automatically.

## Models (all run locally via llama.cpp + Metal)

| Model | Memory | Notes |
|-------|--------|-------|
| Qwen3-VL 2B (Q4) | ~1.5 GB | Default. Matches the paper. |
| SmolVLM 500M | ~0.8 GB | Lightest/fastest; shorter, less accurate output. |
| Qwen3-VL 2B (Q8) | ~2.5 GB | Higher quality. |
| SmolVLM 2.2B / Qwen3-VL 4B | ~3–5 GB | Downloaded on first selection. |

Speech-to-text uses the **Vosk small** English model (~40 MB), kept local.
Total footprint with the default model is well under 2 GB — far below the previous
multi-model stack that maxed out 16 GB.

To change the startup model, edit `default_model` in `launcher/config.json`.

## Files

- `control_server.py` — serves the UI, proxies the VLM, manages the model and STT processes.
- `director.html` — the web interface.
- `config.json` — ports and the model list.
- `download_models.sh` — fetches the Vosk small speech model.
- `logs/` — `vlm.log` and `stt.log` for troubleshooting.
