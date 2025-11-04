# 🚀 GPU Acceleration Setup

## NVIDIA CUDA (Windows/Linux)

### Prerequisites
- NVIDIA GPU with CUDA support
- CUDA Toolkit 12.x (or compatible)
- cuDNN libraries

### Setup
1. llama-server automatically uses CUDA if available with `-ngl 99` flag
2. Verify CUDA is working:
   ```bash
   nvidia-smi
   ```

### Performance
- **With GPU**: ~10-15 FPS inference
- **Without GPU (CPU)**: ~1-2 FPS inference

---

## Apple Silicon (macOS)

### Prerequisites
- Mac with M1/M2/M3 chip
- macOS Sonoma or later

### Setup
llama-server automatically uses Metal Performance Shaders (MPS) on Apple Silicon

### Performance
- **M1/M2 Pro**: ~8-12 FPS
- **M3**: ~15-20 FPS

---

## Current Configuration

This system uses `llama.cpp` with automatic GPU detection:

- **-ngl 99**: Offloads all layers to GPU if available
- Falls back to CPU if no GPU detected

To force CPU mode:
```powershell
.\scripts\start_gpu.ps1 -ForceCPU
```

---

## Troubleshooting

### CUDA not detected
1. Verify CUDA installation: `nvidia-smi`
2. Check llama-server was compiled with CUDA support
3. Re-download CUDA-enabled llama.cpp binaries

### Slow performance
- GPU offloading should give 5-10x speedup
- If still slow, check `nvidia-smi` to verify GPU usage
- Monitor VRAM usage (Qwen3-VL needs ~2GB)
