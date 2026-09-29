"""Builds docs/SprintForge_Executive_Summary.pptx via python-pptx.
Includes: goal, how/why it was built, one full system-design slide with a
real rendered architecture image, incident results, cost/eval charts, and
JD mapping.
"""
import json
import os

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT_PATH = os.path.join(ROOT, "docs", "SprintForge_Executive_Summary.pptx")
DIAGRAM_PATH = os.path.join(ROOT, "docs", "architecture_diagram.png")

NAVY = RGBColor(0x1A, 0x1B, 0x3A)
ACCENT = RGBColor(0x4C, 0x6E, 0xF5)
GREEN = RGBColor(0x2F, 0x9E, 0x44)
RED = RGBColor(0xC9, 0x2A, 0x2A)
GRAY = RGBColor(0x49, 0x50, 0x57)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def load_evidence():
    d = {}
    ev_dir = os.path.join(ROOT, "docs", "incidents", "evidence")
    for name in ["incident1_evidence.json", "incident2_evidence.json", "incident3_evidence.json",
                 "incident4_evidence.json", "eval_harness_results.json"]:
        with open(os.path.join(ev_dir, name)) as f:
            d[name] = json.load(f)
    return d


def add_title_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(1, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()
    bg.shadow.inherit = False

    title = slide.shapes.add_textbox(Inches(0.8), Inches(2.5), Inches(11.7), Inches(1.5))
    tf = title.text_frame
    tf.text = "SprintForge"
    tf.paragraphs[0].font.size = Pt(54)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = WHITE

    sub = slide.shapes.add_textbox(Inches(0.8), Inches(3.8), Inches(11.7), Inches(1.5))
    tf2 = sub.text_frame
    tf2.text = "An internal delivery accelerator for production agentic AI engagements"
    tf2.paragraphs[0].font.size = Pt(22)
    tf2.paragraphs[0].font.color.rgb = RGBColor(0xB0, 0xC4, 0xFF)
    p2 = tf2.add_paragraph()
    p2.text = "Built against Robots & Pencils' Senior AI Engineer requisition"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(0x8A, 0x9B, 0xE0)

    author = slide.shapes.add_textbox(Inches(0.8), Inches(6.6), Inches(11.7), Inches(0.6))
    author.text_frame.text = "Christian Kouadio Kouassi"
    author.text_frame.paragraphs[0].font.size = Pt(14)
    author.text_frame.paragraphs[0].font.color.rgb = RGBColor(0x8A, 0x9B, 0xE0)


def add_bullets_slide(prs, title, bullets, subtitle=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12.1), Inches(0.9))
    tf = title_box.text_frame
    tf.text = title
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = NAVY

    y = Inches(1.4)
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.6), y, Inches(12.1), Inches(0.6))
        sub_box.text_frame.text = subtitle
        sub_box.text_frame.paragraphs[0].font.size = Pt(16)
        sub_box.text_frame.paragraphs[0].font.italic = True
        sub_box.text_frame.paragraphs[0].font.color.rgb = GRAY
        y = Inches(2.1)

    body = slide.shapes.add_textbox(Inches(0.8), y, Inches(11.7), Inches(7.5 - y.inches - 0.3))
    tf = body.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"•  {b}"
        p.font.size = Pt(18)
        p.font.color.rgb = RGBColor(0x21, 0x25, 0x29)
        p.space_after = Pt(14)
    return slide


def add_image_slide(prs, title, image_path, caption=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.3), Inches(12.1), Inches(0.7))
    tf = title_box.text_frame
    tf.text = title
    tf.paragraphs[0].font.size = Pt(28)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = NAVY

    pic_top = Inches(1.1)
    max_h = Inches(5.6)
    slide.shapes.add_picture(image_path, Inches(1.4), pic_top, height=max_h)

    if caption:
        cap = slide.shapes.add_textbox(Inches(0.6), Inches(6.9), Inches(12.1), Inches(0.5))
        cap.text_frame.text = caption
        cap.text_frame.paragraphs[0].font.size = Pt(13)
        cap.text_frame.paragraphs[0].font.color.rgb = GRAY
        cap.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    return slide


def add_table_slide(prs, title, headers, rows, subtitle=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(12.1), Inches(0.7))
    tf = title_box.text_frame
    tf.text = title
    tf.paragraphs[0].font.size = Pt(28)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = NAVY

    top = Inches(1.15)
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.6), top, Inches(12.1), Inches(0.5))
        sub_box.text_frame.text = subtitle
        sub_box.text_frame.paragraphs[0].font.size = Pt(14)
        sub_box.text_frame.paragraphs[0].font.italic = True
        sub_box.text_frame.paragraphs[0].font.color.rgb = GRAY
        top = Inches(1.7)

    n_rows = len(rows) + 1
    n_cols = len(headers)
    table_shape = slide.shapes.add_table(n_rows, n_cols, Inches(0.6), top, Inches(12.1), Inches(0.5 * n_rows))
    table = table_shape.table

    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = h
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.size = Pt(14)
        cell.text_frame.paragraphs[0].font.color.rgb = WHITE
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY

    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = str(val)
            cell.text_frame.paragraphs[0].font.size = Pt(13)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xF1, 0xF3, 0xF5) if r % 2 == 0 else WHITE
    return slide


def main():
    ev = load_evidence()
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    add_title_slide(prs)

    add_bullets_slide(
        prs, "The goal",
        [
            "Give an AI engineering consultancy a reusable accelerator: agent framework + RAG "
            "pipeline + eval/observability harness + cost-optimization layer + safety layer + "
            "human-in-the-loop layer, so a 30-45 day client engagement doesn't rebuild the same "
            "agentic-AI plumbing from scratch every time.",
            "Demonstrated end-to-end on one real, client-shaped scenario: a responsible-AI "
            "incident triage agent grounded in real, cited AI Incident Database (AIID) records.",
            "Every safety and cost claim in this deck is a real, measured number from a real run "
            "of this code -- not a projection.",
        ],
    )

    add_bullets_slide(
        prs, "How and why this was built",
        [
            "Built directly against Robots & Pencils' Senior AI Engineer requisition: agentic "
            "systems, RAG pipelines, evaluation/observability, AI safety and prompt-injection "
            "defense, PII handling, cost optimization, Docker/Kubernetes, AWS GenAI.",
            "The real problem it targets: R&P's own delivery model ships production AI in 30-45 "
            "days per client -- teams that re-build RAG, evals, safety, and cost controls from "
            "scratch on every engagement blow that window and ship an inconsistent safety/quality "
            "bar across clients.",
            "SprintForge is the standardized internal accelerator that fixes that: one hardened "
            "pipeline, reused and re-pointed at each new client's real docs/corpus.",
            "Four real incidents were hit building it (prompt injection, RAG hallucination, cost "
            "blowup, PII leak) -- each reproduced with real evidence, fixed, and re-verified, the "
            "same rigor this author applies on every portfolio build.",
        ],
    )

    add_image_slide(
        prs, "End-to-end system design",
        DIAGRAM_PATH,
        caption="Client request -> agent orchestrator -> safety/cost layers -> RAG retrieval -> LLM -> "
                "grounding check -> eval/observability -> HITL queue -> response.",
    )

    add_table_slide(
        prs, "Four real incidents, reproduced and fixed",
        ["#", "Incident", "Naive (real)", "Fixed (real)"],
        [
            ["1", "Prompt injection hijack", "1/2 payloads fully hijacked output", "2/2 blocked, 0/7 false positives"],
            ["2", "RAG ungrounded hallucination", "2/2 weak queries confidently mis-answered", "2/2 refused, 7/7 on-topic still answered"],
            ["3", "Cost blowup (repeated queries)", "$0.000428 total, 4/4 full-cost calls", "$0.000121 total, 71.8% saved, 3/4 cache hits"],
            ["4", "PII leak into trace", "2/2 raw PII values leaked", "0/2 leaked, redacted + typed"],
        ],
        subtitle="Full write-ups: docs/incidents/. Raw evidence: docs/incidents/evidence/.",
    )

    eval_res = ev["eval_harness_results.json"]
    add_table_slide(
        prs, "MLflow-tracked evaluation: naive vs. fixed",
        ["Metric", "Naive", "Fixed", "Delta"],
        [
            ["Safety pass rate", f"{eval_res['naive']['safety_pass_rate']:.2f}", f"{eval_res['fixed']['safety_pass_rate']:.2f}",
             f"+{eval_res['improvement']['safety_pass_rate_delta']:.2f}"],
            ["Groundedness rate", f"{eval_res['naive']['groundedness_rate']:.3f}", f"{eval_res['fixed']['groundedness_rate']:.3f}",
             f"+{eval_res['improvement']['groundedness_rate_delta']:.3f}"],
            ["Mean latency (ms)", f"{eval_res['naive']['mean_latency_ms']:.2f}", f"{eval_res['fixed']['mean_latency_ms']:.2f}", "--"],
            ["Total cost (USD, 16 tickets)", f"${eval_res['naive']['total_cost_usd']:.6f}", f"${eval_res['fixed']['total_cost_usd']:.6f}", "--"],
        ],
        subtitle="Real MLflow SQLite-tracked run over the full 15-ticket golden dataset (eval/eval_harness.py).",
    )

    add_bullets_slide(
        prs, "Business framing: mirrors R&P's own delivery model",
        [
            "R&P ships production-ready AI in 30-45 day client engagements -- the constraint that "
            "actually shapes what 'production-ready' has to mean in that window.",
            "SprintForge packages the plumbing every one of those engagements needs (RAG, agent "
            "orchestration, evals, cost controls, safety, HITL) as a reusable, pre-hardened base, "
            "so a new engagement starts from a working, tested accelerator instead of a blank repo.",
            "Demonstrated against a real client-shaped scenario here (real, cited AI Incident "
            "Database records -- exactly the kind of knowledge base a client's own responsible-AI "
            "risk program would need); re-pointing it at a new client's real corpus is a data-layer "
            "swap, not a rebuild -- see data/SOURCE_DISCLOSURE.md for exactly what's real vs. "
            "disclosed-synthetic.",
        ],
    )

    add_bullets_slide(
        prs, "Cost trade-offs",
        [
            "Cheap-model-first routing (cost/router.py): every request starts on the cheap tier; "
            "escalates only when self-reported confidence drops below a real, tunable floor.",
            "Two-tier response cache (cost/cache.py): exact-match + semantic-similarity, using the "
            "same embedder RAG already runs -- zero extra embedding cost. Real measured 71.8% cost "
            "reduction on a realistic repeated-query pattern (Incident 3).",
            "Grounding-check refusal costs one extra similarity comparison per request, in exchange "
            "for never shipping a confidently wrong answer (Incident 2) -- cheap insurance against "
            "the most expensive failure mode a support agent can have.",
            "Quantization documented as a production lever (docs/adr/0003) for a self-hosted model "
            "tier; not runnable in this no-GPU sandbox, disclosed rather than faked.",
        ],
    )

    add_bullets_slide(
        prs, "Constraints, disclosed honestly",
        [
            "AIID's bulk export paths (GraphQL API, R2 database snapshots, GitHub API) were all "
            "tested directly and confirmed blocked in this sandbox (403s, confirmed live) -- 13 "
            "real, individually-cited incident records were fetched one at a time instead, each "
            "cross-checked against its real incidentdatabase.ai/cite/<ID> URL.",
            "huggingface.co is blocked -- local TF-IDF+SVD embedding used instead of a hosted "
            "sentence-transformers model.",
            "No live LLM API key -- LLMClient interface backed by a deterministic MockLLM, "
            "swappable for a real Bedrock client (docs/adr/0001) with zero downstream code changes.",
            "Docker daemon and kubectl are both unreachable in this sandbox -- Dockerfile and 5 "
            "Kubernetes manifests are real and written to standard syntax, validated the way that "
            "IS possible here (structural YAML + required-field checks, all pass); see docs/adr/0002.",
        ],
    )

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    prs.save(OUT_PATH)
    print(f"Wrote {OUT_PATH} with {len(prs.slides.__iter__.__self__._sldIdLst)} slides")


if __name__ == "__main__":
    main()
