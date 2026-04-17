"""
seed_demo_data.py
─────────────────
Creates synthetic demo data for the KhataLoan prototype.
Generates THREE distinct business personas to demonstrate the
LangGraph agent's ability to handle diverse data densities:

  1. "The Consistent Kirana"  — High UPI volume, low risk, 3 years steady
  2. "The Seasonal Artisan"   — Festive spikes (Oct-Dec), monsoon gaps, medium risk
  3. "The New Entrant"        — 6-month history, mostly voice notes, high risk

Usage: python scripts/seed_demo_data.py [--persona all|kirana|artisan|entrant]
"""

import json
import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from agents.report_agent import generate_credit_report, compute_metrics
from utils.pdf_generator import generate_pdf
from api.schemas import Transaction, TransactionType, TransactionCategory


# ═══════════════════════════════════════════════════════════════
# PERSONA 1: "The Consistent Kirana"
# ─────────────────────────────────────────────────────────────
# Ramesh Kirana Store — Neighbourhood grocery in Pune.
# 3 years of steady ledger records, high UPI transaction volume,
# low risk, strong DSCR (1.8+).
# This persona proves the agent works on ideal, data-rich profiles.
# ═══════════════════════════════════════════════════════════════

KIRANA_TRANSACTIONS = [
    # ── 2022 (Year 1 — establishing baseline) ──────────────
    # Jan 2022
    Transaction(date="2022-01-05", party="Daily Sales",       amount=3100,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.94),
    Transaction(date="2022-01-08", party="Wholesale Supplier", amount=17500, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="ledger", confidence=0.92),
    Transaction(date="2022-01-20", party="Ramesh Kumar",      amount=85000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2022-01-28", party="Electricity Board", amount=1700,  type=TransactionType.DEBIT,  category=TransactionCategory.UTILITIES, source="upi",    confidence=0.99),
    # Feb 2022
    Transaction(date="2022-02-01", party="Monthly Sales",     amount=88000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.93),
    Transaction(date="2022-02-12", party="Godown Supplies",   amount=21000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    Transaction(date="2022-02-20", party="Helper Salary",     amount=7500,  type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="upi",    confidence=0.99),
    # Mar 2022
    Transaction(date="2022-03-01", party="Monthly Sales",     amount=95000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.94),
    Transaction(date="2022-03-15", party="Fresh Stock",       amount=24000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    Transaction(date="2022-03-28", party="Rent",              amount=7000,  type=TransactionType.DEBIT,  category=TransactionCategory.UTILITIES, source="upi",    confidence=0.99),
    # Apr 2022
    Transaction(date="2022-04-01", party="Monthly Sales",     amount=91000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2022-04-15", party="Supplier",          amount=19000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    # May 2022
    Transaction(date="2022-05-01", party="Monthly Sales",     amount=97000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.95),
    Transaction(date="2022-05-20", party="Stock Purchase",    amount=26000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.99),
    # Jun 2022
    Transaction(date="2022-06-01", party="Monthly Sales",     amount=93000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.93),
    Transaction(date="2022-06-18", party="Labour",            amount=8500,  type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="upi",    confidence=0.99),
    # Jul 2022
    Transaction(date="2022-07-01", party="Monthly Sales",     amount=82000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.91),
    Transaction(date="2022-07-10", party="Supplier",          amount=16000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    # Aug 2022
    Transaction(date="2022-08-01", party="Monthly Sales",     amount=89000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2022-08-25", party="Rent",              amount=7000,  type=TransactionType.DEBIT,  category=TransactionCategory.UTILITIES, source="upi",    confidence=0.99),
    # Sep 2022
    Transaction(date="2022-09-01", party="Monthly Sales",     amount=94000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.93),
    Transaction(date="2022-09-15", party="Festival Stock",    amount=32000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    # Oct 2022 — Diwali bump
    Transaction(date="2022-10-01", party="Monthly Sales",     amount=128000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.95),
    Transaction(date="2022-10-20", party="Extra Staff",       amount=10000, type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="upi",    confidence=0.99),
    # Nov 2022
    Transaction(date="2022-11-01", party="Monthly Sales",     amount=96000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2022-11-15", party="Supplier",          amount=22000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    # Dec 2022
    Transaction(date="2022-12-01", party="Monthly Sales",     amount=101000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.94),
    Transaction(date="2022-12-20", party="Year-end Stock",    amount=28000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),

    # ── 2023 (Year 2 — growth) ─────────────────────────────
    Transaction(date="2023-01-01", party="Monthly Sales",     amount=93000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2023-01-15", party="Wholesale",         amount=20000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    Transaction(date="2023-02-01", party="Monthly Sales",     amount=91000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.93),
    Transaction(date="2023-02-18", party="Helper Salary",     amount=8000,  type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="upi",    confidence=0.99),
    Transaction(date="2023-03-01", party="Monthly Sales",     amount=105000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2023-03-12", party="Fresh Stock",       amount=27000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    Transaction(date="2023-04-01", party="Monthly Sales",     amount=99000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2023-05-01", party="Monthly Sales",     amount=112000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2023-05-20", party="Stock Purchase",    amount=30000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    Transaction(date="2023-06-01", party="Monthly Sales",     amount=101000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.93),
    Transaction(date="2023-07-01", party="Monthly Sales",     amount=78000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.91),
    Transaction(date="2023-08-01", party="Monthly Sales",     amount=92000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2023-09-01", party="Monthly Sales",     amount=98000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2023-10-01", party="Monthly Sales",     amount=141000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.95),
    Transaction(date="2023-10-20", party="Extra Staff",       amount=12000, type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="upi",    confidence=0.99),
    Transaction(date="2023-11-01", party="Monthly Sales",     amount=103000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2023-12-01", party="Monthly Sales",     amount=108000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.94),
    Transaction(date="2023-12-20", party="Year-end Stock",    amount=32000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),

    # ── 2024 (Year 3 — continued stability) ────────────────
    Transaction(date="2024-01-03", party="Daily Sales",       amount=3200,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.95),
    Transaction(date="2024-01-05", party="Wholesale Supplier",amount=18000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.99),
    Transaction(date="2024-01-18", party="Daily Sales",       amount=2900,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.88),
    Transaction(date="2024-01-25", party="Ramesh Kumar",      amount=91000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2024-01-28", party="Electricity Board", amount=1800,  type=TransactionType.DEBIT,  category=TransactionCategory.UTILITIES, source="upi",    confidence=0.99),
    Transaction(date="2024-02-01", party="Monthly Sales",     amount=88500, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.93),
    Transaction(date="2024-02-10", party="Godown Supplies",   amount=22000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    Transaction(date="2024-02-20", party="Helper Salary",     amount=8000,  type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="voice",  confidence=0.85),
    Transaction(date="2024-03-01", party="Monthly Sales",     amount=102000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.94),
    Transaction(date="2024-03-12", party="Fresh Stock",       amount=25000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.99),
    Transaction(date="2024-03-28", party="Rent",              amount=7500,  type=TransactionType.DEBIT,  category=TransactionCategory.UTILITIES, source="upi",    confidence=0.99),
    Transaction(date="2024-04-01", party="Monthly Sales",     amount=97000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2024-04-15", party="Supplier",          amount=20000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.87),
    Transaction(date="2024-05-01", party="Monthly Sales",     amount=108000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2024-05-20", party="Stock Purchase",    amount=28000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    Transaction(date="2024-06-01", party="Monthly Sales",     amount=99500, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.93),
    Transaction(date="2024-06-18", party="Labour",            amount=9000,  type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="voice",  confidence=0.84),
    Transaction(date="2024-07-01", party="Monthly Sales",     amount=71000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.91),
    Transaction(date="2024-07-10", party="Supplier",          amount=15000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
    Transaction(date="2024-08-01", party="Monthly Sales",     amount=85000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2024-09-01", party="Monthly Sales",     amount=93000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2024-09-15", party="Festival Stock",    amount=35000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.88),
    Transaction(date="2024-10-01", party="Monthly Sales",     amount=142000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2024-10-20", party="Extra Staff",       amount=12000, type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="upi",    confidence=0.99),
    Transaction(date="2024-11-01", party="Monthly Sales",     amount=98000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2024-12-01", party="Monthly Sales",     amount=105000,type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.94),
    Transaction(date="2024-12-20", party="Year-end Stock",    amount=30000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.98),
]


# ═══════════════════════════════════════════════════════════════
# PERSONA 2: "The Seasonal Artisan"
# ─────────────────────────────────────────────────────────────
# Lakshmi Handicrafts — Block-printing artisan in Jaipur.
# Sharp seasonal revenue peaks during Oct-Dec (festive/tourist season).
# Dramatic monsoon dip (Jul-Sep). Temporal gaps in records.
# Medium risk — viable but seasonal dependency adds uncertainty.
# ═══════════════════════════════════════════════════════════════

ARTISAN_TRANSACTIONS = [
    # ── 2023 ────────────────────────────────────────────────
    # Jan 2023 — moderate post-season
    Transaction(date="2023-01-05", party="Tourist Shop",      amount=18000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.89),
    Transaction(date="2023-01-20", party="Fabric Supplier",   amount=8000,  type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="ledger", confidence=0.87),
    # Feb 2023
    Transaction(date="2023-02-01", party="Online Orders",     amount=22000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.98),
    Transaction(date="2023-02-15", party="Dye Supplier",      amount=5500,  type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.82),
    # Mar 2023
    Transaction(date="2023-03-01", party="Exhibition Sales",  amount=35000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.90),
    Transaction(date="2023-03-10", party="Wood Blocks",       amount=12000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.80),
    # Apr 2023
    Transaction(date="2023-04-01", party="Monthly Sales",     amount=15000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.88),
    Transaction(date="2023-04-20", party="Rent",              amount=5000,  type=TransactionType.DEBIT,  category=TransactionCategory.UTILITIES, source="upi",    confidence=0.99),
    # May 2023
    Transaction(date="2023-05-01", party="Monthly Sales",     amount=12000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.78),
    # Jun 2023  — start of monsoon slowdown
    Transaction(date="2023-06-01", party="Monthly Sales",     amount=8000,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.75),
    # Jul 2023  — GAP: no records (monsoon shutdown)
    # Aug 2023  — GAP: no records (monsoon shutdown)
    # Sep 2023  — trickle restart
    Transaction(date="2023-09-15", party="Small Order",       amount=6000,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.72),
    # Oct 2023  — festive season BEGINS 🎉
    Transaction(date="2023-10-01", party="Diwali Orders",     amount=55000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.94),
    Transaction(date="2023-10-10", party="Bulk Fabric",       amount=18000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.97),
    Transaction(date="2023-10-25", party="Corporate Gift Order",amount=42000,type=TransactionType.CREDIT,category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    # Nov 2023
    Transaction(date="2023-11-01", party="Festival Sales",    amount=68000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.93),
    Transaction(date="2023-11-15", party="Extra labour",      amount=10000, type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="voice",  confidence=0.80),
    Transaction(date="2023-11-20", party="Artisan helper",    amount=6000,  type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="voice",  confidence=0.78),
    # Dec 2023
    Transaction(date="2023-12-01", party="Christmas Orders",  amount=61000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.98),
    Transaction(date="2023-12-15", party="Year-end Stock",    amount=15000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="ledger", confidence=0.90),

    # ── 2024 (repeating seasonal pattern) ───────────────────
    Transaction(date="2024-01-05", party="Post-season Sales", amount=19000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.88),
    Transaction(date="2024-02-01", party="Online Orders",     amount=21000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.98),
    Transaction(date="2024-03-01", party="Holi Fair",         amount=38000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.91),
    Transaction(date="2024-03-15", party="Dye + Fabric",      amount=14000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.79),
    Transaction(date="2024-04-01", party="Monthly Sales",     amount=14000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.76),
    Transaction(date="2024-05-01", party="Monthly Sales",     amount=11000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.74),
    # Jun 2024 — monsoon dip
    Transaction(date="2024-06-01", party="Small Order",       amount=5000,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.70),
    # Jul 2024 — GAP
    # Aug 2024 — GAP
    Transaction(date="2024-09-10", party="Resume Work",       amount=7000,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.73),
    # Oct 2024 — festive season
    Transaction(date="2024-10-01", party="Navratri Orders",   amount=52000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="ledger", confidence=0.93),
    Transaction(date="2024-10-15", party="Bulk Fabric",       amount=20000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.97),
    Transaction(date="2024-11-01", party="Festival Sales",    amount=72000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.99),
    Transaction(date="2024-11-15", party="Artisan Helper",    amount=8000,  type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="voice",  confidence=0.79),
    Transaction(date="2024-12-01", party="Christmas Orders",  amount=58000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.98),
    Transaction(date="2024-12-20", party="Year-end Stock",    amount=12000, type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="ledger", confidence=0.89),
]


# ═══════════════════════════════════════════════════════════════
# PERSONA 3: "The New Entrant"
# ─────────────────────────────────────────────────────────────
# Priya's Tiffin Service — Home-based tiffin delivery in Mumbai.
# Only 6 months of operation. Records are sparse and mostly
# voice notes (no proper ledger yet). Very few UPI entries.
# High risk — limited history makes assessment uncertain.
# This persona tests the agent's edge-case handling.
# ═══════════════════════════════════════════════════════════════

ENTRANT_TRANSACTIONS = [
    # ── Jul 2024 (startup month) ───────────────────────────
    Transaction(date="2024-07-05", party="First customers",   amount=4500,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.70),
    Transaction(date="2024-07-10", party="Groceries",         amount=3000,  type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.68),
    Transaction(date="2024-07-20", party="Tiffin orders",     amount=6200,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.72),
    Transaction(date="2024-07-25", party="Gas cylinder",      amount=1200,  type=TransactionType.DEBIT,  category=TransactionCategory.UTILITIES, source="voice",  confidence=0.65),
    # Aug 2024
    Transaction(date="2024-08-01", party="Monthly customers", amount=12000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.74),
    Transaction(date="2024-08-08", party="Groceries bulk",    amount=5500,  type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.70),
    Transaction(date="2024-08-20", party="New office order",  amount=8000,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.76),
    # Sep 2024
    Transaction(date="2024-09-01", party="Regular customers", amount=15000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.75),
    Transaction(date="2024-09-10", party="Groceries",         amount=6000,  type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.71),
    Transaction(date="2024-09-18", party="Container purchase",amount=3500,  type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="upi",    confidence=0.95),
    # Oct 2024
    Transaction(date="2024-10-01", party="Monthly customers", amount=18000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.77),
    Transaction(date="2024-10-12", party="Groceries",         amount=7000,  type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.72),
    Transaction(date="2024-10-25", party="Diwali special",    amount=12000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.96),
    # Nov 2024
    Transaction(date="2024-11-01", party="Monthly customers", amount=16500, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.76),
    Transaction(date="2024-11-15", party="Groceries",         amount=6500,  type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.71),
    Transaction(date="2024-11-20", party="Helper payment",    amount=4000,  type=TransactionType.DEBIT,  category=TransactionCategory.LABOUR,    source="voice",  confidence=0.68),
    # Dec 2024
    Transaction(date="2024-12-01", party="Monthly customers", amount=19000, type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="voice",  confidence=0.78),
    Transaction(date="2024-12-10", party="Groceries",         amount=7500,  type=TransactionType.DEBIT,  category=TransactionCategory.INVENTORY, source="voice",  confidence=0.73),
    Transaction(date="2024-12-20", party="Year-end bonus",    amount=3000,  type=TransactionType.CREDIT, category=TransactionCategory.SALES,     source="upi",    confidence=0.94),
]


# ═══════════════════════════════════════════════════════════════
# Persona metadata for reports
# ═══════════════════════════════════════════════════════════════

PERSONAS = {
    "kirana": {
        "name": "Ramesh Kirana Store",
        "description": "Consistent Kirana — 3yr steady, high UPI, low risk",
        "transactions": KIRANA_TRANSACTIONS,
        "demo_id": "DEMO_KIRANA",
    },
    "artisan": {
        "name": "Lakshmi Handicrafts",
        "description": "Seasonal Artisan — festive peaks, monsoon gaps, medium risk",
        "transactions": ARTISAN_TRANSACTIONS,
        "demo_id": "DEMO_ARTISAN",
    },
    "entrant": {
        "name": "Priya's Tiffin Service",
        "description": "New Entrant — 6mo history, mostly voice, high risk",
        "transactions": ENTRANT_TRANSACTIONS,
        "demo_id": "DEMO_ENTRANT",
    },
}


def generate_persona_report(key: str, persona: dict):
    """Generate a full credit report for a single persona."""
    print(f"\n{'═'*60}")
    print(f"  {persona['description']}")
    print(f"{'═'*60}")

    report = generate_credit_report(persona["transactions"])
    report["business_name"] = persona["name"]

    pdf_path = generate_pdf(report, persona["demo_id"])
    print(f"  ✅ PDF generated: {pdf_path}")

    # Ensure output directory exists
    os.makedirs("data/outputs", exist_ok=True)

    summary_path = f"data/outputs/{key}_report_summary.json"
    with open(summary_path, "w") as f:
        json.dump({
            "business_name": report["business_name"],
            "persona": key,
            "persona_description": persona["description"],
            "metrics": report["metrics"],
            "narrative": report["narrative"],
            "missing_data_flags": report["missing_data_flags"],
            "total_transactions": len(report["transactions"]),
            "source_breakdown": {
                "ledger": sum(1 for t in persona["transactions"] if t.source == "ledger"),
                "voice":  sum(1 for t in persona["transactions"] if t.source == "voice"),
                "upi":    sum(1 for t in persona["transactions"] if t.source == "upi"),
            },
        }, f, indent=2)

    print(f"  ✅ Summary JSON: {summary_path}")
    print(f"\n  📊 Key Metrics:")
    for k, v in report["metrics"].items():
        print(f"     {k}: {v}")
    print(f"\n  📝 Narrative:\n     {report['narrative']}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Generate KhataLoan demo credit reports")
    parser.add_argument(
        "--persona", choices=["all", "kirana", "artisan", "entrant"],
        default="all",
        help="Which persona(s) to generate (default: all)",
    )
    args = parser.parse_args()

    print("🏦 KhataLoan — Demo Data Seeder")
    print("   Generating credit reports for diverse business personas...\n")

    if args.persona == "all":
        targets = PERSONAS.items()
    else:
        targets = [(args.persona, PERSONAS[args.persona])]

    reports = {}
    for key, persona in targets:
        reports[key] = generate_persona_report(key, persona)

    # Generate combined comparison summary if all personas
    if args.persona == "all":
        print(f"\n{'═'*60}")
        print("  📋 COMPARISON SUMMARY")
        print(f"{'═'*60}")
        print(f"  {'Persona':<25} {'Score':>6} {'Risk':>8} {'DSCR':>6} {'Months':>7}")
        print(f"  {'─'*52}")
        for key, report in reports.items():
            m = report["metrics"]
            print(f"  {PERSONAS[key]['name']:<25} {m['creditworthiness_score']:>6} {m['risk_level']:>8} {m['dscr']:>6} {m['analysis_period']:>7}")

        comparison_path = "data/outputs/persona_comparison.json"
        comparison = {
            key: {
                "business_name": PERSONAS[key]["name"],
                "score": report["metrics"]["creditworthiness_score"],
                "risk_level": report["metrics"]["risk_level"],
                "dscr": report["metrics"]["dscr"],
                "monthly_avg_revenue": report["metrics"]["monthly_avg_revenue"],
                "recommended_loan_limit": report["metrics"]["recommended_loan_limit"],
            }
            for key, report in reports.items()
        }
        with open(comparison_path, "w") as f:
            json.dump(comparison, f, indent=2)
        print(f"\n  ✅ Comparison JSON: {comparison_path}")

    print("\n🎉 Done! All demo reports generated successfully.")


if __name__ == "__main__":
    main()
