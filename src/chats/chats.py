import asyncio
from datetime import datetime
from pydantic import BaseModel
from dataclasses import dataclass
from src.database.client import get_client
from src.database.tables import CHATS_TABLE
from src.database.utils import page_to_range, build_response

@dataclass
class Chat:
  id: str
  user_id: str

async def create_chat(chat: Chat) -> str:
  chat_date = datetime.now().isoformat()
  supabase = await get_client()
  response = await (
    supabase.table(CHATS_TABLE)
    .insert({
      "id": chat.id,
      "user_id": chat.user_id,
      "created_at": chat_date,
    })
    .execute()
  )
  return response

async def read_chat(chat: Chat):
  supabase = await get_client()
  response = await (
    supabase.table(CHATS_TABLE)
    .select("*")
    .eq("id", chat.id)
    .eq("user_id", chat.user_id)
    .execute()
  )
  if len(response.data) == 0:
    return None
  return response.data[0]

async def list_chats(user_id: str, page: int = 1, page_size: int = 10):
  range = page_to_range(page, page_size)

  supabase = await get_client()
  response = await (
    supabase.table(CHATS_TABLE)
    .select("*", count="exact")
    .eq("user_id", user_id)
    .order("created_at", desc=True)
    .range(range.start, range.end)
    .execute()
  )

  return build_response(response, page, page_size)
