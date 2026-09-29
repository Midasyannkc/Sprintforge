# ADR-0003: Quantization as a documented production cost lever

## Status
Accepted (documented at ADR level, not runnable in this sandbox -- no GPU
and no locally-hosted model weights available here to quantize).

## Context
The JD names cost optimization explicitly, including quantization, alongside
token economics, caching, and model routing (all three of which SprintForge
implements and measures for real -- see `cost/token_counter.py`,
`cost/cache.py`, `cost/router.py`, and Incident 3). Quantization applies at a
different layer (the model weights themselves, for a self-hosted model),
which is out of scope to run for real in this sandbox: there is no GPU and
no locally-hosted model to quantize.

## Decision
Document quantization as the production lever a Robots & Pencils engagement
would evaluate whenever a client's volume or latency requirements justify
self-hosting rather than calling a hosted API (e.g. via Bedrock's custom
model import, or a self-managed vLLM/TGI deployment on EKS): INT8 or INT4
weight quantization trades a measured, bounded quality drop for a real
reduction in per-token compute cost and inference latency at high volume, the
same "cheap-by-default, escalate when needed" principle this project already
implements at the *request* level via `cost/router.py`'s cheap-model-first
routing (route.CONFIDENCE_FLOOR). The two levers compose: routing decides
*which* model tier answers a given request; quantization decides how cheaply
each tier itself can be served once self-hosted.

## Consequences
No quantized-vs-unquantized benchmark numbers are claimed in this repo --
only the token/cost/cache numbers that were actually measured (Incident 3,
`eval/eval_harness.py`) are reported as real. This ADR is the honest,
disclosed boundary of what "cost optimization, including quantization" means
in a sandbox with no GPU, consistent with this author's standing rule of not
asserting a result that wasn't actually run.
