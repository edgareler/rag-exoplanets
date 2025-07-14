import asyncio
from enum import Enum
from fastapi import HTTPException
from nanoid import generate
from dataclasses import dataclass
from src.database.client import get_client
from src.database.tables import MESSAGES_TABLE
from src.database.utils import page_to_range, build_response
from src.chats.chats import read_chat, Chat

class MessageType(str, Enum):
  user = 'user'
  assistant = 'assistant'

@dataclass
class Message:
  chat_id: str
  user_id: str
  message: str
  type: MessageType
  id: str | None = None

async def create_message(message: Message):
  chat = await read_chat(Chat(
    message.chat_id,
    message.user_id,
  ))

  if chat == None or len(chat.data) == 0:
    raise HTTPException(status_code=404, detail="Chat not found for that user.")

  supabase = await get_client()
  response = await (
    supabase.table(MESSAGES_TABLE)
    .insert({
      "id": generate(),
      "chat_id": message.chat_id,
      "user_id": message.user_id,
      "type": message.type,
      "message": message.message,
    })
    .execute()
  )

  return response

async def list_messages(chat: Chat, page: int, page_size: int):
  range = page_to_range(page, page_size)

  supabase = await get_client()
  response = await (
    supabase.table(MESSAGES_TABLE)
    .select("*", count="exact")
    .eq("chat_id", chat.id)
    .eq("user_id", chat.user_id)
    .order("created_at", desc=True)
    .range(range.start, range.end)
    .execute()
  )

  return build_response(response, page, page_size)

