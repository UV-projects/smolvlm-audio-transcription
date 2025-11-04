# AI Director - Installazione Corretta per Windows con CUDA
# Questo script installa le dipendenze nell'ordine corretto

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AI Director - Setup Dipendenze" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠ Virtual environment non attivato!" -ForegroundColor Yellow
    Write-Host "Attivando virtual environment..." -ForegroundColor Yellow
    
    if (Test-Path ".\.venv\Scripts\Activate.ps1") {
        & .\.venv\Scripts\Activate.ps1
    } else {
        Write-Host "Creando virtual environment..." -ForegroundColor Yellow
        python -m venv .venv
        & .\.venv\Scripts\Activate.ps1
    }
}

Write-Host "✓ Virtual environment attivo" -ForegroundColor Green
Write-Host ""

# Step 1: Check CUDA availability
Write-Host "Passo 1: Verifica CUDA" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

# Try to run nvidia-smi and capture output
$nvidiaSmiOutput = $null
try {
    $nvidiaSmiOutput = & nvidia-smi 2>&1
} catch {
    # nvidia-smi not found
}

if ($nvidiaSmiOutput -and $nvidiaSmiOutput -match "NVIDIA") {
    Write-Host "✓ NVIDIA GPU trovata" -ForegroundColor Green
    
    # Try to extract GPU name
    if ($nvidiaSmiOutput -match "GeForce|Quadro|Tesla|RTX|GTX") {
        $gpuLine = ($nvidiaSmiOutput | Select-String "GeForce|Quadro|Tesla|RTX|GTX" | Select-Object -First 1).ToString().Trim()
        Write-Host "  GPU: $($gpuLine -replace '\s+', ' ')" -ForegroundColor Gray
    }
    
    # Extract CUDA version
    if ($nvidiaSmiOutput -match "CUDA Version:\s*(\d+\.\d+)") {
        $cudaVersion = $Matches[1]
        Write-Host "  CUDA Version: $cudaVersion" -ForegroundColor Green
        
        # Determine correct PyTorch CUDA version
        $majorVersion = [int]($cudaVersion.Split('.')[0])
        if ($majorVersion -ge 12) {
            $torchCuda = "cu121"
            Write-Host "  → Userò PyTorch con CUDA 12.1" -ForegroundColor Cyan
        } elseif ($majorVersion -eq 11) {
            $torchCuda = "cu118"
            Write-Host "  → Userò PyTorch con CUDA 11.8" -ForegroundColor Cyan
        } else {
            $torchCuda = "cu121"
            Write-Host "  → Userò PyTorch con CUDA 12.1 (default)" -ForegroundColor Cyan
        }
    } else {
        $torchCuda = "cu121"
        Write-Host "  → Userò PyTorch con CUDA 12.1 (default)" -ForegroundColor Cyan
    }
} else {
    Write-Host "✗ NVIDIA GPU non trovata o driver non installati" -ForegroundColor Red
    Write-Host "  Continuo con versione CPU..." -ForegroundColor Yellow
    $torchCuda = "cpu"
}

Write-Host ""

# Step 2: Install PyTorch with CUDA
Write-Host "Passo 2: Installazione PyTorch" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

if ($torchCuda -eq "cpu") {
    Write-Host "Installando PyTorch (CPU)..." -ForegroundColor Yellow
    pip install torch torchvision torchaudio
} else {
    Write-Host "Installando PyTorch con $torchCuda..." -ForegroundColor Yellow
    pip install torch torchvision torchaudio --index-url "https://download.pytorch.org/whl/$torchCuda"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Errore installazione PyTorch" -ForegroundColor Red
    exit 1
}

Write-Host "✓ PyTorch installato" -ForegroundColor Green
Write-Host ""

# Step 3: Verify PyTorch CUDA
Write-Host "Passo 3: Verifica PyTorch CUDA" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$torchCheckScript = @"
import torch
print('CUDA available:', torch.cuda.is_available())
print('PyTorch version:', torch.__version__)
if torch.cuda.is_available():
    print('CUDA version:', torch.version.cuda)
    print('GPU:', torch.cuda.get_device_name(0))
    print('VRAM:', round(torch.cuda.get_device_properties(0).total_memory/1024**3, 2), 'GB')
else:
    print('Device: CPU')
"@

$torchCheck = python -c $torchCheckScript 2>&1

Write-Host $torchCheck -ForegroundColor Gray
Write-Host ""

if ($torchCheck -match "CUDA available: True") {
    Write-Host "✓ CUDA funzionante in PyTorch!" -ForegroundColor Green
} else {
    Write-Host "⚠ CUDA non disponibile in PyTorch" -ForegroundColor Yellow
    Write-Host "  Il sistema userà la CPU (più lento)" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Install other dependencies
Write-Host "Passo 4: Installazione altre dipendenze" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

Write-Host "Installando pacchetti rimanenti..." -ForegroundColor Yellow
pip install moshi sentencepiece "numpy<2.0" websockets opencv-python ffmpeg-python fastapi "uvicorn[standard]" pydantic pillow

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Errore installazione dipendenze" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Tutte le dipendenze installate" -ForegroundColor Green
Write-Host ""

# Step 5: Final verification
Write-Host "Passo 5: Verifica finale" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

Write-Host "Eseguo test sistema..." -ForegroundColor Yellow
python test_system.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Setup Completato!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prossimi passi:" -ForegroundColor Yellow
Write-Host "  1. Scarica un video di test: .\download_sample_video.ps1" -ForegroundColor White
Write-Host "  2. Avvia il sistema: .\start.ps1" -ForegroundColor White
Write-Host "  3. Seleziona opzione 2 per elaborare video" -ForegroundColor White
Write-Host ""
