"""Grounding check (Incident 2 fix): decides whether retrieval returned
enough real support to answer at all, BEFORE generation runs. Naive path
skips this entirely and lets the LLM (or its parametric fallback) answer
regardless of retrieval quality.
"""

# Similarity below this means "no real chunk is actually relevant" --
# threshold picked from the real similarity gap observed on the real AIID
# incident corpus in this build: on-topic queries measured 0.758-0.968,
# genuinely off-corpus queries measured 0.0 (see
# docs/incidents/incident2_rag_grounding_hallucination.md for the real
# numbers this was tuned against). 0.50 sits well inside that real gap.
GROUNDING_THRESHOLD = 0.50


def is_grounded(retrieved_chunks: list) -> dict:
    if not retrieved_chunks:
        return {"grounded": False, "top_similarity": 0.0, "reason": "no chunks retrieved"}
    top_sim = retrieved_chunks[0]["similarity"]
    grounded = top_sim >= GROUNDING_THRESHOLD
    reason = "ok" if grounded else f"top similarity {top_sim:.3f} below threshold {GROUNDING_THRESHOLD}"
    return {"grounded": grounded, "top_similarity": top_sim, "reason": reason}
