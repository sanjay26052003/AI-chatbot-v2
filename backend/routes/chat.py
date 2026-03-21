from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from models.message import MessageResponse, MessageSend
from routes.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/messages/{other_user_id}", response_model=List[MessageResponse])
async def get_messages(other_user_id: str, limit: int = 50, current_user: dict = Depends(get_current_user)):
    """Get chat messages between current user and another user"""
    from database import get_database
    db = get_database()

    # Query messages between the two users
    cursor = db.messages.find({
        "$or": [
            {"sender_id": str(current_user["_id"]), "receiver_id": other_user_id},
            {"sender_id": other_user_id, "receiver_id": str(current_user["_id"])}
        ]
    }).sort("timestamp", -1).limit(limit)

    messages = []
    all_messages = await cursor.to_list(limit)

    for msg in all_messages:
        messages.append(MessageResponse(
            id=str(msg["_id"]),
            sender_id=msg["sender_id"],
            receiver_id=msg["receiver_id"],
            content=msg["content"],
            timestamp=msg["timestamp"],
            is_ai=msg.get("is_ai", False)
        ))

    # Reverse to get chronological order
    messages.reverse()
    return messages


@router.post("/messages", response_model=MessageResponse)
async def send_message(message: MessageSend, current_user: dict = Depends(get_current_user)):
    """Send a message to another user"""
    from database import get_database
    db = get_database()

    # For AI messages, skip receiver validation
    if message.receiver_id != "AI":
        # Verify receiver exists
        receiver = await db.users.find_one({"_id": message.receiver_id})
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver not found")

    # Create message
    msg_dict = {
        "sender_id": str(current_user["_id"]),
        "receiver_id": message.receiver_id,
        "content": message.content,
        "timestamp": datetime.utcnow(),
        "is_ai": False
    }

    result = await db.messages.insert_one(msg_dict)

    return MessageResponse(
        id=str(result.inserted_id),
        sender_id=msg_dict["sender_id"],
        receiver_id=msg_dict["receiver_id"],
        content=msg_dict["content"],
        timestamp=msg_dict["timestamp"],
        is_ai=msg_dict["is_ai"]
    )
