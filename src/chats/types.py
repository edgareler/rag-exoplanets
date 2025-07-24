from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class Chat:
  id: str
  user_id: str

class ChatCreation(BaseModel):
  user_id: str
