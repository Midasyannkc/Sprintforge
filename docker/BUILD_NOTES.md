# Docker build notes

Real commands, not run in this sandbox (see `docs/adr/0002-docker-k8s-validation-constraint.md`
for why): the daemon cannot be started here, confirmed live.

```bash
# from the repository root
docker build -f docker/Dockerfile -t sprintforge:latest .
docker run -p 8000:8000 sprintforge:latest
curl localhost:8000/health
curl -X POST localhost:8000/triage -H 'content-type: application/json' \
  -d '{"text": "Has predictive policing software been found to have racial bias issues?"}'
```

The image builds the real RAG index (`rag.ingest` -> `rag.embed` ->
`rag.build_index`) at build time so it is self-contained at run time; no
network access is required inside the container.
