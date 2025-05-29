from fastapi import WebSocket
from typing import Dict
import asyncio

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"WebSocket connected for client_id: {client_id}, active connections: {list(self.active_connections.keys())}")

    async def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"WebSocket disconnected for client_id: {client_id}, active connections: {list(self.active_connections.keys())}")

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            print(f"Sending message to client_id: {client_id}, message: {message}")
            await self.active_connections[client_id].send_json(message)
        else:
            print(f"No connection for client_id: {client_id}")

    def send_message_sync(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            print(f"Sync sending message to client_id: {client_id}, message: {message}")
            asyncio.run(self.send_message(client_id, message))
        else:
            print(f"No connection for client_id: {client_id} in sync send")

websocket_manager = WebSocketManager()