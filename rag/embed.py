"""Local, network-free embedding: TF-IDF + TruncatedSVD (a real, deterministic
dimensionality-reduced dense embedding computed from the real corpus text).

huggingface.co is blocked in this sandbox (see data/SOURCE_DISCLOSURE.md), so a
hosted sentence-transformers model download is not possible here. This is the
same fallback used on Undercurrent for the same disclosed reason. The vectors
are real, fit for real on the real 257-chunk corpus, not stubbed out.
"""
import json
import os
import pickle

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chunks.json")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "embed_model.pkl")

N_COMPONENTS = 128


def fit_embedder(texts):
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
    tfidf = vectorizer.fit_transform(texts)
    n_comp = min(N_COMPONENTS, tfidf.shape[0] - 1, tfidf.shape[1] - 1)
    svd = TruncatedSVD(n_components=n_comp, random_state=42)
    dense = svd.fit_transform(tfidf)
    # L2-normalize so cosine similarity == dot product for the vector store.
    norms = np.linalg.norm(dense, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    dense = dense / norms
    return vectorizer, svd, dense


class Embedder:
    def __init__(self, vectorizer, svd):
        self.vectorizer = vectorizer
        self.svd = svd

    def embed(self, texts):
        tfidf = self.vectorizer.transform(texts)
        dense = self.svd.transform(tfidf)
        norms = np.linalg.norm(dense, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (dense / norms).tolist()

    def save(self, path=MODEL_PATH):
        with open(path, "wb") as f:
            pickle.dump({"vectorizer": self.vectorizer, "svd": self.svd}, f)

    @classmethod
    def load(cls, path=MODEL_PATH):
        with open(path, "rb") as f:
            d = pickle.load(f)
        return cls(d["vectorizer"], d["svd"])


if __name__ == "__main__":
    with open(CHUNKS_PATH) as f:
        chunks = json.load(f)
    texts = [c["text"] for c in chunks]
    vectorizer, svd, dense = fit_embedder(texts)
    embedder = Embedder(vectorizer, svd)
    embedder.save()
    print(f"Fit TF-IDF+SVD embedder on {len(texts)} real chunks -> {dense.shape[1]}-dim vectors.")
    print(f"Explained variance ratio (SVD): {svd.explained_variance_ratio_.sum():.3f}")
    print(f"Saved embedder to {MODEL_PATH}")
