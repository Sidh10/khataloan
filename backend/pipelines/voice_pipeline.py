"""
voice_pipeline.py
─────────────────
Transcribes regional-language voice notes using OpenAI Whisper,
then uses GPT-4o to extract structured financial transactions
from natural speech patterns.

Handles: Hindi, Marathi, Tamil, Gujarati, Punjabi, and English voice notes.
Example: "Ramesh ne aaj paanch sau diye" → {party: Ramesh, amount: 500, type: credit}

Regional Translation Layer:
  Includes a Bhashini API–ready transformation function that detects the
  source language, builds a RegionalContext object, and passes a
  standardised English translation downstream to reconstruct_agent.
  When Bhashini API credentials become available, swap the heuristic
  detection logic for real API calls — no other changes needed.
"""

import json
import io
from openai import OpenAI
from api.schemas import Transaction, TransactionType, TransactionCategory

client = OpenAI()

# ── Supported Indian languages (ISO 639-1 + BCP-47 where applicable)
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "bn": "Bengali",
    "te": "Telugu",
    "en": "English",
}

# Simple keyword heuristics for language detection (placeholder for Bhashini)
_LANG_HINTS = {
    "hi": ["hai", "ka", "ki", "ko", "ne", "diya", "liya", "paisa", "hazaar", "rupaye", "aaj", "kal"],
    "mr": ["aahe", "dila", "ghya", "paise", "rupaye", "aaj", "mala"],
    "ta": ["irukku", "panam", "kuduthu", "vaangi", "inru"],
    "gu": ["che", "rupiya", "aapya", "lidha", "paisa"],
    "pa": ["hai", "ditta", "litta", "paise", "rupaye"],
    "bn": ["taka", "diyeche", "niyeche", "aaj"],
    "te": ["undi", "ichadu", "rupayalu", "ivvandi"],
}

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


# ── Regional Translation Layer ───────────────────────────────
def _detect_language(text: str) -> str:
    """
    Lightweight language detection using keyword heuristics.
    Returns ISO 639-1 code.  Will be replaced by Bhashini API.
    """
    text_lower = text.lower()
    scores = {}
    for lang, keywords in _LANG_HINTS.items():
        scores[lang] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] >= 2 else "en"  # fallback to English


def build_regional_context(transcription: str) -> dict:
    """
    Build a RegionalContext object from transcribed text.

    This is the Bhashini API integration point:
    ┌─────────────────────────────────────────────────────┐
    │  When Bhashini credentials are available:           │
    │  1. Replace _detect_language() with Bhashini NLU    │
    │  2. Replace standardized_text with Bhashini         │
    │     translation endpoint output                     │
    │  3. Add script transliteration if needed            │
    └─────────────────────────────────────────────────────┘

    Returns:
        dict with keys:
            - source_language: ISO 639-1 code
            - source_language_name: Human-readable name
            - original_text: Raw Whisper transcription
            - standardized_text: English-normalised text for reconstruct_agent
            - confidence: Detection confidence (0.0–1.0)
            - bhashini_enabled: Whether real Bhashini API was used
    """
    detected_lang = _detect_language(transcription)
    lang_name = SUPPORTED_LANGUAGES.get(detected_lang, "Unknown")

    # For now, Whisper already returns decent English-mixed transcriptions.
    # When Bhashini is live, this will be a proper translation call.
    standardized = transcription  # placeholder — pass-through

    return {
        "source_language": detected_lang,
        "source_language_name": lang_name,
        "original_text": transcription,
        "standardized_text": standardized,
        "confidence": 0.85 if detected_lang != "en" else 0.95,
        "bhashini_enabled": False,
    }


def run_voice_pipeline(voice_notes: list[tuple[str, bytes]]) -> list[Transaction]:
    """
    Transcribe all voice notes, build regional context,
    and extract transactions.

    Returns list of Transaction objects. Each transaction's `notes`
    field is enriched with the detected source language.
    """
    all_transactions = []
    for filename, audio_bytes in voice_notes:
        transcription = transcribe_audio(audio_bytes, filename)
        if not transcription:
            continue

        # Build regional context (Bhashini placeholder)
        regional_ctx = build_regional_context(transcription)

        # Extract transactions from the standardised text
        txns = extract_transactions_from_transcript(regional_ctx["standardized_text"])

        # Enrich each transaction with regional metadata
        for t in txns:
            lang_tag = f"[{regional_ctx['source_language_name']}]"
            t.notes = f"{lang_tag} {t.notes}" if t.notes else lang_tag

        all_transactions.extend(txns)
    return all_transactions
