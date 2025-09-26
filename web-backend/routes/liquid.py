from authentication.tokens import Token, TokenManager
from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect, Depends, status
from utility.websockets import WebSocketManager
from utility.types import ColourAlert

import jwt 

router = APIRouter(
    prefix="/liquid",
    tags=["liquid", "blood", "alert"]
)

connectionManager = WebSocketManager()

@router.post("/detected")
async def post_detected_liquid(token:dict = Depends(TokenManager.requireScope("write"))):
    await connectionManager.broadcast("true")
    return Response(status_code=200)

@router.websocket("/detected/subscribe")
async def subscribe_messages(websocket: WebSocket):
    auth_header = websocket.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    token = auth_header.split(" ")[1]
    token = TokenManager.checkScope(TokenManager().decodeAccessToken(token), "read")

    await connectionManager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connectionManager.disconnect(websocket)


@router.post("/colour")
async def post_detected_liquid(alert:ColourAlert ,token:dict = Depends(TokenManager.requireScope("write"))):
    await connectionManager.broadcast(alert)
    return Response(status_code=200)

@router.websocket("/colour/subscribe")
async def subscribe_messages(websocket: WebSocket):
    auth_header = websocket.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    token = auth_header.split(" ")[1]
    token = TokenManager.checkScope(TokenManager().decodeAccessToken(token), "read")

    await connectionManager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connectionManager.disconnect(websocket)