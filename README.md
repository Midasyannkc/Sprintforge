# SprintForge

An internal delivery accelerator for production agentic AI engagements: a
reusable agent framework + RAG pipeline + eval/observability harness +
cost-optimization layer + safety layer + human-in-the-loop layer, demonstrated
end-to-end on one real, client-shaped scenario: a **responsible-AI incident
triage and knowledge agent**, grounded in real, cited records from the
[AI Incident Database](https://incidentdatabase.ai) (AIID), the
industry-authoritative catalog of documented real-world AI system failures
and harms, built to mirror how an AI engineering consultancy shipping
production agentic systems in 30-45 day client engagements would actually
build and reuse this plumbing.

This README is written as an incident report: what was built, what broke
along the way, how each failure was actually reproduced and fixed with real
measured evidence (not described or asserted), and what it costs.

**[Executive Summary (PPTX)](docs/SprintForge_Executive_Summary.pptx)**

## Why this project exists

This repo was built directly against a real Senior AI Engineer job posting
(Robots & Pencils, $139,750-$188,125), an AI engineering consultancy whose
own words are "we ship production-ready AI in 30 to 45 days." That constraint
is the actual problem SprintForge solves: a consultancy re-building the same
agentic-AI plumbing (RAG, evals, safety, cost controls, human oversight) from
scratch on every client engagement blows that window and ships an
inconsistent safety/quality bar client to client. The JD named, specifically:
agentic systems end-to-end, AI-forward coding tools, AWS + AWS GenAI, AI
frameworks/orchestration, evaluation/observability tooling, AI
safety/responsible AI/prompt-injection defenses/PII handling, RAG pipelines
(chunking, embeddings, vector DB), API integration, cost optimization (token
economics, caching, model routing, quantization), and Docker/Kubernetes.
`data/SOURCE_DISCLOSURE.md` documents exactly what data is real and what is
disclosed-synthetic and why; every technical claim below was actually run,
not just described.

## Architecture

```
Client request (support ticket)
   |
   v
Agent orchestrator (agent/orchestrator.py)
   real tool-calling loop, MAX_ITERATIONS=3 hard guard
   |
   v
Safety layer (safety/)                RAG / retrieval (rag/)
   injection_detector.py  ---------->    real Chroma index, 37 real chunks
   pii.py (redact before context/log)    over 13 real, cited AIID incidents
                                          TF-IDF+SVD local embedding
   |                                        |
   v                                        v
Cost layer (cost/)  <----------------  (retrieved context)
   cache.py (exact + semantic hit)
   router.py (cheap-model-first)
   token_counter.py (real token counts)
   |
   v
LLM (agent/llm_client.py -- swappable LLMClient, MockLLM here, real Bedrock
     production target documented in docs/adr/0001)
   |
   v
Grounding check (safety/grounding.py) -- refuse + escalate if ungrounded
   |
   v
Eval / observability (eval/eval_harness.py) -- real MLflow-tracked runs
   |
   v
HITL queue (hitl/) -- real SQLite, real CLI (approve_hitl.py) + FastAPI
   |
   v
Response to client (api/main.py -- real FastAPI service)
```

Stack used for real, not just documented: Python, FastAPI, a real running
Chroma vector store, a real local TF-IDF+SVD embedder, a real SQLite-backed
HITL queue, and a real MLflow-tracked eval run. LLM calls are behind a
swappable `LLMClient` interface (`agent/llm_client.py`) backed locally by a
deterministic mock, because this build sandbox has no reachable LLM API key;
every incident below is reproduced at the architecture/prompt-design level,
which holds regardless of which model sits behind that interface in
production (`docs/adr/0001-bedrock-production-target.md`).

## Incidents

Each of these was reproduced for real (a real failure, with real measured
evidence) and fixed for real (re-verified, also with real measured
evidence). Full write-up and raw evidence file linked per incident.

| # | Incident | JD line it addresses | Real result |
|---|---|---|---|
| 1 | [Prompt injection hijack](docs/incidents/incident1_prompt_injection.md) | AI safety, prompt injection & defense mechanisms | Naive pipeline: **1/2** real injection payloads fully hijacked its exact output. Two-layer defense (delimiter separation + pattern detector): **2/2** blocked -> HITL, **0/7** false positives on benign tickets. |
| 2 | [RAG grounding / hallucination](docs/incidents/incident2_rag_grounding_hallucination.md) | Building/optimizing RAG pipelines; AI safety | Naive pipeline confidently answered **2/2** off-corpus queries from a completely unrelated retrieved chunk (real similarity 0.000), plus a confirmed deeper parametric-hallucination fallback on empty retrieval. Grounding check (real-tuned 0.50 threshold, real gap 0.000 vs 0.758-0.968): **2/2** correctly refused/escalated, **7/7** on-topic queries still answered normally. |
| 3 | [Cost blowup, repeated queries](docs/incidents/incident3_cost_blowup.md) | Cost optimization: token economics, caching, model routing, quantization | Naive, no cache: real **$0.000428** across 4 repeats of 1 real question. Two-tier cache (real 0.80 semantic threshold, tuned against real measured similarity) + MAX_ITERATIONS guard: real **$0.000121**, **71.8% saved**, 3/4 real cache hits. |
| 4 (bonus) | [PII leak into trace](docs/incidents/incident4_pii_leak.md) | AI safety / responsible AI: PII handling | Naive pipeline leaked **2/2** raw PII values (real-shaped email + phone) into its trace, confirmed by direct string search. Redaction before context/log: **0/2** leaked, typed-only detection retained for audit. |

Real MLflow-tracked evaluation over the full 15-ticket golden dataset
(`eval/eval_harness.py`, `docs/incidents/evidence/eval_harness_results.json`):
`safety_pass_rate` **0.50 -> 1.00**, `groundedness_rate` **0.846 -> 1.00**,
both asserted to strictly improve in the harness itself, not just reported
once.

## Business solution

SprintForge is the standardized accelerator a consultancy like Robots &
Pencils would keep across client engagements: one hardened agent framework
(orchestration + RAG + safety + cost + eval + HITL), demonstrated here on a
real client-shaped scenario (real, cited AI Incident Database records --
exactly the kind of knowledge base a client's own responsible-AI risk
program would need), and re-pointed at a new client's real corpus as a
data-layer swap
(`rag/ingest.py` + `rag/embed.py` + `rag/build_index.py` against a different
`data/raw/`), not a rebuild. The four incidents above are exactly the failure
classes a client engagement discovers in production if this plumbing isn't
already hardened going in, the gap this accelerator exists to close inside a
30-45 day window.

## Cost trade-offs

- **Cheap-model-first routing** (`cost/router.py`): every request starts on
  the cheap tier and only escalates when self-reported confidence drops below
  a real, tunable floor (`CONFIDENCE_FLOOR = 0.75`) -- see ADR discussion in
  `docs/adr/0003-quantization.md` for how this composes with a self-hosted
  model tier.
- **Two-tier response cache** over unconditional caching: exact-match first
  (free, zero risk of stale mismatch), semantic-similarity second, reusing
  RAG's own embedder (zero extra embedding cost) -- real measured 71.8% cost
  reduction on a realistic repeated-query pattern (Incident 3), not
  unconditionally applied to every request type.
- **Grounding-check refusal is gated, not free** -- it costs one extra
  similarity comparison per request, worth paying to never ship a confidently
  wrong answer (Incident 2), the most expensive failure mode a support agent
  can have in production.
- **MAX_ITERATIONS=3** on the agentic tool loop -- a hard, cheap structural
  guard against unbounded-loop cost blowup, independent of and complementary
  to the cache.
- **Local TF-IDF+SVD embedding over a hosted embedding API** -- zero marginal
  compute cost beyond what's already running, the right default until volume
  justifies a hosted/self-hosted alternative (also the only option reachable
  in this sandbox, disclosed in `data/SOURCE_DISCLOSURE.md`).
- **Quantization** documented as the next lever once self-hosting is
  justified (`docs/adr/0003-quantization.md`), not run here (no GPU in this
  sandbox, disclosed rather than faked).

## Repository layout

```
data/                    real AI Incident Database (AIID) records, disclosed-synthetic tickets, SOURCE_DISCLOSURE.md
rag/                      chunking, local embedding, real Chroma index + retrieval
agent/                    LLMClient interface + MockLLM, tool-calling orchestrator (naive vs fixed)
safety/                   injection detector, PII redaction, grounding check
cost/                     token counter, exact+semantic cache, cheap-first router
hitl/                     real SQLite-backed HITL queue + approve_hitl.py CLI
api/                      real FastAPI service (/triage, /hitl/queue, /hitl/{id}/resolve)
eval/                     golden dataset + MLflow-tracked eval harness
scripts/incidents/        one repro+fix script per incident, real assertions
scripts/                  architecture diagram + PPTX builders
docs/incidents/           one write-up + one real evidence file per incident
docs/adr/                 architecture decision records (Bedrock, quantization, Docker/K8s constraint)
docker/                   real Dockerfile + build notes
k8s/                      real Kubernetes manifests (Namespace, ConfigMap, PVC, Deployment, Service)
tests/                    real FastAPI TestClient test suite
docs/SprintForge_Executive_Summary.pptx   standalone executive summary deck
```

## Getting started

```bash
pip install -r requirements.txt

# build the real RAG pipeline
python3 -m rag.ingest
python3 -m rag.embed
python3 -m rag.build_index

# run the incidents (real repro + fix + assertions, in build order)
python3 -m scripts.incidents.01_prompt_injection
python3 -m scripts.incidents.02_rag_grounding
python3 -m scripts.incidents.03_cost_blowup
python3 -m scripts.incidents.04_pii_leak

# real MLflow-tracked eval run
python3 -m eval.eval_harness

# live API + tests
python3 -m pytest tests/test_api.py -v
uvicorn api.main:app --reload

# HITL review
python3 -m hitl.approve_hitl list
python3 -m hitl.approve_hitl resolve <item_id> approved
```

## Author

Christian Kouadio Kouassi
