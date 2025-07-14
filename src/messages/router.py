import asyncio
from fastapi import APIRouter
from pydantic import BaseModel
from src.messages.messages import create_message, list_messages, MessageType, Message
from src.chats.chats import Chat

class MessageCreation(BaseModel):
  user_id: str
  type: MessageType
  message: str

class MessageListRequest(BaseModel):
  user_id: str
  page: int
  page_size: int

router = APIRouter()

@router.post("/chats/{chat_id}/messages/")
async def post_message(chat_id: str, message: MessageCreation):
  return await create_message(Message(
    chat_id=chat_id,
    user_id=message.user_id,
    type=message.type,
    message=message.message,
  ))

@router.get("/chats/{chat_id}/messages/")
async def get_messages(
  chat_id: str,
  user_id: str,
  page: int,
  page_size: int,
):
  return await list_messages(
    chat=Chat(chat_id, user_id),
    page=page,
    page_size=page_size,
  )
