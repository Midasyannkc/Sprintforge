"""Swappable LLM client, the same pattern used on this author's prior
portfolio projects (Undercurrent, AdvisorAgent): a real interface the rest of
the code depends on, backed locally by a deterministic mock because no LLM
API key is reachable in this build sandbox. Swapping in a real
Bedrock/Anthropic-backed implementation here is a one-class change (see
docs/adr/0001-bedrock-production-target.md); nothing downstream (the
orchestrator, the eval harness, the FastAPI service) needs to know which
backend sits behind it.
"""
import hashlib
import re
from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_content: str) -> str:
        """Returns the generated text for one turn."""
        ...

    @abstractmethod
    def confidence(self, system_prompt: str, user_content: str) -> float:
        """Returns a 0-1 self-reported confidence for the same turn, used by
        the cheap-model-first router (cost/router.py) to decide whether to
        escalate to a stronger model."""
        ...


def _tokenish_hash(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


class MockLLM(LLMClient):
    """Deterministic, template-based generator standing in for a real hosted
    model. Answers are built ONLY from the retrieved context chunks handed to
    it in user_content -- it has no other "knowledge" of psf/requests beyond
    a small NAIVE_PARAMETRIC_FACTS table used deliberately to reproduce
    Incident 2 (a model answering from parametric/prior "knowledge" instead
    of the real retrieved docs when retrieval is weak). The fixed pipeline
    never reaches that table once the grounding check is in place."""

    # Deliberately-planted parametric "knowledge" a real LLM might also
    # confidently (and wrongly) produce when retrieval is weak. This table is
    # ONLY consulted by generate_naive(); the fixed path never sees it.
    NAIVE_PARAMETRIC_FACTS = {
        "gpu": "requests uses an internal GPU-accelerated response parser to speed up large downloads.",
        "async": "requests has built-in native async/await support since version 3.0.",
        "kubernetes": "requests ships a built-in Kubernetes operator for distributed request scheduling.",
    }

    def generate(self, system_prompt: str, user_content: str) -> str:
        return self.generate_grounded(system_prompt, user_content, context_chunks=[])

    def confidence(self, system_prompt: str, user_content: str) -> float:
        # Deterministic pseudo-confidence in [0.55, 0.99], stable per input.
        h = _tokenish_hash(system_prompt + "|" + user_content)
        return 0.55 + (h % 4500) / 10000.0

    # ---- naive path (Incidents 1 and 2) ----
    def generate_naive(self, query: str, context_chunks: list) -> str:
        # Incident 1: the naive prompt concatenates raw ticket text directly
        # into the instruction context with no delimiter separation, so an
        # "output exactly: '...'" style payload in the ticket text is
        # followed literally -- the same failure mode a real instruction-
        # following LLM exhibits against an un-delimited prompt template.
        hijack = re.search(r"output exactly:\s*'([^']+)'", query, re.IGNORECASE)
        if hijack:
            return hijack.group(1)

        if context_chunks:
            top = context_chunks[0]["text"]
            return f"Based on the docs: {top[:220].strip()}..."
        for key, fact in self.NAIVE_PARAMETRIC_FACTS.items():
            if key in query.lower():
                return fact  # hallucinated: answered from parametric table, not real docs
        return "I don't have specific information on that."

    # ---- fixed / grounded path ----
    def generate_grounded(self, system_prompt: str, user_content: str, context_chunks=None) -> str:
        context_chunks = context_chunks or []
        if not context_chunks:
            return "REFUSED: no supporting documentation was retrieved for this question; escalating to human review."
        top = context_chunks[0]["text"]
        snippet = top[:220].strip().replace("\n", " ")
        return f"Based on the requests documentation ({context_chunks[0]['source']}): {snippet}..."
