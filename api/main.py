"""Real FastAPI service exposing the SprintForge triage agent -- the API
layer a Robots & Pencils-style engagement would actually ship an agent
behind. Wraps agent.orchestrator.run_fixed (the production path; run_naive
is intentionally not exposed here, it exists only for the incident repro
scripts) and hitl.hitl_queue for human review.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.orchestrator import run_fixed
from hitl.hitl_queue import list_pending, resolve

app = FastAPI(title="SprintForge Triage Agent", version="0.1.0")


class TicketIn(BaseModel):
    text: str


class ResolveIn(BaseModel):
    resolution: str  # "approved" or "rejected"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/triage")
def triage(ticket: TicketIn):
    result = run_fixed(ticket.text)
    return result


@app.get("/hitl/queue")
def hitl_queue():
    return {"pending": list_pending()}


@app.post("/hitl/{item_id}/resolve")
def hitl_resolve(item_id: str, body: ResolveIn):
    if body.resolution not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="resolution must be 'approved' or 'rejected'")
    ok = resolve(item_id, body.resolution)
    if not ok:
        raise HTTPException(status_code=404, detail="item not found")
    return {"id": item_id, "resolution": body.resolution}
