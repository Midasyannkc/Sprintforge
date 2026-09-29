"""Cheap-model-first routing policy: every query is first answered by the
cheap tier; only escalated to the expensive tier when the cheap tier's
self-reported confidence (LLMClient.confidence) is below CONFIDENCE_FLOOR.
Both tiers are the same MockLLM in this sandbox (no live model access), with
disclosed different simulated per-token prices, so the routing DECISION and
its real measured effect on total cost are real even though the underlying
model weights are not swappable live here -- see
docs/adr/0003-quantization.md for the related quantization lever, which is
the same "cheap-by-default, escalate when needed" idea applied at the model
level instead of the request level.
"""
from cost.token_counter import count_tokens

CONFIDENCE_FLOOR = 0.75

# Disclosed simulated per-1K-token prices, cheap vs. capable tier (same
# Haiku-class baseline as cost/token_counter.py for the cheap tier; a
# Sonnet-class multiplier for the capable tier).
CHEAP_PRICE_PER_1K = 0.00025
CAPABLE_PRICE_PER_1K = 0.003


def route(system_prompt: str, user_content: str, llm_client) -> dict:
    conf = llm_client.confidence(system_prompt, user_content)
    tier = "cheap" if conf >= CONFIDENCE_FLOOR else "capable"
    tokens = count_tokens(system_prompt + user_content)
    price = CHEAP_PRICE_PER_1K if tier == "cheap" else CAPABLE_PRICE_PER_1K
    est_cost = (tokens / 1000.0) * price
    return {"tier": tier, "confidence": conf, "tokens": tokens, "est_cost": est_cost}
