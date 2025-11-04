# ==========================================
# AI Director - Smart GPU-Accelerated Startup
# ==========================================
# Auto-detects NVIDIA CUDA, Apple Metal (MPS), or falls back to CPU

param(
    [switch]$ForceCPU = $false
)

Write-Host ""
Write-Host "🚀 AI Director - Smart Startup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
Set-Location $PSScriptRoot\..

# GPU Auto-detection
Write-Host "🔍 Detecting GPU..." -ForegroundColor Yellow

if ($ForceCPU) {
    Write-Host "⚠️  Force CPU mode enabled" -ForegroundColor Yellow
    $nglLayers = 0
    $gpuInfo = "CPU (forced)"
} else {
    # Always use -ngl 99 (llama-server auto-detects GPU)
    # If CUDA/Metal available: uses GPU
    # If not available: falls back to CPU automatically
    $nglLayers = 99
    
    # Check what GPU is available (for display purposes only)
    if (Test-Path "C:\Windows\System32\nvidia-smi.exe") {
        try {
            $nvidiaSmi = & nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1 | Select-Object -First 1
            if ($nvidiaSmi -notlike "*error*") {
                $gpuInfo = "NVIDIA $nvidiaSmi"
                Write-Host "✅ NVIDIA GPU detected: $gpuInfo" -ForegroundColor Green
            } else {
                $gpuInfo = "CPU (CUDA runtime not available)"
                Write-Host "ℹ️  $gpuInfo" -ForegroundColor Gray
            }
        } catch {
            $gpuInfo = "CPU (nvidia-smi failed)"
            Write-Host "ℹ️  $gpuInfo" -ForegroundColor Gray
        }
    } else {
        # Check for Apple Metal via Python (if needed)
        $gpuInfo = "CPU or GPU (auto-detect)"
        Write-Host "ℹ️  GPU auto-detection enabled (-ngl 99)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "📊 Configuration:" -ForegroundColor Cyan
Write-Host "   GPU Layers (-ngl): $nglLayers" -ForegroundColor White
Write-Host ""

# Add llama.cpp to PATH
$env:Path = "C:\Tools\llama.cpp;" + $env:Path

Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host "🎬 Starting Servers" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host ""

# 1. VLM Server (Qwen3-VL)
Write-Host "1️⃣  Starting Qwen3-VL-2B (VLM)..." -ForegroundColor Yellow
$modelPath = "C:\Users\Eugenio\AppData\Local\llama.cpp\Qwen_Qwen3-VL-2B-Instruct-GGUF_Qwen3VL-2B-Instruct-Q4_K_M.gguf"
$mmprojPath = "C:\Users\Eugenio\AppData\Local\llama.cpp\mmproj-Qwen3VL-2B-Instruct-F16.gguf"
$llamaExe = "C:\Tools\llama.cpp\llama-server.exe"
$llamaCmd = "cd '$PSScriptRoot\..'; Write-Host '🤖 Qwen3-VL-2B VLM Server' -ForegroundColor Green; Write-Host 'GPU: $gpuInfo' -ForegroundColor Cyan; Write-Host 'Layers offloaded (-ngl): $nglLayers' -ForegroundColor Gray; Write-Host ''; & '$llamaExe' --model '$modelPath' --mmproj '$mmprojPath' --port 8080 --ctx-size 4096 --n-predict 512 --temp 0.7 --top-p 0.9 --top-k 40 --repeat-penalty 1.1 --threads 8 --batch-size 512 --ubatch-size 128 --flash-attn --mlock --no-mmap --gpu-layers $nglLayers"
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $llamaCmd -WindowStyle Normal

Start-Sleep -Seconds 3

# 2. Audio STT
Write-Host "2️⃣  Starting Audio STT (Vosk)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..'; Write-Host '🎤 Audio STT Server (Vosk)' -ForegroundColor Green; Write-Host 'Port: ws://localhost:8765' -ForegroundColor Cyan; Write-Host ''; python src\audio\main.py" -WindowStyle Normal

Start-Sleep -Seconds 2

# 3. Video Analyzer
Write-Host "3️⃣  Starting Video Analyzer..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..'; Write-Host '🎬 Video Analyzer' -ForegroundColor Green; Write-Host 'Port: ws://localhost:8766' -ForegroundColor Cyan; Write-Host 'Video: ted-talk.mp4 @ 25 FPS (native)' -ForegroundColor Gray; Write-Host ''; python src\vision\video_analyzer.py ted-talk.mp4" -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ ALL SERVERS STARTED" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Active Servers:" -ForegroundColor Cyan
Write-Host "   🤖 Qwen3-VL (VLM):     http://localhost:8080  [$gpuInfo]" -ForegroundColor White
Write-Host "   🎤 Audio STT (Vosk):   ws://localhost:8765" -ForegroundColor White
Write-Host "   🎬 Video Analyzer:     ws://localhost:8766  (25 FPS)" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Open in browser:" -ForegroundColor Cyan
Write-Host "   file:///$PSScriptRoot/../web/unified_interface.html" -ForegroundColor White
Write-Host ""
Write-Host "📝 Instructions:" -ForegroundColor Yellow
Write-Host "   1. Select '🎬 Video File' from dropdown" -ForegroundColor White
Write-Host "   2. Click '▶ Start System'" -ForegroundColor White
Write-Host "   3. Speak into microphone for STT" -ForegroundColor White
Write-Host "   4. Watch VLM Response box for video analysis" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  To stop: Close the PowerShell windows" -ForegroundColor Yellow
Write-Host ""
