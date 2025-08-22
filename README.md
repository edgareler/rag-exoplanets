# Retrieval-Augmented Generation (RAG) for Exoplanets Research

A compact, teaching-first backend demonstrating Retrieval-Augmented Generation (RAG) with local models.
This repo is built as a learning artifact, where everything is organized so someone new to RAG can follow the steps you took, reproduce them, and experiment safely.

## Exoplanets

I'm a Space enthusiast, and Exoplanets is a domain that had always fascinated me, but I barely had any knowledge about it.

That's why I choose it for this RAG experiment. But, as you can imagine, you can use this repository to any domain you need, leveraging the capabilities of LLMs and vector DBs to build a comprehensive knowledge base.

The papers used in the Live Chat (to be released) are listed at [./papers/README.md](./papers/README.md).

## Purpose & audience

This repository’s sole purpose is to teach RAG (index → retrieve → augment → generate). It’s aimed at engineers or researchers who want a hands-on, minimal but realistic stack:

- [FastAPI](https://github.com/fastapi/fastapi) backend (serves the RAG API)
- [LlamaIndex](https://www.llamaindex.ai/) for ingestion, chunking, vector store abstraction, and orchestration
- Local LLM via `llama-cpp` (Meta-Llama-3.1 or similar)
- Local embedding model (HuggingFace `BAAI/bge-small-en-v1.5` recommended)
- Persistent vector DB ([Chroma](https://www.trychroma.com/)) for retrieval
- [Minimal Next.js frontend](https://github.com/edgareler/rag-exoplanets-frontend) can consume the streamed answers

If you want a "how I learned RAG" repository to show and teach others, this README will guide learners step-by-step.

## What you'll learn (high level)

- How to convert PDFs → text → tokenized chunks → embeddings
- How to persist vectors in Chroma and load them for retrieval
- How to compose an efficient prompt (system, summary, retrieved context, recent messages)
- How to call a local LLM (llama-cpp) and stream the result back to the client
- How to troubleshoot common RAG problems (tokenizer mismatch, token limits, stop/echo issues)

## Architecture (simple view)

```
[PDFs / papers]  --> preprocess (chunk + embed) --> [Chroma persistent collection]
                                      ↑
                           (index built once offline)
                                      ↓
[User request] --> FastAPI (retriever + prompt builder) --> llama-cpp (local LLM)
                                          ↘ (streaming) ↗
                                     Next.js client (streamed UI)
```

## Quick start (prereqs & run)

**Prerequisites (dev machine)**

- Python 3.10+
- (Optional GPU) CUDA & drivers: if you want GPU inference, build llama-cpp-python with CUDA/cuBLAS.
- `pip` / virtualenv / `pipenv`

**Recommended install (example)**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Notes:

- If you plan to run `llama-cpp` on GPU, you may need to compile `llama-cpp-python` with `CMAKE_ARGS="-DLLAMA_CUBLAS=on"` (see project README of `llama-cpp-python`).

Place your private PDFs in `./papers/` (this repo ignores them).

**Run (dev)**
```bash
# build the index (preprocess): run your preprocess script e.g.
python scripts/preprocess.py   # (this creates ./chroma_storage)
# start FastAPI
uvicorn src.api.chat:app --reload --port 8000
```
(If you already have your own script name, run that, the important part is: preprocess → persist → start server.)


## Project layout (what learners should explore)
```
src/
  api/
    chat.py             # FastAPI endpoints (streaming response)
  llm/
    llama_service.py    # model loading, generate(), streaming wrapper
    prompt.py           # helpers: build_messages(), build_summary_messages()
  ingestion/
    preprocess.py       # chunking, embedding, Chroma persistence
  storage/               # (gitignored) runtime paths: chroma_storage, model files
tests/                   # examples and small unit tests for learners
scripts/                 # convenience scripts (indexing, re-indexing)
requirements.txt
README.md
```

## Step-by-step learning flow (recommended order)

1. **Read `ingestion/preprocess.py`**: see how documents are split (TokenTextSplitter), embedded, and stored in Chroma.
     - Exercise: change `chunk_size` to 256 tokens (smaller chunks) and re-run.
2. **Inspect `src/llm/prompt.py`**: learn how system/context/summary/recent messages are combined into a `messages` list for `create_chat_completion`.
      - Exercise: replace recent messages with a 1-sentence summary and compare answers.
3. **Start the server and test a simple query (no streaming first)**: confirm the retriever returns sensible nodes.
4. **Enable streaming response** in `src/api/chat.py` (look for `StreamingResponse`) and wire the frontend to consume the stream.
      - Exercise: measure latency for answers with 1, 2, 3 retrieved nodes.
5. **Tuning**: experiment with n_ctx (model context window), `max_tokens` for outputs, and `temperature/top_p`.
      - Exercise: set `max_tokens=400` and ask for a "200-word" descriptive paragraph, and compare completion quality.
6. **Troubleshooting**: replicate and fix common issues (see next section).

## How to build the `messages` payload (recommended pattern)

Use the chat API style messages (do **not** concatenate roles manually into a single string). Example pattern:

```python
messages = [
  {"role": "system", "content": SYSTEM_PROMPT},
  {"role": "user", "content": "Conversation summary:\n" + recent_summary},      # short, token-light
  {"role": "user", "content": "Context:\n" + retrieved_context},              # pulled from Chroma
  # recent turns as separate dicts:
  {"role": "user", "content": "Last question"},
  {"role": "assistant", "content": "Assistant reply"},
  {"role": "user", "content": current_user_question}
]
```

Why this pattern?

- It matches `create_chat_completion()` expectations (Meta LLaMA chat format).
- It keeps token usage predictable.
- It allows the model to understand roles and turn boundaries.

## Teaching exercises (short, practical)

1. **Replace Chroma with in-memory search**: export embeddings to JSON and do cosine search in Python, compare speed/quality.
2. **Summarize vs raw history**: automatically summarize the last 4 messages and compare answers against sending full last 4 messages.
3. **Embedding mismatch demo**: intentionally load a different embedding model at query-time and observe retrieval degradation (KeyError-like issues).
4. **Stop/echo experiments**: toggle `echo=True/False` and different `stop` tokens to see effect on outputs and speed.

## Troubleshooting (concise cheat-sheet)

- **Short or cut responses**
  - Check `stop` parameter, using `"\n"` or `"Q:"` can cut output prematurely. Prefer a rare stop token or rely on `max_tokens`.
  - Avoid `echo=True` in production (it echoes the prompt into the output).
  - Increase `max_tokens` or instruct `"Provide up to 200 words..."` in system prompt.
- **KeyError: '959' or token/id errors**
  - Embedding model used at indexing must match embedding model set at query time.
  - Always set `Settings.embed_model = HuggingFaceEmbedding(...)` before loading the index.
- **Index persistence problems**
  - With Chroma: ensure the correct `persist_dir` and collection name are used.
  - With FAISS (used in a previous version): avoid manually renaming files; let the vector store persist method write its binary.
- **Missing OpenAI key errors**
  - LlamaIndex `as_query_engine()` defaults to OpenAI if no LLM passed. Either:
    - Use `index.as_retriever()` and call local LLM manually, or
    - Provide a local LLM object to `as_query_engine(llm=your_local_llm)`.
- **Slow generation**
  - Large context means slower generation. Restrict retrieved tokens (fewer chunks, smaller chunks).
  - CPU inference is slower than GPU. Use GPU/compile with cuBLAS for speed.
  - Stop strings add overhead at each token; prefer rare or none.
- **Model on CPU instead of GPU**
  - Reinstall/compile `llama-cpp-python` with `CMAKE_ARGS="-DLLAMA_CUBLAS=on"` and set n_gpu_layers when loading:
    ```bash
    pipenv shell
    CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python \
    --force-reinstall --no-binary :all:
    ```

## Teaching tips (for workshop or tutorial)

- Start students with small docs (1 to 3 papers) and `chunk_size=256`. Let them see immediate retrieval results.
- Ask them to intentionally break the pipeline (wrong embed model, rename files) and then debug, this solidifies understanding.
- Make a short checklist for deployment: `preprocess → persist → start server → healthcheck → query`.

## Contributing & license

This repo is intended to be fully open and re-used for teaching. If you want to add exercises, notes, or more examples (e.g., using Pinecone or Qdrant), open a PR.

License: MIT
