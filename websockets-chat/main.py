from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
import uvicorn
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ValidationError, field_validator


app = FastAPI()
html_path = Path(__file__).parent
clients = []
users = {}

class IncomingMessage(BaseModel):
    type: Literal["message"]
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value or len(value) > 200:
            raise ValueError("Message is empty or too long")

        return value

@app.get("/")
async def get():
    html = (html_path / "chat.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html, status_code=200)

def make_error(detail: str) -> dict:
    return {
        "type": "error",
        "detail": detail,
    }

def make_message(user: str, text: str) -> dict:
    return {
        "type": "message",
        "user": user,
        "text": text,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

def make_private_message(sender: str, recipient: str, text: str) -> dict:
    return {
        "type": "private",
        "from": sender,
        "to": recipient,
        "text": text,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

async def broadcast(message: dict):
    for client in clients:
        await client["websocket"].send_json(message)

async def send_private(sender: str, command_text: str, websocket: WebSocket):
    command_parts = command_text.split(maxsplit=2)

    if len(command_parts) < 3:
        await websocket.send_json(make_error("Private message format: /w username text"))
        return

    recipient = command_parts[1]
    text = command_parts[2].strip()

    if not text:
        await websocket.send_json(make_error("Message is empty or too long"))
        return

    recipient_websocket = users.get(recipient)

    if recipient_websocket is None:
        await websocket.send_json(make_error(f"User {recipient} is not connected"))
        return

    private_message = make_private_message(sender, recipient, text)
    await recipient_websocket.send_json(private_message)

    if recipient_websocket is not websocket:
        await websocket.send_json(private_message)

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str | None = Query(default=None),
):
    await websocket.accept()

    if username is None or username.strip() == "":
        await websocket.send_json(make_error("Username is required"))
        await websocket.close()
        return

    username = username.strip()

    if username in users:
        await websocket.send_json(make_error("Username is already connected"))
        await websocket.close()
        return

    client_data = {
        "websocket": websocket,
        "username": username,
    }

    clients.append(client_data)
    users[username] = websocket
    await broadcast(make_message("system", f"{username} joined | online: {len(clients)}"))

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except ValueError:
                await websocket.send_json(make_error("Invalid JSON"))
                continue

            try:
                incoming_message = IncomingMessage.model_validate(data)
            except ValidationError:
                await websocket.send_json(make_error("Message is empty or too long"))
                continue

            if incoming_message.text.startswith("/w "):
                await send_private(username, incoming_message.text, websocket)
                continue

            await broadcast(make_message(username, incoming_message.text))
    except WebSocketDisconnect:
        clients.remove(client_data)
        users.pop(username, None)
        await broadcast(make_message("system", f"{username} left | online: {len(clients)}"))


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
