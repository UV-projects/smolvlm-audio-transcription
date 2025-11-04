"""
Configuration Manager for AI Director
Handles model selection, server configuration, and runtime settings
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    repo: str
    name: str
    description: str
    vram_gb: float


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str
    websocket_port: int
    http_port: int
    max_concurrent_streams: int


@dataclass
class VideoConfig:
    """Video processing configuration"""
    default_fps: int
    frame_queue_size: int
    enable_audio: bool
    loop_video: bool


@dataclass
class DeviceConfig:
    """Device preferences"""
    prefer_cuda: bool
    fallback_to_cpu: bool


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get_active_stt_model(self) -> ModelConfig:
        """Get active STT model configuration"""
        active = self.config['active_models']['stt']
        model_data = self.config['models']['stt'][active]
        return ModelConfig(**model_data)
    
    def get_active_vlm_model(self) -> ModelConfig:
        """Get active VLM model configuration"""
        active = self.config['active_models']['vlm']
        model_data = self.config['models']['vlm'][active]
        return ModelConfig(**model_data)
    
    def set_active_stt_model(self, size: str):
        """Set active STT model by size (small, medium, large)"""
        if size not in self.config['models']['stt']:
            raise ValueError(f"Unknown STT model size: {size}")
        self.config['active_models']['stt'] = size
        self.save_config()
    
    def set_active_vlm_model(self, size: str):
        """Set active VLM model by size (small, medium, large)"""
        if size not in self.config['models']['vlm']:
            raise ValueError(f"Unknown VLM model size: {size}")
        self.config['active_models']['vlm'] = size
        self.save_config()
    
    def get_server_config(self) -> ServerConfig:
        """Get server configuration"""
        return ServerConfig(**self.config['server'])
    
    def get_video_config(self) -> VideoConfig:
        """Get video configuration"""
        return VideoConfig(**self.config['video'])
    
    def get_device_config(self) -> DeviceConfig:
        """Get device configuration"""
        return DeviceConfig(**self.config['device'])
    
    def list_available_models(self, model_type: str = 'stt') -> Dict[str, ModelConfig]:
        """List all available models of a specific type"""
        models = {}
        for size, model_data in self.config['models'][model_type].items():
            models[size] = ModelConfig(**model_data)
        return models
    
    def get_total_vram_usage(self) -> float:
        """Calculate total VRAM usage for active models"""
        stt_model = self.get_active_stt_model()
        vlm_model = self.get_active_vlm_model()
        return stt_model.vram_gb + vlm_model.vram_gb
    
    def can_run_on_gpu(self, available_vram_gb: float) -> bool:
        """Check if active models can run on GPU with available VRAM"""
        return self.get_total_vram_usage() <= available_vram_gb
    
    def suggest_models_for_vram(self, available_vram_gb: float) -> Dict[str, str]:
        """Suggest best model sizes for available VRAM"""
        suggestions = {'stt': 'small', 'vlm': 'small'}
        
        # Try to fit the largest models possible
        for stt_size in ['medium', 'small']:
            for vlm_size in ['medium', 'small']:
                stt_vram = self.config['models']['stt'][stt_size]['vram_gb']
                vlm_vram = self.config['models']['vlm'][vlm_size]['vram_gb']
                
                if stt_vram + vlm_vram <= available_vram_gb:
                    return {'stt': stt_size, 'vlm': vlm_size}
        
        return suggestions


def main():
    """CLI for configuration management"""
    import sys
    
    config = ConfigManager()
    
    if len(sys.argv) < 2:
        print("AI Director Configuration Manager")
        print("\nUsage:")
        print("  python config_manager.py list [stt|vlm]       - List available models")
        print("  python config_manager.py active                - Show active models")
        print("  python config_manager.py set-stt <size>        - Set STT model")
        print("  python config_manager.py set-vlm <size>        - Set VLM model")
        print("  python config_manager.py vram                  - Show VRAM usage")
        print("  python config_manager.py suggest <vram_gb>     - Suggest models for VRAM")
        return
    
    command = sys.argv[1]
    
    if command == 'list':
        model_type = sys.argv[2] if len(sys.argv) > 2 else 'stt'
        models = config.list_available_models(model_type)
        print(f"\nAvailable {model_type.upper()} models:")
        for size, model in models.items():
            print(f"\n  {size}:")
            print(f"    Name: {model.name}")
            print(f"    Repo: {model.repo}")
            print(f"    Description: {model.description}")
            print(f"    VRAM: {model.vram_gb} GB")
    
    elif command == 'active':
        stt = config.get_active_stt_model()
        vlm = config.get_active_vlm_model()
        print("\nActive Models:")
        print(f"\n  STT: {stt.name}")
        print(f"    Repo: {stt.repo}")
        print(f"    VRAM: {stt.vram_gb} GB")
        print(f"\n  VLM: {vlm.name}")
        print(f"    Repo: {vlm.repo}")
        print(f"    VRAM: {vlm.vram_gb} GB")
        print(f"\n  Total VRAM: {config.get_total_vram_usage()} GB")
    
    elif command == 'set-stt':
        size = sys.argv[2]
        config.set_active_stt_model(size)
        print(f"STT model set to: {size}")
    
    elif command == 'set-vlm':
        size = sys.argv[2]
        config.set_active_vlm_model(size)
        print(f"VLM model set to: {size}")
    
    elif command == 'vram':
        total = config.get_total_vram_usage()
        print(f"\nTotal VRAM required for active models: {total} GB")
        
        # Try to get available VRAM
        try:
            import torch
            if torch.cuda.is_available():
                available = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                print(f"Available GPU VRAM: {available:.2f} GB")
                print(f"Can run on GPU: {config.can_run_on_gpu(available)}")
        except ImportError:
            print("Install PyTorch to check available VRAM")
    
    elif command == 'suggest':
        vram_gb = float(sys.argv[2])
        suggestions = config.suggest_models_for_vram(vram_gb)
        print(f"\nRecommended models for {vram_gb} GB VRAM:")
        print(f"  STT: {suggestions['stt']}")
        print(f"  VLM: {suggestions['vlm']}")


if __name__ == "__main__":
    main()
