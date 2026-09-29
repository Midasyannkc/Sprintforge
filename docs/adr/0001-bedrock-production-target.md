# ADR-0001: AWS Bedrock as the real production LLM target

## Status
Accepted (documented, not runnable in this sandbox -- no live AWS credentials exist here).

## Context
The JD names AWS + AWS GenAI offerings specifically. SprintForge's `LLMClient`
interface (`agent/llm_client.py`) is deliberately backed by a deterministic
`MockLLM` for this build because no LLM API key is reachable in this sandbox.
The interface boundary is designed so that swapping in a real backend is a
single new class, not an architecture change.

## Decision
Production target: **Amazon Bedrock**, via a `BedrockLLMClient(LLMClient)`
implementation that calls `bedrock-runtime` `InvokeModel`/`Converse`, most
likely against an Anthropic Claude model on Bedrock for the generation and
confidence-scoring calls this project's `LLMClient.generate()` /
`LLMClient.confidence()` methods expose. Bedrock is chosen over calling a
model provider's API directly because:

- it sits inside the client's own AWS account and VPC, which matches how a
  30-45 day Robots & Pencils client engagement would actually need to deploy
  (client-owned data boundary, client-owned billing, client IAM policy
  control over which model families are enabled) -- see the README's
  "Business solution" section;
- Bedrock Guardrails gives a second, managed layer for PII/content filtering
  that composes with (not replaces) this project's own
  `safety/pii.py`/`safety/injection_detector.py`, the same defense-in-depth
  principle already used for prompt injection;
- token-level usage/cost is emitted directly in the Bedrock response
  metadata, which `cost/token_counter.py`'s real token-counting logic is
  written to consume once a live client is swapped in (today it counts real
  tokens over the real prompt text with a disclosed assumed price instead).

## Consequences
- Every real number in this repo's `docs/incidents/` and README that would
  ordinarily come from live model calls (latency, cost) is instead computed
  from the real prompt/response text this pipeline actually builds, with an
  explicitly disclosed price assumption (see `cost/token_counter.py`,
  `data/SOURCE_DISCLOSURE.md`). Swapping in `BedrockLLMClient` does not
  change any downstream code -- `agent/orchestrator.py`,
  `eval/eval_harness.py`, and `api/main.py` all depend on `LLMClient`, never
  on `MockLLM` directly.
- IAM/VPC/model-access setup itself is out of scope for this sandbox build
  and is not asserted as done.
