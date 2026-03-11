"""
report_agent.py
───────────────
Computes credit metrics from reconstructed transactions
and uses GPT-4o to generate a plain-English business narrative.
"""

import json
from collections import defaultdict
from openai import OpenAI
from api.schemas import Transaction, TransactionType, CreditMetrics

client = OpenAI()

NARRATIVE_PROMPT = """
You are a senior credit analyst at an Indian bank assessing a small business loan application.
Below are the financial metrics computed from a small business owner's records.

Write a concise, professional credit assessment narrative (3–4 sentences) that:
- Summarises the business's revenue trend
- Notes any seasonal patterns or anomalies
- States the overall creditworthiness
- Recommends whether to proceed with lending

Metrics:
{metrics}

Write in plain English. Be factual and balanced. No bullet points.
"""


def compute_metrics(transactions: list[Transaction]) -> dict:
    """
    Compute core credit metrics from transaction list.
    Returns dict with all metrics + missing_data_flags.
    """
    credits = [t for t in transactions if t.type == TransactionType.CREDIT and t.amount > 0]
    debits  = [t for t in transactions if t.type == TransactionType.DEBIT  and t.amount > 0]

    total_revenue  = sum(t.amount for t in credits)
    total_expenses = sum(t.amount for t in debits)

    # Group by month for averages
    monthly_revenue = defaultdict(float)
    for t in credits:
        month = (t.date or "unknown")[:7]  # YYYY-MM
        monthly_revenue[month] += t.amount

    num_months = max(len(monthly_revenue), 1)
    monthly_avg_revenue  = total_revenue / num_months
    monthly_avg_expenses = total_expenses / num_months
    net_monthly_surplus  = monthly_avg_revenue - monthly_avg_expenses

    # DSCR: Net surplus / estimated monthly debt obligation
    # Assume debt obligation = 10% of avg monthly revenue (conservative)
    estimated_debt_obligation = monthly_avg_revenue * 0.10
    dscr = round(net_monthly_surplus / max(estimated_debt_obligation, 1), 2)

    # Creditworthiness score (0–100)
    score = min(100, max(0, int(
        (min(dscr, 3) / 3) * 40 +          # DSCR contribution (max 40 pts)
        (min(num_months, 24) / 24) * 30 +   # Data length contribution (max 30 pts)
        (min(monthly_avg_revenue, 200000) / 200000) * 30  # Revenue contribution (max 30 pts)
    )))

    risk_level = "LOW" if score >= 65 else "MEDIUM" if score >= 40 else "HIGH"

    # Recommended loan = 3x monthly net surplus, capped at 12x avg monthly revenue
    recommended_loan = min(net_monthly_surplus * 3, monthly_avg_revenue * 12)

    # Date range
    dates = sorted([t.date for t in transactions if t.date])
    date_range = f"{dates[0][:7]} – {dates[-1][:7]}" if dates else "Unknown"

    # Missing data flags
    missing_flags = []
    if num_months < 6:
        missing_flags.append(f"Only {num_months} month(s) of data available — ideally 12+ months needed")
    if not credits:
        missing_flags.append("No revenue transactions detected — ledger may be incomplete")
    if monthly_avg_revenue == 0:
        missing_flags.append("Could not compute revenue — please upload more ledger pages")

    return {
        "monthly_avg_revenue": round(monthly_avg_revenue, 2),
        "monthly_avg_expenses": round(monthly_avg_expenses, 2),
        "net_monthly_surplus": round(net_monthly_surplus, 2),
        "dscr": dscr,
        "creditworthiness_score": score,
        "risk_level": risk_level,
        "recommended_loan_limit": round(max(recommended_loan, 0), 2),
        "analysis_period": date_range,
        "missing_data_flags": missing_flags,
    }


def generate_narrative(metrics: dict) -> str:
    """Use GPT-4o to write a professional credit assessment narrative."""
    prompt = NARRATIVE_PROMPT.format(metrics=json.dumps(metrics, indent=2))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def generate_credit_report(transactions: list[Transaction]) -> dict:
    """
    Full credit report generation:
    1. Compute metrics
    2. Generate narrative
    3. Return complete report dict
    """
    metrics = compute_metrics(transactions)
    narrative = generate_narrative(metrics)

    return {
        "job_id": "",
        "business_name": None,
        "transactions": [t.model_dump() for t in transactions],
        "metrics": {k: v for k, v in metrics.items() if k != "missing_data_flags"},
        "narrative": narrative,
        "missing_data_flags": metrics["missing_data_flags"],
        "pdf_url": "",
    }
