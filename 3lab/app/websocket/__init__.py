from fastapi import WebSocket
from typing import Dict
import asyncio
import time

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"[DEBUG] WebSocket connected for client_id: {client_id}, active connections: {list(self.active_connections.keys())}, time: {time.ctime()}")

    async def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].close()
            except Exception as e:
                print(f"[DEBUG] Error closing WebSocket for client_id: {client_id}, error: {e}, time: {time.ctime()}")
            del self.active_connections[client_id]
            print(f"[DEBUG] WebSocket disconnected for client_id: {client_id}, active connections: {list(self.active_connections.keys())}, time: {time.ctime()}")

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            print(f"[DEBUG] Sending message to client_id: {client_id}, message: {message}, time: {time.ctime()}")
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                print(f"[DEBUG] Error sending message to client_id: {client_id}, error: {e}, time: {time.ctime()}")
                await self.disconnect(client_id)
        else:
            print(f"[DEBUG] No connection for client_id: {client_id}, time: {time.ctime()}")

    async def send_message_sync(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            print(f"[DEBUG] Async sending message to client_id: {client_id}, message: {message}, time: {time.ctime()}")
            try:
                await self.send_message(client_id, message)
            except Exception as e:
                print(f"[DEBUG] Error in async send for client_id: {client_id}, error: {e}, time: {time.ctime()}")
                await self.disconnect(client_id)
        else:
            print(f"[DEBUG] No connection for client_id: {client_id} in async send, time: {time.ctime()}")

websocket_manager = WebSocketManager()