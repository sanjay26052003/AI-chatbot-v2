from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    receiver_id: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    content: str
    timestamp: datetime
    is_ai: bool = False

    class Config:
        from_attributes = True


class MessageSend(BaseModel):
    receiver_id: str
    content: str
