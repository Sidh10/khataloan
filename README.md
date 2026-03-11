# KhataLoan 📒→🏦

> **From Bahi-Khata to Bank Loan — powered by Generative AI**

KhataLoan is the first system that reconstructs a **bank-ready financial credit profile** for Indian MSMEs from zero digital history — starting from photographs of handwritten ledgers, regional-language voice notes, and UPI screenshots.

---

## 🎯 The Problem

India has **63 million MSMEs** contributing 30% of GDP. Over **84% have never accessed formal credit** — not because they aren't creditworthy, but because banks demand digital records that informal businesses simply don't have.

Most small business owners only have:
- 📒 Handwritten bahi-khata notebooks (Hindi / Marathi / Tamil)
- 🎙️ WhatsApp voice notes: *"Ramesh ne aaj 500 diye"*
- 📱 Fragmented UPI payment screenshots

**KhataLoan bridges this gap.** It reads what they have, reconstructs their financial history, and generates a structured credit profile that banks can actually use.

> 💡 This targets India's **₹25 lakh crore MSME credit gap** — the largest financially excluded population on earth. [RBI, 2024]

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        KhataLoan                            │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  INGEST  │───▶│  UNDERSTAND  │───▶│   RECONSTRUCT    │  │
│  │          │    │              │    │                  │  │
│  │ • Photos │    │ • GPT-4o     │    │ • LangGraph      │  │
│  │ • Audio  │    │   Vision OCR │    │   Agent          │  │
│  │ • UPI    │    │ • Whisper    │    │ • Deduplication  │  │
│  │   shots  │    │   voice STT  │    │ • Gap filling    │  │
│  └──────────┘    └──────────────┘    └────────┬─────────┘  │
│                                               │             │
│  ┌────────────────────────────────────────────▼──────────┐  │
│  │                      OUTPUT                           │  │
│  │  • Bank-ready PDF credit report                       │  │
│  │  • Business health dashboard (React)                  │  │
│  │  • Gap report: what's missing & why                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TailwindCSS, Axios |
| **Backend** | FastAPI, Python 3.11 |
| **OCR** | GPT-4o Vision (handwritten Devanagari/Tamil/English) |
| **Voice STT** | OpenAI Whisper API (multilingual) |
| **Agent Orchestration** | LangGraph |
| **LLM** | GPT-4o (transaction extraction, narrative generation) |
| **PDF Generation** | ReportLab |
| **Database** | PostgreSQL + SQLAlchemy |
| **Image Processing** | OpenCV (deskew, denoise, contrast) |
| **Deployment** | Docker + Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- OpenAI API key

### 1. Clone the repository
```bash
git clone https://github.com/your-team/khataloan.git
cd khataloan
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Add your OpenAI API key to .env
```

### 3. Run with Docker (recommended)
```bash
docker-compose up --build
```

The app will be available at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 4. Or run locally (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

---

## 📁 Project Structure

```
khataloan/
│
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   ├── api/
│   │   ├── routes.py            # API route definitions
│   │   └── schemas.py           # Pydantic request/response models
│   ├── agents/
│   │   ├── orchestrator.py      # LangGraph agent graph definition
│   │   ├── monitor_agent.py     # Transaction ingestion & normalisation
│   │   ├── reconstruct_agent.py # Deduplication, gap-filling, categorisation
│   │   └── report_agent.py      # Credit profile narrative generation
│   ├── pipelines/
│   │   ├── ocr_pipeline.py      # GPT-4o Vision OCR for ledger images
│   │   ├── voice_pipeline.py    # Whisper STT + LLM intent extraction
│   │   └── upi_pipeline.py      # UPI screenshot parsing
│   └── utils/
│       ├── pdf_generator.py     # ReportLab PDF credit report builder
│       ├── image_processor.py   # OpenCV preprocessing
│       └── db.py                # Database connection & models
│
├── frontend/
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── UploadZone.jsx   # Drag-and-drop multi-file uploader
│       │   ├── ProcessingView.jsx # Live pipeline status tracker
│       │   ├── CreditReport.jsx # Final report display
│       │   └── TransactionTable.jsx
│       ├── pages/
│       │   ├── Home.jsx
│       │   ├── Upload.jsx
│       │   └── Report.jsx
│       └── hooks/
│           └── useUpload.js
│
├── data/
│   ├── samples/                 # Sample ledger images & audio for demo
│   └── outputs/                 # Generated PDF reports
│
├── docs/
│   ├── architecture.md          # Detailed architecture documentation
│   ├── api.md                   # API endpoint documentation
│   └── demo.md                  # How to run the demo
│
├── scripts/
│   └── seed_demo_data.py        # Script to load sample data for demo
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔄 How It Works — Step by Step

### Step 1: Upload Artifacts
The business owner uploads any combination of:
- Photos of handwritten ledger pages
- Voice note recordings (any Indian language)
- UPI transaction screenshots

### Step 2: Multimodal Understanding
Three parallel pipelines run simultaneously:

**OCR Pipeline** (`pipelines/ocr_pipeline.py`)
- OpenCV preprocesses images (deskew, denoise, enhance contrast)
- GPT-4o Vision reads handwritten text — including Devanagari, Tamil, and mixed scripts
- Extracts structured transactions: `{date, party, amount, type, notes}`

**Voice Pipeline** (`pipelines/voice_pipeline.py`)
- Whisper API transcribes audio in the detected language
- GPT-4o extracts financial intent from natural speech
- *"Ramesh ne aaj paanch sau diye"* → `{party: Ramesh, amount: 500, type: credit, date: today}`

**UPI Pipeline** (`pipelines/upi_pipeline.py`)
- GPT-4o Vision parses UPI screenshots
- Extracts: transaction ID, amount, counterparty, timestamp

### Step 3: LangGraph Agent Reconstruction
The `orchestrator.py` agent:
1. **Merges** all three streams into a unified transaction list
2. **Deduplicates** — same transaction in ledger + voice → merged once
3. **Categorises** — inventory, sales, labour, loan repayment, etc.
4. **Fills temporal gaps** — infers missing months from context
5. **Flags anomalies** — unusual spikes, missing periods, round-number patterns

### Step 4: Credit Profile Generation
- Calculates key metrics: Monthly Average Revenue, DSCR, Working Capital Cycle
- GPT-4o writes a plain-English business narrative
- ReportLab generates a structured PDF credit report
- React dashboard displays results with charts and transaction table

---

## 📊 Sample Output

```json
{
  "business_name": "Ramesh Kirana Store",
  "analysis_period": "Jan 2022 – Dec 2024",
  "monthly_avg_revenue": 94500,
  "monthly_avg_expenses": 71200,
  "net_monthly_surplus": 23300,
  "dscr": 1.84,
  "creditworthiness_score": 72,
  "risk_level": "LOW",
  "narrative": "This business shows consistent monthly revenue between ₹80,000–₹1.1L over 36 months, with a seasonal dip in July likely attributable to monsoon patterns. Net creditworthy behaviour observed throughout the analysis period.",
  "recommended_loan_limit": 280000,
  "missing_data_flags": ["Aug 2023 ledger page missing", "No UPI records before Oct 2022"]
}
```

---

## 🗺️ Roadmap

- [x] Project structure & architecture
- [x] OCR pipeline (GPT-4o Vision)
- [x] Voice pipeline (Whisper)
- [x] LangGraph agent orchestration
- [x] PDF credit report generator
- [x] React upload & dashboard UI
- [ ] Bhashini API integration (22 Indian languages — Phase 2)
- [ ] RBI MSME guideline compliance mapping (Phase 2)
- [ ] Mobile PWA (Phase 2)
- [ ] Bank API integration (Phase 3)

---

## 🔐 Privacy & Compliance

- All uploaded data is processed in-memory and never stored permanently without consent
- Generated reports are encrypted at rest (AES-256)
- Compliant with **India's DPDP Act 2023** (Digital Personal Data Protection)
- PII redaction layer before any external API calls

---

## 👥 Team

Built for **Hack & Break Innovation Challenge** on Unstop.

| Role | Responsibility |
|---|---|
| Backend Lead | FastAPI, LangGraph agents, pipelines |
| Frontend Lead | React UI, dashboard, upload flow |
| AI/ML Lead | Prompt engineering, OCR, voice extraction |
| Research Lead | RBI guidelines, credit metrics, compliance |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*KhataLoan — because creditworthiness was never the problem. Data was.*
