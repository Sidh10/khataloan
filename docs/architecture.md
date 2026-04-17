# KhataLoan — Architecture Documentation

## Overview

KhataLoan uses a **multi-stage multimodal pipeline** orchestrated by a LangGraph agent.
The system accepts three types of financial artifacts, processes them in parallel,
reconstructs a unified transaction history, and generates a bank-ready credit profile.

---

## Pipeline Stages

### Stage 1 — Artifact Ingestion
- **Endpoint:** `POST /api/v1/upload`
- Files are received and stored in memory (not persisted without consent)
- A background job is created and a `job_id` is returned immediately
- Client polls `GET /api/v1/status/{job_id}` for live progress

### Stage 2 — Parallel Understanding (Three Pipelines)

#### 2A. OCR Pipeline (`pipelines/ocr_pipeline.py`)
1. OpenCV preprocessing: deskew, denoise, CLAHE contrast enhancement
2. GPT-4o Vision: reads handwritten text in any script
3. Structured extraction: `{date, party, amount, type, notes, confidence}`

#### 2B. Voice Pipeline (`pipelines/voice_pipeline.py`)
1. OpenAI Whisper: transcribes audio in detected language (auto-detect)
2. GPT-4o: extracts financial intent from natural speech
3. Handles spoken numbers: "paanch sau" → 500, "ek hazaar" → 1000

#### 2C. UPI Pipeline (`pipelines/upi_pipeline.py`)
1. GPT-4o Vision: reads UPI app screenshot
2. Extracts: amount, party, date, transaction ID, type

### Stage 3 — Reconstruction Agent (`agents/reconstruct_agent.py`)
1. **Merge:** Combine all three transaction streams
2. **Deduplicate:** Remove same transaction appearing in multiple sources
3. **Categorise:** Label each transaction (sales/inventory/labour/utilities/other)
4. **Flag gaps:** Identify missing months or anomalous patterns

### Stage 4 — Report Agent (`agents/report_agent.py`)
1. Compute financial metrics (DSCR, monthly averages, credit score)
2. Generate plain-English narrative via GPT-4o
3. Create PDF via ReportLab

---

## LangGraph Agent Graph

```
START
  │
  ▼
[node_ocr] ──▶ [node_voice] ──▶ [node_upi]
                                     │
                                     ▼
                              [node_reconstruct]
                                     │
                                     ▼
                               [node_report]
                                     │
                                    END
```

> **Note:** Nodes run sequentially in this implementation for simplicity.
> In production, `ocr`, `voice`, and `upi` nodes would run in parallel using asyncio.

---

## Credit Scoring Algorithm

```
Score (0-100) =
  (min(DSCR, 3) / 3) × 40        # DSCR contributes up to 40 points
  + (min(months, 24) / 24) × 30  # Data length contributes up to 30 points
  + (min(revenue, 200K) / 200K) × 30  # Revenue level contributes up to 30 points

Risk Level:
  score ≥ 65 → LOW
  score ≥ 40 → MEDIUM
  score < 40 → HIGH

Recommended Loan = min(net_surplus × 3, avg_monthly_revenue × 12)
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/upload` | Upload artifacts, returns `job_id` |
| `GET`  | `/api/v1/status/{job_id}` | Poll processing status |
| `GET`  | `/api/v1/report/{job_id}` | Get complete credit report JSON |
| `GET`  | `/api/v1/report/{job_id}/pdf` | Download PDF credit report |
| `GET`  | `/health` | Health check |
| `GET`  | `/docs` | Interactive API documentation (Swagger) |

---

## Data Privacy

- Files are processed in-memory and **not stored permanently**
- No data is sent to third parties beyond OpenAI API calls
- OpenAI API calls use the user's own API key
- Generated PDFs are stored locally in `data/outputs/` only
- Compliant with **India's DPDP Act 2023**
