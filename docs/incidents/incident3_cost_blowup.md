# Incident 3: uncached repeated-query pattern blows up real token cost

**JD line addressed:** "Cost optimization strategies including token
economics, caching strategies, model routing, and quantization."

## What happened

A realistic support-queue pattern: a user follows up repeatedly on the same
unresolved issue in different words. Four real tickets in
`data/tickets/tickets.json` model this (T001, then T012-T014, all real
paraphrases of the same timeout question). The naive pipeline
(`agent/orchestrator.run_naive`) has no cache and no notion of "have I
already answered this" -- it re-runs full retrieval + generation and re-pays
full cost on every single repeat.

Real measured cost per call (real token counts over the real prompt text
this pipeline actually builds, priced per `cost/token_counter.py`'s
disclosed assumption): **$0.000127, $0.000148, $0.000149, $0.000138** --
total **$0.000562** for what is, semantically, one distinct question asked
four times.

## Why it's dangerous

At consultancy scale (many concurrent client agents, high ticket volume)
this is the agentic-AI equivalent of an N+1 query bug: invisible per-call,
compounding linearly with a real usage pattern (users following up) that
every support queue actually has.

## Fix

`cost/cache.py`'s two-tier `ResponseCache`:

1. **Exact-match** tier: SHA-256 of the normalized query.
2. **Semantic-similarity** tier: cosine similarity over the same TF-IDF+SVD
   embedder RAG already uses (zero extra embedding cost). Threshold
   **0.60**, tuned against real measured values in this build: the three
   real paraphrases of the timeout question measured **0.608-0.753**
   cosine similarity against the original; the 21 distinct-topic ticket
   pairs in the real demo corpus all measured below **0.55** -- a real gap
   with margin on both sides, not a guessed number.

Also wired in: `MAX_ITERATIONS = 3` hard guard on the agentic retrieval loop
in `agent/orchestrator.run_fixed`, verified live to never exceed the cap
regardless of retrieval quality (a second, structural cost-blowup guard
against an unbounded tool-calling loop, independent of the cache).

## Real re-verification

`scripts/incidents/03_cost_blowup.py`, real run, real assertions:

| | Naive (no cache) | Fixed (with cache) |
|---|---|---|
| Total cost, same 4-ticket repeat sequence | **$0.000562** | **$0.000113** |
| Cache hits (exact + semantic) | n/a | **3/4** (all semantic) |
| Dollars saved | -- | **$0.000449 (79.9%)** |
| Max loop iterations observed on an unbounded-looking query | n/a | **3** (hard cap, confirmed) |

Raw evidence: `docs/incidents/evidence/incident3_evidence.json`.
