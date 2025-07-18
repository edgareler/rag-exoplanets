from src.rag.load import load_retriever
from src.llm.llm import generate
from src.llm.prompt import build_prompt

def question(question: str, top_k: int = 4) -> str:
  retriever = load_retriever()

  print("Querying nodes...")
  nodes = retriever.retrieve(question)

  context = "\n\n".join([node.get_content() for node in nodes])

  prompt = build_prompt(
    question=question,
    context=context,
    summary=None,
    conversation=None,
  )

  response = generate(prompt)

  return str(response)
