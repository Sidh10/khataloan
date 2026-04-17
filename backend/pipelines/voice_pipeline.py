"""
voice_pipeline.py
─────────────────
Transcribes regional-language voice notes using OpenAI Whisper,
then uses GPT-4o to extract structured financial transactions
from natural speech patterns.

Handles: Hindi, Marathi, Tamil, Gujarati, Punjabi, and English voice notes.
Example: "Ramesh ne aaj paanch sau diye" → {party: Ramesh, amount: 500, type: credit}
"""

import json
import io
from openai import OpenAI
from api.schemas import Transaction, TransactionType, TransactionCategory

client = OpenAI()

EXTRACTION_PROMPT = """
You are an expert at understanding Indian small business accounting spoken in regional languages.
Below is a transcription of a voice note from a shop owner recording their daily transactions.

Extract ALL financial transactions mentioned. For each transaction return:
- date (string if mentioned, null if not)
- party (name of person or business, null if not mentioned)
- amount (numeric value only — interpret spoken numbers: "paanch sau" = 500, "ek hazaar" = 1000)
- type ("credit" if money received / "debit" if money paid / "unknown")
- notes (any additional context from the note)
- confidence (0.0–1.0)

Transcription:
{transcription}

Respond ONLY with a JSON array. No explanation, no markdown.
"""


def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    """
    Use Whisper API to transcribe audio. Automatically detects language.
    Returns transcribed text.
    """
    audio_file = io.BytesIO(audio_bytes)
    # Whisper needs a filename hint for format detection
    audio_file.name = filename

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text",
    )
    return transcript


def extract_transactions_from_transcript(transcription: str) -> list[Transaction]:
    """
    Use GPT-4o to extract structured transactions from Whisper transcription.
    """
    prompt = EXTRACTION_PROMPT.format(transcription=transcription)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
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
                source="voice",
                confidence=float(item.get("confidence", 0.75)),
            )
            transactions.append(t)
        except Exception:
            continue

    return transactions


def run_voice_pipeline(voice_notes: list[tuple[str, bytes]]) -> list[Transaction]:
    """Transcribe all voice notes and extract transactions."""
    all_transactions = []
    for filename, audio_bytes in voice_notes:
        transcription = transcribe_audio(audio_bytes, filename)
        if transcription:
            txns = extract_transactions_from_transcript(transcription)
            all_transactions.extend(txns)
    return all_transactions
