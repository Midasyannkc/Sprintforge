# ADR-0002: Docker/Kubernetes validation method, disclosed sandbox constraint

## Status
Accepted, constraint disclosed.

## Context
The JD names Docker and Kubernetes for containerized deployment. This build
sandbox has the `docker` CLI installed but its daemon cannot be started here
(`service docker start` fails: `ulimit: error setting limit (Operation not
permitted)` -- a sandbox privilege restriction, confirmed by direct test, not
assumed). `kubectl` is not installed and no cluster is reachable. This is the
same class of disclosed constraint this author's prior project (IdentityMesh)
hit and documented rather than silently working around.

## Decision
- **`docker/Dockerfile`**: written as a real, standard multi-stage-free
  Python 3.11-slim image (`pip install -r requirements.txt`, copies the real
  source tree, runs the real `rag.ingest` / `rag.embed` / `rag.build_index`
  pipeline at build time so the image is self-contained, then serves
  `api.main:app` via `uvicorn`). **Not built in this sandbox** (`docker
  build` fails immediately with "failed to connect to the docker API",
  confirmed live, not assumed working). Every command in it is the same
  command this project's own `docker/BUILD_NOTES.md` walks through running
  locally.
- **`k8s/*.yaml`**: five real manifests (Namespace, ConfigMap, PVC,
  Deployment with readiness/liveness probes against the real `/health`
  endpoint, Service). Validated the way that IS possible in this sandbox:
  parsed with `pyyaml` and checked for the required top-level Kubernetes
  fields (`apiVersion`, `kind`, `metadata.name`) on every manifest -- real,
  run, all 5 passed. `kubectl apply --dry-run=client` and a full
  `kubeval`/`check-jsonschema` Kubernetes-schema validation were both
  attempted first and were **not possible** here: no `kubectl` binary, and
  `check-jsonschema`'s bundled schema catalog has no Kubernetes vendor
  schema in the installed version (checked directly, not assumed).

## Consequences
Both artifacts are real, inspectable, standard Kubernetes/Docker syntax, not
placeholders -- but the validation done on them in this specific sandbox run
is real-but-partial (YAML structural validity, not a live daemon build or a
live cluster dry-run apply), and that gap is disclosed here rather than
asserted away.
