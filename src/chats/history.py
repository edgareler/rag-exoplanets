import sys
from src.llm.llm import MAX_TOKENS, count_tokens, generate
from src.llm.prompt import build_summary_prompt, build_title_prompt
from src.chats.chats import read_chat, update_chat
from src.chats.types import Chat
from src.messages.messages import list_messages
from src.messages.types import PreviousMessage

async def build_history(chat_id: str, user_id: str):
  chat = await read_chat(Chat(
    chat_id,
    user_id,
  ))

  if chat == None:
    raise Exception("Chat not found for that user.")

  # 1. Get messages history
  all_messages: list[dict] = []
  page: int = 1
  page_size: int = 50
  total_pages: int = sys.maxsize

  while page <= total_pages:
    res = await list_messages(
      chat=Chat(
        chat_id,
        user_id,
      ),
      page=page,
      page_size=page_size,
      descending=False,
    )

    if total_pages == sys.maxsize:
      total_pages = res.metadata.total_pages

    all_messages.extend(res.data)

    page += 1

  # 2. Build chat history
  # 2.1 Get last 4 raw messages (2 user, 2 assistant)
  recent_messages = all_messages[-4:]
  recent_messages_text = ""
  recent_messages_json: list[PreviousMessage] = []

  for message in recent_messages:
    recent_messages_text += message["type"].capitalize() + ": " + message["message"] + "\n\n"
    recent_messages_json.append({
      "role": message["type"],
      "content": message["message"],
    })

  # 2.2 Get all older messages
  old_messages = all_messages[0:-4]

  # 2.3 Summarize the older messages with the LLM
  old_messages_summary = None
  old_messages_json: list[PreviousMessage] = []

  if len(old_messages) > 0:
    old_messages_summary = ""

    base_prompt_tokens = count_tokens(build_summary_prompt(""))

    summary_token_count = 0

    for message in old_messages:
      if summary_token_count == 0:
        summary_token_count = base_prompt_tokens

      message_content = message["type"].capitalize() + ": " + message["message"] + "\n\n"
      message_tokens = count_tokens(message_content)

      old_messages_json.append({
        "role": message["type"],
        "content": message["message"],
      })

      if summary_token_count + message_tokens > (MAX_TOKENS / 2):
        old_messages_summary = generate(build_summary_prompt(old_messages_summary)) + "\n\n"
        old_messages_summary += message_content
        summary_token_count = count_tokens(build_summary_prompt(old_messages_summary))
      else:
        old_messages_summary += message_content
        summary_token_count += message_tokens

    old_messages_summary = generate(build_summary_prompt(old_messages_summary))

  title = generate(build_title_prompt(old_messages_summary, recent_messages_text))

  # 3. Update history fields
  db_response = await update_chat(
    chat=Chat(
      chat_id,
      user_id,
    ),
    title=title,
    recent_history=recent_messages_json,
    old_history=old_messages_json,
    old_history_summary=old_messages_summary,
  )

  print("Chat history updated")
