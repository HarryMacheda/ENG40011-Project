from collections import defaultdict
from typing import Any, Dict, List, Optional
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[Optional[str], List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, key: Optional[str] = None):
        await websocket.accept()
        self.active_connections[key].append(websocket)

    def disconnect(self, websocket: WebSocket, key: Optional[str] = None):
        if websocket in self.active_connections.get(key, []):
            self.active_connections[key].remove(websocket)

    async def broadcast_text(self, message: str, key: Optional[str] = None):
        conns = self.active_connections.get(key, [])
        disconnected = []
        for ws in conns:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws, key)

    async def broadcast_json(self, message: Any, key: Optional[str] = None):
        data = jsonable_encoder(message)
        conns = self.active_connections.get(key, [])
        disconnected = []
        for ws in conns:
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws, key)

    async def broadcast_all_json(self, message: Any):
        data = jsonable_encoder(message)
        for key, conns in list(self.active_connections.items()):
            disconnected = []
            for ws in conns:
                try:
                    await ws.send_json(data)
                except Exception:
                    disconnected.append(ws)
            for ws in disconnected:
                self.disconnect(ws, key)