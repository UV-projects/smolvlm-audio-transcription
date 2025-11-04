# Script per avviare tutti i server del sistema AI Director
# Uso: .\start_all_servers.ps1

Write-Host "🚀 Avvio AI Director - Sistema Completo" -ForegroundColor Cyan
Write-Host ""

# Aggiungi llama.cpp al PATH
$env:Path = "C:\Tools\llama.cpp;" + $env:Path

# Vai nella directory del progetto
Set-Location $PSScriptRoot

Write-Host "1️⃣ Avvio llama-server (VLM - Qwen3-VL-2B-Instruct)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "`$env:Path = 'C:\Tools\llama.cpp;' + `$env:Path; llama-server -hf Qwen/Qwen3-VL-2B-Instruct-GGUF -ngl 99" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "2️⃣ Avvio Audio STT (Vosk)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python src\audio\main.py" -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host "3️⃣ Avvio Video Analyzer (ted-talk.mp4)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python src\vision\video_analyzer.py ted-talk.mp4" -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "✅ TUTTI I SERVER SONO STATI AVVIATI!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Server Attivi:" -ForegroundColor Cyan
Write-Host "   • Qwen3-VL-2B VLM:       http://localhost:8080" -ForegroundColor White
Write-Host "   • Audio STT (Vosk):      ws://localhost:8765" -ForegroundColor White
Write-Host "   • Video Analyzer:        ws://localhost:8766 (25 FPS)" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Apri il browser:" -ForegroundColor Cyan
Write-Host "   file:///$PSScriptRoot/web/unified_interface.html" -ForegroundColor White
Write-Host ""
Write-Host "📝 Istruzioni:" -ForegroundColor Cyan
Write-Host "   1. Nel browser, seleziona '🎬 Video File' dal dropdown" -ForegroundColor White
Write-Host "   2. Clicca '▶ Start System'" -ForegroundColor White
Write-Host "   3. Parla nel microfono per audio STT" -ForegroundColor White
Write-Host "   4. Guarda video + VLM Qwen3 + trascrizione in tempo reale!" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Per fermare i server, chiudi le finestre PowerShell" -ForegroundColor Yellow
