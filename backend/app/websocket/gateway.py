"""WebSocket gateway for real-time events."""
import json
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_token

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and channel subscriptions."""

    def __init__(self):
        # channel -> set of WebSocket connections
        self._channels: Dict[str, Set[WebSocket]] = {}
        # websocket -> set of subscribed channels
        self._subscriptions: Dict[WebSocket, Set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self._subscriptions[websocket] = set()

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            channels = self._subscriptions.pop(websocket, set())
            for ch in channels:
                self._channels.get(ch, set()).discard(websocket)
                if not self._channels[ch]:
                    self._channels.pop(ch, None)

    async def subscribe(self, websocket: WebSocket, channel: str):
        async with self._lock:
            self._channels.setdefault(channel, set()).add(websocket)
            self._subscriptions.setdefault(websocket, set()).add(channel)

    async def unsubscribe(self, websocket: WebSocket, channel: str):
        async with self._lock:
            self._channels.get(channel, set()).discard(websocket)
            self._subscriptions.get(websocket, set()).discard(channel)

    async def broadcast(self, channel: str, event: str, data: dict):
        """Broadcast an event to all subscribers of a channel."""
        message = json.dumps({"event": event, "channel": channel, "data": data})

        async with self._lock:
            targets = list(self._channels.get(channel, set()))

        for ws in targets:
            try:
                await ws.send_text(message)
            except Exception:
                # Connection broken — clean up
                await self.disconnect(ws)

    async def broadcast_all(self, event: str, data: dict):
        """Broadcast to all connected clients."""
        message = json.dumps({"event": event, "data": data})

        async with self._lock:
            targets = []
            for subs in self._subscriptions.values():
                targets.extend(subs)

        # Send to all unique sockets
        sent_to = set()
        for ch in self._channels:
            for ws in self._channels[ch]:
                if ws in sent_to:
                    continue
                sent_to.add(ws)
                try:
                    await ws.send_text(message)
                except Exception:
                    await self.disconnect(ws)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None),
):
    """WebSocket endpoint with token auth, subscribe/unsubscribe, and broadcasting."""
    # Authenticate via token
    if token:
        payload = decode_token(token)
        if not payload:
            await websocket.close(code=4001)
            return

    await manager.connect(websocket)

    try:
        # Send welcome
        await websocket.send_text(json.dumps({
            "event": "connected",
            "data": {"message": "Connected to SmartResort real-time gateway"},
        }))

        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
                action = msg.get("action")
                channel = msg.get("channel")

                if action == "subscribe" and channel:
                    await manager.subscribe(websocket, channel)
                    await websocket.send_text(json.dumps({
                        "event": "subscribed",
                        "data": {"channel": channel},
                    }))
                elif action == "unsubscribe" and channel:
                    await manager.unsubscribe(websocket, channel)
                elif action == "ping":
                    await websocket.send_text(json.dumps({"event": "pong", "data": {}}))
                else:
                    await websocket.send_text(json.dumps({
                        "event": "error",
                        "data": {"message": "Unknown action"},
                    }))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "event": "error",
                    "data": {"message": "Invalid JSON"},
                }))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


def get_connection_manager() -> ConnectionManager:
    """Return the singleton connection manager."""
    return manager
