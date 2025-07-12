import os
from llama_cpp import Llama
from dotenv import load_dotenv

load_dotenv()

llm = None

def load_model():
  global llm
  if llm == None:
    llm = Llama(
      model_path = os.environ.get("MODEL_PATH"),
      n_gpu_layers=-1,
    )

def generate(prompt, max_tokens=None):
  return llm(
    prompt=prompt,
    max_tokens=max_tokens,
    stop=["Q:", "\n"],
    echo=True,
  )

def count_tokens(prompt):
  tokens = llm.tokenize(prompt.encode("utf-8"))
  return len(tokens)
