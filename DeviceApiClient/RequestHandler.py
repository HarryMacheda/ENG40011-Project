import json
from typing import Optional, Dict, Any, Union
import httpx
import websockets
import asyncio


class RequestHandler:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}

    async def request(
        self,
        endpoint: str,
        method: str = "GET",
        body: Optional[Union[Dict[str, Any]]] = None,
        isForm: bool = False,
    ) -> Any:
        url = f"{self.base_url}{endpoint}"
        method = method.upper()

        async with httpx.AsyncClient(verify=False) as client:
            request_headers = self.headers.copy()
            if isForm and body is not None:
                data = body
                request_headers["Content-Type"] = "application/x-www-form-urlencoded"
            elif body is not None:
                data = json.dumps(body.dict())
                request_headers["Content-Type"] = "application/json"
            else:
                data = None

            response = await client.request(
                method=method,
                url=url,
                headers=request_headers,
                data=data
            )

            response.raise_for_status()
            return response.json() if response.content else None

    async def connect_websocket(self, path: str) -> websockets.WebSocketClientProtocol:
        ws_url = self.base_url.replace("http", "ws") + path
        try:
            websocket = await websockets.connect(ws_url)
            return websocket
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
            raise
