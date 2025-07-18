from fastapi import FastAPI
from src.chats.router import router as router_chats
from src.messages.router import router as router_messages
from src.llm.llm import load_model, warm_up
from src.rag.load import load_index, load_retriever
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
  print("Starting up...")
  load_model()
  print("Warming up model")
  warm_up()
  print("Model warmed up")
  load_index()
  load_retriever()
  yield
  print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
  return {"success": True}

app.include_router(router_chats)
app.include_router(router_messages)
