import faiss
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

script_directory = Path(__file__).parent.resolve()

def preprocess():
  papers_directory = f"{script_directory}/../../papers"

  print("Reading docs...")

  reader = SimpleDirectoryReader(
    input_dir=papers_directory,
    required_exts=[".pdf"],
  )

  print("Extending docs...")

  all_docs = []

  for docs in reader.iter_data():
    all_docs.extend(docs)

  print("Loading model...")

  Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
  embedding_dim = 384

  print("Configuring vector index...")

  faiss_index = faiss.IndexFlatL2(embedding_dim)
  vector_store = FaissVectorStore(faiss_index=faiss_index)
  storage_context = StorageContext.from_defaults(vector_store=vector_store)

  print("Generating vectors...")

  index = VectorStoreIndex.from_documents(
    all_docs,
    storage_context=storage_context,
  )

  print("Persisting vectors in storage...")

  storage_directory = f"{script_directory}/../../storage"
  index.storage_context.persist(storage_directory)

  print("Preprocess done.")

if __name__ == "__main__":
  preprocess()
