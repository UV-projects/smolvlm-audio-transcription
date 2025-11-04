"""
REST API Wrapper for n8n Integration
Provides HTTP endpoints to control video streams and get analysis results
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import json
import uuid
from pathlib import Path
from datetime import datetime
import base64

from config_manager import ConfigManager

app = FastAPI(title="AI Director API", version="1.0.0")

# Enable CORS for n8n integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state management
active_streams: Dict[str, dict] = {}
analysis_results: Dict[str, List[dict]] = {}
config_manager = ConfigManager()


# Pydantic models for API
class StreamCreate(BaseModel):
    video_path: str
    enable_audio: bool = True
    stream_name: Optional[str] = None
    loop: bool = True


class StreamControl(BaseModel):
    action: str  # start, stop, pause, resume


class ModelSwitch(BaseModel):
    model_type: str  # stt or vlm
    size: str  # small, medium, large


class AnalysisQuery(BaseModel):
    stream_id: str
    query: str
    max_results: int = 10


# API Endpoints

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "AI Director API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "streams": "/streams",
            "models": "/models",
            "analysis": "/analysis",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    import torch
    
    return {
        "status": "healthy",
        "cuda_available": torch.cuda.is_available(),
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "active_streams": len(active_streams),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/models")
async def list_models():
    """List all available models and current selection"""
    return {
        "stt_models": {
            size: {
                "name": model.name,
                "description": model.description,
                "vram_gb": model.vram_gb
            }
            for size, model in config_manager.list_available_models('stt').items()
        },
        "vlm_models": {
            size: {
                "name": model.name,
                "description": model.description,
                "vram_gb": model.vram_gb
            }
            for size, model in config_manager.list_available_models('vlm').items()
        },
        "active": {
            "stt": config_manager.config['active_models']['stt'],
            "vlm": config_manager.config['active_models']['vlm']
        },
        "total_vram_required": config_manager.get_total_vram_usage()
    }


@app.post("/models/switch")
async def switch_model(model_switch: ModelSwitch):
    """Switch active model"""
    try:
        if model_switch.model_type == 'stt':
            config_manager.set_active_stt_model(model_switch.size)
        elif model_switch.model_type == 'vlm':
            config_manager.set_active_vlm_model(model_switch.size)
        else:
            raise HTTPException(status_code=400, detail="Invalid model_type. Use 'stt' or 'vlm'")
        
        return {
            "success": True,
            "message": f"{model_switch.model_type.upper()} model switched to {model_switch.size}",
            "note": "Restart streams for changes to take effect"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/streams")
async def list_streams():
    """List all active video streams"""
    return {
        "active_streams": [
            {
                "stream_id": stream_id,
                "stream_name": info.get("name"),
                "video_path": info.get("video_path"),
                "status": info.get("status"),
                "start_time": info.get("start_time"),
                "frames_processed": info.get("frames_processed", 0),
                "enable_audio": info.get("enable_audio", False)
            }
            for stream_id, info in active_streams.items()
        ],
        "total_streams": len(active_streams),
        "max_streams": config_manager.get_server_config().max_concurrent_streams
    }


@app.post("/streams/create")
async def create_stream(stream: StreamCreate, background_tasks: BackgroundTasks):
    """Create a new video stream"""
    
    # Check if video file exists
    if not Path(stream.video_path).exists():
        raise HTTPException(status_code=404, detail=f"Video file not found: {stream.video_path}")
    
    # Check max concurrent streams
    max_streams = config_manager.get_server_config().max_concurrent_streams
    if len(active_streams) >= max_streams:
        raise HTTPException(
            status_code=429,
            detail=f"Maximum concurrent streams ({max_streams}) reached"
        )
    
    # Generate unique stream ID
    stream_id = str(uuid.uuid4())
    
    # Create stream info
    stream_info = {
        "stream_id": stream_id,
        "name": stream.stream_name or f"Stream_{len(active_streams) + 1}",
        "video_path": stream.video_path,
        "enable_audio": stream.enable_audio,
        "loop": stream.loop,
        "status": "created",
        "start_time": datetime.now().isoformat(),
        "frames_processed": 0
    }
    
    active_streams[stream_id] = stream_info
    analysis_results[stream_id] = []
    
    # TODO: Start actual video processing in background
    # background_tasks.add_task(process_stream, stream_id)
    
    return {
        "success": True,
        "stream_id": stream_id,
        "message": "Stream created successfully",
        "stream_info": stream_info
    }


@app.post("/streams/{stream_id}/control")
async def control_stream(stream_id: str, control: StreamControl):
    """Control a stream (start, stop, pause, resume)"""
    
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    action = control.action.lower()
    
    if action not in ["start", "stop", "pause", "resume"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Update stream status
    active_streams[stream_id]["status"] = action
    
    # TODO: Implement actual stream control logic
    
    return {
        "success": True,
        "stream_id": stream_id,
        "action": action,
        "message": f"Stream {action} command executed"
    }


@app.delete("/streams/{stream_id}")
async def delete_stream(stream_id: str):
    """Delete a stream"""
    
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    # TODO: Stop processing before deletion
    
    del active_streams[stream_id]
    if stream_id in analysis_results:
        del analysis_results[stream_id]
    
    return {
        "success": True,
        "message": "Stream deleted successfully"
    }


@app.get("/analysis/{stream_id}")
async def get_analysis(stream_id: str, limit: int = 100):
    """Get analysis results for a specific stream"""
    
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    results = analysis_results.get(stream_id, [])
    
    return {
        "stream_id": stream_id,
        "total_results": len(results),
        "results": results[-limit:] if limit else results
    }


@app.post("/analysis/query")
async def query_analysis(query: AnalysisQuery):
    """Query analysis results with filters"""
    
    if query.stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    results = analysis_results.get(query.stream_id, [])
    
    # Simple text search in transcriptions and vision analysis
    filtered = [
        r for r in results
        if query.query.lower() in str(r).lower()
    ]
    
    return {
        "stream_id": query.stream_id,
        "query": query.query,
        "matches": len(filtered),
        "results": filtered[:query.max_results]
    }


@app.get("/stats")
async def get_stats():
    """Get overall statistics"""
    
    total_frames = sum(s.get("frames_processed", 0) for s in active_streams.values())
    total_analysis = sum(len(results) for results in analysis_results.values())
    
    return {
        "active_streams": len(active_streams),
        "total_frames_processed": total_frames,
        "total_analysis_results": total_analysis,
        "models": {
            "stt": config_manager.get_active_stt_model().name,
            "vlm": config_manager.get_active_vlm_model().name
        },
        "vram_usage_gb": config_manager.get_total_vram_usage()
    }


@app.websocket("/ws/{stream_id}")
async def websocket_stream(websocket: WebSocket, stream_id: str):
    """WebSocket endpoint for real-time stream data"""
    await websocket.accept()
    
    try:
        while True:
            # Send stream updates
            if stream_id in active_streams:
                data = {
                    "type": "stream_update",
                    "stream_id": stream_id,
                    "status": active_streams[stream_id]["status"],
                    "frames": active_streams[stream_id].get("frames_processed", 0)
                }
                await websocket.send_json(data)
            
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        print(f"Client disconnected from stream {stream_id}")


# n8n Webhook Examples
@app.post("/webhook/n8n/stream-event")
async def n8n_stream_event(event_data: dict):
    """
    Webhook endpoint for n8n to receive stream events
    Example payload:
    {
        "event": "frame_analyzed",
        "stream_id": "...",
        "data": {...}
    }
    """
    # Process n8n webhook
    return {"received": True, "event": event_data.get("event")}


@app.get("/export/n8n")
async def export_n8n_workflow():
    """Export n8n workflow template"""
    workflow = {
        "name": "AI Director Workflow",
        "nodes": [
            {
                "name": "HTTP Request - Create Stream",
                "type": "n8n-nodes-base.httpRequest",
                "parameters": {
                    "url": "http://localhost:8000/streams/create",
                    "method": "POST"
                }
            },
            {
                "name": "HTTP Request - Get Analysis",
                "type": "n8n-nodes-base.httpRequest",
                "parameters": {
                    "url": "http://localhost:8000/analysis/{{$node[\"HTTP Request - Create Stream\"].json[\"stream_id\"]}}",
                    "method": "GET"
                }
            }
        ]
    }
    
    return workflow


if __name__ == "__main__":
    import uvicorn
    
    server_config = config_manager.get_server_config()
    
    print(f"\nStarting AI Director API Server...")
    print(f"HTTP API: http://{server_config.host}:{server_config.http_port}")
    print(f"WebSocket: ws://{server_config.host}:{server_config.websocket_port}")
    print(f"\nAPI Documentation: http://{server_config.host}:{server_config.http_port}/docs")
    
    uvicorn.run(
        app,
        host=server_config.host,
        port=server_config.http_port,
        log_level="info"
    )
