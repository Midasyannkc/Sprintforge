"""Renders a real architecture diagram image (matplotlib, boxes + arrows) for
the executive summary deck: client request -> agent orchestrator ->
RAG/retrieval -> safety/cost layer -> LLM -> eval/observability -> HITL
queue -> response.
"""
import os

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "architecture_diagram.png")

BOXES = [
    # (x, y, w, h, label, color)
    (0.5, 8.6, 3.0, 0.9, "Client request\n(support ticket)", "#4C6EF5"),
    (0.5, 7.0, 3.0, 0.9, "Agent orchestrator\ntool-calling loop\nMAX_ITERATIONS guard", "#5C7CFA"),
    (0.5, 5.4, 3.0, 0.9, "Safety layer\ninjection detector\nPII redaction", "#F76707"),
    (4.2, 5.4, 3.0, 0.9, "RAG / retrieval\nreal Chroma index\nTF-IDF+SVD embed", "#12B886"),
    (4.2, 7.0, 3.0, 0.9, "Cost layer\nresponse cache\ncheap-first router", "#F59F00"),
    (7.9, 6.2, 3.0, 0.9, "LLM\n(LLMClient interface\nBedrock production target)", "#7048E8"),
    (7.9, 4.4, 3.0, 0.9, "Grounding check\n(refuse if ungrounded)", "#E64980"),
    (4.2, 3.0, 3.0, 0.9, "Eval / observability\nMLflow-tracked runs", "#495057"),
    (0.5, 1.4, 3.0, 0.9, "HITL queue\nSQLite, real CLI + API", "#C92A2A"),
    (7.9, 1.4, 3.0, 0.9, "Response to client\n(triage answer)", "#2F9E44"),
]

ARROWS = [
    (2.0, 8.6, 2.0, 7.9),      # client -> orchestrator
    (2.0, 7.0, 2.0, 6.3),      # orchestrator -> safety
    (3.5, 5.85, 4.2, 5.85),    # safety -> RAG
    (5.7, 6.3, 5.7, 7.0),      # RAG -> cost layer
    (7.2, 7.45, 7.9, 6.9),     # cost layer -> LLM
    (9.4, 6.2, 9.4, 5.3),      # LLM -> grounding check
    (7.9, 4.6, 5.7, 3.9),      # grounding check -> eval
    (4.2, 3.45, 2.0, 3.45),    # eval -> (down to) HITL, via mid arrow below
    (2.0, 3.45, 2.0, 2.3),     # eval-ish -> HITL
    (9.4, 4.4, 9.4, 2.3),      # grounding check -> response (grounded path)
    (2.0, 1.4, 2.0, 0.75),
    (2.0, 0.75, 7.9, 0.75),
    (7.9, 0.75, 7.9, 1.4),     # HITL -> response (after human resolves)
]


def build():
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("SprintForge: Support/Triage Agent Accelerator Architecture", fontsize=15, fontweight="bold", pad=15)

    for x, y, w, h, label, color in BOXES:
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.06,rounding_size=0.08",
            linewidth=1.5, edgecolor=color, facecolor=color, alpha=0.18,
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=9.5, color="#1a1a1a", fontweight="medium")

    for x0, y0, x1, y1 in ARROWS:
        arrow = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=14, linewidth=1.3, color="#495057")
        ax.add_patch(arrow)

    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=180, facecolor="white")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    build()
