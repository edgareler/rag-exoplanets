from typing import Union
from fastapi import FastAPI
from src.chats.router import router as router_chats
from src.messages.router import router as router_messages

app = FastAPI()

@app.get("/")
def read_root():
  return {"success": True}

app.include_router(router_chats)
app.include_router(router_messages)
