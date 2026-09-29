# Data Source Disclosure

## Real data

**Source:** [`psf/requests`](https://github.com/psf/requests) — the real, widely-used
Python HTTP library (Apache-2.0, ~52k GitHub stars). SprintForge's demo scenario is a
support/triage agent a Robots & Pencils client engagement would build for a project like
this one: a real open-source (or client) codebase with real user-facing documentation
that a triage agent must answer questions from, grounded, not guessed.

**Exact files fetched, real, verbatim, via `raw.githubusercontent.com` (tested reachable
in this sandbox; see constraint note below), commit ref `main` on 2026-09-29:**

| File | Raw URL | Bytes |
|---|---|---|
| `README.md` | https://raw.githubusercontent.com/psf/requests/main/README.md | 2,906 |
| `HISTORY.md` | https://raw.githubusercontent.com/psf/requests/main/HISTORY.md | 64,563 |
| `docs/user/quickstart.rst` | https://raw.githubusercontent.com/psf/requests/main/docs/user/quickstart.rst | 19,213 |
| `docs/user/advanced.rst` | https://raw.githubusercontent.com/psf/requests/main/docs/user/advanced.rst | 41,903 |
| `docs/user/authentication.rst` | https://raw.githubusercontent.com/psf/requests/main/docs/user/authentication.rst | 5,854 |
| `docs/community/faq.rst` | https://raw.githubusercontent.com/psf/requests/main/docs/community/faq.rst | 3,745 |
| `docs/community/recommended.rst` | https://raw.githubusercontent.com/psf/requests/main/docs/community/recommended.rst | 2,174 |
| `docs/api.rst` | https://raw.githubusercontent.com/psf/requests/main/docs/api.rst | 7,333 |
| `docs/dev/contributing.rst` | https://raw.githubusercontent.com/psf/requests/main/docs/dev/contributing.rst | 6,584 |

Stored verbatim in `data/raw/`. This is the real corpus `rag/ingest.py` chunks and
`rag/embed.py` embeds. Every retrieval and grounding result reported in this repo's
README and `docs/incidents/` runs against this real text, not a paraphrase or a
hand-written summary of it.

## Constraint hit and disclosed: GitHub Issues REST API is unreachable in this sandbox

The JD-aligned original plan was to also ingest real GitHub Issues from `psf/requests`
via `GET /repos/psf/requests/issues`. Tested directly:

```
$ curl https://api.github.com/repos/psf/requests/issues?state=all&per_page=5
HTTP 403 — "GitHub access to this repository is not enabled for this session."
```

`api.github.com` is blocked wholesale in this build sandbox (confirmed via both direct
`curl` and the `WebFetch` tool — both returned 403; `codeload.github.com` and the
`github.com` HTML issue pages are blocked the same way). Only `raw.githubusercontent.com`
is reachable. This is disclosed here rather than silently worked around: the corpus below
is real README/docs text (the JD's own named fallback: "README, and docs"), not real
issues. No issue text in this repo is fabricated or presented as if it came from the
GitHub API.

## Synthetic, disclosed

- **Support tickets / user queries** (`data/tickets/tickets.json`): a fixed set of
  realistic support questions written for this demo (e.g. "how do I set a timeout on a
  request", "does requests verify SSL certificates by default"), styled on the kind of
  question a `requests` user actually asks in real issues and Stack Overflow threads, but
  **not copied from any real ticket or issue** — clearly synthetic, used only to drive the
  triage agent's retrieval and generation path. Includes two adversarial tickets
  (prompt-injection payloads, Incident 1) and one PII-bearing ticket (Incident 4), both
  also clearly synthetic and labeled as such in the file.
- **Cost/usage numbers** (token counts, per-token price, cache hit rate): token counts are
  computed for real over the real prompts this pipeline actually builds (not invented);
  the **per-token dollar price** used to convert that into a dollar figure is a disclosed
  assumption (Claude 3 Haiku-class list pricing as of this build, documented in
  `cost/token_counter.py`), since no live billing account exists in this sandbox.
- **AWS Bedrock, quantization**: documented at ADR level (`docs/adr/`) as the real
  production target/lever, not run live — no AWS credentials exist in this sandbox. See
  `docs/adr/0001-bedrock-production-target.md` and `docs/adr/0003-quantization.md`.

## Embedding model constraint, disclosed

`huggingface.co` is also blocked in this sandbox (`curl` and `WebFetch` both return a
proxy `403`), so a hosted `sentence-transformers` model download is not possible here.
`rag/embed.py` uses a local TF-IDF + TruncatedSVD embedding (scikit-learn, no network
dependency) — the same fallback this author used on Undercurrent for the same reason, and
disclosed there the same way.
