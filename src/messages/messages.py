import asyncio
from datetime import datetime
from enum import Enum
from fastapi import HTTPException
from nanoid import generate as nanoid
from dataclasses import dataclass
from src.database.client import get_client
from src.database.tables import MESSAGES_TABLE
from src.database.utils import page_to_range, build_response, DBResponse
from src.chats.chats import read_chat, Chat
from src.rag.query import question
from src.llm.llm import generate
from src.llm.prompt import build_prompt

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
  user_message_date = datetime.now().isoformat()

  chat = await read_chat(Chat(
    message.chat_id,
    message.user_id,
  ))

  if chat == None:
    raise HTTPException(status_code=404, detail="Chat not found for that user.")

  supabase = await get_client()

  context = question(message.message)
  summary = chat["old_history_summary"]
  conversation = chat["recent_history"]

  prompt = build_prompt(
    question=message.message,
    context=context,
    summary=summary,
    conversation=conversation,
  )

  response = generate(prompt)

  assistant_message_date = datetime.now().isoformat()

  db_response = await (
    supabase.table(MESSAGES_TABLE)
    .insert([
      {
        "id": nanoid(),
        "chat_id": message.chat_id,
        "user_id": message.user_id,
        "type": message.type,
        "message": message.message,
        "created_at": user_message_date,
      },
      {
        "id": nanoid(),
        "chat_id": message.chat_id,
        "user_id": message.user_id,
        "type": MessageType.assistant,
        "message": response,
        "created_at": assistant_message_date,
      },
    ])
    .execute()
  )

  return dict(
    data=response,
  )

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

