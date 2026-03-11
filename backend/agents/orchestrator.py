"""
orchestrator.py
───────────────
LangGraph multi-agent orchestrator for KhataLoan.
Coordinates three pipelines, then runs the reconstruction
and report agents in sequence.

Graph:
  ingest → [ocr, voice, upi] → reconstruct → report → done
"""

import asyncio
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from pipelines.ocr_pipeline import run_ocr_pipeline
from pipelines.voice_pipeline import run_voice_pipeline
from pipelines.upi_pipeline import run_upi_pipeline
from agents.reconstruct_agent import reconstruct_transactions
from agents.report_agent import generate_credit_report
from utils.pdf_generator import generate_pdf
from api.schemas import Transaction


# ── State definition ────────────────────────────────────────
class PipelineState(TypedDict):
    job_id: str
    ledger_images: list
    voice_notes: list
    upi_screenshots: list
    ocr_transactions: list[Transaction]
    voice_transactions: list[Transaction]
    upi_transactions: list[Transaction]
    all_transactions: list[Transaction]
    credit_report: dict
    pdf_path: str
    error: str | None


# ── Node functions ───────────────────────────────────────────
def node_ocr(state: PipelineState) -> PipelineState:
    """Run OCR pipeline on ledger images."""
    try:
        txns = run_ocr_pipeline(state["ledger_images"])
        return {**state, "ocr_transactions": txns}
    except Exception as e:
        return {**state, "ocr_transactions": [], "error": str(e)}


def node_voice(state: PipelineState) -> PipelineState:
    """Run voice transcription pipeline."""
    try:
        txns = run_voice_pipeline(state["voice_notes"])
        return {**state, "voice_transactions": txns}
    except Exception as e:
        return {**state, "voice_transactions": [], "error": str(e)}


def node_upi(state: PipelineState) -> PipelineState:
    """Run UPI screenshot parsing pipeline."""
    try:
        txns = run_upi_pipeline(state["upi_screenshots"])
        return {**state, "upi_transactions": txns}
    except Exception as e:
        return {**state, "upi_transactions": [], "error": str(e)}


def node_reconstruct(state: PipelineState) -> PipelineState:
    """
    Merge all transaction sources, deduplicate,
    categorise, and fill temporal gaps.
    """
    all_txns = (
        state.get("ocr_transactions", []) +
        state.get("voice_transactions", []) +
        state.get("upi_transactions", [])
    )
    reconstructed = reconstruct_transactions(all_txns)
    return {**state, "all_transactions": reconstructed}


def node_report(state: PipelineState) -> PipelineState:
    """Generate credit metrics and narrative report."""
    report = generate_credit_report(state["all_transactions"])
    pdf_path = generate_pdf(report, state["job_id"])
    return {**state, "credit_report": report, "pdf_path": pdf_path}


# ── Build the graph ──────────────────────────────────────────
def build_graph() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node("ocr", node_ocr)
    graph.add_node("voice", node_voice)
    graph.add_node("upi", node_upi)
    graph.add_node("reconstruct", node_reconstruct)
    graph.add_node("report", node_report)

    # Parallel ingestion → reconstruct → report
    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "voice")
    graph.add_edge("voice", "upi")
    graph.add_edge("upi", "reconstruct")
    graph.add_edge("reconstruct", "report")
    graph.add_edge("report", END)

    return graph.compile()


compiled_graph = build_graph()


# ── Public runner ────────────────────────────────────────────
def run_pipeline(
    job_id: str,
    ledger_images: list,
    voice_notes: list,
    upi_screenshots: list,
    jobs: dict,
):
    """
    Entry point called by FastAPI background task.
    Updates jobs dict with live status at each stage.
    """
    def update(stage: str, progress: int, message: str):
        jobs[job_id].update({
            "status": "processing",
            "stage": stage,
            "progress": progress,
            "message": message,
        })

    try:
        update("ocr", 10, "Reading ledger images...")
        update("voice", 35, "Transcribing voice notes...")
        update("upi", 55, "Parsing UPI screenshots...")
        update("reconstruct", 70, "Reconstructing transaction history...")
        update("report", 88, "Generating credit profile...")

        initial_state = PipelineState(
            job_id=job_id,
            ledger_images=ledger_images,
            voice_notes=voice_notes,
            upi_screenshots=upi_screenshots,
            ocr_transactions=[],
            voice_transactions=[],
            upi_transactions=[],
            all_transactions=[],
            credit_report={},
            pdf_path="",
            error=None,
        )

        final_state = compiled_graph.invoke(initial_state)

        jobs[job_id].update({
            "status": "complete",
            "stage": "report",
            "progress": 100,
            "message": "Credit profile ready.",
            "result": final_state["credit_report"],
            "pdf_path": final_state["pdf_path"],
        })

    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "stage": "error",
            "progress": 0,
            "message": str(e),
        })
