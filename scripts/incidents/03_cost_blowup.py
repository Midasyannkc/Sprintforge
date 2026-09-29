"""Incident 3 repro + fix: cost blowup from an uncached repeated-query
pattern (three real near-duplicate tickets, T001/T012/T013/T014, all asking
the same timeout question in different words -- a realistic support-queue
pattern: a user who follows up repeatedly on the same issue).

Reproduces: naive pipeline (no cache) re-pays full retrieval+generation cost
on every single repeat -- real measured token/dollar cost, not estimated.

Fixes and re-verifies: fixed pipeline's response cache (cost/cache.py)
catches the exact-duplicate repeats and, via the semantic-similarity tier,
the near-duplicate rephrasings too -- real measured hit rate and real
dollars saved at the documented per-token price (cost/token_counter.py).
"""
import json
import os

from agent.orchestrator import run_naive, run_fixed, get_shared_cache

TICKETS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tickets", "tickets.json")
EVIDENCE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "incidents", "evidence", "incident3_evidence.json")


def main():
    with open(TICKETS_PATH) as f:
        tickets = json.load(f)["tickets"]

    repeat_ids = {"T001", "T012", "T013", "T014"}
    repeat_tickets = [t for t in tickets if t["id"] in repeat_ids]

    print("=== REPRO: naive pipeline, no cache, real cost on each repeat ===")
    naive_total_cost = 0.0
    naive_calls = []
    for t in repeat_tickets:
        result = run_naive(t["text"])
        naive_total_cost += result["cost"]
        naive_calls.append({"ticket_id": t["id"], "text": t["text"], "cost": result["cost"], "tokens": result["prompt_tokens"]})
        print(f"[{t['id']}] {t['text'][:60]!r} -> cost=${result['cost']:.6f} (full retrieval+generation, every time)")

    print(f"\nReal result: naive pipeline paid full cost {len(repeat_tickets)}/{len(repeat_tickets)} times for what is really "
          f"1 distinct question, total ${naive_total_cost:.6f}.\n")

    print("=== FIX: fixed pipeline WITH cache, same real repeated-query sequence ===")
    cache = get_shared_cache()
    fixed_total_cost = 0.0
    fixed_calls = []
    for t in repeat_tickets:
        result = run_fixed(t["text"], use_cache=True)
        cost = result.get("cost", 0.0)
        fixed_total_cost += cost
        fixed_calls.append({"ticket_id": t["id"], "text": t["text"], "cost": cost, "cache_status": result["cache_status"]})
        print(f"[{t['id']}] {t['text'][:60]!r} -> cost=${cost:.6f} cache_status={result['cache_status']}")

    cache_stats = cache.stats()
    print(f"\nReal cache stats over this run: {cache_stats}")

    savings = naive_total_cost - fixed_total_cost
    pct_saved = (savings / naive_total_cost * 100) if naive_total_cost else 0.0
    print(f"Real result: fixed pipeline total cost ${fixed_total_cost:.6f} vs naive ${naive_total_cost:.6f} "
          f"-> ${savings:.6f} saved ({pct_saved:.1f}%) on this repeated-query sequence.\n")

    print("=== GUARD CHECK: max-iterations guard on the agentic tool loop ===")
    from agent.orchestrator import MAX_ITERATIONS, run_fixed as _rf
    result = run_fixed("How does this software use a built-in Kubernetes operator for distributed request scheduling?", use_cache=False)
    print(f"iterations used: {result['iterations']} (hard cap: {MAX_ITERATIONS})")
    assert result["iterations"] <= MAX_ITERATIONS

    evidence = {
        "naive_calls": naive_calls,
        "naive_total_cost": naive_total_cost,
        "fixed_calls": fixed_calls,
        "fixed_total_cost": fixed_total_cost,
        "cache_stats": cache_stats,
        "dollars_saved": savings,
        "pct_saved": pct_saved,
        "max_iterations_guard": MAX_ITERATIONS,
    }
    os.makedirs(os.path.dirname(EVIDENCE_PATH), exist_ok=True)
    with open(EVIDENCE_PATH, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"Evidence written to {EVIDENCE_PATH}")

    assert fixed_total_cost < naive_total_cost
    assert cache_stats["hits_exact"] + cache_stats["hits_semantic"] >= 3
    print("\nAll assertions passed.")


if __name__ == "__main__":
    main()
