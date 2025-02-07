from fastapi import APIRouter, WebSocket
from typing import List

router = APIRouter()
active_connections: List[WebSocket] = []

@router.websocket("/ws/anomalies")
async def websocket_anomalies(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Mantiene la conexión activa
    except:
        active_connections.remove(websocket)
