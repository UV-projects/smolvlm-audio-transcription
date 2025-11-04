#!/usr/bin/env python3
"""
GPU Detection Utility
Detects NVIDIA CUDA, Apple Metal (MPS), or falls back to CPU
"""

import subprocess
import sys
import platform

def detect_gpu():
    """
    Detects available GPU and returns optimal configuration
    
    Returns:
        dict: {
            'type': 'cuda' | 'metal' | 'cpu',
            'device': 'cuda:0' | 'mps' | 'cpu',
            'llama_ngl': int (number of layers to offload),
            'info': str (GPU info)
        }
    """
    result = {
        'type': 'cpu',
        'device': 'cpu',
        'llama_ngl': 0,
        'info': 'No GPU detected'
    }
    
    # Check for NVIDIA CUDA
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
            result = {
                'type': 'cuda',
                'device': 'cuda:0',
                'llama_ngl': 99,  # Offload all layers
                'info': f'{gpu_name} ({gpu_memory:.1f} GB VRAM)'
            }
            print(f"✅ NVIDIA GPU detected: {result['info']}", file=sys.stderr)
            return result
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️  CUDA check failed: {e}", file=sys.stderr)
    
    # Check for Apple Metal (MPS)
    if platform.system() == 'Darwin':  # macOS
        try:
            import torch
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                result = {
                    'type': 'metal',
                    'device': 'mps',
                    'llama_ngl': 1,  # Metal uses different offloading
                    'info': 'Apple Silicon (Metal Performance Shaders)'
                }
                print(f"✅ Apple GPU detected: {result['info']}", file=sys.stderr)
                return result
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️  Metal check failed: {e}", file=sys.stderr)
    
    # Fallback to CPU
    print(f"ℹ️  Using CPU (no GPU detected)", file=sys.stderr)
    return result

if __name__ == '__main__':
    import json
    gpu_info = detect_gpu()
    print(json.dumps(gpu_info))
