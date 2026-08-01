import os
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket import websocket_manager, runtime_debug_logs

router = APIRouter()


@router.get("/debug-logs")
async def get_debug_logs():
    """Return worker PID and captured runtime debug logs for worker identification."""
    return {
        "worker_pid": os.getpid(),
        "active_connections_count": len(websocket_manager.active_connections),
        "debug_logs": list(runtime_debug_logs)
    }


@router.websocket("/ws")
@router.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-Time WebSocket Subscription Endpoint.
    
    Subscribes connected clients (Admin Web Dashboard, Mobile Apps) to live events:
    - VISITOR_REGISTERED
    - VISITOR_CHECKED_IN
    - VISITOR_CHECKED_OUT
    - VISITOR_UPDATED
    - VISITOR_DELETED
    """
    await websocket_manager.connect(websocket)
    try:
        # Send initial connection acknowledgment
        await websocket.send_json({
            "event": "CONNECTED",
            "message": "Connected to Temple Management Real-Time Event Hub",
            "status": "ONLINE",
            "worker_pid": os.getpid(),
            "active_connections_count": len(websocket_manager.active_connections)
        })

        while True:
            # Maintain active connection and listen for heartbeat ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception:
        websocket_manager.disconnect(websocket)
