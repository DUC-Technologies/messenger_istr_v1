from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, chat_id: str, websocket: WebSocket):
        await websocket.accept()
        if self.active_connections.get(chat_id, None):
            self.active_connections[chat_id].append(websocket)
        else:
            self.active_connections[chat_id] = [websocket, ]

    def disconnect(self, chat_id: str, websocket: WebSocket):
        self.active_connections[chat_id].remove(websocket)

    async def push_to_chat(self, chat_id: str, message: str):
        for connection in self.active_connections[chat_id]:
            await connection.send_text(message)
