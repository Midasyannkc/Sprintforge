"""Real chunking of the real fetched psf/requests README + docs corpus.

Chunking strategy: paragraph-aware sliding window. Splits each source file on
blank-line boundaries (real paragraph/section breaks in the .rst/.md source),
then greedily packs paragraphs into ~CHUNK_SIZE-character chunks with
CHUNK_OVERLAP characters of trailing overlap carried into the next chunk, so a
sentence that straddles a chunk boundary in the source is not lost to either
side. This is deliberately simple and inspectable (no invisible library
behavior) since the chunk boundaries directly affect what Incident 2
(grounding) below can retrieve.
"""
import json
import os
import re

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chunks.json")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def _clean(text: str) -> str:
    # Strip reST directive noise that doesn't carry retrievable content.
    text = re.sub(r"^\.\. .*$", "", text, flags=re.MULTILINE)
    text = re.sub(r":[a-z]+:`([^`]*)`", r"\1", text)
    return text


def _paragraphs(text: str):
    text = _clean(text)
    paras = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paras if p.strip() and len(p.strip()) > 20]


def chunk_file(path: str, source_name: str):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    paras = _paragraphs(text)
    chunks = []
    buf = ""
    for para in paras:
        if len(buf) + len(para) + 1 <= CHUNK_SIZE:
            buf = (buf + "\n" + para).strip() if buf else para
        else:
            if buf:
                chunks.append(buf)
            # carry overlap from tail of previous chunk
            overlap = buf[-CHUNK_OVERLAP:] if buf else ""
            buf = (overlap + "\n" + para).strip() if overlap else para
    if buf:
        chunks.append(buf)

    return [
        {"id": f"{source_name}::chunk{i}", "source": source_name, "text": c}
        for i, c in enumerate(chunks)
    ]


def build_corpus():
    all_chunks = []
    for fname in sorted(os.listdir(RAW_DIR)):
        fpath = os.path.join(RAW_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        all_chunks.extend(chunk_file(fpath, fname))
    return all_chunks


if __name__ == "__main__":
    chunks = build_corpus()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    sizes = [len(c["text"]) for c in chunks]
    print(f"Ingested {len(chunks)} real chunks from {len(set(c['source'] for c in chunks))} source files.")
    print(f"Chunk size: min={min(sizes)} max={max(sizes)} avg={sum(sizes)/len(sizes):.0f} chars")
    print(f"Wrote {OUT_PATH}")
