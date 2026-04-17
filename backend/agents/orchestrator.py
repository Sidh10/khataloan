"""
orchestrator.py
───────────────
LangGraph multi-agent orchestrator for KhataLoan.
Coordinates three pipelines in PARALLEL, then runs the reconstruction
and report agents in sequence.

Graph:
  parallel_ingest (ocr ‖ voice ‖ upi) → reconstruct → report → done

The three understanding pipelines execute concurrently via asyncio.gather,
matching our documented "Parallel Understanding" architecture.
"""

import asyncio
import time
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
    pipeline_timings: dict  # NEW: track per-pipeline latency


# ── Async pipeline wrappers ──────────────────────────────────
async def _run_ocr_async(ledger_images: list) -> list[Transaction]:
    """Run OCR pipeline in a thread (OpenAI calls are synchronous)."""
    return await asyncio.to_thread(run_ocr_pipeline, ledger_images)


async def _run_voice_async(voice_notes: list) -> list[Transaction]:
    """Run voice pipeline in a thread (Whisper + GPT calls are synchronous)."""
    return await asyncio.to_thread(run_voice_pipeline, voice_notes)


async def _run_upi_async(upi_screenshots: list) -> list[Transaction]:
    """Run UPI pipeline in a thread (GPT-4o Vision calls are synchronous)."""
    return await asyncio.to_thread(run_upi_pipeline, upi_screenshots)


# ── Node functions ───────────────────────────────────────────
def node_parallel_ingest(state: PipelineState) -> PipelineState:
    """
    Run OCR, Voice, and UPI pipelines CONCURRENTLY using asyncio.gather.
    This replaces the previous sequential ocr → voice → upi chain
    and aligns with our documented 'Parallel Understanding' architecture.
    """
    async def _gather_pipelines():
        t_start = time.perf_counter()

        ocr_task   = _run_ocr_async(state["ledger_images"])
        voice_task = _run_voice_async(state["voice_notes"])
        upi_task   = _run_upi_async(state["upi_screenshots"])

        results = await asyncio.gather(
            ocr_task, voice_task, upi_task,
            return_exceptions=True,
        )

        t_elapsed = time.perf_counter() - t_start
        return results, t_elapsed

    # Get or create an event loop safely
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an existing async context (e.g. FastAPI)
        # Use nest_asyncio or run in a new thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            results, elapsed = pool.submit(
                lambda: asyncio.run(_gather_pipelines())
            ).result()
    else:
        results, elapsed = asyncio.run(_gather_pipelines())

    # Unpack results, handling any per-pipeline failures gracefully
    ocr_txns   = results[0] if not isinstance(results[0], Exception) else []
    voice_txns = results[1] if not isinstance(results[1], Exception) else []
    upi_txns   = results[2] if not isinstance(results[2], Exception) else []

    # Capture errors (if any pipeline failed, log but don't abort)
    errors = []
    for i, (name, res) in enumerate(zip(["ocr", "voice", "upi"], results)):
        if isinstance(res, Exception):
            errors.append(f"{name}_pipeline: {str(res)}")

    return {
        **state,
        "ocr_transactions": ocr_txns,
        "voice_transactions": voice_txns,
        "upi_transactions": upi_txns,
        "pipeline_timings": {
            "parallel_ingest_seconds": round(elapsed, 2),
            "pipelines_executed": 3,
            "errors": errors,
        },
        "error": "; ".join(errors) if errors else None,
    }


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

    # Single parallel-ingest node replaces sequential ocr → voice → upi
    graph.add_node("parallel_ingest", node_parallel_ingest)
    graph.add_node("reconstruct", node_reconstruct)
    graph.add_node("report", node_report)

    # parallel_ingest → reconstruct → report → END
    graph.set_entry_point("parallel_ingest")
    graph.add_edge("parallel_ingest", "reconstruct")
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
        update("parallel_ingest", 10, "Running OCR, Voice & UPI pipelines in parallel...")
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
            pipeline_timings={},
        )

        final_state = compiled_graph.invoke(initial_state)

        jobs[job_id].update({
            "status": "complete",
            "stage": "report",
            "progress": 100,
            "message": "Credit profile ready.",
            "result": final_state["credit_report"],
            "pdf_path": final_state["pdf_path"],
            "pipeline_timings": final_state.get("pipeline_timings", {}),
        })

    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "stage": "error",
            "progress": 0,
            "message": str(e),
        })
