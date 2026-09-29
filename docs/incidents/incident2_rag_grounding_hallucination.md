# Incident 2: RAG pipeline answers confidently from ungrounded retrieval

**JD line addressed:** "Building and optimizing RAG pipelines" +
"understanding of AI safety, responsible AI practices."

## What happened

Chroma's `collection.query()` always returns its top-`k` nearest neighbors,
even when none of them are actually relevant to the question -- there is no
natural "empty result" signal with a fixed `k`. The naive pipeline
(`agent/orchestrator.run_naive`) never checks the real similarity score
before presenting the top chunk as a confident answer.

Run against two real, genuinely off-corpus tickets (`data/tickets/tickets.json`,
category `weak_retrieval`) -- misrouted-sounding questions the real 13-incident
AIID corpus (`data/SOURCE_DISCLOSURE.md`) says nothing about:

- **T008**, "...what is the average rainfall in the Amazon rainforest during
  monsoon season?" -- real top-retrieved-chunk similarity **0.000** (an
  entirely unrelated chunk, the Boeing 737 MAX MCAS incident record),
  presented confidently as `"Based on the docs: ...Boeing 737 MAX MCAS
  Crashes..."`.
- **T009**, "...what's the recommended tire pressure for a mountain bike on
  gravel trails?" -- real similarity **0.000**, again the unrelated Boeing
  MCAS chunk presented as if it answered the bike-tire question.

Real result: **2/2** weak-retrieval queries confidently answered from a
completely unrelated retrieved chunk, with no hedge or refusal.

**A second, worse variant was also confirmed directly**: `MockLLM.generate_naive`
has a small planted parametric-fact table (`NAIVE_PARAMETRIC_FACTS`) it falls
back to on a *genuinely* empty retrieval result -- called directly with
`context_chunks=[]` on a query about "quantum-computing-related AI
incidents", it fabricates `"The AI Incident Database has documented over 200
confirmed quantum-computing-related AI training failures"` outright, a clean
hallucination with no retrieved support at all and a real-sounding but
entirely made-up statistic.

## Why it's dangerous

This is the generative-AI equivalent of a data pipeline silently joining the
wrong row: syntactically fine output, semantically false, and nothing about
the response looks obviously broken to a downstream consumer or a
risk/compliance reviewer skimming a transcript -- especially dangerous here,
where the whole point of the agent is to be a trustworthy source on real
documented AI harms.

## Fix

`safety/grounding.py`'s `is_grounded()` checks the real top-retrieval
similarity against a threshold **tuned against real measured values in this
build**: the 7 real on-topic queries in the golden set measured
**0.758-0.968** cosine similarity; the two genuinely off-corpus queries above
measured **0.000** -- a wide, real gap, not a guessed number.
`GROUNDING_THRESHOLD = 0.50` sits in that gap. Below it,
`agent/orchestrator.run_fixed` refuses to answer and escalates to HITL
instead of generating.

## Real re-verification

`scripts/incidents/02_rag_grounding.py`, real run, real assertions:

| | Naive | Fixed |
|---|---|---|
| Weak-retrieval queries answered from an unrelated chunk | **2/2** | 0/2 |
| Weak-retrieval queries correctly refused/escalated | 0/2 | **2/2** |
| On-topic queries still answered normally (not over-blocked) | 7/7 | **7/7** |

The MLflow-tracked eval harness (`eval/eval_harness.py`) confirms this holds
across the full 15-ticket golden set: `groundedness_rate` **0.846 -> 1.00**
(naive -> fixed), fixed strictly >= naive, asserted in code, not just
reported once.

Raw evidence: `docs/incidents/evidence/incident2_evidence.json`,
`docs/incidents/evidence/eval_harness_results.json`.
