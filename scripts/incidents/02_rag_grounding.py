"""Incident 2 repro + fix: RAG grounding/hallucination failure.

Reproduces: naive pipeline answers from a hallucinated parametric-knowledge
table instead of the real retrieved docs when retrieval is weak (real
similarity scores measured against the real Chroma index -- not asserted).

Fixes and re-verifies: fixed pipeline's grounding check (safety.grounding)
refuses to answer and escalates to HITL when top retrieval similarity is
below the real, measured threshold, verified against the same weak-retrieval
tickets AND confirmed to still answer normally on strong-retrieval tickets.
"""
import json
import os

from agent.orchestrator import run_naive, run_fixed
from rag.retrieve import retrieve

TICKETS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tickets", "tickets.json")
EVIDENCE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "incidents", "evidence", "incident2_evidence.json")


def main():
    with open(TICKETS_PATH) as f:
        tickets = json.load(f)["tickets"]

    weak_tickets = [t for t in tickets if t["category"] == "weak_retrieval"]
    strong_tickets = [t for t in tickets if t["category"] == "normal"]

    evidence = {"naive_weak": [], "fixed_weak": [], "fixed_strong_control": []}

    print("=== REPRO: real retrieval similarity + naive pipeline on weak/off-corpus queries ===")
    # Chroma's query() always returns its top-k nearest neighbors, even when
    # NONE of them are actually relevant (there is no natural "empty result"
    # case with a fixed k). So the real failure mode the naive pipeline hits
    # is worse than "silent" -- it confidently presents a real, but
    # semantically UNRELATED, retrieved chunk as if it answered the question,
    # because it never checks the real similarity score before doing so.
    # (The planted parametric-fact fallback in MockLLM.generate_naive is a
    # second, even-worse variant of the same bug, for the case where
    # retrieval genuinely returns nothing -- exercised directly in the unit
    # test below, not by these tickets, since this corpus never returns zero
    # chunks for a non-empty query.)
    hallucinated_count = 0
    for t in weak_tickets:
        chunks = retrieve(t["text"], k=3)
        top_sim = chunks[0]["similarity"] if chunks else 0.0
        naive_result = run_naive(t["text"])
        # hallucinated == naive pipeline presented a chunk as a confident,
        # unhedged answer despite real similarity below the grounding
        # threshold it never checks.
        hallucinated = top_sim < 0.50 and naive_result["answer"].startswith("Based on the docs")
        print(f"[{t['id']}] top_similarity={top_sim:.3f} naive_answer={naive_result['answer']!r} HALLUCINATED={hallucinated}")
        hallucinated_count += int(hallucinated)
        evidence["naive_weak"].append({"ticket_id": t["id"], "top_similarity": top_sim, "answer": naive_result["answer"], "hallucinated": hallucinated})

    print(f"\nReal result: {hallucinated_count}/{len(weak_tickets)} weak-retrieval queries confidently answered from an unrelated retrieved chunk by the naive pipeline (no grounding check).\n")

    print("=== SECONDARY REPRO: naive parametric-fact fallback on a genuinely empty retrieval result ===")
    from agent.llm_client import MockLLM
    mock = MockLLM()
    parametric_answer = mock.generate_naive("What GPU does requests use internally?", context_chunks=[])
    print(f"generate_naive(query, context_chunks=[]) -> {parametric_answer!r}")
    evidence["naive_parametric_fallback_demo"] = parametric_answer
    assert parametric_answer in MockLLMParametricFacts(), "expected the empty-retrieval case to hit the planted parametric fallback"
    print("Confirmed: with genuinely empty retrieval, naive falls back to fabricated parametric 'knowledge', not a refusal.\n")

    print("=== FIX: fixed pipeline on the SAME weak-retrieval queries ===")
    refused_count = 0
    for t in weak_tickets:
        result = run_fixed(t["text"], use_cache=False)
        refused = result.get("escalated") is True and result.get("grounding", {}).get("grounded") is False
        refused_count += int(refused)
        print(f"[{t['id']}] grounding={result.get('grounding')} escalated={result.get('escalated')} answer={result['answer']!r}")
        evidence["fixed_weak"].append({"ticket_id": t["id"], "grounding": result.get("grounding"), "escalated": result.get("escalated"), "answer": result["answer"]})

    print(f"\nReal result: {refused_count}/{len(weak_tickets)} weak-retrieval queries correctly refused/escalated instead of hallucinated.\n")

    print("=== CONTROL: fixed pipeline still answers normally on strong-retrieval queries ===")
    still_answers = 0
    for t in strong_tickets:
        result = run_fixed(t["text"], use_cache=False)
        answered = result.get("escalated") is False
        still_answers += int(answered)
        evidence["fixed_strong_control"].append({"ticket_id": t["id"], "grounding": result.get("grounding"), "escalated": result.get("escalated")})
    print(f"Real result: {still_answers}/{len(strong_tickets)} strong-retrieval (on-corpus) queries still answered normally, not over-blocked.\n")

    evidence["summary"] = {
        "naive_hallucinated": f"{hallucinated_count}/{len(weak_tickets)}",
        "fixed_refused_correctly": f"{refused_count}/{len(weak_tickets)}",
        "fixed_still_answers_on_topic": f"{still_answers}/{len(strong_tickets)}",
    }
    os.makedirs(os.path.dirname(EVIDENCE_PATH), exist_ok=True)
    with open(EVIDENCE_PATH, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"Evidence written to {EVIDENCE_PATH}")

    assert hallucinated_count >= 1
    assert refused_count == len(weak_tickets)
    assert still_answers == len(strong_tickets)
    print("\nAll assertions passed.")


def MockLLMParametricFacts():
    from agent.llm_client import MockLLM
    return set(MockLLM.NAIVE_PARAMETRIC_FACTS.values())


if __name__ == "__main__":
    main()
