import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.chats.router import router as router_chats
from src.messages.router import router as router_messages
from src.llm.llm import load_model, warm_up, unload_model
from src.rag.load import load_index, load_retriever, unload_index
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware

load_dotenv()

RAG_API_KEY = os.getenv("RAG_API_KEY")

class APIKeyMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    header_api_key = request.headers.get("RAG-API-Key")
    if header_api_key != RAG_API_KEY:
      return JSONResponse(
        status_code=401,
        content={"error": "Unauthorized: Invalid API key"}
      )
    return await call_next(request)

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
  unload_index()
  unload_model()

app = FastAPI(lifespan=lifespan)

app.add_middleware(APIKeyMiddleware)

@app.get("/")
def read_root():
  return {"success": True}

app.include_router(router_chats)
app.include_router(router_messages)
