#!/usr/bin/env python3
"""
AI Director - demo control server.

One process that:
  - serves the web UI (director.html) at http://127.0.0.1:<control_port>/
  - manages the VLM backend (llama-server) and the speech-to-text backend (Vosk)
  - exposes a small JSON API so everything is controlled from the browser GUI
  - proxies VLM requests so the page talks to a single origin (no IP editing)

Standard library only. Designed for Apple Silicon (Metal) on a 16 GB machine.
"""

import atexit
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.expanduser("~/Library/Caches/llama.cpp")
LLAMA = os.path.join(ROOT, "build", "bin", "llama-server")
AUDIO_PY = os.path.join(ROOT, "src", "audio", "audio.py")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

with open(os.path.join(HERE, "config.json")) as f:
    CFG = json.load(f)

CONTROL_PORT = CFG.get("control_port", 8000)
VLM_PORT = CFG.get("vlm_port", 8080)
STT_PORT = CFG.get("stt_port", 2700)
VLM_CTX = CFG.get("vlm_context", 4096)
NGL = CFG.get("gpu_layers", 99)
MODELS = {m["id"]: m for m in CFG["models"]}

VOSK_CANDIDATES = [
    os.path.join(ROOT, "models", "vosk-model-small-en-us-0.15"),
    os.path.join(ROOT, "models", "vosk-model-en-us-0.42-gigaspeech"),
]

# ----------------------------------------------------------------------------- state
S = {
    "vlm": None,          # Popen
    "stt": None,          # Popen
    "active_model": CFG.get("default_model", CFG["models"][0]["id"]),
    "starting": False,
}
LOCK = threading.RLock()


# ----------------------------------------------------------------------------- helpers
def model_paths(mid):
    """Return (cmd_args, ready). Prefer cached local files; fall back to -hf."""
    m = MODELS.get(mid)
    if not m:
        return None, False
    if m.get("model"):
        mp = os.path.join(CACHE, m["model"])
        pp = os.path.join(CACHE, m["mmproj"]) if m.get("mmproj") else None
        ready = os.path.exists(mp) and (pp is None or os.path.exists(pp))
        args = ["-m", mp] + (["--mmproj", pp] if pp else [])
        return args, ready
    if m.get("hf"):
        return ["-hf", m["hf"]], False  # ready=False -> needs download on first use
    return None, False


def models_payload():
    out = []
    for m in CFG["models"]:
        _, ready = model_paths(m["id"])
        out.append({"id": m["id"], "name": m["name"], "note": m.get("note", ""), "ready": ready})
    return out


def vosk_model_dir():
    for p in VOSK_CANDIDATES:
        if os.path.isdir(p):
            return p
    return None


def port_open(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()


def vlm_ready():
    """llama-server returns 200 on /health when the model is fully loaded."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/health" % VLM_PORT, timeout=1) as r:
            return r.status == 200
    except Exception:
        return False


def proc_rss_mb(*procs):
    pids = [str(p.pid) for p in procs if p and p.poll() is None]
    if not pids:
        return 0
    try:
        out = subprocess.check_output(["ps", "-o", "rss=", "-p", ",".join(pids)], text=True)
        return int(sum(int(x) for x in out.split()) / 1024)
    except Exception:
        return 0


def alive(p):
    return p is not None and p.poll() is None


def kill(p):
    if not alive(p):
        return
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    except Exception:
        try:
            p.terminate()
        except Exception:
            pass
    try:
        p.wait(timeout=6)
    except Exception:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            pass


def start_vlm(mid):
    args, _ = model_paths(mid)
    if args is None:
        raise RuntimeError("Unknown model: %s" % mid)
    kill(S["vlm"])
    cmd = [LLAMA, *args, "--host", "127.0.0.1", "--port", str(VLM_PORT),
           "-ngl", str(NGL), "-c", str(VLM_CTX)]
    logf = open(os.path.join(LOG_DIR, "vlm.log"), "w")
    S["vlm"] = subprocess.Popen(cmd, cwd=ROOT, stdout=logf, stderr=subprocess.STDOUT,
                                start_new_session=True)
    S["active_model"] = mid


def start_stt():
    if alive(S["stt"]):
        return
    vd = vosk_model_dir()
    if not vd:
        raise RuntimeError("No Vosk model found in models/. Run download_models.sh.")
    env = dict(os.environ, VOSK_SERVER_PORT=str(STT_PORT), VOSK_SAMPLE_RATE="16000")
    logf = open(os.path.join(LOG_DIR, "stt.log"), "w")
    S["stt"] = subprocess.Popen([sys.executable, AUDIO_PY, vd], cwd=ROOT, env=env,
                                stdout=logf, stderr=subprocess.STDOUT, start_new_session=True)


def start_all(mid):
    with LOCK:
        S["starting"] = True
        try:
            start_vlm(mid)
            start_stt()
        finally:
            S["starting"] = False


def stop_all():
    with LOCK:
        kill(S["vlm"]); S["vlm"] = None
        kill(S["stt"]); S["stt"] = None


def status():
    vlm_run = alive(S["vlm"]) and port_open(VLM_PORT)
    ready = vlm_run and vlm_ready()
    m = MODELS.get(S["active_model"], {})
    return {
        "vlm": {"running": vlm_run, "ready": ready, "model_name": m.get("name", S["active_model"]),
                "port": VLM_PORT},
        "stt": {"running": alive(S["stt"]) and port_open(STT_PORT), "port": STT_PORT,
                "model": os.path.basename(vosk_model_dir() or "none")},
        "active_model": S["active_model"],
        "models": models_payload(),
        "mem_mb": proc_rss_mb(S["vlm"], S["stt"]),
        "starting": S["starting"],
    }


# ----------------------------------------------------------------------------- http
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n) if n else b""

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html", "/director.html"):
            with open(os.path.join(HERE, "director.html"), "rb") as fh:
                return self._send(200, fh.read(), "text/html; charset=utf-8")
        if path == "/api/status":
            return self._send(200, status())
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        try:
            if path == "/v1/chat/completions":
                return self._proxy_vlm()
            if path == "/api/start":
                mid = (json.loads(self._body() or b"{}")).get("model") or S["active_model"]
                threading.Thread(target=start_all, args=(mid,), daemon=True).start()
                return self._send(200, {"ok": True, "model": mid})
            if path == "/api/stop":
                stop_all()
                return self._send(200, {"ok": True})
            if path == "/api/restart":
                mid = (json.loads(self._body() or b"{}")).get("model") or S["active_model"]
                stop_all()
                threading.Thread(target=start_all, args=(mid,), daemon=True).start()
                return self._send(200, {"ok": True, "model": mid})
            if path == "/api/model":
                mid = (json.loads(self._body() or b"{}")).get("model")
                if mid not in MODELS:
                    return self._send(400, {"error": "unknown model"})
                threading.Thread(target=start_vlm, args=(mid,), daemon=True).start()
                return self._send(200, {"ok": True, "model": mid})
            return self._send(404, {"error": "not found"})
        except BrokenPipeError:
            pass
        except Exception as e:
            return self._send(500, {"error": str(e)})

    def _proxy_vlm(self):
        body = self._body()
        req = urllib.request.Request(
            "http://127.0.0.1:%d/v1/chat/completions" % VLM_PORT,
            data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return self._send(r.status, r.read(), "application/json")
        except urllib.error.HTTPError as e:
            return self._send(e.code, e.read(), "application/json")
        except Exception as e:
            return self._send(502, {"error": "VLM backend not reachable: %s" % e})


def main():
    if not os.path.exists(LLAMA):
        print("WARNING: llama-server not found at", LLAMA)
    srv = ThreadingHTTPServer(("127.0.0.1", CONTROL_PORT), Handler)

    atexit.register(stop_all)

    def shutdown(*_):
        print("\nShutting down backends...")
        stop_all()
        # Call srv.shutdown() from a separate thread: calling it on the same
        # thread that runs serve_forever() would deadlock.
        threading.Thread(target=srv.shutdown, daemon=True).start()
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        try:
            signal.signal(sig, shutdown)
        except Exception:
            pass

    print("AI Director control server: http://127.0.0.1:%d" % CONTROL_PORT)
    try:
        srv.serve_forever()
    finally:
        stop_all()


if __name__ == "__main__":
    main()
