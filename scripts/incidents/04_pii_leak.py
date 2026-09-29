"""Incident 4 repro + fix: PII leaking into LLM context and logs.

Reproduces: the naive pipeline puts the real ticket text (a real name, real-
shaped email, real-shaped phone number -- synthetic values, see
data/SOURCE_DISCLOSURE.md) directly into the prompt sent toward the LLM AND
into the trace object that would be logged, with no redaction.

Fixes and re-verifies: the fixed pipeline's safety.pii.redact_pii() strips
PII from the ticket text BEFORE it reaches the retrieval query, the prompt,
or the returned trace -- verified live by asserting none of the raw PII
strings appear anywhere in the fixed trace.
"""
import json
import os

from agent.orchestrator import run_naive, run_fixed
from safety.pii import detect_pii

TICKETS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tickets", "tickets.json")
EVIDENCE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "incidents", "evidence", "incident4_evidence.json")


def main():
    with open(TICKETS_PATH) as f:
        tickets = json.load(f)["tickets"]
    ticket = next(t for t in tickets if t["category"] == "pii")

    real_pii = detect_pii(ticket["text"])
    print(f"Ticket {ticket['id']} real PII detected in source text: {real_pii}")

    print("\n=== REPRO: naive pipeline, PII flows straight into the prompt/trace ===")
    naive_result = run_naive(ticket["text"])
    naive_trace_str = json.dumps(naive_result)
    leaked = [v for vals in real_pii.values() for v in vals if v in naive_trace_str]
    print(f"naive prompt/trace contains raw PII values: {leaked}")

    print("\n=== FIX: fixed pipeline, PII redacted before context/log ===")
    fixed_result = run_fixed(ticket["text"], use_cache=False)
    fixed_trace_str = json.dumps(fixed_result)
    still_leaked = [v for vals in real_pii.values() for v in vals if v in fixed_trace_str]
    print(f"fixed pii_found (typed, no raw values): {fixed_result.get('pii_found')}")
    print(f"fixed prompt/trace still contains raw PII values: {still_leaked}")

    evidence = {
        "ticket_id": ticket["id"],
        "real_pii_in_source": real_pii,
        "naive_leaked_values": leaked,
        "fixed_pii_found_typed": fixed_result.get("pii_found"),
        "fixed_leaked_values": still_leaked,
        "fixed_answer": fixed_result.get("answer"),
    }
    os.makedirs(os.path.dirname(EVIDENCE_PATH), exist_ok=True)
    with open(EVIDENCE_PATH, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"\nEvidence written to {EVIDENCE_PATH}")

    assert len(leaked) >= 1, "expected naive pipeline to leak real PII into its trace"
    assert len(still_leaked) == 0, "expected fixed pipeline to leak ZERO raw PII values"
    print("\nAll assertions passed: naive really leaked PII, fixed really redacted all of it.")


if __name__ == "__main__":
    main()
