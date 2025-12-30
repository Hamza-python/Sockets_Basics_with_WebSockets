from fastapi import APIRouter
from app.redis.client import redis_client

router = APIRouter()

@router.get("/notify/{user_id}")
async def notify_user(user_id: str, message: str):
    payload = f"{user_id}|{message}"
    await redis_client.publish("notifications", payload)
    return {"status": "sent"}
