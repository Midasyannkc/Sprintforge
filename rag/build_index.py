"""Builds a real, running Chroma collection over the real 257-chunk corpus,
using the locally-fit TF-IDF+SVD embedder (rag/embed.py) as the embedding
function. Persisted to disk so the API/agent layer can query it without
re-fitting the embedder on every process start.
"""
import json
import os

import chromadb

from rag.embed import Embedder, CHUNKS_PATH

PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db")
COLLECTION_NAME = "requests_docs"


def build():
    with open(CHUNKS_PATH) as f:
        chunks = json.load(f)
    embedder = Embedder.load()

    client = chromadb.PersistentClient(path=PERSIST_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    texts = [c["text"] for c in chunks]
    vectors = embedder.embed(texts)
    ids = [c["id"] for c in chunks]
    metadatas = [{"source": c["source"]} for c in chunks]

    # Chroma add() has a batch add limit on some backends; this corpus is
    # small enough (257) to add in one call, but chunk defensively anyway.
    BATCH = 200
    for i in range(0, len(ids), BATCH):
        collection.add(
            ids=ids[i:i + BATCH],
            embeddings=vectors[i:i + BATCH],
            documents=texts[i:i + BATCH],
            metadatas=metadatas[i:i + BATCH],
        )
    return collection


if __name__ == "__main__":
    collection = build()
    print(f"Built real Chroma collection '{COLLECTION_NAME}' with {collection.count()} real chunks.")
    print(f"Persisted to {PERSIST_DIR}")
