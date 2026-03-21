from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from bson import ObjectId
from datetime import datetime
from typing import Dict, Set
import socketio

from config import get_settings
from database import connect_to_mongo, close_mongo_connection, get_database
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from services.ai_service import get_ai_response

settings = get_settings()

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

# Create FastAPI app
fastapi_app = FastAPI(title="Real-Time AI Chat API", version="1.0.0")

# Wrap with Socket.IO ASGI app
app = socketio.ASGIApp(sio, fastapi_app)

# CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
fastapi_app.include_router(auth_router)
fastapi_app.include_router(chat_router)


@sio.event
async def connect(sid, *args, **kwargs):
    print(f"Connect called with sid={sid}")
    # Get token from auth or query string
    token = None

    # Parse arguments - auth is passed as second positional arg
    if len(args) >= 2:
        auth_data = args[1]
        if isinstance(auth_data, dict) and 'token' in auth_data:
            token = auth_data.get('token')
    elif 'auth' in kwargs:
        token = kwargs.get('auth', {}).get('token')

    if not token:
        print(f"Connection rejected: No token provided for sid={sid}")
        raise ConnectionRefusedError("No token provided")

    user_id = await get_user_from_token(token)
    if not user_id:
        print(f"Connection rejected: Invalid token for sid={sid}")
        raise ConnectionRefusedError("Invalid token")

    # Save session
    await sio.save_session(sid, {'user_id': user_id})
    await sio.enter_room(sid, user_id)

    # Verify session was saved
    session = await sio.get_session(sid)
    print(f"Session saved for {user_id}: {session}")

    print(f"User {user_id} connected with sid={sid}")

    # Broadcast online status
    await sio.emit('status', {
        'user_id': user_id,
        'status': 'online'
    }, room=user_id, skip_sid=sid)

    print(f"User {user_id} connected")


@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    user_id = session.get('user_id')
    if user_id:
        await sio.leave_room(sid, user_id)
        # Broadcast offline status
        await sio.emit('status', {
            'user_id': user_id,
            'status': 'offline'
        })
        print(f"User {user_id} disconnected")


@sio.event
async def send_message(sid, data):
    session = await sio.get_session(sid)
    sender_id = session.get('user_id')
    print(f"send_message received: sid={sid}, sender_id={sender_id}, data={data}")
    if not sender_id:
        print("No sender_id in session!")
        return

    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()

    if not receiver_id or not content:
        print("Missing receiver_id or content")
        return

    db = get_database()

    # Check if AI message
    is_ai_message = receiver_id == 'AI' or content.startswith('/ai ')
    ai_response_content = None

    if is_ai_message:
        # Process AI message
        cursor = db.messages.find({
            '$or': [
                {'sender_id': sender_id, 'receiver_id': 'AI'},
                {'sender_id': 'AI', 'receiver_id': sender_id}
            ]
        }).sort('timestamp', -1).limit(10)
        cursor_list = await cursor.to_list(10)

        history = []
        for msg in reversed(cursor_list):
            history.append({
                'role': 'assistant' if msg['sender_id'] == 'AI' else 'user',
                'content': msg['content']
            })

        # Add current message
        user_content = content.replace('/ai ', '') if content.startswith('/ai ') else content
        history.append({'role': 'user', 'content': user_content})

        # Get AI response
        ai_response_content = await get_ai_response(history)
        receiver_id = 'AI'

    # Store message in database
    msg_dict = {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': datetime.utcnow(),
        'is_ai': is_ai_message
    }
    result = await db.messages.insert_one(msg_dict)

    # Create message response
    message_response = {
        'type': 'message',
        'id': str(result.inserted_id),
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': msg_dict['timestamp'].isoformat(),
        'is_ai': is_ai_message
    }

    # Send to sender
    await sio.emit('message', message_response, room=sender_id)

    # Send to receiver if they're in their room (online)
    await sio.emit('message', message_response, room=receiver_id)

    # If AI message, also send AI response
    if is_ai_message and ai_response_content:
        # Store AI response
        ai_msg_dict = {
            'sender_id': 'AI',
            'receiver_id': sender_id,
            'content': ai_response_content,
            'timestamp': datetime.utcnow(),
            'is_ai': True
        }
        ai_result = await db.messages.insert_one(ai_msg_dict)

        ai_response = {
            'type': 'message',
            'id': str(ai_result.inserted_id),
            'sender_id': 'AI',
            'receiver_id': sender_id,
            'content': ai_response_content,
            'timestamp': ai_msg_dict['timestamp'].isoformat(),
            'is_ai': True
        }

        # Send AI response to user
        await sio.emit('message', ai_response, room=sender_id)


@sio.event
async def typing(sid, data):
    session = await sio.get_session(sid)
    user_id = session.get('user_id')
    if not user_id:
        return

    receiver_id = data.get('receiver_id')
    is_typing = data.get('is_typing', False)

    await sio.emit('typing', {
        'user_id': user_id,
        'is_typing': is_typing
    }, room=receiver_id)


@sio.event
async def private_message(sid, data):
    """Handle private messages between users"""
    session = await sio.get_session(sid)
    sender_id = session.get('user_id')
    if not sender_id:
        return

    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()

    if not receiver_id or not content:
        return

    db = get_database()

    # Store message in database
    msg_dict = {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': datetime.utcnow(),
        'is_ai': False
    }
    result = await db.messages.insert_one(msg_dict)

    message_response = {
        'type': 'message',
        'id': str(result.inserted_id),
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': msg_dict['timestamp'].isoformat(),
        'is_ai': False
    }

    # Send to sender
    await sio.emit('message', message_response, room=sender_id)

    # Send to receiver
    await sio.emit('message', message_response, room=receiver_id)


async def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


@fastapi_app.on_event("startup")
async def startup():
    await connect_to_mongo()


@fastapi_app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()


@fastapi_app.get("/")
async def root():
    return {"message": "Real-Time AI Chat API", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
