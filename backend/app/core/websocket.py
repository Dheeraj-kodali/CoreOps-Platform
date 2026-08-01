import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("app.websocket")


class ConnectionManager:
    """Enterprise WebSocket Connection Manager for Real-Time Event Broadcasting."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast real-time event payload to all connected clients."""
        payload = {
            "event": event_type,
            "data": data,
            "timestamp": data.get("timestamp")
        }
        message_str = json.dumps(payload)
        disconnected_clients = []

        for connection in list(self.active_connections):
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.warning(f"Failed to send to client ({e}), marking for disconnect.")
                disconnected_clients.append(connection)

        for connection in disconnected_clients:
            self.disconnect(connection)


websocket_manager = ConnectionManager()
