"""
ocr_pipeline.py
───────────────
Processes handwritten ledger images using OpenCV preprocessing
and GPT-4o Vision to extract structured financial transactions.

Supports: Hindi, Marathi, Tamil, English, and mixed-script ledgers.
"""

import base64
import json
import cv2
import numpy as np
from openai import OpenAI
from api.schemas import Transaction, TransactionType, TransactionCategory

client = OpenAI()

OCR_PROMPT = """
You are an expert at reading handwritten Indian financial ledgers (bahi-khata).
This image shows a page from a small business ledger written in Hindi, Marathi, Tamil, or English.

Extract ALL financial transactions visible. For each transaction return:
- date (string, best guess if unclear, null if completely unreadable)
- party (name of person/business, null if absent)
- amount (numeric value only, no currency symbols)
- type ("credit" if money received / "debit" if money paid / "unknown" if unclear)
- notes (any additional context)
- confidence (0.0–1.0 reflecting how clearly you could read this entry)

Respond ONLY with a JSON array of transactions. No explanation, no markdown.
Example:
[
  {"date": "2024-01-15", "party": "Ramesh", "amount": 500, "type": "credit", "notes": "grain purchase", "confidence": 0.9},
  {"date": null, "party": "Suresh Transport", "amount": 1200, "type": "debit", "notes": null, "confidence": 0.7}
]
"""


def preprocess_image(image_bytes: bytes) -> bytes:
    """
    Apply OpenCV preprocessing to improve OCR accuracy:
    - Convert to grayscale
    - Deskew (straighten tilted pages)
    - Denoise
    - Enhance contrast via CLAHE
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Deskew
    coords = np.column_stack(np.where(gray < 200))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        (h, w) = gray.shape
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # CLAHE contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    _, processed = cv2.imencode(".jpg", enhanced, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return processed.tobytes()


def extract_transactions_from_image(image_bytes: bytes, filename: str = "") -> list[Transaction]:
    """
    Run GPT-4o Vision on a preprocessed ledger image.
    Returns a list of extracted Transaction objects.
    """
    processed = preprocess_image(image_bytes)
    b64 = base64.b64encode(processed).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": OCR_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }
        ],
        max_tokens=2000,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []

    transactions = []
    for item in items:
        try:
            t = Transaction(
                date=item.get("date"),
                party=item.get("party"),
                amount=float(item.get("amount", 0)),
                type=TransactionType(item.get("type", "unknown")),
                category=TransactionCategory.OTHER,
                notes=item.get("notes"),
                source="ledger",
                confidence=float(item.get("confidence", 0.8)),
            )
            transactions.append(t)
        except Exception:
            continue

    return transactions


def run_ocr_pipeline(ledger_images: list[tuple[str, bytes]]) -> list[Transaction]:
    """Process all uploaded ledger images and return combined transaction list."""
    all_transactions = []
    for filename, image_bytes in ledger_images:
        txns = extract_transactions_from_image(image_bytes, filename)
        all_transactions.extend(txns)
    return all_transactions
