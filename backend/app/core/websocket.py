import os
import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("app.websocket")

runtime_debug_logs = []

class ConnectionManager:
    """Enterprise WebSocket Connection Manager for Real-Time Event Broadcasting."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        client_ip = websocket.client.host if websocket.client else "unknown"
        log_msg = f"[DEBUG RUNTIME LOG] Browser Connected | Worker PID: {os.getpid()} | Client IP: {client_ip} | active_connections: {len(self.active_connections)}"
        logger.info(log_msg)
        print(log_msg, flush=True)
        runtime_debug_logs.append(log_msg)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            log_msg = f"[DEBUG RUNTIME LOG] Browser Disconnected | Worker PID: {os.getpid()} | active_connections: {len(self.active_connections)}"
            logger.info(log_msg)
            print(log_msg, flush=True)
            runtime_debug_logs.append(log_msg)

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast real-time event payload to all connected clients."""
        pid = os.getpid()
        initial_conn_count = len(self.active_connections)
        clients_sent = 0

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
                clients_sent += 1
            except Exception as e:
                logger.warning(f"Failed to send to client ({e}), marking for disconnect.")
                disconnected_clients.append(connection)

        for connection in disconnected_clients:
            self.disconnect(connection)

        log_msg = f"[DEBUG RUNTIME LOG] Broadcast | Worker PID: {pid} | Event: {event_type} | active_connections: {initial_conn_count} | clients_sent: {clients_sent}"
        logger.info(log_msg)
        print(log_msg, flush=True)
        runtime_debug_logs.append(log_msg)


websocket_manager = ConnectionManager()
