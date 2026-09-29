"""Human-in-the-loop escalation queue, backed by a real local SQLite file --
the same pattern this author has used on Undercurrent, Trustline and
Bulkhead. Every safety/cost decision in this project that decides NOT to
auto-answer (injection flagged, ungrounded/low-confidence answer, cost-policy
escalation, PII found) writes here instead of silently guessing or dropping.
A human resolves each item with approve_hitl.py before it can affect
anything downstream; nothing here auto-resolves itself.
"""
import json
import os
import sqlite3
import time
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "exports", "hitl_queue.db")


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hitl_items (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            reason TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at REAL NOT NULL,
            resolved_at REAL,
            resolution TEXT
        )
    """)
    return conn


def escalate(source: str, reason: str, payload: dict) -> str:
    item_id = str(uuid.uuid4())[:8]
    conn = _conn()
    conn.execute(
        "INSERT INTO hitl_items (id, source, reason, payload, status, created_at) "
        "VALUES (?, ?, ?, ?, 'pending', ?)",
        (item_id, source, reason, json.dumps(payload), time.time()),
    )
    conn.commit()
    conn.close()
    return item_id


def list_pending():
    conn = _conn()
    rows = conn.execute(
        "SELECT id, source, reason, payload, created_at FROM hitl_items WHERE status='pending' "
        "ORDER BY created_at ASC"
    ).fetchall()
    conn.close()
    return [
        {"id": r[0], "source": r[1], "reason": r[2], "payload": json.loads(r[3]), "created_at": r[4]}
        for r in rows
    ]


def resolve(item_id: str, resolution: str) -> bool:
    """resolution: 'approved' or 'rejected'"""
    conn = _conn()
    conn.execute(
        "UPDATE hitl_items SET status='resolved', resolved_at=?, resolution=? WHERE id=?",
        (time.time(), resolution, item_id),
    )
    conn.commit()
    changed = conn.total_changes
    conn.close()
    return changed > 0


def stats() -> dict:
    conn = _conn()
    rows = conn.execute("SELECT status, COUNT(*) FROM hitl_items GROUP BY status").fetchall()
    conn.close()
    return dict(rows)
