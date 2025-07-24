from fastapi import APIRouter, BackgroundTasks
from src.messages.types import MessageCreation, Message
from src.messages.messages import create_message, list_messages
from src.chats.types import Chat
from src.chats.history import build_history

router = APIRouter()

@router.post("/chats/{chat_id}/messages/")
async def post_message(
  chat_id: str,
  message: MessageCreation,
  background_tasks: BackgroundTasks,
):
  response = await create_message(Message(
    chat_id=chat_id,
    user_id=message.user_id,
    type=message.type,
    message=message.message,
  ))

  background_tasks.add_task(build_history, chat_id, message.user_id)

  return response

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
