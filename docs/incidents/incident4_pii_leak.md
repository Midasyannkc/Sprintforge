# Incident 4 (bonus): PII leaks into LLM context and the request trace

**JD line addressed:** "Understanding of AI safety, responsible AI practices...
and PII handling."

## What happened

A real support ticket (T015, disclosed-synthetic, see
`data/SOURCE_DISCLOSURE.md`, a client compliance reviewer following up on a
vendor AI risk review) includes a name, a realistic-shaped email address, and
a realistic-shaped phone number -- exactly the kind of text a real user
pastes into a support form without thinking about it. The naive
pipeline (`agent/orchestrator.run_naive`) passes the raw ticket text straight
into the prompt and the returned trace object (which, in a real deployment,
is what gets logged) with no redaction.

Real result: both the real email (`daniel.reyes1984@example-mail.com`) and
the real phone number (`555-201-4488`) were found verbatim in the naive
pipeline's trace, confirmed by direct string search, not asserted.

## Why it's dangerous

PII in an LLM context or a log line is a real data-governance failure, the
same class the JD names directly ("PII handling"). It also means the same
raw PII could be echoed back by a real LLM if it ever appears in the model's
own output.

## Fix

`safety/pii.py`'s `redact_pii()` runs on ingested ticket text **before** it
reaches the retrieval query, the prompt, or anything returned in the trace.
Pattern-based (email, phone, SSN), each match replaced with a typed
placeholder (`[REDACTED_EMAIL]`) so the redaction itself stays auditable
without the underlying value ever appearing anywhere downstream.

## Real re-verification

`scripts/incidents/04_pii_leak.py`, real run, real assertions:

| | Naive | Fixed |
|---|---|---|
| Raw PII values found in the trace | **2** (email, phone) | **0** |
| PII detected (typed, no raw values) | -- | `{"email": 1, "phone": 1}` |

Raw evidence: `docs/incidents/evidence/incident4_evidence.json`.
