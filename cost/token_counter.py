"""Real token counting over the real prompt strings this pipeline actually
builds (not invented after the fact). Uses tiktoken's cl100k_base encoding
(a real, widely-used tokenizer) when available; falls back to a disclosed
chars/4 proxy if tiktoken can't load in this environment.

Dollar pricing is a disclosed ASSUMPTION (no live billing account exists in
this sandbox): Claude 3 Haiku-class list pricing as of this build --
$0.25 / 1M input tokens, $1.25 / 1M output tokens -- used consistently
everywhere a dollar figure is reported in this repo.
"""
PRICE_PER_1K_INPUT = 0.00025
PRICE_PER_1K_OUTPUT = 0.00125

try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        return len(_ENC.encode(text))
except Exception:
    def count_tokens(text: str) -> int:
        return max(1, len(text) // 4)


def estimate_cost(input_text: str, output_text: str = "") -> float:
    in_tok = count_tokens(input_text)
    out_tok = count_tokens(output_text)
    return (in_tok / 1000.0) * PRICE_PER_1K_INPUT + (out_tok / 1000.0) * PRICE_PER_1K_OUTPUT


if __name__ == "__main__":
    sample = "How do I set a timeout on a requests.get call so it doesn't hang forever?"
    print(count_tokens(sample), "tokens")
    print(f"${estimate_cost(sample, 'Based on the docs: ...'):.6f}")
