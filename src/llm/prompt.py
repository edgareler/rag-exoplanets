from llama_cpp import ChatCompletionRequestMessage
from src.messages.types import PreviousMessage, MessageRole

system_prompt = """You are an AI research assistant specialized in astrophysics.

You will receive a set of scientific document excerpts as context. Answer the user’s question accurately, based only on the provided context.

Guidelines:
- Write a complete, informative, and concise answer (aim for one clear paragraph of up to ~200 words, or use bullet points only if they significantly improve clarity).
- Summarize key data, methods, or findings when relevant.
- Use scientific terminology when appropriate, but briefly define terms that may be unfamiliar.
- Do not refer to diagrams, figures, or tables unless they are explicitly described in the context.
- If the context lacks sufficient information, say so clearly—do not speculate.

Respond in full sentences. Avoid repetition. Keep the response focused and helpful for a scientific audience."""

def build_prompt(question: str,
                 context: str,
                 summary: str,
                 recent_messages: str) -> str:
  prompt: str = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{system_prompt}\n"

  if context:
    prompt = f"{prompt}\nContext:\n{context}\n"

  if summary:
    prompt = f"{prompt}\nPrior conversation summary::\n{summary}\n"

  if recent_messages:
    prompt = f"{prompt}\n{recent_messages}\n"

  prompt = prompt + (
    "\n<|eot_id|>\n\n"
    "<|start_header_id|>user<|end_header_id|>\n"
    f"{question}\n"
    "<|start_header_id|>assistant<|end_header_id|>\n"
  )

  return prompt

def build_history(messages: list[dict]) -> str:
  history: str = ""

  for m in messages:
    message_type = "user" if m.type == "user" else "assistant"
    prompt = prompt + (
      f"<|start_header_id|>{message_type}<|end_header_id|>\n"
      f"{m.message}<|eot_id|>\n\n"
    )

  return history

def build_summary_prompt(messages: str) -> str:
  prompt: str = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a helpful assistant. Summarize the following chat messages in a concise and informative way. Focus on the user’s intent and relevant assistant replies.
<|start_header_id|>user<|end_header_id|>
{messages}
<|start_header_id|>assistant<|end_header_id|>
""".format(messages=messages)
  return prompt

def build_title_prompt(summary: str, recent_messages: str) -> str:
  prompt: str = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a helpful assistant. Generate a concise and descriptive title for the following chat. The title should reflect the main topic or task discussed. This title will be used for a software menu, so it must be short and use appropriated words for that context. Return only the title, with no quotes.
<|start_header_id|>user<|end_header_id|>
"""
  if summary:
    prompt = f"{prompt}\n\nPrior conversation summary::\n{summary}"

  if recent_messages:
    prompt = f"{prompt}\n\n{recent_messages}"

  prompt = f"{prompt}\n\n<|start_header_id|>assistant<|end_header_id|>\n"

  return prompt

def build_chat_request(
  question: str,
  base_prompt: str = system_prompt,
  context: str = None,
  summary: str = None,
  recent_messages: list[PreviousMessage] = [],
) -> list[ChatCompletionRequestMessage]:
  messages: list[ChatCompletionRequestMessage] = [
    {
      "role": "system",
      "content": base_prompt,
    }
  ]

  if context:
    messages.append({
      "role": MessageRole.user,
      "content": f"Context:\n{context}"
    })

  if summary:
    messages.append({
      "role": MessageRole.user,
      "content": f"Prior conversation summary:\n{summary}"
    })

  if recent_messages:
    messages.extend(recent_messages)

  messages.append({
    "role": MessageRole.user,
    "content": question,
  })

  return messages
