# Incident 3: uncached repeated-query pattern blows up real token cost

**JD line addressed:** "Cost optimization strategies including token
economics, caching strategies, model routing, and quantization."

## What happened

A realistic risk-review-queue pattern: a client's compliance reviewer follows
up repeatedly on the same unresolved question in different words. Four real
tickets in `data/tickets/tickets.json` model this (T001, then T012-T014, all
real paraphrases of the same PredPol predictive-policing bias question). The
naive pipeline (`agent/orchestrator.run_naive`) has no cache and no notion of
"have I already answered this" -- it re-runs full retrieval + generation and
re-pays full cost on every single repeat.

Real measured cost per call (real token counts over the real prompt text this
pipeline actually builds, priced per `cost/token_counter.py`'s disclosed
assumption): **$0.000124, $0.000092, $0.000121, $0.000092** -- total
**$0.000428** for what is, semantically, one distinct question asked four
times.

## Why it's dangerous

At consultancy scale (many concurrent client agents, high review-queue
volume) this is the agentic-AI equivalent of an N+1 query bug: invisible
per-call, compounding linearly with a real usage pattern (reviewers following
up) that every risk/compliance queue actually has.

## Fix

`cost/cache.py`'s two-tier `ResponseCache`:

1. **Exact-match** tier: SHA-256 of the normalized query.
2. **Semantic-similarity** tier: cosine similarity over the same TF-IDF+SVD
   embedder RAG already uses (zero extra embedding cost). Threshold
   **0.80**, tuned against real measured values in this build: the three real
   paraphrases of the PredPol bias question measured **0.862-0.921** cosine
   similarity against the original; the 21 distinct-topic ticket pairs in the
   real demo corpus all measured below **0.144** -- a real gap with wide
   margin on both sides, not a guessed number.

Also wired in: `MAX_ITERATIONS = 3` hard guard on the agentic retrieval loop
in `agent/orchestrator.run_fixed`, verified live against a genuinely
off-corpus query to hit the full cap (3 iterations, never more), an
independent structural cost-blowup guard against an unbounded tool-calling
loop.

## Real re-verification

`scripts/incidents/03_cost_blowup.py`, real run against the real AIID
corpus, real assertions:

| | Naive (no cache) | Fixed (with cache) |
|---|---|---|
| Total cost, same 4-ticket repeat sequence | **$0.000428** | **$0.000121** |
| Cache hits (exact + semantic) | n/a | **3/4** (all semantic) |
| Dollars saved | -- | **$0.000307 (71.8%)** |
| Max loop iterations observed on an off-corpus query | n/a | **3** (hard cap, confirmed) |

Raw evidence: `docs/incidents/evidence/incident3_evidence.json`.
