import asyncio
from pydantic import BaseModel
from fastapi import APIRouter
from pydantic import BaseModel
from src.chats.chats import create_chat, list_chats, read_chat

class ChatCreation(BaseModel):
  id: str
  user_id: str

router = APIRouter()

@router.post("/chats/")
async def post_chat(chat: ChatCreation):
  return await create_chat(chat)

@router.get("/chats/")
async def get_chats(user_id: str):
  return await list_chats(user_id)

@router.get("/chats/{chat_id}")
async def get_chat(chat_id: str):
  return await read_chat(chat_id)
