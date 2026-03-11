"""
seed_demo_data.py
─────────────────
Creates synthetic demo data for the KhataLoan prototype.
Run this to generate sample ledger text and a demo credit profile
without needing real uploaded files.

Usage: python scripts/seed_demo_data.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from agents.report_agent import generate_credit_report, compute_metrics
from utils.pdf_generator import generate_pdf
from api.schemas import Transaction, TransactionType, TransactionCategory

# ── Synthetic 12-month transaction history for "Ramesh Kirana Store" ───
DEMO_TRANSACTIONS = [
    # Jan 2024
    Transaction(date="2024-01-03", party="Daily Sales",      amount=3200,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.95),
    Transaction(date="2024-01-05", party="Wholesale Supplier",amount=18000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY,  source="ledger", confidence=0.92),
    Transaction(date="2024-01-18", party="Daily Sales",      amount=2900,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="voice",  confidence=0.88),
    Transaction(date="2024-01-25", party="Ramesh Kumar",     amount=91000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.90),
    Transaction(date="2024-01-28", party="Electricity Board",amount=1800,  type=TransactionType.DEBIT,  category=TransactionCategory.UTILITIES,  source="upi",    confidence=0.99),
    # Feb 2024
    Transaction(date="2024-02-01", party="Monthly Sales",    amount=88500, type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.93),
    Transaction(date="2024-02-10", party="Godown Supplies",  amount=22000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY,  source="ledger", confidence=0.91),
    Transaction(date="2024-02-20", party="Helper Salary",    amount=8000,  type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,     source="voice",  confidence=0.85),
    # Mar 2024
    Transaction(date="2024-03-01", party="Monthly Sales",    amount=102000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.94),
    Transaction(date="2024-03-12", party="Fresh Stock",      amount=25000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY,  source="ledger", confidence=0.90),
    Transaction(date="2024-03-28", party="Rent",             amount=7500,  type=TransactionType.DEBIT,  category=TransactionCategory.UTILITIES,  source="upi",    confidence=0.99),
    # Apr 2024
    Transaction(date="2024-04-01", party="Monthly Sales",    amount=97000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.93),
    Transaction(date="2024-04-15", party="Supplier",         amount=20000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY,  source="voice",  confidence=0.87),
    # May 2024
    Transaction(date="2024-05-01", party="Monthly Sales",    amount=108000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.95),
    Transaction(date="2024-05-20", party="Stock Purchase",   amount=28000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY,  source="ledger", confidence=0.92),
    # Jun 2024
    Transaction(date="2024-06-01", party="Monthly Sales",    amount=99500, type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.93),
    Transaction(date="2024-06-18", party="Labour",           amount=9000,  type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,     source="voice",  confidence=0.84),
    # Jul 2024 — monsoon dip
    Transaction(date="2024-07-01", party="Monthly Sales",    amount=71000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.91),
    Transaction(date="2024-07-10", party="Supplier",         amount=15000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY,  source="ledger", confidence=0.90),
    # Aug 2024
    Transaction(date="2024-08-01", party="Monthly Sales",    amount=85000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.92),
    # Sep 2024
    Transaction(date="2024-09-01", party="Monthly Sales",    amount=93000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.93),
    Transaction(date="2024-09-15", party="Festival Stock",   amount=35000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY,  source="voice",  confidence=0.88),
    # Oct 2024 — Diwali spike
    Transaction(date="2024-10-01", party="Monthly Sales",    amount=142000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.95),
    Transaction(date="2024-10-20", party="Extra Staff",      amount=12000, type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,     source="upi",    confidence=0.99),
    # Nov 2024
    Transaction(date="2024-11-01", party="Monthly Sales",    amount=98000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.93),
    # Dec 2024
    Transaction(date="2024-12-01", party="Monthly Sales",    amount=105000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,      source="ledger", confidence=0.94),
    Transaction(date="2024-12-20", party="Year-end Stock",   amount=30000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY,  source="voice",  confidence=0.87),
]


def main():
    print("🏦 KhataLoan — Generating demo credit report...")
    report = generate_credit_report(DEMO_TRANSACTIONS)
    report["business_name"] = "Ramesh Kirana Store"

    pdf_path = generate_pdf(report, "DEMO0001")
    print(f"✅ PDF generated: {pdf_path}")

    summary_path = "data/outputs/demo_report_summary.json"
    with open(summary_path, "w") as f:
        # Save metrics summary (not full transactions for brevity)
        json.dump({
            "business_name": report["business_name"],
            "metrics": report["metrics"],
            "narrative": report["narrative"],
            "missing_data_flags": report["missing_data_flags"],
            "total_transactions": len(report["transactions"]),
        }, f, indent=2)

    print(f"✅ Summary JSON: {summary_path}")
    print("\n📊 Key Metrics:")
    for k, v in report["metrics"].items():
        print(f"   {k}: {v}")
    print(f"\n📝 Narrative:\n   {report['narrative']}")


if __name__ == "__main__":
    main()
