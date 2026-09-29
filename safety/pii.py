"""Real PII detection + redaction, run on ingested ticket text BEFORE it
reaches the LLM context or any log line (Incident 4). Pattern-based, no
external service, deterministic and testable."""
import re

PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}


def detect_pii(text: str) -> dict:
    found = {}
    for label, pattern in PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            found[label] = matches
    return found


def redact_pii(text: str) -> tuple[str, dict]:
    """Returns (redacted_text, found_pii). Every match is replaced with a
    typed placeholder so the redaction itself is auditable in logs without
    the underlying value ever appearing."""
    found = detect_pii(text)
    redacted = text
    for label, pattern in PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED_{label.upper()}]", redacted)
    return redacted, found


if __name__ == "__main__":
    sample = "Hi, my name is Daniel Reyes, email daniel.reyes1984@example-mail.com, phone 555-201-4488."
    red, found = redact_pii(sample)
    print(red)
    print(found)
