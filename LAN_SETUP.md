# 🌐 LAN Access - Quick Setup Guide

Access your AI Director from any device on your local network (Mac, phone, tablet, another PC).

## 📝 Step-by-Step Instructions

### 1️⃣ Find Your Windows PC's IP Address

Open PowerShell and run:

```powershell
ipconfig
```

Look for the **IPv4 Address** under your active network adapter (usually "Ethernet adapter" or "Wireless LAN adapter"):

```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

**Your IP**: `192.168.1.100` (example - yours will be different)

---

### 2️⃣ Configure Windows Firewall

Open PowerShell **as Administrator** and run these commands:

```powershell
# Allow WebSocket server (port 8765)
New-NetFirewallRule -DisplayName "AI Director WebSocket" -Direction Inbound -Protocol TCP -LocalPort 8765 -Action Allow

# Allow HTTP server (port 8080)
New-NetFirewallRule -DisplayName "AI Director HTTP" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

✅ You should see:
```
Name                  : {GUID}
DisplayName           : AI Director WebSocket
...
```

---

### 3️⃣ Start Both Servers

#### Terminal 1: Video Analysis Server

```powershell
cd e:\dev\ai-director\smolvlm-audio-transcription
.venv\Scripts\activate
python main_video.py your_video.mp4 --frames 15
```

✅ Wait for: `🌐 WebSocket: ws://0.0.0.0:8765`

#### Terminal 2: HTTP Server

```powershell
cd e:\dev\ai-director\smolvlm-audio-transcription
.venv\Scripts\activate
python serve_html.py
```

✅ You should see:
```
🌐 Starting HTTP Server on http://0.0.0.0:8080
🔗 Access from LAN: http://192.168.1.100:8080/index_video.html
```

---

### 4️⃣ Access from Other Devices

On your **Mac, phone, or tablet**, open a web browser and go to:

```
http://192.168.1.100:8080/index_video.html
```

Replace `192.168.1.100` with **your PC's IP address** from Step 1.

---

## ✅ Checklist

- [ ] Found Windows PC IP address (`ipconfig`)
- [ ] Added firewall rules (ports 8765 and 8080)
- [ ] Started `main_video.py` (WebSocket server)
- [ ] Started `serve_html.py` (HTTP server)
- [ ] Both devices on same WiFi network
- [ ] Opened browser on other device: `http://[PC-IP]:8080/index_video.html`

---

## 🔧 Troubleshooting

### ❌ Can't connect from other device

**Check network:**
```powershell
# Ping from your Mac/phone to Windows PC
ping 192.168.1.100
```

If ping fails:
- Ensure both devices are on the **same WiFi network**
- Check Windows Firewall settings in Control Panel
- Try disabling Windows Firewall temporarily (testing only!)

**Check servers are running:**
```powershell
# Check if ports are listening
netstat -an | findstr "8080 8765"
```

Should show:
```
TCP    0.0.0.0:8080           0.0.0.0:0              LISTENING
TCP    0.0.0.0:8765           0.0.0.0:0              LISTENING
```

### ❌ WebSocket connection failed

**Browser console (F12) shows:**
```
WebSocket connection to 'ws://localhost:8765' failed
```

**Solution**: The HTML is auto-detecting the host. Make sure:
1. You accessed via `http://[PC-IP]:8080/index_video.html` (not `localhost`)
2. The WebSocket server (`main_video.py`) is running
3. Firewall rule for port 8765 is active

### ❌ Video not loading

**Check video file path:**
```powershell
python main_video.py e:\full\path\to\video.mp4 --frames 15
```

Use **absolute paths** if relative paths fail.

---

## 📱 Mobile Access Tips

### iOS Safari
- Works out of the box
- Use full URL: `http://192.168.1.100:8080/index_video.html`

### Android Chrome
- Works out of the box
- May need to allow "insecure content" for `http://` (not `https://`)

### macOS Safari/Chrome
- Works perfectly
- Can bookmark for quick access

---

## 🔐 Security Notes

⚠️ **This setup is for LOCAL NETWORK ONLY**

- Do **NOT** expose ports 8080 or 8765 to the internet
- Use only on trusted WiFi networks
- For internet access, set up a VPN or reverse proxy with HTTPS

---

## 🚀 Advanced: Access from Anywhere

To access from outside your home network:

### Option 1: Tailscale (Recommended)
1. Install [Tailscale](https://tailscale.com/) on Windows PC and remote device
2. Use Tailscale IP instead of local IP

### Option 2: ngrok
```powershell
# Install ngrok
choco install ngrok

# Tunnel HTTP server
ngrok http 8080
```

### Option 3: Cloudflare Tunnel
1. Install [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
2. Configure tunnel for port 8080

---

## 📞 Need Help?

- Check the main [README.md](README.md)
- Open an issue on [GitHub](https://github.com/UV-projects/ai-director)
- Ensure Python and servers are running without errors

---

**Happy streaming! 🎬**
