from fastapi import APIRouter, WebSocket, Depends, HTTPException
from app.websocket import websocket_manager
from app.cruds.user import get_user
from sqlalchemy.orm import Session
from app.db.base import get_db
import asyncio
import time
import redis
import json
import websockets

router = APIRouter()

async def get_token(websocket: WebSocket, token: str = None):
    if not token or token != "secret_token":
        await websocket.close(code=1008)
        raise HTTPException(status_code=403, detail="Invalid token")
    return token

async def redis_listener(client_id: str, websocket: WebSocket):
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    pubsub = redis_client.pubsub()
    pubsub.subscribe(f"ws_{client_id}")
    print(f"[DEBUG] Subscribed to Redis channel ws_{client_id}, time: {time.ctime()}")

    try:
        while True:
            message = pubsub.get_message(timeout=1.0)
            if message and message['type'] == 'message':
                data = json.loads(message['data'].decode('utf-8'))
                await websocket_manager.send_message(client_id, data)
                print(f"[DEBUG] Sent Redis message to client_id: {client_id}, message: {data}, time: {time.ctime()}")
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"[DEBUG] Redis listener error for client_id: {client_id}, error: {e}, time: {time.ctime()}")
    finally:
        pubsub.unsubscribe()
        redis_client.close()
        print(f"[DEBUG] Redis listener closed for client_id: {client_id}, time: {time.ctime()}")

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, token: str = Depends(get_token), db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        await websocket.close(code=1008)
        raise HTTPException(status_code=404, detail="User not found")
    
    client_id = str(user_id)
    await websocket_manager.connect(client_id, websocket)
    await websocket_manager.send_message(client_id, {"test": "Connection established"})
    print(f"[DEBUG] WebSocket connection established for client_id: {client_id}, time: {time.ctime()}")

    redis_task = asyncio.create_task(redis_listener(client_id, websocket))

    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
                await websocket_manager.send_message(client_id, {"message": f"Received: {data}"})
            except asyncio.TimeoutError:
                await websocket_manager.send_message(client_id, {"type": "ping", "message": "Keep-alive"})
                print(f"[DEBUG] Sent ping to client_id: {client_id}, time: {time.ctime()}")
            except websockets.exceptions.ConnectionClosed:
                print(f"[DEBUG] WebSocket connection closed for client_id: {client_id}, time: {time.ctime()}")
                break
    except Exception as e:
        print(f"[DEBUG] WebSocket error for client_id: {client_id}, error: {e}, time: {time.ctime()}")
    finally:
        redis_task.cancel()
        await websocket_manager.disconnect(client_id)
        print(f"[DEBUG] WebSocket disconnected for client_id: {client_id}, time: {time.ctime()}")