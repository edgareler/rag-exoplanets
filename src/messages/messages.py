from datetime import datetime
from fastapi import HTTPException
from nanoid import generate as nanoid
from src.messages.types import Message, MessageRole
from src.database.client import get_client
from src.database.tables import MESSAGES_TABLE
from src.database.utils import page_to_range, build_response
from src.chats.chats import read_chat
from src.chats.types import Chat
from src.rag.query import question
from src.llm.llm import generate, complete_chat
from src.llm.prompt import build_prompt, build_chat_request

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
  recent_messages = chat["recent_history"]

  chat_request = build_chat_request(
    question=message.message,
    context=context,
    summary=summary,
    recent_messages=recent_messages,
  )

  response = complete_chat(chat_request)

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
        "type": MessageRole.assistant,
        "message": response,
        "created_at": assistant_message_date,
      },
    ])
    .execute()
  )

  return dict(
    data=response,
  )

async def list_messages(
  chat: Chat,
  page: int,
  page_size: int,
  descending: bool = True
):
  range = page_to_range(page, page_size)

  supabase = await get_client()
  response = await (
    supabase.table(MESSAGES_TABLE)
    .select("*", count="exact")
    .eq("chat_id", chat.id)
    .eq("user_id", chat.user_id)
    .order("created_at", desc=descending)
    .range(range.start, range.end)
    .execute()
  )

  return build_response(response, page, page_size)

