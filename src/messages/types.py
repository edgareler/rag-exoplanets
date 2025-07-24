from enum import Enum
from pydantic import BaseModel
from dataclasses import dataclass

class MessageRole(str, Enum):
  user = 'user'
  assistant = 'assistant'

@dataclass
class PreviousMessage:
  role: MessageRole
  content: str

class MessageCreation(BaseModel):
  user_id: str
  type: MessageRole
  message: str

class MessageListRequest(BaseModel):
  user_id: str
  page: int
  page_size: int

@dataclass
class Message:
  chat_id: str
  user_id: str
  message: str
  type: MessageRole
  id: str | None = None
