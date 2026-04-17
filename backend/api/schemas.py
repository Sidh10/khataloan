from pydantic import BaseModel
from typing import Optional
from enum import Enum


class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    UNKNOWN = "unknown"


class TransactionCategory(str, Enum):
    SALES = "sales"
    INVENTORY = "inventory"
    LABOUR = "labour"
    LOAN_REPAYMENT = "loan_repayment"
    UTILITIES = "utilities"
    OTHER = "other"


class Transaction(BaseModel):
    date: Optional[str]
    party: Optional[str]
    amount: float
    type: TransactionType
    category: TransactionCategory = TransactionCategory.OTHER
    notes: Optional[str]
    source: str  # "ledger", "voice", "upi"
    confidence: float = 1.0


class CreditMetrics(BaseModel):
    monthly_avg_revenue: float
    monthly_avg_expenses: float
    net_monthly_surplus: float
    dscr: float
    creditworthiness_score: int  # 0–100
    risk_level: str              # LOW / MEDIUM / HIGH
    recommended_loan_limit: float
    analysis_period: str


class CreditProfileResponse(BaseModel):
    job_id: str
    business_name: Optional[str]
    transactions: list[Transaction]
    metrics: CreditMetrics
    narrative: str
    missing_data_flags: list[str]
    pdf_url: str


class ProcessingStatus(BaseModel):
    job_id: str
    status: str   # queued | processing | complete | failed
    stage: str    # ingest | ocr | voice | upi | reconstruct | report
    progress: int # 0–100
    message: str
