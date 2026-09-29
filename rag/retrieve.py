"""Real retrieval over the real Chroma collection. Returns the top-k chunks
plus their real cosine similarity scores, which the grounding check
(safety/grounding.py, Incident 2) uses to decide whether the pipeline has
enough real support to answer at all.
"""
import os

import chromadb

from rag.embed import Embedder

PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db")
COLLECTION_NAME = "requests_docs"

_embedder = None
_collection = None


def _get_collection():
    global _embedder, _collection
    if _collection is None:
        _embedder = Embedder.load()
        client = chromadb.PersistentClient(path=PERSIST_DIR)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query: str, k: int = 3):
    collection = _get_collection()
    query_vec = _embedder.embed([query])[0]
    result = collection.query(query_embeddings=[query_vec], n_results=k)
    hits = []
    for doc, meta, dist, cid in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0], result["ids"][0]
    ):
        # Chroma cosine space returns distance = 1 - cosine_similarity.
        similarity = 1.0 - dist
        hits.append({"id": cid, "source": meta["source"], "text": doc, "similarity": similarity})
    return hits


if __name__ == "__main__":
    for q in ["how do I set a timeout", "does requests use a GPU internally"]:
        print(f"\nQuery: {q}")
        for h in retrieve(q, k=3):
            print(f"  [{h['similarity']:.3f}] {h['source']} :: {h['text'][:80]!r}")
