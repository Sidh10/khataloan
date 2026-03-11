"""
upi_pipeline.py
───────────────
Parses UPI payment screenshots using GPT-4o Vision.
Handles: PhonePe, GPay, Paytm, BHIM, and generic UPI app screenshots.
"""

import base64
import json
from openai import OpenAI
from api.schemas import Transaction, TransactionType, TransactionCategory

client = OpenAI()

UPI_PROMPT = """
This is a screenshot from a UPI payment app (PhonePe / GPay / Paytm / BHIM).
Extract the transaction details:
- date (string, from the screenshot)
- party (sender or receiver name)
- amount (numeric value only)
- type ("credit" if money was received / "debit" if money was sent)
- transaction_id (UPI reference number if visible)
- notes (payment note/description if any)
- confidence (0.0–1.0)

Respond ONLY with a single JSON object. No markdown, no explanation.
"""


def parse_upi_screenshot(image_bytes: bytes) -> Transaction | None:
    """Extract transaction details from a single UPI screenshot."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": UPI_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }
        ],
        max_tokens=500,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        item = json.loads(raw)
        return Transaction(
            date=item.get("date"),
            party=item.get("party"),
            amount=float(item.get("amount", 0)),
            type=TransactionType(item.get("type", "unknown")),
            category=TransactionCategory.OTHER,
            notes=item.get("notes") or item.get("transaction_id"),
            source="upi",
            confidence=float(item.get("confidence", 0.95)),
        )
    except Exception:
        return None


def run_upi_pipeline(upi_screenshots: list[tuple[str, bytes]]) -> list[Transaction]:
    """Process all UPI screenshots and return transaction list."""
    transactions = []
    for filename, image_bytes in upi_screenshots:
        t = parse_upi_screenshot(image_bytes)
        if t:
            transactions.append(t)
    return transactions
