from ..authentication.tokens import Token, TokenManager
from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect, Depends, status
from ..utility.websockets import WebSocketManager
from StandardLibrary.PythonTypes import ColourAlert

import jwt 

router = APIRouter(
    prefix="/liquid",
    tags=["liquid", "blood", "alert"]
)

detectionManager = WebSocketManager()

@router.post("/{room}/detected")
async def post_detected_liquid(room:str, token:dict = Depends(TokenManager.requireScope("write"))):
    await detectionManager.broadcast_json({"room": room})
    return Response(status_code=200)

@router.websocket("/detected/subscribe")
async def subscribe_messages(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    token = TokenManager.checkScope(TokenManager().decodeAccessToken(token), "read")

    await detectionManager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        detectionManager.disconnect(websocket)


colourManager = WebSocketManager()

@router.post("/{room}/colour")
async def post_detected_liquid(room:str, alert:ColourAlert , token:dict = Depends(TokenManager.requireScope("write"))):
    await colourManager.broadcast_json(alert, key=room)
    return Response(status_code=200)

@router.websocket("/colour/subscribe")
async def subscribe_messages(websocket: WebSocket, room: str = None):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    token = TokenManager.checkScope(TokenManager().decodeAccessToken(token), "read")

    await colourManager.connect(websocket, key=room)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        colourManager.disconnect(websocket)