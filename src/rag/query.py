from src.rag.load import load_retriever

def question(question: str, top_k: int = 4) -> str:
  retriever = load_retriever()

  print("Querying nodes...")
  nodes = retriever.retrieve(question)

  context = "\n\n".join([node.get_content() for node in nodes])

  return context
