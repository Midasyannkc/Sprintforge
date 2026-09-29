# Data Source Disclosure

## Correction note (read first)

An earlier version of this corpus used the real `psf/requests` open-source
library's README/docs as a generic RAG demo corpus. That was replaced: the
data now comes directly from Robots & Pencils' own industry — AI engineering
/ responsible enterprise-AI delivery — per an explicit correction. SprintForge's
demo scenario is now a **responsible-AI incident triage and knowledge agent**,
grounded in real, industry-authoritative documented AI incident reports, the
kind of knowledge base an R&P client engagement helping an enterprise
understand and triage AI-risk questions would actually need.

## Real data

**Source:** the [AI Incident Database](https://incidentdatabase.ai) (AIID),
maintained by the Responsible AI Collaborative
(`github.com/responsible-ai-collaborative/aiid`) — the real, citable,
industry-authoritative database of documented real-world AI system failures
and harms. This is squarely on-topic for an AI safety / responsible-AI
triage agent, and directly maps to the JD's "AI safety, responsible AI
practices" requirement.

**Exact real incidents fetched, real, individually cited, stored in
`data/raw/`:**

| File | AIID Incident ID | Title | Reported | Source URL |
|---|---|---|---|---|
| `aiid_incident_001.md` | 1 | YouTube Kids app presents inappropriate content | 2015 | https://incidentdatabase.ai/cite/1 |
| `aiid_incident_003.md` | 3 | Boeing 737 MAX MCAS crashes | 2018-2019 | https://incidentdatabase.ai/cite/3 |
| `aiid_incident_007.md` | 7 | Wikipedia vandalism-prevention bot loop | 2017 | https://incidentdatabase.ai/cite/7 |
| `aiid_incident_045.md` | 45 | Defamation via Google autocomplete | 2011-2018 | https://incidentdatabase.ai/cite/45 |
| `aiid_incident_054.md` | 54 | Predictive policing bias, PredPol | 2015 | https://incidentdatabase.ai/cite/54 |
| `aiid_incident_146.md` | 146 | Delphi AI ethics model, racially biased answers | 2021 | https://incidentdatabase.ai/cite/146 |
| `aiid_incident_248.md` | 248 | Automated license plate reader, wrongful detainment | 2018 | https://incidentdatabase.ai/cite/248 |
| `aiid_incident_486.md` | 486 | Synthesia AI video tool abused for pro-China disinformation | 2022 | https://incidentdatabase.ai/cite/486 |
| `aiid_incident_541.md` | 541 | ChatGPT produced false court citations (Mata v. Avianca) | 2023 | https://incidentdatabase.ai/cite/541 |
| `aiid_incident_579.md` | 579 | DALL-E stereotyping of non-cisgendered people | 2023 | https://incidentdatabase.ai/cite/579 |
| `aiid_incident_608.md` | 608 | UnitedHealth AI algorithm allegedly denies medical coverage | 2023 | https://incidentdatabase.ai/cite/608 |
| `aiid_incident_633.md` | 633 | AI image-editing tool inappropriately alters lawmaker's photo | 2024 | https://incidentdatabase.ai/cite/633 |
| `aiid_incident_661.md` | 661 | Leonardo AI platform allegedly used for nonconsensual deepfakes | 2024 | https://incidentdatabase.ai/cite/661 |

13 real, named, independently verifiable AI incidents, chosen to span a
realistic enterprise AI-risk range a responsible-AI triage agent needs to
answer questions about: algorithmic bias, safety-critical system failure,
LLM hallucination, generative-AI misuse/deepfakes, healthcare AI denial of
care, and autonomous-system feedback loops. Every fact in `data/raw/`
(incident ID, title, date, description, named systems/developers/deployers)
is real and independently checkable at the cited `incidentdatabase.ai/cite/<ID>`
URL — none of it is invented.

## Constraint hit and disclosed: bulk AIID export is unreachable in this sandbox

The original plan was to bulk-fetch AIID's full incident set via its public
GraphQL API or its published weekly database snapshot files. All three real,
documented bulk-access paths were tried directly and confirmed blocked by
this sandbox's egress policy, not assumed:

```
$ curl -X POST https://incidentdatabase.ai/api/graphql ...
  -> CONNECT tunnel failed, response 403 (agent-proxy: connect_rejected, organization policy)

$ curl https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/AIID_Excel_Export-....xlsx
  -> CONNECT tunnel failed, response 403 (agent-proxy: connect_rejected, organization policy)

$ curl https://api.github.com/repos/responsible-ai-collaborative/aiid
  -> HTTP 403 ("GitHub access to this repository is not enabled for this session")
```

The AIID GitHub repository itself was also checked directly and confirmed to
hold **no static incident data files** — the project's own README states the
data lives in a MongoDB database, synced to Algolia for search, not
committed to git as JSON/CSV.

**What was reachable and used instead:** individual, real AIID incident
report pages (`incidentdatabase.ai/cite/<ID>`) via the `WebFetch` tool, one
incident at a time. Each page was fetched with an explicit prompt to return
the incident's real ID, title, reported date(s), description, and named
parties. This is disclosed precisely: `WebFetch` converts the fetched page to
text and has a small model extract the requested fields per the prompt, so
the wording in `data/raw/` is not a byte-for-byte HTML scrape the way the
`raw.githubusercontent.com` files in this project's earlier iteration were.
The underlying facts (incident ID, title, date, description, named
systems/developers) are real and were cross-checked against the cited URL
for each of the 13 incidents used here — nothing in `data/raw/` was invented
or paraphrased from a non-AIID source.

## Synthetic, disclosed

- **Support/triage tickets** (`data/tickets/tickets.json`): a fixed set of
  realistic questions an enterprise client's risk/compliance team might ask
  a responsible-AI triage agent (e.g. "has predictive policing software been
  found to have bias issues", "can generative AI tools be misused to create
  deepfakes of real people"), styled on the kind of question this database
  is built to answer, but **not copied from any real client interaction** —
  clearly synthetic. Includes two adversarial tickets (prompt-injection
  payloads), one off-corpus/weak-retrieval pair, and one PII-bearing ticket,
  all labeled synthetic in the file.
- **Cost/usage numbers**: token counts are computed for real over the real
  prompts this pipeline actually builds; the per-token dollar price used to
  convert that into a dollar figure is a disclosed assumption (documented in
  `cost/token_counter.py`), since no live billing account exists in this
  sandbox.
- **AWS Bedrock, quantization**: documented at ADR level (`docs/adr/`) as
  the real production target/lever, not run live.

## Embedding model constraint, disclosed

`huggingface.co` is blocked in this sandbox (`curl` and `WebFetch` both
return a proxy 403), so a hosted `sentence-transformers` model download is
not possible here. `rag/embed.py` uses a local TF-IDF + TruncatedSVD
embedding (scikit-learn, no network dependency).
