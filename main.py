import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.redis.client import redis_client
from app.websocket.manager import manager
from app.api.notify import router
# from app.websocket.routes import websocket_endpoint

app = FastAPI()

@app.get("/")
def root():
    return {"status": "server running"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

# async def ws_route(websocket, user_id: str):
#     await websocket_endpoint(websocket, user_id)

async def redis_subscriber():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("notifications")

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = message["data"]
            user_id, text = data.split("|", 1)
            await manager.send_personal_message(user_id, text)

@app.on_event("startup")
async def startup():
    asyncio.create_task(redis_subscriber())

app.include_router(router)
