def build_prompt(question: str,
                 context: str,
                 summary: str,
                 conversation: str) -> str:
  prompt: str = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an AI research assistant specialized in astrophysics.
You are given a set of scientific document excerpts as context. Answer the question based on those documents.
Always prioritize accuracy, citing relevant information or methods when possible.
Keep answers concise, clear, and focused on the question.
Use scientific terminology when appropriate, and structure your response in full sentences.
"""

  if context:
    prompt = f"{prompt}\nContext:\n{context}\n"

  if summary:
    prompt = f"{prompt}\nPrior conversation summary::\n{summary}\n"

  if conversation:
    prompt = f"{prompt}\n{conversation}\n"

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

def build_title_prompt(summary: str, conversation: str) -> str:
  prompt: str = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a helpful assistant. Generate a concise and descriptive title for the following chat. The title should reflect the main topic or task discussed. This title will be used for a software menu, so it must be short and use appropriated words for that context. Return only the title, with no quotes.
<|start_header_id|>user<|end_header_id|>
"""
  if summary:
    prompt = f"{prompt}\n\nPrior conversation summary::\n{summary}"

  if conversation:
    prompt = f"{prompt}\n\n{conversation}"

  prompt = f"{prompt}\n\n<|start_header_id|>assistant<|end_header_id|>\n"

  return prompt
