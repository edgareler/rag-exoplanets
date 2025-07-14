import os
from supabase import acreate_client, AsyncClient
from dotenv import load_dotenv

load_dotenv()
db_client = None

async def get_client() -> AsyncClient:
  global db_client
  if db_client != None:
    return db_client

  url: str = os.environ.get("SUPABASE_URL")
  key: str = os.environ.get("SUPABASE_KEY")
  db_client = await acreate_client(url, key)

  return db_client
