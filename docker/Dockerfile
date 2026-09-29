FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent/ agent/
COPY rag/ rag/
COPY eval/ eval/
COPY cost/ cost/
COPY safety/ safety/
COPY hitl/ hitl/
COPY api/ api/
COPY data/raw/ data/raw/
COPY data/tickets/ data/tickets/

# Build-time real data pipeline: chunk the real corpus, fit the real
# embedder, build the real Chroma index -- so the image is self-contained
# and doesn't need a build step at container start.
RUN python3 -m rag.ingest && python3 -m rag.embed && python3 -m rag.build_index

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
