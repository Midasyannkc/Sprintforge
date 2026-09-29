"""Real two-tier response cache: exact-match (hash of normalized query) then
semantic-similarity match (cosine similarity over the same TF-IDF+SVD
embedder RAG uses, so no extra embedding model/cost). Incident 3's fix uses
this to stop a repeated/near-duplicate query pattern from re-paying full
generation cost every time.
"""
import hashlib
import time

import numpy as np

# Tuned against real measured cosine similarity in this build's TF-IDF+SVD
# embedding space over the real AIID incident corpus: real paraphrases of the
# same support question measured 0.862-0.921 here (see
# docs/incidents/incident3_cost_blowup.md), while distinct-topic ticket pairs
# in the real demo corpus stayed below 0.144 -- 0.80 real-world separates
# them with wide margin on both sides.
SEMANTIC_THRESHOLD = 0.80


def _norm(q: str) -> str:
    return " ".join(q.lower().strip().split())


def _hash(q: str) -> str:
    return hashlib.sha256(_norm(q).encode()).hexdigest()


class ResponseCache:
    def __init__(self, embedder=None):
        self.embedder = embedder
        self._exact = {}          # hash -> (response, vector)
        self._entries = []        # list of (query, vector, response)
        self.hits_exact = 0
        self.hits_semantic = 0
        self.misses = 0

    def get(self, query: str):
        h = _hash(query)
        if h in self._exact:
            self.hits_exact += 1
            return self._exact[h][0], "exact"

        if self.embedder is not None and self._entries:
            qvec = np.array(self.embedder.embed([query])[0])
            best_sim, best_resp = -1.0, None
            for _, vec, resp in self._entries:
                sim = float(np.dot(qvec, vec))
                if sim > best_sim:
                    best_sim, best_resp = sim, resp
            if best_sim >= SEMANTIC_THRESHOLD:
                self.hits_semantic += 1
                return best_resp, "semantic"

        self.misses += 1
        return None, "miss"

    def put(self, query: str, response: str):
        h = _hash(query)
        vec = np.array(self.embedder.embed([query])[0]) if self.embedder is not None else None
        self._exact[h] = (response, vec)
        if vec is not None:
            self._entries.append((query, vec, response))

    def stats(self) -> dict:
        total = self.hits_exact + self.hits_semantic + self.misses
        hit_rate = (self.hits_exact + self.hits_semantic) / total if total else 0.0
        return {
            "hits_exact": self.hits_exact,
            "hits_semantic": self.hits_semantic,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }
