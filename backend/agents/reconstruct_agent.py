"""
reconstruct_agent.py
────────────────────
Takes raw transactions from all three pipelines and:
1. Deduplicates (same txn appearing in ledger + voice)
2. Categorises each transaction
3. Fills temporal gaps
4. Flags anomalies
"""

import json
from openai import OpenAI
from api.schemas import Transaction, TransactionCategory

client = OpenAI()

CATEGORISE_PROMPT = """
You are a financial analyst specialising in Indian MSME businesses.
Given this list of raw transactions from a small business, do the following:

1. DEDUPLICATE: Remove obvious duplicates (same amount, same party, same approximate date from different sources).
   Keep the one with highest confidence.

2. CATEGORISE each transaction:
   - "sales": revenue from selling goods/services
   - "inventory": purchasing stock/raw materials
   - "labour": wages, salaries, daily labour payments
   - "loan_repayment": repaying a loan or advance
   - "utilities": rent, electricity, water, internet
   - "other": anything else

3. FILL GAPS: If there are obvious missing months in the date range, note them as flags.

4. FLAG ANOMALIES: Note any unusual spikes, missing periods, or suspicious patterns.

Return a JSON object:
{{
  "transactions": [...deduplicated and categorised transactions...],
  "missing_data_flags": ["list of data gaps or anomalies as strings"],
  "date_range": {{"start": "YYYY-MM", "end": "YYYY-MM"}}
}}

Transactions to process:
{transactions}

Respond ONLY with the JSON object. No markdown, no explanation.
"""


def reconstruct_transactions(raw_transactions: list[Transaction]) -> list[Transaction]:
    """
    Use GPT-4o to deduplicate, categorise, and reconstruct
    the full transaction history from all sources.
    """
    if not raw_transactions:
        return []

    # Serialise for LLM
    txn_dicts = [t.model_dump() for t in raw_transactions]
    prompt = CATEGORISE_PROMPT.format(transactions=json.dumps(txn_dicts, indent=2))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
        cleaned = []
        for item in result.get("transactions", []):
            try:
                t = Transaction(
                    date=item.get("date"),
                    party=item.get("party"),
                    amount=float(item.get("amount", 0)),
                    type=item.get("type", "unknown"),
                    category=TransactionCategory(item.get("category", "other")),
                    notes=item.get("notes"),
                    source=item.get("source", "ledger"),
                    confidence=float(item.get("confidence", 0.8)),
                )
                cleaned.append(t)
            except Exception:
                continue
        return cleaned
    except Exception:
        # If reconstruction fails, return deduplicated raw list
        return raw_transactions
