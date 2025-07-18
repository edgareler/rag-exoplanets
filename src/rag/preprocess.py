import chromadb
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

script_directory = Path(__file__).parent.resolve()

def preprocess():
  papers_directory = f"{script_directory}/../../papers"
  storage_directory = f"{script_directory}/../../storage"

  print("Loading model...")

  Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

  print("Reading docs...")

  all_docs = SimpleDirectoryReader(
    input_dir=papers_directory,
    required_exts=[".pdf"],
  ).load_data()

  print("Splitting documents into chunks...")
  splitter = TokenTextSplitter(chunk_size=253, chunk_overlap=32)
  nodes = splitter.get_nodes_from_documents(all_docs)

  print("Configuring vector index...")

  chroma_client = chromadb.PersistentClient(path=f"{storage_directory}/chroma_db")
  chroma_collection = chroma_client.create_collection("exoplanets")
  vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
  storage_context = StorageContext.from_defaults(vector_store=vector_store)

  print("Generating vectors...")

  index = VectorStoreIndex(
    nodes,
    storage_context=storage_context,
    embed_model=Settings.embed_model
  )

  print("Persisting vectors in storage...")

  index.storage_context.persist(persist_dir=storage_directory)

  print("Preprocess done.")

if __name__ == "__main__":
  preprocess()
