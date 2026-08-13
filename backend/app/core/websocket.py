import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from app.core.config import settings

logger = logging.getLogger("app.websocket")

REDIS_CHANNEL = "temple_realtime_events"


class ConnectionManager:
    """Production-Grade Multi-Worker Redis Pub/Sub WebSocket Connection Manager."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.redis_client: Optional[Any] = None
        self.pubsub_task: Optional[asyncio.Task] = None
        self._is_listening: bool = False

    async def start_redis_pubsub(self):
        """Initialize Redis connection and start Pub/Sub listener background task for this Gunicorn worker process."""
        if self._is_listening:
            return

        redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        try:
            import redis.asyncio as aioredis
            self.redis_client = aioredis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=2.0,
                socket_timeout=2.0,
            )
            await asyncio.wait_for(self.redis_client.ping(), timeout=2.0)
            self._is_listening = True
            self.pubsub_task = asyncio.create_task(self._listen_redis_channel())
            logger.info(f"[Redis PubSub] Worker PID: {os.getpid()} successfully connected to Redis at '{redis_url}' and subscribed to channel '{REDIS_CHANNEL}'")
        except Exception as e:
            logger.warning(f"[Redis PubSub Warning] Worker PID: {os.getpid()} operating in local fallback mode ({e}).")
            self.redis_client = None

    async def stop_redis_pubsub(self):
        """Stop Pub/Sub listener task on worker process shutdown."""
        self._is_listening = False
        if self.pubsub_task:
            self.pubsub_task.cancel()
            self.pubsub_task = None
        if self.redis_client:
            try:
                await self.redis_client.close()
            except Exception:
                pass
            self.redis_client = None

    async def _listen_redis_channel(self):
        """Continuously listen for incoming published messages on the Redis Pub/Sub channel."""
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(REDIS_CHANNEL)
            pid = os.getpid()
            logger.info(f"[Redis Subscribe] Worker PID: {pid} listening for events on Redis channel '{REDIS_CHANNEL}'...")

            async for message in pubsub.listen():
                if not self._is_listening:
                    break
                if message and message.get("type") == "message":
                    raw_data = message.get("data")
                    if raw_data:
                        try:
                            payload = json.loads(raw_data)
                            event_type = payload.get("event", "UNKNOWN")
                            logger.info(
                                f"[Redis Subscribe] Worker PID: {pid} received event '{event_type}' from Redis. "
                                f"Broadcasting to {len(self.active_connections)} local WebSocket connections."
                            )
                            await self._local_broadcast(payload)
                        except Exception as ex:
                            logger.error(f"[Redis Listener Error] Failed to parse message payload: {ex}")
        except asyncio.CancelledError:
            logger.info("[Redis PubSub] Listener task cancelled.")
            raise
        except Exception as e:
            logger.error(f"[Redis PubSub Exception] Worker PID: {os.getpid()} listener error: {e}")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"[WebSocket] Client Connected | Worker PID: {os.getpid()} | active_connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"[WebSocket] Client Disconnected | Worker PID: {os.getpid()} | active_connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Publish real-time event payload to Redis channel so all Gunicorn worker processes receive and broadcast to local clients."""
        payload = {
            "event": event_type,
            "data": data,
            "timestamp": data.get("timestamp")
        }
        message_str = json.dumps(payload)
        pid = os.getpid()

        published_to_redis = False
        if self.redis_client and self._is_listening:
            try:
                await self.redis_client.publish(REDIS_CHANNEL, message_str)
                published_to_redis = True
                logger.info(f"[Redis Publish] Worker PID: {pid} published event '{event_type}' to Redis channel '{REDIS_CHANNEL}'.")
            except Exception as e:
                logger.error(f"[Redis Publish Error] Worker PID: {pid} failed to publish to Redis ({e}).")

        # Fallback to local broadcast if Redis publishing is not active
        if not published_to_redis:
            await self._local_broadcast(payload)

    async def _local_broadcast(self, payload: Dict[str, Any]):
        """Send event payload to WebSocket clients connected locally to THIS worker process."""
        message_str = json.dumps(payload)
        disconnected_clients = []
        clients_sent = 0

        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message_str)
                clients_sent += 1
            except Exception as e:
                logger.warning(f"Failed to send to client ({e}), marking for disconnect.")
                disconnected_clients.append(connection)

        for connection in disconnected_clients:
            self.disconnect(connection)

        logger.info(
            f"[WebSocket Local Broadcast] Worker PID: {os.getpid()} | Event: {payload.get('event')} | "
            f"active_connections: {len(self.active_connections)} | clients_sent: {clients_sent}"
        )


websocket_manager = ConnectionManager()
