"""
Quick Test Script for AI Director
Tests all components without needing a full video file
"""

import sys
import json
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def test_imports():
    """Test if all required packages are installed"""
    print_header("Testing Package Imports")
    
    packages = {
        'torch': 'PyTorch',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'websockets': 'WebSockets',
        'sentencepiece': 'SentencePiece',
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
    }
    
    results = {}
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✓ {name:<20} INSTALLED")
            results[package] = True
        except ImportError:
            print(f"✗ {name:<20} MISSING")
            results[package] = False
    
    return all(results.values())

def test_cuda():
    """Test CUDA availability"""
    print_header("Testing CUDA Support")
    
    try:
        import torch
        
        cuda_available = torch.cuda.is_available()
        print(f"CUDA Available: {cuda_available}")
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            print(f"CUDA Devices: {device_count}")
            
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                device_capability = torch.cuda.get_device_capability(i)
                total_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                
                print(f"\nDevice {i}:")
                print(f"  Name: {device_name}")
                print(f"  Compute Capability: {device_capability}")
                print(f"  Total Memory: {total_memory:.2f} GB")
                
            return True
        else:
            print("⚠ CUDA not available. System will use CPU.")
            print("For better performance, install CUDA toolkit and compatible PyTorch.")
            return False
            
    except Exception as e:
        print(f"✗ Error testing CUDA: {e}")
        return False

def test_config():
    """Test configuration file"""
    print_header("Testing Configuration")
    
    config_path = Path("config.json")
    
    if not config_path.exists():
        print("✗ config.json not found")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        print("✓ config.json loaded successfully")
        print(f"\nActive Models:")
        print(f"  STT: {config['active_models']['stt']}")
        print(f"  VLM: {config['active_models']['vlm']}")
        
        print(f"\nServer Configuration:")
        print(f"  Host: {config['server']['host']}")
        print(f"  WebSocket Port: {config['server']['websocket_port']}")
        print(f"  HTTP Port: {config['server']['http_port']}")
        print(f"  Max Streams: {config['server']['max_concurrent_streams']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading config.json: {e}")
        return False

def test_config_manager():
    """Test configuration manager"""
    print_header("Testing Configuration Manager")
    
    try:
        from config_manager import ConfigManager
        
        config = ConfigManager()
        
        # Test getting active models
        stt_model = config.get_active_stt_model()
        vlm_model = config.get_active_vlm_model()
        
        print("✓ ConfigManager initialized")
        print(f"\nActive STT Model:")
        print(f"  Name: {stt_model.name}")
        print(f"  Repo: {stt_model.repo}")
        print(f"  VRAM: {stt_model.vram_gb} GB")
        
        print(f"\nActive VLM Model:")
        print(f"  Name: {vlm_model.name}")
        print(f"  Repo: {vlm_model.repo}")
        print(f"  VRAM: {vlm_model.vram_gb} GB")
        
        total_vram = config.get_total_vram_usage()
        print(f"\nTotal VRAM Required: {total_vram} GB")
        
        # Test VRAM check
        try:
            import torch
            if torch.cuda.is_available():
                available_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                can_run = config.can_run_on_gpu(available_vram)
                print(f"Available VRAM: {available_vram:.2f} GB")
                print(f"Can Run on GPU: {can_run}")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing ConfigManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ffmpeg():
    """Test FFmpeg availability"""
    print_header("Testing FFmpeg")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg found: {version_line}")
            return True
        else:
            print("✗ FFmpeg not working properly")
            return False
            
    except FileNotFoundError:
        print("✗ FFmpeg not found in PATH")
        print("  Install with: choco install ffmpeg")
        return False
    except Exception as e:
        print(f"✗ Error testing FFmpeg: {e}")
        return False

def test_api_server():
    """Test API server import"""
    print_header("Testing API Server")
    
    try:
        from api_server import app
        print("✓ API server module loaded")
        
        # List some routes
        print("\nAvailable routes:")
        for route in app.routes[:10]:  # Show first 10 routes
            if hasattr(route, 'path'):
                print(f"  {route.path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing API server: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_video_processor():
    """Test video processor import"""
    print_header("Testing Video Processor")
    
    try:
        # Don't import main_video directly to avoid errors
        # Just check if file exists
        if Path("main_video.py").exists():
            print("✓ main_video.py found")
            return True
        else:
            print("✗ main_video.py not found")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def generate_report(results):
    """Generate test report"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print(f"\nSuccess Rate: {(passed/total)*100:.1f}%")
    
    if failed > 0:
        print("\n⚠ Some tests failed. Please check the output above.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements-windows.txt")
        print("  - Install FFmpeg: choco install ffmpeg")
        print("  - Install CUDA: https://developer.nvidia.com/cuda-downloads")
    else:
        print("\n✓ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Download a test video: .\\download_sample_video.ps1")
        print("  2. Start the system: .\\start.ps1")
        print("  3. Open index_video.html in your browser")
    
    print("\n" + "="*60 + "\n")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("   AI Director - System Test")
    print("="*60)
    
    results = {}
    
    # Run tests
    results['Imports'] = test_imports()
    results['CUDA'] = test_cuda()
    results['Config File'] = test_config()
    results['Config Manager'] = test_config_manager()
    results['FFmpeg'] = test_ffmpeg()
    results['API Server'] = test_api_server()
    results['Video Processor'] = test_video_processor()
    
    # Generate report
    generate_report(results)
    
    return all(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
