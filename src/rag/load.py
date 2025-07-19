import gc
import chromadb
from pathlib import Path
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

script_directory = Path(__file__).parent.resolve()

index = None
query_engine = None
retriever = None

def load_index():
  global index
  if index == None:
    print("Loading embedding model...")

    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.llm = None

    print("Loading RAG index...")
    persist_dir = f"{script_directory}/../../storage"

    chroma_client = chromadb.PersistentClient(path=f"{persist_dir}/chroma_db")
    chroma_collection = chroma_client.get_or_create_collection("exoplanets")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    index = VectorStoreIndex.from_vector_store(
      vector_store,
      embed_model=Settings.embed_model,
    )
    print("RAG index loaded.")
  return index

def load_retriever():
  global retriever
  if retriever == None:
    index = load_index()
    print("Loading retriever...")
    retriever = index.as_retriever(similarity_top_k=4)
    print("Retriever loaded")
  return retriever

def unload_index():
  global index
  del index
  gc.collect()
