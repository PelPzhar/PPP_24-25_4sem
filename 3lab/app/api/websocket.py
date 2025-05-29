from fastapi import APIRouter, WebSocket, Depends, HTTPException
from app.websocket import websocket_manager
from app.cruds.user import get_user
from sqlalchemy.orm import Session
from app.db.base import get_db

router = APIRouter()

async def get_token(websocket: WebSocket, token: str = None):
    if not token or token != "secret_token":
        await websocket.close(code=1008)
        raise HTTPException(status_code=403, detail="Invalid token")
    return token

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, token: str = Depends(get_token), db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        await websocket.close(code=1008)
        raise HTTPException(status_code=404, detail="User not found")
    
    client_id = str(user_id)
    await websocket_manager.connect(client_id, websocket)
    await websocket_manager.send_message(client_id, {"test": "Connection established"})
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.send_message(client_id, {"message": f"Received: {data}"})
    except Exception as e:
        print(f"WebSocket error for client_id {client_id}: {e}")
        await websocket_manager.disconnect(client_id)